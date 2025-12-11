# Data Model: Transactions

> **Module**: Books OS  
> **Version**: 1.0.0  

---

## Overview

The transactions data model captures financial transactions from source systems (QBO, bank feeds) and tracks their progression through the classification pipeline. It separates raw ingested data from categorized/enriched data to maintain audit trail and enable reprocessing.

---

## Table: `transactions_raw`

Raw transactions as received from source systems before any processing.

```sql
CREATE TABLE transactions_raw (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenant
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- External References
    source_system VARCHAR(50) NOT NULL,   -- qbo, bank_feed, manual
    source_id VARCHAR(100) NOT NULL,      -- External system ID
    source_sync_id UUID REFERENCES sync_history(id),
    
    -- Transaction Core
    transaction_type VARCHAR(50) NOT NULL, -- invoice, bill, payment, transfer, expense, journal
    transaction_date DATE NOT NULL,
    posted_date DATE,
    
    -- Amounts (stored in cents for precision)
    amount_cents BIGINT NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Parties
    vendor_name VARCHAR(255),
    vendor_id UUID REFERENCES vendors(id),
    customer_name VARCHAR(255),
    customer_id UUID REFERENCES customers(id),
    
    -- Description & Metadata
    description TEXT,
    memo TEXT,
    reference_number VARCHAR(100),
    raw_payload JSONB,                    -- Full API response for debugging
    
    -- Processing Status
    processing_status VARCHAR(20) DEFAULT 'pending',
    processing_error TEXT,
    processed_at TIMESTAMPTZ,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    
    -- Constraints
    CONSTRAINT unique_source_transaction UNIQUE (tenant_id, source_system, source_id),
    CONSTRAINT valid_source CHECK (source_system IN ('qbo', 'bank_feed', 'jobber', 'servicetitan', 'manual')),
    CONSTRAINT valid_status CHECK (processing_status IN ('pending', 'processing', 'completed', 'error', 'skipped'))
);

-- Indexes
CREATE INDEX idx_txn_raw_tenant ON transactions_raw(tenant_id);
CREATE INDEX idx_txn_raw_date ON transactions_raw(tenant_id, transaction_date);
CREATE INDEX idx_txn_raw_status ON transactions_raw(tenant_id, processing_status);
CREATE INDEX idx_txn_raw_source ON transactions_raw(tenant_id, source_system, source_id);
CREATE INDEX idx_txn_raw_vendor ON transactions_raw(tenant_id, vendor_id);
CREATE INDEX idx_txn_raw_customer ON transactions_raw(tenant_id, customer_id);

-- RLS
ALTER TABLE transactions_raw ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON transactions_raw
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

---

## Table: `transactions_categorized`

Enriched transactions with classification, job tagging, and approval status.

```sql
CREATE TABLE transactions_categorized (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenant
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Link to Raw
    raw_transaction_id UUID NOT NULL REFERENCES transactions_raw(id),
    
    -- Account Classification
    account_id UUID NOT NULL REFERENCES accounts(id),
    cost_code_id UUID REFERENCES cost_codes(id),
    
    -- Job Tagging
    job_id UUID REFERENCES jobs(id),
    job_task_id UUID REFERENCES job_tasks(id),
    
    -- Transaction Details (denormalized for performance)
    transaction_type VARCHAR(50) NOT NULL,
    transaction_date DATE NOT NULL,
    amount_cents BIGINT NOT NULL,
    description TEXT,
    
    -- Classification Metadata
    classification_method VARCHAR(50) NOT NULL, -- rule, ml, llm, manual
    confidence_score DECIMAL(5,4),              -- 0.0000 to 1.0000
    classification_reason TEXT,                 -- Explanation for audit
    suggested_by VARCHAR(50),                   -- agent name or user_id
    
    -- Approval Status
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    
    -- Posting Status
    posted_to_qbo BOOLEAN DEFAULT false,
    qbo_posting_id VARCHAR(100),
    posting_error TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT valid_classification_method CHECK (classification_method IN ('rule', 'ml', 'llm', 'manual', 'bulk')),
    CONSTRAINT valid_approval_status CHECK (approval_status IN ('pending', 'auto_approved', 'approved', 'rejected', 'needs_review'))
);

-- Indexes
CREATE INDEX idx_txn_cat_tenant ON transactions_categorized(tenant_id);
CREATE INDEX idx_txn_cat_raw ON transactions_categorized(raw_transaction_id);
CREATE INDEX idx_txn_cat_account ON transactions_categorized(tenant_id, account_id);
CREATE INDEX idx_txn_cat_job ON transactions_categorized(tenant_id, job_id);
CREATE INDEX idx_txn_cat_date ON transactions_categorized(tenant_id, transaction_date);
CREATE INDEX idx_txn_cat_approval ON transactions_categorized(tenant_id, approval_status);
CREATE INDEX idx_txn_cat_method ON transactions_categorized(tenant_id, classification_method);

-- RLS
ALTER TABLE transactions_categorized ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON transactions_categorized
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

---

## Table: `transaction_splits`

For transactions split across multiple accounts or jobs.

```sql
CREATE TABLE transaction_splits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Parent Transaction
    categorized_transaction_id UUID NOT NULL REFERENCES transactions_categorized(id) ON DELETE CASCADE,
    
    -- Split Details
    account_id UUID NOT NULL REFERENCES accounts(id),
    cost_code_id UUID REFERENCES cost_codes(id),
    job_id UUID REFERENCES jobs(id),
    amount_cents BIGINT NOT NULL,
    description TEXT,
    
    -- Metadata
    split_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    
    CONSTRAINT positive_amount CHECK (amount_cents > 0)
);

-- Indexes
CREATE INDEX idx_txn_splits_parent ON transaction_splits(categorized_transaction_id);
CREATE INDEX idx_txn_splits_job ON transaction_splits(tenant_id, job_id);

-- RLS
ALTER TABLE transaction_splits ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON transaction_splits
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

---

## Table: `classification_feedback`

Captures human corrections for model improvement.

```sql
CREATE TABLE classification_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Transaction Reference
    categorized_transaction_id UUID NOT NULL REFERENCES transactions_categorized(id),
    
    -- Original Classification
    original_account_id UUID REFERENCES accounts(id),
    original_confidence DECIMAL(5,4),
    original_method VARCHAR(50),
    
    -- Corrected Classification
    corrected_account_id UUID NOT NULL REFERENCES accounts(id),
    corrected_job_id UUID REFERENCES jobs(id),
    
    -- Feedback Details
    corrected_by UUID NOT NULL REFERENCES users(id),
    correction_reason TEXT,
    
    -- Training Status
    used_for_training BOOLEAN DEFAULT false,
    training_batch_id VARCHAR(100),
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT now(),
    
    CONSTRAINT different_classification CHECK (original_account_id != corrected_account_id OR original_account_id IS NULL)
);

-- Indexes
CREATE INDEX idx_feedback_tenant ON classification_feedback(tenant_id);
CREATE INDEX idx_feedback_training ON classification_feedback(used_for_training);

-- RLS
ALTER TABLE classification_feedback ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON classification_feedback
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

---

## Transaction Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSACTION PROCESSING PIPELINE              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐                                                   │
│  │  Source  │  QBO Webhook / Bank Feed / Manual Upload          │
│  │  System  │                                                   │
│  └────┬─────┘                                                   │
│       │                                                         │
│       ▼                                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ transactions_raw                                          │  │
│  │ status: pending                                           │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│       ┌───────────────────┼───────────────────┐                │
│       │                   │                   │                │
│       ▼                   ▼                   ▼                │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐            │
│  │  Rules  │   →    │   ML    │   →    │   LLM   │            │
│  │ Engine  │        │ Model   │        │ Agent   │            │
│  └────┬────┘        └────┬────┘        └────┬────┘            │
│       │                  │                  │                  │
│       └──────────────────┼──────────────────┘                  │
│                          │                                     │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ transactions_categorized                                  │  │
│  │ + confidence_score + classification_method               │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│       ┌───────────────────┴───────────────────┐                │
│       │                                       │                │
│       ▼                                       ▼                │
│  ┌─────────────┐                      ┌─────────────┐         │
│  │ confidence  │                      │ confidence  │         │
│  │   ≥ 95%     │                      │   < 95%     │         │
│  │ AUTO_APPROVE│                      │ NEEDS_REVIEW│         │
│  └──────┬──────┘                      └──────┬──────┘         │
│         │                                    │                 │
│         │         ┌──────────────────────────┘                 │
│         │         │                                            │
│         │         ▼                                            │
│         │    ┌─────────────┐                                   │
│         │    │   Human     │                                   │
│         │    │   Review    │                                   │
│         │    │   Queue     │                                   │
│         │    └──────┬──────┘                                   │
│         │           │                                          │
│         │           ▼                                          │
│         │    ┌─────────────┐                                   │
│         │    │  Approve /  │                                   │
│         │    │  Correct    │───────┐                           │
│         │    └──────┬──────┘       │                           │
│         │           │              ▼                           │
│         │           │    ┌─────────────────┐                  │
│         │           │    │classification   │                  │
│         │           │    │_feedback        │                  │
│         │           │    └─────────────────┘                  │
│         │           │                                          │
│         └───────────┼──────────────────────────────────────────┤
│                     │                                          │
│                     ▼                                          │
│            ┌─────────────┐                                     │
│            │ Post to QBO │                                     │
│            └─────────────┘                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Confidence Thresholds

| Range | Classification | Action |
|-------|----------------|--------|
| 95-100% | High Confidence | Auto-approve, commit immediately |
| 80-94% | Medium Confidence | Auto-approve, flag for batch review |
| 60-79% | Low Confidence | Requires human confirmation |
| 0-59% | Very Low | Route to exception queue with context |

---

## Data Sources & Sync

| Table | Source | Sync Frequency | Method |
|-------|--------|----------------|--------|
| transactions_raw | QBO | Near real-time | Webhook + polling |
| transactions_raw | Bank Feed (via QBO) | Hourly | QBO sync |
| transactions_raw | Jobber | Hourly | Polling |
| transactions_categorized | Classification Agent | On new raw transaction | Event-driven |
| classification_feedback | Human UI | On correction | Event-driven |

---

## Key Queries

### Pending Review Queue

```sql
SELECT tc.*, tr.description, tr.vendor_name
FROM transactions_categorized tc
JOIN transactions_raw tr ON tc.raw_transaction_id = tr.id
WHERE tc.tenant_id = :tenant_id
  AND tc.approval_status = 'needs_review'
ORDER BY tc.confidence_score ASC, tc.transaction_date DESC
LIMIT 50;
```

### Classification Accuracy by Method

```sql
SELECT 
    classification_method,
    COUNT(*) as total,
    AVG(CASE WHEN cf.id IS NULL THEN 1 ELSE 0 END) as accuracy_rate,
    AVG(confidence_score) as avg_confidence
FROM transactions_categorized tc
LEFT JOIN classification_feedback cf ON tc.id = cf.categorized_transaction_id
WHERE tc.tenant_id = :tenant_id
  AND tc.created_at > now() - interval '30 days'
GROUP BY classification_method;
```

### Untagged COGS Transactions

```sql
SELECT tc.*, a.name as account_name, a.trade_category
FROM transactions_categorized tc
JOIN accounts a ON tc.account_id = a.id
WHERE tc.tenant_id = :tenant_id
  AND a.requires_job_tag = true
  AND tc.job_id IS NULL
  AND tc.approval_status IN ('approved', 'auto_approved');
```

---

## Update Triggers

```sql
-- Update timestamp on categorized transaction change
CREATE OR REPLACE FUNCTION update_categorized_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER txn_categorized_updated
    BEFORE UPDATE ON transactions_categorized
    FOR EACH ROW
    EXECUTE FUNCTION update_categorized_timestamp();

-- Mark raw as processed when categorized
CREATE OR REPLACE FUNCTION mark_raw_processed()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE transactions_raw 
    SET processing_status = 'completed',
        processed_at = now()
    WHERE id = NEW.raw_transaction_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER txn_categorized_created
    AFTER INSERT ON transactions_categorized
    FOR EACH ROW
    EXECUTE FUNCTION mark_raw_processed();
```
