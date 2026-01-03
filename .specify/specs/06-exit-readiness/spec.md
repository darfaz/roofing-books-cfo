# Exit Readiness Specification

> **Feature**: 06-exit-readiness
> **Status**: Implemented
> **Priority**: P1 (High)
> **Last Updated**: 2026-01-02

---

## Overview

Exit Readiness provides a due diligence checklist and document management system to help owners prepare for M&A. It tracks required documents and auto-generates a CIM (Confidential Information Memorandum) outline.

**Target User**: Owner preparing for exit (6-24 months out)
**Access Frequency**: Weekly during exit preparation
**Key Question Answered**: "Am I ready for due diligence, and what do I still need?"

---

## User Stories

### US-01: View Due Diligence Checklist
**As a** roofing contractor owner
**I want to** see what documents a buyer will require
**So that** I can start gathering them before a deal

**Acceptance Criteria**:
- [ ] Display checklist of 7 standard M&A document categories
- [ ] Show completion status (complete/incomplete/partial)
- [ ] Calculate overall readiness percentage
- [ ] Indicate priority/importance of each item

### US-02: Upload Documents
**As a** roofing contractor owner
**I want to** upload documents to each checklist category
**So that** I have a secure deal room ready for buyers

**Acceptance Criteria**:
- [ ] File upload for each checklist item
- [ ] Support common formats (PDF, XLSX, DOCX, JPG, PNG)
- [ ] Show uploaded file name, size, date
- [ ] Allow multiple files per category
- [ ] Secure storage (Supabase Storage)

### US-03: Delete Documents
**As a** roofing contractor owner
**I want to** remove uploaded documents
**So that** I can replace outdated files

**Acceptance Criteria**:
- [ ] Delete button for each uploaded file
- [ ] Confirmation before delete
- [ ] Remove from storage and database

### US-04: View CIM Outline
**As a** roofing contractor owner
**I want to** see an auto-generated CIM outline
**So that** I understand what information to prepare for buyers

**Acceptance Criteria**:
- [ ] Display standard CIM sections
- [ ] Show which sections have supporting data
- [ ] Indicate data gaps
- [ ] Link to relevant uploads

### US-05: Track Overall Readiness
**As a** roofing contractor owner
**I want to** see my overall exit readiness score
**So that** I know how prepared I am

**Acceptance Criteria**:
- [ ] Readiness score 0-100%
- [ ] Visual progress indicator
- [ ] List of missing items
- [ ] Estimated time to complete remaining items

---

## Due Diligence Checklist

| # | Category | Description | Priority | Documents Needed |
|---|----------|-------------|----------|------------------|
| 1 | Financial Statements | 3-5 years of P&L, Balance Sheet | Critical | Annual P&L, BS, CF statements |
| 2 | Tax Returns | 3-5 years federal and state | Critical | Business tax returns |
| 3 | AR/AP Aging | Current aging reports | High | AR aging, AP aging reports |
| 4 | Asset List | Equipment, vehicles, property | High | Fixed asset schedule |
| 5 | Organization Chart | Structure and key personnel | Medium | Org chart, key employee list |
| 6 | KPI Dashboard | Metrics and unit economics | Medium | Job profitability, crew metrics |
| 7 | Safety & Insurance | Records, policies, compliance | High | Insurance certs, safety records |

---

## CIM Outline (Auto-Generated)

```
CONFIDENTIAL INFORMATION MEMORANDUM

1. Executive Summary
   - Company overview
   - Investment highlights
   - Financial summary

2. Company Overview
   - History and founding
   - Service offerings
   - Geographic coverage
   - Competitive advantages

3. Industry Overview
   - Roofing market size and trends
   - Local market dynamics
   - Growth drivers

4. Operations
   - Service delivery model
   - Crew structure and capacity
   - Equipment and fleet
   - Quality control processes

5. Sales & Marketing
   - Customer acquisition channels
   - Sales process
   - Marketing spend and ROI
   - Customer concentration

6. Management Team
   - Organization structure
   - Key personnel bios
   - Succession considerations

7. Financial Performance
   - Historical financials (3-5 years)
   - Revenue trends
   - Profitability metrics
   - Working capital requirements

8. Growth Opportunities
   - Market expansion
   - Service line additions
   - Operational improvements

9. Risk Factors
   - Key dependencies
   - Regulatory considerations
   - Market risks

APPENDICES
A. Financial Statements
B. Tax Returns
C. Customer Analysis
D. Equipment List
E. Insurance Certificates
```

---

## Data Model

### Checklist Item
```typescript
interface ChecklistItem {
  id: string
  category: string
  title: string
  description: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  status: 'complete' | 'partial' | 'incomplete'
  documents: UploadedDoc[]
}
```

### Uploaded Document
```typescript
interface UploadedDoc {
  id: string
  tenant_id: string
  checklist_item_id: string
  file_name: string
  content_type: string
  size_bytes: number
  storage_path: string
  uploaded_by: string
  uploaded_at: string
}
```

### Exit Readiness Summary
```typescript
interface ExitReadinessSummary {
  readiness_score: number  // 0-100
  items_complete: number
  items_total: number
  critical_missing: string[]
  estimated_completion_hours: number
}
```

---

## Storage Architecture

Files stored in Supabase Storage bucket `deal-room`:

```
deal-room/
└── {tenant_id}/
    ├── financial-statements/
    │   ├── 2023-pnl.pdf
    │   └── 2023-balance-sheet.xlsx
    ├── tax-returns/
    │   └── 2023-1120s.pdf
    ├── ar-ap-aging/
    │   └── ar-aging-dec-2024.pdf
    └── ...
```

### Storage Policies
- Files encrypted at rest
- Tenant isolation via RLS
- Max file size: 50MB
- Allowed types: PDF, XLSX, XLS, DOCX, DOC, JPG, JPEG, PNG

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/valuation/exit-readiness` | GET | Get checklist status and uploads |
| `/api/valuation/exit-readiness/upload` | POST | Upload document |
| `/api/valuation/exit-readiness/files/{id}` | DELETE | Delete document |
| `/api/valuation/exit-readiness/summary` | GET | Get readiness summary |

### Upload Request
```
POST /api/valuation/exit-readiness/upload
Content-Type: multipart/form-data

file: [binary]
checklist_item_id: "financial-statements"
```

### Upload Response
```json
{
  "doc_id": "uuid-here",
  "file_name": "2023-pnl.pdf",
  "storage_path": "deal-room/tenant-123/financial-statements/2023-pnl.pdf",
  "size_bytes": 245678
}
```

---

## UI Components

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  EXIT READINESS                         Score: 43% 🟡       │
├─────────────────────────────────────────────────────────────┤
│  DUE DILIGENCE CHECKLIST                                    │
│                                                             │
│  [█████████░░░░░░░░░░░░░] 43% Ready                        │
│  3 of 7 categories complete                                 │
├─────────────────────────────────────────────────────────────┤
│  📄 Financial Statements (3-5 years)           ✅ Complete │
│     └─ 2023-pnl.pdf (245 KB) · 2024-01-15    [🗑️ Delete]  │
│     └─ 2022-pnl.pdf (198 KB) · 2024-01-15    [🗑️ Delete]  │
│     [+ Upload Document]                                     │
├─────────────────────────────────────────────────────────────┤
│  📋 Tax Returns (3-5 years)                    ✅ Complete │
│     └─ 2023-1120s.pdf (1.2 MB) · 2024-01-10  [🗑️ Delete]  │
│     [+ Upload Document]                                     │
├─────────────────────────────────────────────────────────────┤
│  💰 AR/AP Aging Reports                        ⚠️ Partial  │
│     └─ ar-aging-nov.pdf (89 KB) · 2024-12-01 [🗑️ Delete]  │
│     ⚠️ Missing: AP aging report                            │
│     [+ Upload Document]                                     │
├─────────────────────────────────────────────────────────────┤
│  🏗️ Asset List                                 ❌ Missing  │
│     No documents uploaded                                   │
│     [+ Upload Document]                                     │
├─────────────────────────────────────────────────────────────┤
│  👥 Organization Chart                         ❌ Missing  │
│  📊 KPI Dashboard                              ❌ Missing  │
│  🛡️ Safety & Insurance                        ✅ Complete │
├─────────────────────────────────────────────────────────────┤
│  AUTO-GENERATED CIM OUTLINE                    [Expand ▼]  │
│  └─ 9 sections | 3 with data | 6 need content              │
└─────────────────────────────────────────────────────────────┘
```

---

## Status Logic

```typescript
function calculateItemStatus(item: ChecklistItem): Status {
  if (item.documents.length === 0) {
    return 'incomplete'
  }

  // Check if all required sub-items have documents
  const requiredDocs = getRequiredDocs(item.category)
  const uploadedTypes = item.documents.map(d => d.file_name)

  if (requiredDocs.every(rd => uploadedTypes.some(ut => ut.includes(rd)))) {
    return 'complete'
  }

  return 'partial'
}

function calculateReadinessScore(items: ChecklistItem[]): number {
  const weights = { critical: 3, high: 2, medium: 1, low: 0.5 }
  let totalWeight = 0
  let completedWeight = 0

  items.forEach(item => {
    const weight = weights[item.priority]
    totalWeight += weight
    if (item.status === 'complete') {
      completedWeight += weight
    } else if (item.status === 'partial') {
      completedWeight += weight * 0.5
    }
  })

  return Math.round((completedWeight / totalWeight) * 100)
}
```

---

## Review Checklist

- [ ] All 7 checklist categories display correctly
- [ ] File upload works for all allowed types
- [ ] Files are stored in correct tenant path
- [ ] Delete removes file from storage and database
- [ ] Readiness score calculates correctly
- [ ] CIM outline shows appropriate sections
- [ ] Demo mode shows sample checklist state
