# Agent Spec: Month-End Close Orchestrator

> **Module**: Books OS  
> **Version**: 1.0.0  
> **Agent Type**: Orchestrator with Human Checkpoints  

---

## Overview

The Close Orchestrator manages the month-end close process for each client. It generates the close checklist, assigns tasks to agents and humans, tracks progress, sends reminders, and ensures the close is completed within the target timeline (≤ 5 business days).

---

## Agent Identity

| Property | Value |
|----------|-------|
| **Name** | `close_orchestrator` |
| **Autonomy Level** | Orchestration (coordinates other agents and humans) |
| **Trigger** | First business day of new month (auto) or manual initiation |
| **Output** | Completed close run with certified books |
| **Escalation Target** | Senior bookkeeper / Finance Lead |

---

## Input Schema

```typescript
interface CloseInitiationInput {
  tenant_id: string;
  period_year: number;
  period_month: number;           // 1-12
  initiated_by: 'auto' | 'manual';
  initiator_user_id?: string;
  
  // Configuration
  close_deadline?: string;        // ISO date, defaults to 7th business day
  priority?: 'normal' | 'urgent';
}
```

---

## Output Schema

```typescript
interface CloseRunOutput {
  close_run_id: string;
  tenant_id: string;
  period: string;                 // "2025-01"
  
  status: 'in_progress' | 'blocked' | 'completed' | 'certified';
  
  // Progress
  tasks_total: number;
  tasks_completed: number;
  tasks_blocked: number;
  completion_percent: number;
  
  // Timeline
  initiated_at: string;
  target_completion: string;
  actual_completion?: string;
  business_days_elapsed: number;
  
  // Certification
  certified_by?: string;
  certified_at?: string;
  certification_notes?: string;
  
  // Key Outputs
  reports_generated: string[];    // URLs to generated reports
  adjustments_made: AdjustmentSummary[];
  exceptions_remaining: number;
}
```

---

## Close Checklist Template

The checklist is generated from a template and customized per tenant based on their configuration.

### Standard Close Tasks

| # | Task | Assignee | Priority | Dependencies | Auto-Completable |
|---|------|----------|----------|--------------|------------------|
| 1 | Sync all source systems | Agent | P0 | None | Yes |
| 2 | Process pending transactions | Agent | P0 | 1 | Yes |
| 3 | Review exception queue | Human | P0 | 2 | No |
| 4 | Categorize unclassified transactions | Agent/Human | P0 | 2 | Partial |
| 5 | Tag untagged COGS to jobs | Human | P0 | 4 | No |
| 6 | Complete bank reconciliation | Agent/Human | P0 | 1 | Partial |
| 7 | Review credit card reconciliation | Human | P1 | 1 | No |
| 8 | Review AR aging | Human | P1 | 2 | No |
| 9 | Review AP aging | Human | P1 | 2 | No |
| 10 | Record accruals | Human | P1 | 4 | No |
| 11 | Record prepaid amortization | Agent | P1 | None | Yes |
| 12 | Record depreciation | Agent | P1 | None | Yes |
| 13 | Review payroll entries | Human | P1 | 1 | No |
| 14 | Job costing review | Human | P1 | 5 | No |
| 15 | Generate draft P&L | Agent | P0 | 1-14 | Yes |
| 16 | Generate draft Balance Sheet | Agent | P0 | 1-14 | Yes |
| 17 | Management review call | Human | P0 | 15,16 | No |
| 18 | Post final adjustments | Human | P0 | 17 | No |
| 19 | Generate final reports | Agent | P0 | 18 | Yes |
| 20 | Certify close | Human | P0 | 19 | No |

---

## Database Schema

```sql
-- Close Run Master Record
CREATE TABLE close_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    
    -- Period
    period_year INTEGER NOT NULL,
    period_month INTEGER NOT NULL,
    period_label VARCHAR(7) NOT NULL, -- "2025-01"
    
    -- Status
    status VARCHAR(20) DEFAULT 'in_progress',
    
    -- Timeline
    initiated_at TIMESTAMPTZ DEFAULT now(),
    target_completion TIMESTAMPTZ NOT NULL,
    actual_completion TIMESTAMPTZ,
    business_days_elapsed INTEGER DEFAULT 0,
    
    -- Certification
    certified_by UUID REFERENCES users(id),
    certified_at TIMESTAMPTZ,
    certification_notes TEXT,
    
    -- Metadata
    initiated_by VARCHAR(20) NOT NULL,
    initiator_user_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    
    CONSTRAINT unique_tenant_period UNIQUE (tenant_id, period_year, period_month),
    CONSTRAINT valid_status CHECK (status IN ('in_progress', 'blocked', 'completed', 'certified', 'cancelled'))
);

-- Close Tasks
CREATE TABLE close_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    close_run_id UUID NOT NULL REFERENCES close_runs(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    
    -- Task Definition
    task_number INTEGER NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    task_description TEXT,
    priority VARCHAR(10) DEFAULT 'P1',
    
    -- Assignment
    assignee_type VARCHAR(20) NOT NULL, -- agent, human, hybrid
    assignee_agent VARCHAR(50),         -- agent name if agent
    assignee_user_id UUID REFERENCES users(id),
    
    -- Dependencies
    depends_on INTEGER[],               -- task_numbers this depends on
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    completed_by VARCHAR(100),          -- user_id or agent name
    
    -- Results
    result_summary TEXT,
    result_data JSONB,
    error_message TEXT,
    
    -- Blocking
    is_blocking BOOLEAN DEFAULT false,
    blocking_reason TEXT,
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    
    CONSTRAINT valid_priority CHECK (priority IN ('P0', 'P1', 'P2')),
    CONSTRAINT valid_assignee_type CHECK (assignee_type IN ('agent', 'human', 'hybrid')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked', 'skipped'))
);

-- Indexes
CREATE INDEX idx_close_runs_tenant ON close_runs(tenant_id);
CREATE INDEX idx_close_runs_period ON close_runs(period_year, period_month);
CREATE INDEX idx_close_tasks_run ON close_tasks(close_run_id);
CREATE INDEX idx_close_tasks_status ON close_tasks(close_run_id, status);
```

---

## Orchestration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  CLOSE ORCHESTRATION FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐                                           │
│  │ TRIGGER          │  1st business day of month OR manual      │
│  │ (Cron / Manual)  │                                           │
│  └────────┬─────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌──────────────────┐                                           │
│  │ Initialize Close │  Create close_run record                  │
│  │ Run              │  Generate task checklist                  │
│  └────────┬─────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    TASK EXECUTION LOOP                    │  │
│  │                                                           │  │
│  │  For each task (in dependency order):                     │  │
│  │                                                           │  │
│  │  ┌─────────────┐                                          │  │
│  │  │ Check Deps  │──No──▶ Wait / Check Again               │  │
│  │  │ Satisfied?  │                                          │  │
│  │  └──────┬──────┘                                          │  │
│  │         │ Yes                                             │  │
│  │         ▼                                                 │  │
│  │  ┌─────────────────────────────────────────┐             │  │
│  │  │              DISPATCH TASK               │             │  │
│  │  ├─────────────────────────────────────────┤             │  │
│  │  │                                         │             │  │
│  │  │  If Agent Task:                         │             │  │
│  │  │    → Invoke agent                       │             │  │
│  │  │    → Capture result                     │             │  │
│  │  │    → Mark complete                      │             │  │
│  │  │                                         │             │  │
│  │  │  If Human Task:                         │             │  │
│  │  │    → Send notification                  │             │  │
│  │  │    → Wait for completion signal         │             │  │
│  │  │    → Send reminders if overdue          │             │  │
│  │  │                                         │             │  │
│  │  │  If Hybrid Task:                        │             │  │
│  │  │    → Agent does prep work               │             │  │
│  │  │    → Human reviews/approves             │             │  │
│  │  │                                         │             │  │
│  │  └─────────────────────────────────────────┘             │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│           │                                                     │
│           ▼                                                     │
│  ┌──────────────────┐                                           │
│  │ All P0 Tasks     │                                           │
│  │ Complete?        │──No──▶ Continue Loop / Escalate          │
│  └────────┬─────────┘                                           │
│           │ Yes                                                 │
│           ▼                                                     │
│  ┌──────────────────┐                                           │
│  │ Request          │  Human reviews final reports              │
│  │ Certification    │  Signs off on close                       │
│  └────────┬─────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌──────────────────┐                                           │
│  │ CLOSE CERTIFIED  │  Lock period, archive                     │
│  └──────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Task Implementations

### Task 1: Sync All Source Systems

```python
async def execute_sync_task(close_run_id: str, tenant_id: str):
    """
    Triggers full sync from all connected integrations.
    """
    integrations = await get_active_integrations(tenant_id)
    
    results = []
    for integration in integrations:
        sync_result = await trigger_sync(
            tenant_id=tenant_id,
            integration=integration.type,  # qbo, jobber, etc.
            full_sync=True
        )
        results.append(sync_result)
    
    # Wait for all syncs to complete
    all_complete = await wait_for_syncs(results, timeout_minutes=30)
    
    return {
        "success": all_complete,
        "integrations_synced": len(results),
        "last_sync_times": {r.integration: r.completed_at for r in results}
    }
```

### Task 6: Bank Reconciliation

```python
async def execute_bank_reconciliation(close_run_id: str, tenant_id: str, period: str):
    """
    Automated bank reconciliation with exception flagging.
    """
    # Get bank statement balance (from QBO or direct feed)
    statement_balance = await get_bank_statement_balance(tenant_id, period)
    
    # Get book balance
    book_balance = await get_book_balance(tenant_id, period)
    
    # Calculate reconciling items
    outstanding_checks = await get_outstanding_checks(tenant_id, period)
    deposits_in_transit = await get_deposits_in_transit(tenant_id, period)
    
    adjusted_book = book_balance - outstanding_checks + deposits_in_transit
    
    difference = statement_balance - adjusted_book
    
    result = {
        "statement_balance": statement_balance,
        "book_balance": book_balance,
        "outstanding_checks": outstanding_checks,
        "deposits_in_transit": deposits_in_transit,
        "adjusted_book_balance": adjusted_book,
        "difference": difference,
        "reconciled": abs(difference) < 0.01
    }
    
    if not result["reconciled"]:
        # Flag for human review
        await create_reconciliation_exception(
            tenant_id=tenant_id,
            period=period,
            difference=difference,
            details=result
        )
        
    return result
```

### Task 15/16: Generate Reports

```python
async def generate_financial_reports(close_run_id: str, tenant_id: str, period: str):
    """
    Generate P&L and Balance Sheet using python-accounting.
    """
    from python_accounting import Entity, Report
    
    entity = await load_entity(tenant_id)
    
    # Generate P&L
    pnl = Report.income_statement(
        entity=entity,
        start_date=f"{period}-01",
        end_date=last_day_of_month(period)
    )
    
    # Generate Balance Sheet
    bs = Report.balance_sheet(
        entity=entity,
        as_of=last_day_of_month(period)
    )
    
    # Store reports
    pnl_url = await store_report(tenant_id, period, "pnl", pnl.to_pdf())
    bs_url = await store_report(tenant_id, period, "bs", bs.to_pdf())
    
    return {
        "pnl_url": pnl_url,
        "bs_url": bs_url,
        "pnl_summary": {
            "revenue": pnl.total_revenue,
            "cogs": pnl.total_cogs,
            "gross_profit": pnl.gross_profit,
            "operating_expenses": pnl.total_opex,
            "net_income": pnl.net_income
        },
        "bs_summary": {
            "total_assets": bs.total_assets,
            "total_liabilities": bs.total_liabilities,
            "equity": bs.total_equity
        }
    }
```

---

## Notification Templates

### Close Initiated

```
Subject: Month-End Close Started for {period}

Hi {owner_name},

The month-end close process for {period} has been initiated.

Target completion: {target_date}
Tasks to complete: {total_tasks}

You'll receive updates as we progress. No action needed from you until the review stage.

View progress: {dashboard_url}
```

### Human Task Assignment

```
Subject: Action Required: {task_name} for {period} Close

Hi {assignee_name},

You have a new task for the {period} month-end close:

Task: {task_name}
Priority: {priority}
Due: {due_date}

Description:
{task_description}

Complete this task: {task_url}

Blocking tasks waiting on this: {blocking_count}
```

### Daily Progress Update

```
Subject: {period} Close Progress: {completion_percent}% Complete

Close Status: {status}
Day: {business_day}/5

Completed: {completed_count}/{total_count} tasks
In Progress: {in_progress_count}
Blocked: {blocked_count}

{if blocked_count > 0}
⚠️ Blocked Tasks:
{for task in blocked_tasks}
- {task.name}: {task.blocking_reason}
{/for}
{/if}

View full status: {dashboard_url}
```

### Close Ready for Certification

```
Subject: {period} Close Ready for Certification

Hi {owner_name},

The books for {period} are ready for your review and certification.

Key Metrics:
- Revenue: {revenue}
- Gross Profit: {gross_profit} ({gp_margin}%)
- Net Income: {net_income}

Reports:
- P&L: {pnl_url}
- Balance Sheet: {bs_url}

Please review and certify: {certification_url}

If you have questions or need adjustments, reply to this email or contact your bookkeeper.
```

---

## Tools Available to Orchestrator

| Tool | Purpose |
|------|---------|
| `create_close_run` | Initialize new close run |
| `generate_checklist` | Create tasks from template |
| `dispatch_agent_task` | Invoke agent for task |
| `send_notification` | Send email/Slack to assignee |
| `update_task_status` | Mark task progress |
| `check_dependencies` | Validate task can start |
| `escalate_task` | Escalate overdue/blocked task |
| `generate_report` | Create financial reports |
| `certify_close` | Lock period and archive |

---

## Escalation Rules

| Condition | Action | Recipient |
|-----------|--------|-----------|
| Task overdue by 1 day | Send reminder | Assignee |
| Task overdue by 2 days | Send escalation | Assignee + Manager |
| Task overdue by 3 days | Flag as blocked | Senior Finance |
| Close overdue by deadline | Executive alert | Owner + Finance Lead |
| Critical exception found | Immediate escalation | Finance Lead |

---

## Success Metrics

| Metric | Target | Alert |
|--------|--------|-------|
| Average close days | ≤ 5 business days | > 7 days |
| On-time close rate | > 90% | < 80% |
| Certification rate | 100% | Any uncertified |
| Exception resolution time | < 24 hours | > 48 hours |
| Task automation rate | > 60% | < 50% |
