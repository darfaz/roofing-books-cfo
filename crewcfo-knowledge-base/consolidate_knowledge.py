#!/usr/bin/env python3
"""
Knowledge Consolidation Script for CrewCFO

This script:
1. Processes chat exports from Claude and ChatGPT
2. Auto-classifies content into appropriate domains
3. Scrapes your own website into markdown
4. Deduplicates similar content
5. Rebuilds the vector store

Usage:
    python consolidate_knowledge.py --process-imports
    python consolidate_knowledge.py --scrape-website https://crewcfo.com
    python consolidate_knowledge.py --dedupe
    python consolidate_knowledge.py --rebuild
    python consolidate_knowledge.py --all
"""
import os
import json
import shutil
import hashlib
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

load_dotenv()

# Optional imports for web scraping
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import html2text
    HAS_HTML2TEXT = True
except ImportError:
    HAS_HTML2TEXT = False

from agents.librarian import Librarian
from loader import DOMAIN_CONFIG, get_domain_stats


# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_DIR = Path("./data")
IMPORTS_DIR = DATA_DIR / "imports"
ARCHIVE_DIR = DATA_DIR / "archive"


# =============================================================================
# IMPORT PROCESSING
# =============================================================================

def process_imports(
    librarian: Librarian,
    dry_run: bool = False,
    confidence_threshold: float = 0.7,
) -> Dict:
    """
    Process all files in the imports folder, classify them,
    and move to appropriate domains.

    Args:
        librarian: Librarian instance
        dry_run: If True, don't actually move files
        confidence_threshold: Minimum confidence to auto-move

    Returns:
        Processing results
    """
    if not IMPORTS_DIR.exists():
        return {"error": "Imports directory not found"}

    results = {
        "processed": 0,
        "moved": 0,
        "kept": 0,
        "errors": [],
        "classifications": [],
    }

    # Get all files in imports
    files = [f for f in IMPORTS_DIR.iterdir() if f.is_file()]

    print(f"\n📥 Processing {len(files)} files from imports...")

    for file_path in files:
        try:
            # Skip hidden files
            if file_path.name.startswith("."):
                continue

            print(f"\n  📄 {file_path.name}")

            # Classify the file
            domain, reasoning = librarian.classify_file(str(file_path))

            classification = {
                "file": file_path.name,
                "domain": domain,
                "reasoning": reasoning,
            }
            results["classifications"].append(classification)

            print(f"     → {domain}: {reasoning[:50]}...")

            # Move file if not dry run and domain is not imports
            if not dry_run and domain != "imports":
                target_dir = DATA_DIR / domain
                target_dir.mkdir(exist_ok=True)
                target_path = target_dir / file_path.name

                # Handle conflicts
                if target_path.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    target_path = target_dir / f"{timestamp}_{file_path.name}"

                shutil.move(str(file_path), str(target_path))
                print(f"     ✅ Moved to {domain}/")
                results["moved"] += 1
            else:
                results["kept"] += 1

            results["processed"] += 1

        except Exception as e:
            results["errors"].append({"file": file_path.name, "error": str(e)})
            print(f"     ❌ Error: {e}")

    return results


def split_chat_export(file_path: Path, output_dir: Path) -> List[Path]:
    """
    Split a large chat export into individual conversations.

    Args:
        file_path: Path to chat export markdown file
        output_dir: Directory to write individual files

    Returns:
        List of created file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Try to split by conversation markers
    # Claude exports often have "---" or "# User:" patterns
    # ChatGPT exports might have different patterns

    created_files = []

    # Simple split by major headers
    sections = content.split("\n# ")

    if len(sections) > 1:
        for i, section in enumerate(sections[1:], 1):
            if len(section.strip()) < 100:
                continue

            # Extract title from first line
            lines = section.strip().split("\n")
            title = lines[0][:50].strip()
            safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
            safe_title = safe_title.replace(" ", "_")

            filename = f"{safe_title}_{i}.md"
            output_path = output_dir / filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# {section}")

            created_files.append(output_path)

    return created_files


# =============================================================================
# WEBSITE SCRAPING
# =============================================================================

def scrape_website(
    base_url: str,
    output_dir: Path,
    max_pages: int = 50,
    include_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
) -> Dict:
    """
    Scrape a website and convert pages to markdown.

    Args:
        base_url: Website URL to scrape
        output_dir: Directory to save markdown files
        max_pages: Maximum pages to scrape
        include_paths: Only scrape paths starting with these
        exclude_paths: Skip paths starting with these

    Returns:
        Scraping results
    """
    if not HAS_BS4:
        return {"error": "BeautifulSoup not installed. Run: pip install beautifulsoup4"}

    if not HAS_HTML2TEXT:
        return {"error": "html2text not installed. Run: pip install html2text"}

    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "scraped": 0,
        "errors": [],
        "files": [],
    }

    visited = set()
    to_visit = [base_url]

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0

    print(f"\n🌐 Scraping {base_url}...")

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)

        if url in visited:
            continue

        visited.add(url)

        try:
            # Parse URL
            parsed = urlparse(url)

            # Check include/exclude paths
            if include_paths:
                if not any(parsed.path.startswith(p) for p in include_paths):
                    continue

            if exclude_paths:
                if any(parsed.path.startswith(p) for p in exclude_paths):
                    continue

            # Fetch page
            response = requests.get(url, timeout=10, headers={
                "User-Agent": "CrewCFO Knowledge Scraper"
            })
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()

            # Get main content
            main = soup.find("main") or soup.find("article") or soup.find("body")

            if main:
                # Convert to markdown
                markdown = h.handle(str(main))

                # Generate filename
                path_parts = parsed.path.strip("/").split("/")
                if not path_parts or not path_parts[0]:
                    filename = "index.md"
                else:
                    filename = "_".join(path_parts) + ".md"

                # Save file
                output_path = output_dir / filename

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(f"# {soup.title.string if soup.title else 'Untitled'}\n\n")
                    f.write(f"*Source: {url}*\n\n")
                    f.write(markdown)

                results["files"].append(str(output_path))
                results["scraped"] += 1
                print(f"  ✅ {filename}")

            # Find links to other pages on same domain
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = urljoin(url, href)
                link_parsed = urlparse(full_url)

                # Only follow links on same domain
                if link_parsed.netloc == parsed.netloc:
                    # Skip anchors and files
                    if "#" in full_url:
                        full_url = full_url.split("#")[0]
                    if full_url.endswith((".pdf", ".jpg", ".png", ".css", ".js")):
                        continue

                    if full_url not in visited and full_url not in to_visit:
                        to_visit.append(full_url)

        except Exception as e:
            results["errors"].append({"url": url, "error": str(e)})
            print(f"  ❌ Error scraping {url}: {e}")

    return results


# =============================================================================
# DEDUPLICATION
# =============================================================================

def find_file_duplicates(
    data_dir: Path,
    threshold: float = 0.9,
) -> List[Dict]:
    """
    Find duplicate files based on content hash and similarity.

    Args:
        data_dir: Data directory to scan
        threshold: Similarity threshold

    Returns:
        List of duplicate pairs
    """
    # First pass: exact duplicates by hash
    hashes = {}
    duplicates = []

    for domain_dir in data_dir.iterdir():
        if not domain_dir.is_dir():
            continue

        for file_path in domain_dir.glob("**/*"):
            if not file_path.is_file():
                continue

            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    file_hash = hashlib.md5(content).hexdigest()

                if file_hash in hashes:
                    duplicates.append({
                        "type": "exact",
                        "file1": str(hashes[file_hash]),
                        "file2": str(file_path),
                    })
                else:
                    hashes[file_hash] = file_path

            except Exception as e:
                print(f"  Error reading {file_path}: {e}")

    return duplicates


def archive_duplicates(
    duplicates: List[Dict],
    data_dir: Path,
    keep_strategy: str = "first",
) -> Dict:
    """
    Archive duplicate files.

    Args:
        duplicates: List of duplicate pairs
        data_dir: Data directory
        keep_strategy: Which file to keep ("first", "larger")

    Returns:
        Archive results
    """
    archived = []
    errors = []

    for dup in duplicates:
        try:
            file1 = Path(dup["file1"])
            file2 = Path(dup["file2"])

            # Determine which to archive
            if keep_strategy == "larger":
                to_archive = file1 if file1.stat().st_size < file2.stat().st_size else file2
            else:
                to_archive = file2  # Keep first, archive second

            # Move to archive
            archive_dir = data_dir / "archive"
            archive_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = archive_dir / f"{timestamp}_{to_archive.name}"

            shutil.move(str(to_archive), str(archive_path))
            archived.append(str(to_archive))

        except Exception as e:
            errors.append({"files": dup, "error": str(e)})

    return {"archived": archived, "errors": errors}


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="CrewCFO Knowledge Consolidation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python consolidate_knowledge.py --process-imports
  python consolidate_knowledge.py --scrape-website https://crewcfo.com
  python consolidate_knowledge.py --dedupe
  python consolidate_knowledge.py --rebuild
  python consolidate_knowledge.py --all
        """
    )

    parser.add_argument(
        "--process-imports",
        action="store_true",
        help="Process and classify files in imports/"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    parser.add_argument(
        "--scrape-website",
        type=str,
        metavar="URL",
        help="Scrape a website to markdown"
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Maximum pages to scrape (default: 50)"
    )

    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="Find and archive duplicate files"
    )

    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild the vector store"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show knowledge base statistics"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all operations: process-imports, dedupe, rebuild"
    )

    args = parser.parse_args()

    # Initialize librarian
    librarian = Librarian()

    # Process based on arguments
    if args.stats or (not any([args.process_imports, args.scrape_website, args.dedupe, args.rebuild, args.all])):
        stats = get_domain_stats()
        print("\n📊 Knowledge Base Statistics\n")
        total = sum(stats.values())
        for domain, count in sorted(stats.items()):
            bar = "█" * min(count, 20)
            print(f"  {domain:20} {count:4} {bar}")
        print(f"\n  {'TOTAL':20} {total:4}")
        return

    if args.process_imports or args.all:
        print("\n" + "=" * 60)
        print("PROCESSING IMPORTS")
        print("=" * 60)
        results = process_imports(librarian, dry_run=args.dry_run)
        print(f"\n📊 Results:")
        print(f"   Processed: {results['processed']}")
        print(f"   Moved: {results['moved']}")
        print(f"   Kept in imports: {results['kept']}")
        if results['errors']:
            print(f"   Errors: {len(results['errors'])}")

    if args.scrape_website:
        print("\n" + "=" * 60)
        print("SCRAPING WEBSITE")
        print("=" * 60)
        output_dir = DATA_DIR / "marketing" / "website"
        results = scrape_website(
            args.scrape_website,
            output_dir,
            max_pages=args.max_pages,
        )
        print(f"\n📊 Results:")
        print(f"   Scraped: {results.get('scraped', 0)} pages")
        if results.get('errors'):
            print(f"   Errors: {len(results['errors'])}")

    if args.dedupe or args.all:
        print("\n" + "=" * 60)
        print("FINDING DUPLICATES")
        print("=" * 60)
        duplicates = find_file_duplicates(DATA_DIR)
        print(f"\n   Found {len(duplicates)} exact duplicates")

        if duplicates and not args.dry_run:
            print("   Archiving duplicates...")
            archive_results = archive_duplicates(duplicates, DATA_DIR)
            print(f"   Archived: {len(archive_results['archived'])} files")

    if args.rebuild or args.all:
        print("\n" + "=" * 60)
        print("REBUILDING VECTOR STORE")
        print("=" * 60)
        result = librarian.rebuild_index()
        print(f"\n   ✅ Rebuilt with {result['total_chunks']} chunks")
        print("\n   Chunks by domain:")
        for domain, count in sorted(result.get("by_domain", {}).items()):
            print(f"     {domain:20} {count:4}")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
