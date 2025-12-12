# Docker Image Size Optimization

## Current Setup

We've optimized Docker images by splitting requirements:

- **`requirements.txt`** - Core dependencies (~500-800MB images)
- **`requirements-full.txt`** - Includes OCR/ML (~3.7GB images)

## Image Size Comparison

| Configuration | Image Size | Reduction | Use Case |
|---------------|------------|-----------|----------|
| Core (requirements.txt) | **~1.46GB** | 60% smaller | **Recommended** - API + Dashboard + QBO sync |
| Full (requirements-full.txt) | ~3.7GB | Original | Only when OCR functionality is implemented |

**Result**: Reduced Docker image size from **3.67GB → 1.46GB** (saved ~2.2GB per image!)

## What Was Removed from Core

The following were moved to `requirements-full.txt` because they're not currently used:
- `tensorflow>=2.15.0` (~2-3GB) - For InvoiceNet OCR (not yet implemented)
- `opencv-python>=4.9.0` (~500MB) - For InvoiceNet OCR (not yet implemented)
- `python-accounting>=1.0.0` - For double-entry accounting (MySQL dependency)

## Using Full Requirements

### Option 1: Update Dockerfile (when OCR is needed)

Change in `Dockerfile`:
```dockerfile
# Change from:
COPY requirements.txt .
# To:
COPY requirements-full.txt requirements.txt
```

### Option 2: Install separately in container

```bash
docker-compose exec api pip install -r requirements-full.txt
```

### Option 3: Multi-stage build with optional OCR

Create separate Dockerfile.ocr that includes full requirements.

## Benefits

✅ **Faster builds** - Less dependencies to install  
✅ **Smaller images** - Faster pulls and deployments  
✅ **Lower costs** - Less storage and bandwidth  
✅ **Faster startup** - Smaller images load quicker  

## When to Use Full Requirements

Add back TensorFlow/opencv only when:
1. OCR service is implemented (`src/services/ocr/`)
2. InvoiceNet integration is complete
3. You need invoice/receipt processing from images

Until then, use the minimal `requirements.txt` for optimal performance.

