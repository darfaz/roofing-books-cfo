# Agent Spec: Classification Agent

> **Module**: Books OS  
> **Version**: 1.0.0  
> **Agent Type**: Autonomous with Human Escalation  

---

## Overview

The Classification Agent is responsible for automatically categorizing financial transactions from QuickBooks Online and bank feeds into the appropriate chart of accounts and cost codes. It uses a tiered approach (rules → ML → LLM) to optimize for accuracy and cost.

---

## Agent Identity

| Property | Value |
|----------|-------|
| **Name** | `classification_agent` |
| **Autonomy Level** | Semi-autonomous |
| **Trigger** | New transaction in `transactions_raw` with status `pending` |
| **Output** | Categorized transaction in `transactions_categorized` |
| **Escalation Target** | Human review queue |

---

## Input Schema

```typescript
interface ClassificationInput {
  transaction_id: string;        // UUID from transactions_raw
  tenant_id: string;
  
  // Transaction Data
  transaction_type: 'expense' | 'income' | 'transfer' | 'bill' | 'invoice';
  amount_cents: number;
  transaction_date: string;      // ISO date
  
  // Descriptive Fields
  description: string;
  memo?: string;
  reference_number?: string;
  
  // Party Information
  vendor_name?: string;
  vendor_id?: string;
  customer_name?: string;
  customer_id?: string;
  
  // Context
  existing_vendor_mappings?: VendorMapping[];
  recent_similar_transactions?: Transaction[];
  tenant_coa: Account[];
  tenant_cost_codes: CostCode[];
  tenant_jobs: Job[];            // Active jobs for potential linking
}

interface VendorMapping {
  vendor_name: string;
  default_account_id: string;
  default_cost_code_id?: string;
  transaction_count: number;
  last_used_date: string;
}
```

---

## Output Schema

```typescript
interface ClassificationOutput {
  transaction_id: string;
  
  // Classification Result
  account_id: string;
  cost_code_id?: string;
  job_id?: string;
  
  // Confidence & Method
  confidence_score: number;      // 0.0 to 1.0
  classification_method: 'rule' | 'ml' | 'llm' | 'manual';
  
  // Explanation (for audit and human review)
  classification_reason: string;
  alternative_accounts?: AlternativeClassification[];
  
  // Approval Recommendation
  recommended_action: 'auto_approve' | 'needs_review' | 'escalate';
  review_reason?: string;
}

interface AlternativeClassification {
  account_id: string;
  confidence_score: number;
  reason: string;
}
```

---

## Classification Pipeline

### Stage 1: Rule-Based Classification (Highest Priority)

**Purpose**: Handle known patterns with 100% accuracy and zero cost.

```python
class RuleBasedClassifier:
    """
    Rules are checked in order of specificity.
    First matching rule wins.
    """
    
    def classify(self, transaction: ClassificationInput) -> ClassificationOutput | None:
        # Rule Priority Order:
        # 1. Exact vendor + amount match (recurring)
        # 2. Vendor name mapping
        # 3. Description keyword patterns
        # 4. Amount-based rules (e.g., round numbers = likely payroll)
        
        # Check vendor mapping first
        if transaction.vendor_name:
            mapping = self.get_vendor_mapping(
                transaction.tenant_id, 
                transaction.vendor_name
            )
            if mapping and mapping.transaction_count >= 3:
                return ClassificationOutput(
                    account_id=mapping.default_account_id,
                    cost_code_id=mapping.default_cost_code_id,
                    confidence_score=0.98,
                    classification_method='rule',
                    classification_reason=f"Vendor '{transaction.vendor_name}' has been consistently mapped to this account ({mapping.transaction_count} times)",
                    recommended_action='auto_approve'
                )
        
        # Check keyword patterns
        keywords = self.extract_keywords(transaction.description)
        pattern_match = self.match_keywords_to_account(keywords, transaction.tenant_coa)
        if pattern_match:
            return pattern_match
        
        return None  # Fall through to ML
```

**Rule Categories**:

| Category | Example Pattern | Account Mapping |
|----------|----------------|-----------------|
| Payroll | "ADP", "Gusto", round amounts on Friday | 6100 - Payroll |
| Fuel | "Shell", "Chevron", "BP" | 6210 - Vehicle Fuel |
| Materials | "ABC Supply", "Beacon", "SRS" | 5200 - Materials |
| Insurance | "State Farm", "Progressive" WC | 6500 - Insurance |
| Rent | Same amount, 1st of month | 6310 - Rent |

### Stage 2: ML Classification (Fallback)

**Purpose**: Handle patterns learned from historical data.

```python
class MLClassifier:
    """
    XGBoost model trained on tenant's historical categorizations.
    Falls back to global model if tenant has < 100 transactions.
    """
    
    def __init__(self):
        self.global_model = load_model('global_classifier.pkl')
        self.tenant_models = {}
    
    def classify(self, transaction: ClassificationInput) -> ClassificationOutput | None:
        # Feature extraction
        features = self.extract_features(transaction)
        
        # Select model
        model = self.get_tenant_model(transaction.tenant_id) or self.global_model
        
        # Predict with probability
        probabilities = model.predict_proba(features)
        top_class = probabilities.argmax()
        top_confidence = probabilities.max()
        
        if top_confidence >= 0.60:
            return ClassificationOutput(
                account_id=self.class_to_account[top_class],
                confidence_score=top_confidence,
                classification_method='ml',
                classification_reason=f"ML model prediction based on similar historical transactions",
                alternative_accounts=self.get_alternatives(probabilities),
                recommended_action=self.get_recommendation(top_confidence)
            )
        
        return None  # Fall through to LLM
    
    def extract_features(self, txn: ClassificationInput) -> np.ndarray:
        """
        Feature vector for ML model:
        - TF-IDF of description (100 dims)
        - Amount bucket (10 buckets)
        - Day of week (7)
        - Day of month (31)
        - Vendor embedding (50 dims)
        - Transaction type (one-hot, 5)
        """
        pass
```

**Model Training**:
- Global model: Trained on anonymized data from all tenants
- Tenant model: Trained when tenant has 100+ categorized transactions
- Retraining: Weekly batch job with new feedback data

### Stage 3: LLM Classification (Last Resort)

**Purpose**: Handle complex, ambiguous, or novel transactions requiring reasoning.

```python
class LLMClassifier:
    """
    Uses GPT-4 or Claude for intelligent categorization.
    Only invoked when rules and ML fail (< 60% confidence).
    """
    
    def classify(self, transaction: ClassificationInput) -> ClassificationOutput:
        prompt = self.build_prompt(transaction)
        
        response = self.call_llm(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": CLASSIFICATION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.content)
        
        return ClassificationOutput(
            account_id=result['account_id'],
            cost_code_id=result.get('cost_code_id'),
            job_id=result.get('job_id'),
            confidence_score=result['confidence'],
            classification_method='llm',
            classification_reason=result['reasoning'],
            alternative_accounts=result.get('alternatives', []),
            recommended_action=self.get_recommendation(result['confidence'])
        )
```

**System Prompt**:

```
You are an expert construction bookkeeper specializing in roofing contractors.

Your task is to categorize financial transactions into the correct chart of accounts.

CONTEXT:
- Business: Roofing contractor
- Typical expenses: Materials (shingles, underlayment), labor, equipment, vehicles, insurance
- Typical income: Residential and commercial roofing jobs

RULES:
1. Match to the most specific account available
2. Consider vendor name, description, amount, and timing
3. For job-related expenses (materials, labor), suggest a job if context available
4. Provide confidence score (0.0-1.0) based on certainty
5. Always explain your reasoning

OUTPUT FORMAT (JSON):
{
  "account_id": "UUID of best matching account",
  "cost_code_id": "UUID of cost code if applicable",
  "job_id": "UUID of job if this expense relates to a specific job",
  "confidence": 0.85,
  "reasoning": "Explanation of classification logic",
  "alternatives": [
    {"account_id": "UUID", "confidence": 0.10, "reason": "Could also be..."}
  ]
}
```

---

## Confidence Thresholds & Actions

| Confidence | Action | Queue |
|------------|--------|-------|
| ≥ 95% | Auto-approve and post | None |
| 80-94% | Auto-approve with flag | Batch review (next day) |
| 60-79% | Stage for review | Needs review (human confirms) |
| < 60% | Escalate | Exception queue (immediate) |

---

## Tools Available to Agent

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `get_vendor_history` | Retrieve past transactions for vendor | When vendor_name present |
| `get_similar_transactions` | Find similar description/amount combos | For ML feature enrichment |
| `get_active_jobs` | List jobs that could match transaction | For COGS transactions |
| `get_account_by_id` | Retrieve account details | For validation |
| `create_classification` | Write result to transactions_categorized | Final step |
| `route_to_review` | Add to human review queue | When confidence < 80% |

---

## Error Handling

| Error Type | Handling |
|------------|----------|
| LLM API timeout | Retry 2x, then route to review |
| ML model unavailable | Skip to LLM |
| Invalid account_id returned | Log error, route to review |
| Missing required context | Route to review with context request |

---

## Monitoring & Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Rule classification rate | > 50% | < 40% |
| ML classification rate | > 30% | < 20% |
| LLM classification rate | < 20% | > 30% (cost alert) |
| Overall auto-approval rate | > 80% | < 70% |
| Accuracy (post-human-verification) | > 95% | < 90% |
| Average processing time | < 2s | > 5s |

---

## Feedback Loop

```
┌───────────────────────────────────────────────────────────────┐
│                     FEEDBACK LOOP                              │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     │
│  │ Transaction │ ──▶ │Classification│ ──▶ │  Staged     │     │
│  │   Input     │     │   Agent     │     │  Result     │     │
│  └─────────────┘     └─────────────┘     └──────┬──────┘     │
│                                                  │            │
│                           ┌──────────────────────┤            │
│                           │                      │            │
│                           ▼                      ▼            │
│                    ┌─────────────┐        ┌─────────────┐    │
│                    │ Auto-Approve│        │Human Review │    │
│                    └──────┬──────┘        └──────┬──────┘    │
│                           │                      │            │
│                           │           ┌──────────┤            │
│                           │           │          │            │
│                           │           ▼          ▼            │
│                           │    ┌─────────┐ ┌─────────┐       │
│                           │    │ Confirm │ │ Correct │       │
│                           │    └────┬────┘ └────┬────┘       │
│                           │         │           │             │
│                           │         │           ▼             │
│                           │         │    ┌─────────────┐     │
│                           │         │    │  Feedback   │     │
│                           │         │    │  Record     │     │
│                           │         │    └──────┬──────┘     │
│                           │         │           │             │
│                           └─────────┴───────────┘             │
│                                     │                         │
│                                     ▼                         │
│                           ┌─────────────────┐                │
│                           │ Weekly Retrain  │                │
│                           │ (ML + Rules)    │                │
│                           └─────────────────┘                │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Example Invocation

```python
# n8n or Temporal workflow
@workflow
async def process_transaction(transaction_id: str):
    # Load transaction
    transaction = await get_transaction(transaction_id)
    
    # Initialize agent
    agent = ClassificationAgent(
        tenant_id=transaction.tenant_id,
        tools=[
            GetVendorHistoryTool(),
            GetSimilarTransactionsTool(),
            GetActiveJobsTool(),
        ]
    )
    
    # Run classification
    result = await agent.classify(transaction)
    
    # Handle result
    if result.recommended_action == 'auto_approve':
        await create_categorized_transaction(result)
        await post_to_qbo(result)
    elif result.recommended_action == 'needs_review':
        await create_categorized_transaction(result, status='needs_review')
        await notify_reviewer(result)
    else:
        await create_exception(transaction, result)
```
