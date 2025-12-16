Below is a product feature plan for a **Valuation Intelligence Module**
that plugs into the existing **CrewCFO / Books OS + Finance Command
Center + Growth & Valuation OS** stack, and stays compliant with the
**Books OS Constitution** (QBO as source of truth, no Excel, audit
trail, automation tiers + human escalation).

**1) Feature map: 5 core valuation features**

**Feature A --- Real-time Valuation Engine (TTM SDE / EBITDA + EV
ranges)**

**What it does**

-   Computes **TTM SDE** and **TTM EBITDA**, then renders **valuation
    ranges** using:

    -   **SDE multiples** for smaller owner-operated firms

    -   **EBITDA multiples** for more investor-grade firms

-   Applies **Matador tier multipliers** as the "multiple selector"
    layer:

    -   Below-average / average / above-average tier logic (e.g., \~3×
        EBITDA → \~4.5--5× → \~7×+), plus revenue multiple references

-   Provides "**value delta**" view tying KPI improvements to implied
    exit multiple (aligns with Growth & Valuation OS deliverables).

**Primary UI outputs**

-   "Estimated Business Value" (range + confidence band)

-   "Multiple driver" explanation (why your implied multiple is X today)

**Feature B --- Value Driver Scoring Engine (Matador Driver Model → Tier
Assignment)**

**What it does**

-   Scores the business across Matador-style drivers (minimum viable
    set):

    -   **Management Independence**

    -   **Financial Records Quality**

    -   **Recurring Revenue**

    -   **Operational Systems**

    -   **Customer Base Diversity**

    -   **Market Outlook**

-   Converts driver scores into:

    -   **Tier** (Below Avg / Avg / Above Avg)

    -   **Multiple uplift/downshift** rules that feed Feature A's
        valuation engine

**Primary UI outputs**

-   Scorecards per driver (0--100), with "what moved this score"
    explainability

-   Tier badge + "next tier" threshold guidance

**Feature C --- Valuation Levers & Scenario Simulator (No-Excel
"What-if")**

**What it does**

-   Owner adjusts a small number of levers; system recalculates:

    -   EBITDA/SDE uplift (via job margin, overhead, AR days, etc.)

    -   Multiple uplift (via driver score improvements)

-   Example levers:

    -   "Recurring revenue from maintenance plans ↑"

    -   "Owner hours/week ↓ / layer-in GM"

    -   "Crew productivity ↑ (labor hours per square ↓)"

    -   "Gross margin ↑ (price discipline + material variance control)"

**Constraint compliance**

-   **No manual Excel**; scenarios live inside Spec-OS and are computed
    from synced financial + ops telemetry.

**Feature D --- Exit Readiness & Deal Room Builder (Due Diligence
Automation)**

**What it does**

-   Builds a "**Deal Room**" checklist and automatically assembles
    artifacts buyers request:

    -   3--5 years financials, tax returns, AR/AP aging, asset lists,
        org chart, KPIs, safety/insurance docs, etc.

-   Produces a draft "CIM-like" packet outline (system-generated;
    human-reviewed).

**Primary UI outputs**

-   Exit readiness score + "red flags" (missing documents, unresolved
    compliance items)

-   Auto-generated data room index (with completeness status)

**Feature E --- Valuation Roadmap Agent (Quarterly "Spec Jam" + Weekly
Actions)**

**What it does**

-   Generates a customized action roadmap to hit a target valuation:

    -   Weekly: operational + finance tasks

    -   Monthly: close discipline + KPI improvements

    -   Quarterly: **"Spec Jam"** review cadence (already a Growth &
        Valuation OS automation concept).

-   Operates like an AI coach that can answer: "What can I do to improve
    my multiple?" and convert recommendations into tasks
    (Torch/Takeoff/Ridgeline alignment).

**2) Data dependencies (by feature) + extraction/sync approach**

**Shared baseline data layer (existing Books OS plumbing)**

Use the existing **Data Plumbing** approach and tables (extend, don't
redesign): tenants, transactions_raw, transactions_categorized, jobs,
job_costs, invoices, payments, vendors, customers, sync_history...

-   **QBO** is system of record.

-   **Field service integration mandatory** (Jobber/ServiceTitan) for
    job costing + ops metrics.

**Feature A --- Real-time Valuation Engine**

**Financial data**

-   P&L / BS / CF inputs, TTM rollups (from transactions_categorized +
    financial statement generator)

-   Owner add-backs + normalization inputs (captured via guided "SDE
    adjustments" workflow; human-reviewed)

**Operational data**

-   Job profitability + WIP/over-under billing where applicable (from
    jobs, job_costs, WIP automation if enabled)

**Sync**

-   QBO hourly + webhook/batch reconciliation pattern from Phase 1;
    compute valuation nightly + on-demand.

**Feature B --- Driver Scoring Engine**

**Financial records quality**

-   Close timeliness + % job-tagged revenue/COGS (constitution
    non-negotiable)

**Management independence**

-   Owner involvement proxy metrics (owner-coded time entries, approval
    frequency, sales dependency flags) --- may start as
    **self-reported + lightweight signals**, then refine.

**Recurring revenue**

-   Maintenance plan invoices, subscription-like repeating customers,
    repeat-job rate (from QBO customer/invoice patterns + CRM tags)

**Operational systems**

-   Crew efficiency (labor hours per square, rework rates, cycle time)
    if available (Jobber/ServiceTitan + job cost engine concept)

**Feature C --- Scenario Simulator**

Uses Feature A outputs plus:

-   Pricing/margin insights + scenario modeling hooks already planned in
    Finance Command Center (±10%, ±20% patterns)

-   Crew productivity metrics (planned)

**Feature D --- Exit Readiness & Deal Room**

Data room artifact feeds:

-   Financial statements + AR/AP aging (Books OS standard reports)

-   Operational KPIs + safety/insurance placeholders (document upload +
    checklist validation)

**Feature E --- Roadmap Agent**

Inputs:

-   Driver score gaps (Feature B)

-   KPI trends (Books OS + Finance Command Center dashboards + weekly
    brief agent concept)

-   Change recommendations mapped into tasks and escalated via
    automation tiers.

**3) UX design concepts: "Valuation Dashboard" inside Spec-OS**

**Navigation placement**\
Finance Command Center → **Valuation** (or Growth & Valuation OS →
Valuation)

**Dashboard layout (owner-friendly, 1-screen core)**

1.  **Valuation Meter (top card)**

    -   "Estimated Value Range: \$X -- \$Y"

    -   "Basis: TTM SDE / EBITDA"

    -   "Current Tier: Average (4.5--5× EBITDA) → Next Tier: Above Avg
        (7×+)"

2.  **Multipliers Panel**

    -   Shows the current implied multiple and the tier band

    -   "Why this multiple?" bullets: clean books, owner dependency,
        recurring revenue, ops maturity

3.  **Value Driver Scorecards (grid)**

    -   Each driver: score, trend arrow, and 1--3 "next actions"

    -   "Risk factor tags" (e.g., "Owner-dependent sales", "Low
        recurring revenue", "Books not closed by day 7")

4.  **Value Delta Timeline**

    -   Month-by-month implied value trend

    -   "What moved value?" annotations (margin change, AR days,
        recurring revenue, driver score changes)

5.  **Roadmap (right rail or second tab)**

    -   "Next 2 improvements" recommendations (matches Spec-OS
        productized OS philosophy)

    -   Weekly tasks + quarterly Spec Jam agenda

6.  **Exit Readiness tab**

    -   Checklist + Deal Room completeness meter

    -   Export buttons (CIM outline, KPI pack, financial package)

**4) AI / automation logic (per feature) with Books OS tiering +
escalation**

**Common automation rules (platform-wide)**

-   **Tiered AI strategy**: Rules → ML → LLM last resort, with
    confidence scoring.

-   **Human-in-the-loop thresholds**:

    -   ≥95% auto-commit

    -   80--94% commit + flagged review

    -   60--79% draft, human confirmation

    -   \<60% exception queue

-   **Human approval required for amounts \> \$5,000** (for any
    auto-generated adjusting entry, normalization add-back, or reclass
    impacting valuation outputs).

-   **No auto-posting adjusting entries** in v1.

**Feature A --- Valuation Engine**

**Automation level**

-   Mostly **rules-based** + deterministic computations:

    -   TTM rollups, normalization worksheets, EV math

-   **LLM used only for**:

    -   Explaining "why value moved"

    -   Drafting plain-English valuation narratives

-   **Human-in-loop**

    -   SDE add-backs and normalization require review (especially
        anything that resembles adjusting entries).

**Feature B --- Driver Scoring**

**Automation level**

-   **Rules-based scoring** for quantifiable drivers (close timeliness,
    job-tagging %, recurring rev %, gross margin stability)

-   **Hybrid** for qualitative drivers (management independence,
    operational systems maturity):

    -   Start with structured questionnaire + evidence uploads

    -   Then progressively infer via telemetry (approvals, owner tasks,
        CRM notes)

**Human-in-loop**

-   If the model proposes a tier jump that changes implied multiple
    materially, require owner acknowledgement and show "evidence
    checklist."

**Feature C --- Scenario Simulator**

**Automation level**

-   Rules-based engine + constraints; no ML required initially

-   Uses existing "scenario modeling" patterns in your CFO layer

**Human-in-loop**

-   None required to run scenarios; required only if user wants to
    "apply changes" that would trigger accounting actions or SOP
    deployments.

**Feature D --- Exit Readiness + Deal Room**

**Automation level**

-   Rules-based checklist + document classification (OCR/LLM for
    labeling and indexing)

-   LLM drafts CIM outline and buyer Q&A prep; **always human-reviewed**
    before sharing externally.

**Human-in-loop**

-   Mandatory for any outbound package finalization ("Share data room"
    step gated).

**Feature E --- Roadmap Agent**

**Automation level**

-   LLM planner + deterministic prioritization:

    -   Prioritize actions that improve (a) EBITDA/SDE and (b) tier
        drivers with highest multiple impact

-   Converts recommendations into **Spec-OS tasks** with owners/roles,
    due dates, and dependencies.

**Escalation**

-   If tasks are blocked by missing data (e.g., job costing not
    enforced), system escalates to implement prerequisite epics first
    (job tagging, close discipline).

**5) Scenarios: 3 example user stories**

**Story 1 --- "\$1.5M → \$3M in 24 months"**

-   Owner sets goal: "Double valuation in 24 months."

-   System response:

    -   Current value = TTM EBITDA × current tier multiple

    -   Gap decomposition:

        1.  EBITDA uplift plan (job margins, overhead, AR days)

        2.  Multiple uplift plan (driver score moves: independence +
            recurring rev)

    -   Outputs a roadmap: "Top 5 moves" + weekly tasks + quarterly Spec
        Jam.

**Story 2 --- "I want to be owner-independent"**

-   Owner indicates: "I need the business to run without me."

-   System response:

    -   Driver score flags "Management Independence" below threshold

    -   Produces:

        -   Org chart gap checklist (GM/ops lead)

        -   SOP + delegation plan inside Spec-OS tasks

        -   KPI gates: % jobs requiring owner intervention, approval
            frequency, etc.

**Story 3 --- "Preparing for PE roll-up / recap"**

-   Owner explores exit options: full sale vs recap vs roll-up.

-   System response:

    -   Asks a short intake (desired liquidity, willingness to stay,
        EBITDA size)

    -   Produces:

        -   Recommended path + readiness deltas (e.g., minimum reporting
            package, KPIs, management depth)

        -   Deal room checklist and due diligence packet builder

**6) Output types: reports, dashboards, alerts, insights cadence**

**Weekly (Owner-facing)**

-   **Valuation & Drivers Snapshot** (1 page)

    -   Value range change vs last week

    -   Top 3 drivers moving

    -   "Next 2 improvements" tasks

-   **CFO Weekly Brief (valuation section added)** building on the
    existing "CFO Weekly Brief Agent" epic.

**Monthly (Close + valuation truth)**

-   **Valuation Rebase Report**

    -   Locks to month-end close outputs (avoid noise)

    -   Shows: normalized EBITDA/SDE, tier changes, confidence changes

-   **Value Delta Attribution**

    -   Bridge: Last month's value → this month's value (EBITDA change
        vs multiple change)

**Quarterly (Strategic)**

-   **Quarterly Spec Jam Pack**

    -   Driver score review + roadmap refresh

    -   "Exit readiness" progress

    -   Scenario refresh (12--24 month target)

**Alerts (event-driven)**

-   "Tier-risk alerts":

    -   Books not closed by 7th business day

    -   Job-tagging compliance falls below threshold

    -   Recurring revenue % drops / churn spikes

    -   Owner-dependence proxy increases (owner approvals/tasks rising)

**7) Integration notes: where this lives in CrewCFO architecture**

**Recommended module placement**

-   Add a new bounded context: valuation_intelligence

    -   Reads from: Books OS reporting outputs + job costing + cash
        forecast tables

    -   Writes to: valuation_snapshots, driver_scores, roadmaps,
        deal_room_artifacts, alerts

**Minimal schema additions (illustrative)**

-   valuation_snapshots(tenant_id, as_of_date, ttm_revenue, ttm_sde,
    ttm_ebitda, tier, multiple_low, multiple_high, ev_low, ev_high,
    confidence_score, drivers_json, audit_log_ref)

-   driver_scores(tenant_id, as_of_date, driver_key, score,
    evidence_refs, computed_by, confidence)

-   roadmap_items(tenant_id, created_at, driver_key, expected_impact_ev,
    effort_level, automation_tier, task_refs\[\])

All outputs must maintain an **audit trail** consistent with the
Constitution's requirements.

If you want, I can convert this into an **Epic/Story breakdown** that
matches your existing speckit.plan style (Phase X → Epics → tasks/est
hours), with a clean "Valuation Intelligence Phase" that plugs after
**Phase 3: Finance Command Center**.
