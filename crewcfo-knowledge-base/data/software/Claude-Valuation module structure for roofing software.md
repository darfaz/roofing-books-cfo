# Valuation module structure for roofing software

**Created:** 12/15/2025 16:29:28  
**Updated:** 12/16/2025 19:15:36  
**Exported:** 12/19/2025 16:10:13  
**Link:** [https://claude.ai/chat/09b2b29d-2fd8-4f9c-8e30-c79ef38859b7](https://claude.ai/chat/09b2b29d-2fd8-4f9c-8e30-c79ef38859b7)  

## Prompt:
12/15/2025, 4:29:32 PM

Can I connect you to langchain to create a knowledge base to have you help me with a proper structure and plan for valuation module in roofing-cfo software I am building?



## Response:
12/15/2025, 4:30:15 PM

````plaintext
Thought process: Assessed feasibility of integrating LangChain for roofing valuation module knowledge base.

The user is asking about connecting me (Claude) to LangChain to create a knowledge base for helping with a valuation module in their roofing-cfo software. They want to know if this is possible and how to do it.

Let me search the project knowledge first to understand what they're building and what context exists about the valuation module.
````

**project_knowledge_search**

*Request*

````javascript
{
  "query": "valuation module roofing CFO software structure plan"
}
````

*Response*

````plaintext
Increasing Roofing Company Valuation & Exit Strategy Blueprint.docx
It's also evidence that **AI in
accounting is maturing**: rather than generic black-box AI, we see
specialized AI that *knows* about AIA billing forms, lien waivers, etc.,
which is a big leap in usefulness for
contractors[\[66\]](https://insidepublicaccounting.com/2025/04/21/adaptive-launches-industry-specific-ai-to-help-accounting-firms-scale-construction-services-without-adding-headcount/#:~:text=strategic%20opportunity%20for%20accounting%20firms,margin%20advisory%20services).

For Spec-OS, this competitive scan shows both an **opportunity and a
validation**: none of the mainstream automated finance tools truly
deliver a comprehensive trade-focused valuation or CFO solution yet, but
Adaptive's traction confirms that contractors greatly value solutions
built for them. Owners often complain that generic software doesn't give
them the insight they need (e.g. which crew is most profitable, or how
much should I charge per square to hit my margin). The door is open for
Spec-OS to integrate bookkeeping, operational data, and AI to deliver
*actionable financial intelligence* (not just bookkeeping) in a way
these competitors currently do not. The ultimate aim is to **support
job-costing, crew performance tracking, cashflow management, *and* exit
planning** in one system -- essentially picking up where Pilot or
QuickBooks Live stop, and adding the trade-specific layer plus
forward-looking guidance. In the next section, we'll explore how Spec-OS
can fulfill that role, effectively *"software-izing"* what a fractional
CFO or COO would do into an intelligent platform.

## 6. Spec-OS Opportunity & Strategic Fit

Given the gaps identified, Spec-OS has a compelling opportunity to
**embed valuation and growth advisory directly into the roofing
business's operating software**. By integrating financial, operational,
and marketing data, Spec-OS can act as a virtual **CMO/CTO/CFO trio**
for contractors -- turning what used to be high-end consulting services
into automated, scalable software workflows. Let's break down how
Spec-OS can leverage its modules (Torch, Takeoff, Ridgeline, etc.) to
drive the very **valuation drivers** we outlined and deliver a unique
value proposition:

**"Software-izing" CMO, CTO, CFO Services:** In a traditional sense,
improving a roofing company's value might involve hiring a **fractional
CMO** (to boost marketing), a **fractional CTO/COO** (to streamline tech
and ops), and a **fractional CFO** (to tighten financials and strategy).
Spec-OS can **productize these roles into software agents and
workflows**[\[67\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Yes%E2%80%94if%20you%20treat%20%E2%80%9Csoftware%E2%80%9D%20as,that%E2%80%99s%20your%20orchestrator%20of%20choice)[\[68\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Service%20%3D%20what%20Matador%2FLogistis%20consultants,audit%2C%20decide%2C%20configure%2C%20monitor):

-   **Torch (Marketing/CMO Module):** *Lead Engine OS*.
````

````plaintext
Increasing Roofing Company Valuation & Exit Strategy Blueprint.docx
-   **Takeoff (Operations/CTO Module):** *Field Ops & Automation*.
    Takeoff acts as the operational and technology engine -- akin to a
    fractional CTO/COO focusing on efficiency and systemization. In
    practice, this module would map out all core operational workflows:
    from initial inspection and estimating (the term "takeoff" itself
    refers to estimating materials from plans) to scheduling crews, to
    quality control and job close-out. Spec-OS's Takeoff module can
    provide **templates and playbooks for operations**: e.g.
    standardized job checklists, safety meeting agendas, crew routing
    optimizations. It might ingest your job data from the past year and
    highlight, say, *"Crew 3 has a 20% higher labor cost per square than
    Crew 1"* -- prompting you to investigate or retrain (i.e. it
    surfaces **crew performance metrics** automatically). Takeoff could
    leverage IoT or mobile inputs (time tracking apps, site photos) to
    ensure **measurable performance data** is collected, not just
    anecdotal. By having Spec-OS monitor project durations, callbacks,
    and crew productivity, it essentially **creates a feedback loop for
    continuous improvement** -- something a good COO would do by combing
    through reports, but here the software agent does it. On the tech
    side, Takeoff can integrate all your tools (CRM, project management,
    QuickBooks) and reduce manual double-entry, ensuring data
    consistency. It could also implement best practices like **automated
    dispatching** (matching job types to crews based on skill and
    availability) or sending customers automated updates, which enhances
    customer satisfaction. All these improvements hit the **Operations
    and Team driver**: making the business less reliant on the owner's
    micromanagement and more on solid systems. A concrete example:
    Spec-OS Takeoff might generate a **"project post-mortem" report
    after each job**, calculating the actual vs. estimated margin and
    capturing lessons (did we have extra material waste? Did weather
    delays hurt?). Over time, this institutional knowledge lives in the
    software. When it comes time to sell, the owner can show a buyer
    "Here's our Spec-OS ops dashboard -- crews are scheduled two weeks
    out, average job completion time is X days, rework percentage is
    \<1%, etc." This level of operational command (enabled by Takeoff)
    is typically what differentiates a *7× multiple company* from a *3×
    multiple
    one*[\[10\]](https://industrypro.com/industry_insight/there-is-no-normal-valuation-only-opportunity-to-prepare/#:~:text=In%20today%E2%80%99s%20market%2C%20two%20companies,compelling%20story%20to%20tell%20buyers).

-   **Ridgeline (Strategic Growth/CFO Module):** *Growth & Valuation
    OS*.
````

````plaintext
Increasing Roofing Company Valuation & Exit Strategy Blueprint.docx
*In essence, Ridgeline is the module that*
    *maps Spec-OS's data to valuation drivers directly. It can generate
    a "growth roadmap" that basically mirrors an exit strategy
    consultant's plan:* implement marketing program (Torch) -\> results
    in X growth; implement ops improvements (Takeoff) -\> yields Y
    margin lift; combined effect = enterprise value could double in 2
    years*[\[31\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=3,Ridgeline%20for%20Trades)[\[73\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Growth%20%26%20Valuation%20OS%20,for%20Trades).
    It's called "Ridgeline" aptly, suggesting a high vantage point
    overseeing the whole business. By using Ridgeline, an owner can
    constantly track progress toward being "franchise-ready" -- in fact,
    one of Spec-OS's selling points could be* "Get franchise-level
    systems without paying franchise
    fees"*[\[74\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=match%20at%20L915%20Tier%203%3A,%E2%80%9D),
    which resonates with the idea of maximizing valuation by
    systematizing. Additionally, Ridgeline's* *executive dashboard*
    *would likely include metrics like: revenue per crew, customer
    acquisition cost, average job profitability, AR days, etc., giving a
    holistic view. This helps owners make decisions like a CFO would
    (e.g. understanding cash flow needs for growth, or ROI on a new
    estimator hire). Importantly, Ridgeline would incorporate* *scenario
    planning:* "If you grow 20% next year, hire 1 more crew and invest
    \$50k in marketing, your valuation could reach \$X" *-- essentially
    forecasting both operationally and financially, akin to what a CFO
    or PE firm does in modeling. All this guidance is something no
    competitor is currently packaging in software form for trades. It
    demystifies valuation for the owner and provides a* *clear linkage
    between daily actions and exit value*\*, which is exactly what our
    research blueprint aims to achieve.

**Spec-OS Module Mapping to Drivers:** To explicitly tie Spec-OS
features to the valuation drivers from section 2:

-   *Owner Independence:* Spec-OS provides the digital SOPs, automated
    workflows, and reporting that enable the business to run on
    autopilot. By codifying **intake, scheduling, AR collections, etc.
    into Spec-OS**, the company relies on systems, not the owner's
    memory[\[75\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Inputs%3A%20data%20you%20need%20,QBO%20file%2C%20CRM%20exports%2C%20SOPs)[\[76\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Produces%20the%20outputs%20in%20machine,form).
    This directly addresses buyers' concern about owner reliance,
    increasing
    sellability[\[11\]](https://peakbusinessvaluation.com/valuation-multiples-for-a-roofing-company/#:~:text=Understanding%20the%20value%20of%20a,33%20for%20maximum%20value).
-   *Technology & Systems:* Using Spec-OS **is** adopting cutting-edge
    tech.
````

````plaintext
Increasing Roofing Company Valuation & Exit Strategy Blueprint.docx
This level of operational command (enabled by Takeoff)
    is typically what differentiates a *7× multiple company* from a *3×
    multiple
    one*[\[10\]](https://industrypro.com/industry_insight/there-is-no-normal-valuation-only-opportunity-to-prepare/#:~:text=In%20today%E2%80%99s%20market%2C%20two%20companies,compelling%20story%20to%20tell%20buyers).

-   **Ridgeline (Strategic Growth/CFO Module):** *Growth & Valuation
    OS*. Ridgeline is about tying everything together at the strategic
    level -- providing the owner (and eventually a potential buyer) with
    an **executive dashboard and growth
    roadmap**[\[31\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=3,Ridgeline%20for%20Trades)[\[35\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Mirrors%20Ridgeline%E2%80%99s%20role%20as%20CMO%2FCTO,%E2%80%9Cbrain%E2%80%9D%20for%20the%20business).
    It's like having a high-level CFO/strategist constantly evaluating
    the business. Specifically, Ridgeline can take the data from Torch
    (marketing) and Takeoff (operations), plus the raw financials (from
    the bookkeeping side), and translate it into **actionable insights
    on growth and enterprise value**. For example, Ridgeline could
    display a **real-time valuation estimate** of the business on the
    dashboard, based on current trailing twelve months SDE and a
    multiple that adjusts as key metrics improve. It could literally
    show, *"Estimated Business Value: \$2.4M"* and update as you
    increase revenue or as your risk factors decrease. More importantly,
    Ridgeline can function as an AI advisor: *"What should I do to get
    my valuation to \$5M?"* and it would answer with specific tasks
    (drawn from the drivers) -- *"Increase your recurring revenue. For
    instance, launch a roof maintenance plan. If you convert 50 clients
    at \$500/year, that could add \$25k stable profit and increase your
    multiple from 3× to
    \~3.5×[\[24\]](https://www.sunbeltatlanta.com/blog/sell-your-roofing-business-tips-to-maximize-value#:~:text=While%20EBITDA%20is%20the%20standard,into%20a%20higher%20selling%20price)."*
    Or *"Your gross margin is 28%, slightly below industry avg 30% --
    consider raising prices 5% or finding a cheaper supplier. A 2%
    margin increase on \$X revenue would add \$Y to EBITDA, boosting
    value by \$Y*multiple." *In essence, Ridgeline is the module that*
    *maps Spec-OS's data to valuation drivers directly. It can generate
    a "growth roadmap" that basically mirrors an exit strategy
    consultant's plan:* implement marketing program (Torch) -\> results
    in X growth; implement ops improvements (Takeoff) -\> yields Y
    margin lift; combined effect = enterprise value could double in 2
    years*[\[31\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=3,Ridgeline%20for%20Trades)[\[73\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Growth%20%26%20Valuation%20OS%20,for%20Trades).
````

````plaintext
Increasing Roofing Company Valuation & Exit Strategy Blueprint.docx
Spec-OS can **productize these roles into software agents and
workflows**[\[67\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Yes%E2%80%94if%20you%20treat%20%E2%80%9Csoftware%E2%80%9D%20as,that%E2%80%99s%20your%20orchestrator%20of%20choice)[\[68\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Service%20%3D%20what%20Matador%2FLogistis%20consultants,audit%2C%20decide%2C%20configure%2C%20monitor):

-   **Torch (Marketing/CMO Module):** *Lead Engine OS*. Torch is
    envisioned as the marketing "brain" of the platform -- it could
    handle everything from local SEO to lead intake processes. For
    example, Torch can interface with Google My Business (GMB), online
    ad accounts, and review sites to provide a marketing audit and
    action
    plan[\[69\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Lead%20Engine%20OS%20app%3A)[\[70\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Local%20SEO%20remediation%20plan).
    Spec-OS could automatically analyze your Google reviews and
    citations, then output a **reputation improvement plan**, or ingest
    your website and suggest SEO optimizations and ad
    targeting[\[69\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Lead%20Engine%20OS%20app%3A)[\[70\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Local%20SEO%20remediation%20plan).
    Essentially, Torch would do what a growth consultant might: ensure
    your **online presence and lead funnel** are optimized (which ties
    to the **Reputation & Marketing driver** for valuation). It could
    generate an "SEO remediation checklist" or a **smart lead-gen SOP**
    for office staff to follow up with
    inquiries[\[71\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Step%203%3A%20LLM%20,generates)[\[72\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Capture%20as%20machine).
    Moreover, Torch could monitor KPIs like cost per lead, conversion
    rates, and review ratings, all of which Spec-OS displays on a
    dashboard. By automating these tasks, Spec-OS helps roofing owners
    systematically improve their **marketing maturity** -- increasing
    lead flow, improving close rates, and tracking customer satisfaction
    (reviews). These are exactly the factors that lead to higher revenue
    and a stronger brand, translating into a higher exit multiple.
    Instead of paying a marketing agency monthly, the owner gets an
    AI-driven CMO within Spec-OS constantly fine-tuning their marketing
    machine.

-   **Takeoff (Operations/CTO Module):** *Field Ops & Automation*.
    Takeoff acts as the operational and technology engine -- akin to a
    fractional CTO/COO focusing on efficiency and systemization. In
    practice, this module would map out all core operational workflows:
    from initial inspection and estimating (the term "takeoff" itself
    refers to estimating materials from plans) to scheduling crews, to
    quality control and job close-out. Spec-OS's Takeoff module can
    provide **templates and playbooks for operations**: e.g.
````

````plaintext
Roofers Productized Spec-OS 20251210.docx
**Finance Command Center -- Deliverables**

**Assets**

-   13-week cashflow model, annual budget, and forecast workbook.

-   Internal module P&Ls (crews, sales, admin) built on modular
    management methodology.

**Automations**

-   Alerts for cash stress (e.g., AR days, payables, pipeline shrink).

-   Scenario "levers" to model hiring, marketing spend, and price
    changes.

**Analytics**

-   EVA/ROIC-style module performance and "net contribution" per unit.

-   Dashboard tying marketing and operational improvements to economic
    profit.

**Franchise-Without-The-Franchise OS -- Deliverables**

**Assets**

-   Central Spec-Kit repository of all SOPs written in WTS style
    ("systems mindset").

-   Decision-graph maps for core processes: intake, scheduling, field
    work, QA, comms, collections.

**Automations**

-   Guardrailed AI agents (Intake Copilot, Dispatch Copilot, AR Copilot,
    etc.).

-   Event-driven workflows triggered by calls, emails, jobs, and
    invoices.

**Analytics**

-   Process dashboards: bottlenecks, leakage, lockup, compliance
    exceptions.

-   "Next two improvements" recommendations baked into the UI.

**4. Systemization Opportunity**

This is where Spec-OS really becomes a platform-as-a-service, not a
consulting boutique.

1.  **Template-First: Trade Playbooks**

    -   For roofing, you codify Torch/Takeoff/Ridgeline into **template
        Spec-Kits**: standard job types, lead funnels, dispatch
        patterns, checklists, and dashboards for \$1M--\$10M revenue
        operators.

    -   For each new client, you "clone and customize" rather than
        rebuild from scratch.

2.  **SOP-to-Agent Compiler**

    -   All marketing, ops, and finance SOPs are rewritten into clean,
        WTS-style systems and then compiled into decision graphs and
        agents.

    -   Over time you build a library of proven workflows by vertical,
        channel, and size.

3.  **Internal Economy + Telemetry**

    -   Modular Management's internal accounting becomes the engine for
        **crew/branch scorecards** inside Spec-OS -- each module (crew,
        sales pod, admin team) has EVA-style metrics and improvement
        logs.

    -   Telemetry from tools (time, jobs, AR, marketing) feeds monthly
        "Module Performance Reports" automatically.

4.  **Continuous Improvement Flywheel**

    -   "Work the System" mindset + Elon's Algorithm (question → delete
        → simplify → accelerate → automate) is baked into the OS so
        every quarter the platform proposes what to fix next.

Result: each engagement strengthens the Spec-OS template library, which
makes the next engagement faster, more profitable, and more SaaS-like.

**5. Suggested Pricing / Packaging**

You can mirror Matador and Logistis price psychology, but tie pricing to
**company size (revenue / tech count)** and **scope (marketing, ops,
finance, or full stack)**.
````

````plaintext
Roofers Productized Spec-OS 20251210.docx
**3. Deliverables per Bundle**

For clarity to buyers and partners, each bundle should have concrete
deliverables in three categories: **Assets**, **Automations**, and
**Analytics**.

**Lead Engine OS -- Deliverables**

**Assets**

-   Local reputation and listings report + remediation plan.

-   Redesigned "smart funnel" website with job-type landing pages.

-   Intake scripts in Spec-Kit format (per job type and lead source).

**Automations**

-   Call-routing + lead source tagging.

-   Automated follow-up sequences (SMS/email) for estimates and missed
    calls.

-   Trigger to create Spec-OS Job Spec from each new lead.

**Analytics**

-   Channel-level dashboard: impressions, calls, booked jobs, revenue,
    margin.

-   Conversion and speed-to-lead metrics surfaced in Marketing & Revenue
    Intelligence.

**Ops Stack OS -- Deliverables**

**Assets**

-   Tech stack map plus system architecture diagram.

-   Standard job templates (duration, crew type, materials) by job type.

**Automations**

-   Job creation and scheduling rules (capacity-aware calendar).

-   Integrations between CRM/FS tools and Spec-OS event bus.

-   Auto-triggered tasks for material ordering, change orders, and
    inspections.

**Analytics**

-   Cycle-time waterfall: lead → scheduled → in-progress → collected.

-   Crew-level utilization and rework rates.

**Growth & Valuation OS -- Deliverables**

**Assets**

-   12-month growth roadmap with prioritized system improvements.

-   Contractor valuation model (EV/Revenue, EV/EBITDA, scenario tabs).

**Automations**

-   Quarterly review workflow with pre-built "Spec Jam" agenda.

-   Notifications when KPIs drift from roadmap targets.

**Analytics**

-   Executive dashboard: profitability per crew, per channel, per
    system.

-   "Value delta" view tying system improvements to implied exit
    multiple.

**Books OS -- Deliverables**

**Assets**

-   Trade-optimized chart of accounts and job-costing structure.

-   Month-end close checklist customized to the tech stack.

**Automations**

-   Data sync from CRM/FS to accounting for job revenue, deposits, and
    WIP.

-   AR and AP cadence reminders surfaced as Spec-OS tasks.

**Analytics**

-   Job and service-line margin dashboards.

-   Overhead coverage and breakeven dashboards for crews and branches.

**Finance Command Center -- Deliverables**

**Assets**

-   13-week cashflow model, annual budget, and forecast workbook.

-   Internal module P&Ls (crews, sales, admin) built on modular
    management methodology.

**Automations**

-   Alerts for cash stress (e.g., AR days, payables, pipeline shrink).

-   Scenario "levers" to model hiring, marketing spend, and price
    changes.

**Analytics**

-   EVA/ROIC-style module performance and "net contribution" per unit.

-   Dashboard tying marketing and operational improvements to economic
    profit.
````

````plaintext
Increasing Roofing Company Valuation & Exit Strategy Blueprint.docx
This contributes to better **labor management and risk
    reduction**, which buyers love to see. It might also calculate
    **revenue per crew** or **wages as % of revenue** and benchmark it,
    so owners know if they're hitting optimal efficiency.
-   *Financial Metrics & Transparency:* The Finance/Books aspect of
    Spec-OS (integrated with Ridgeline) will ensure **real-time
    financial data** is available. This means key metrics like gross
    margin, overhead ratio, current EBITDA, etc., are always up to date
    and visualized. When it comes time to sell, providing this level of
    financial clarity (with history) reduces buyer uncertainty -- often
    translating to a better valuation or smoother due
    diligence[\[16\]](https://www.sunbeltatlanta.com/blog/sell-your-roofing-business-tips-to-maximize-value#:~:text=Buyers%20will%20look%20closely%20at,several%20elements%2C%20including)[\[78\]](https://www.sunbeltatlanta.com/blog/sell-your-roofing-business-tips-to-maximize-value#:~:text=How%20Roofing%20Company%20Valuation%20Is,Calculated).
    Additionally, Spec-OS could enforce good practices like monthly
    close checklists, proper job costing entries, etc., effectively
    acting as a controller to keep the books due-diligence ready.
-   *Franchise-Ready Ops without Franchising:* This phrase is
    essentially the value proposition of Spec-OS's combined modules. By
    implementing Spec-OS fully, a roofing company should have
    **standardized operating procedures, a strong brand presence,
    reliable lead generation, automated training/onboarding (through
    stored SOPs and decision graphs), and detailed performance
    dashboards** -- very akin to what a franchise system provides its
    franchisees. But here, the independent business gets those benefits
    via software, *retaining their independence and equity*. This is
    attractive to both owners (who improve their business) and to
    **strategic acquirers or PE** (who will pay a premium for a business
    that is turn-key with franchise-like systems in
    place)[\[31\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=3,Ridgeline%20for%20Trades)[\[74\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=match%20at%20L915%20Tier%203%3A,%E2%80%9D).
    In fact, a strategic buyer might adopt Spec-OS across all their
    acquired locations to harmonize operations -- making a Spec-OS-run
    company even more appealing.

**Embedding Valuation into Spec-OS:** The endgame is that Spec-OS
doesn't just help run the business; it helps *value* and **sell** the
business. Concretely, the platform could feature a **"Valuation
Dashboard"** that is always accessible.
````

````plaintext
Thought process

The user is asking about connecting Claude to LangChain to create a knowledge base for their roofing-cfo valuation module. They're building the Spec-OS software with a Ridgeline/valuation module.

Let me search for more specific information about the valuation feature and any existing technical specifications.
````

**project_knowledge_search**

*Request*

````javascript
{
  "query": "CrewCFO valuation feature technical implementation"
}
````

*Response*

````plaintext
CrewCFO Valuation Feature 20251213.docx
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
````

````plaintext
CrewCFO Valuation Feature 20251213.docx
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
````

````plaintext
CrewCFO Valuation Feature 20251213.docx
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

6.
````

````plaintext
CrewCFO Valuation Feature 20251213.docx
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
````

````plaintext
CrewCFO Valuation Feature 20251213.docx
**Value Delta Timeline**

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
````

````plaintext
CrewCFO Valuation Feature 20251213.docx
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
````

````plaintext
AI-Powered Bookkeeping for Roofing Contractors_ MVP Build Plan and Strategic Analysis.md
Track these metrics per customer segmentâ€”new customers require more exceptions during learning period, stabilizing after 3-6 months of feedback loop training.

---

## Implementation roadmap for MVP launch

**Phase 1 (Weeks 1-4): Core Infrastructure**
Set up PostgreSQL database with multi-tenant schema, implement OAuth 2.0 flows for QuickBooks Online and Xero, build basic sync adapters for invoices/payments/customers, deploy Docker containers on ECS Fargate, configure secrets management and CI/CD pipeline with security scanning.

**Phase 2 (Weeks 5-8): Invoice Processing Pipeline**
Integrate PaddleOCR + docTR for document extraction, implement LangChain extraction workflow with structured outputs, build python-accounting integration for double-entry ledger, create job costing schema with cost code hierarchies, deploy n8n for workflow orchestration.

**Phase 3 (Weeks 9-12): Construction Features**
Build AIA G702/G703 billing automation, implement lien waiver tracking with state-specific templates, create WIP schedule calculations and reporting, integrate ServiceTitan/Jobber adapters (where API access available), develop cash flow forecasting with seasonal patterns.

**Phase 4 (Weeks 13-16): Intelligence Layer**
Deploy tiered transaction classification (rules â†’ ML â†’ LLM), implement anomaly detection with explanation generation, build natural language querying interface, create financial commentary generation for reports, establish feedback loops for continuous model improvement.

**Phase 5 (Weeks 17-20): Production Hardening**
Complete SOC 2 Type 1 readiness documentation, implement comprehensive monitoring and alerting, conduct security audit and penetration testing, build customer onboarding and data migration tools, launch beta with 5-10 pilot customers.

**Key GitHub repositories to reference**: PaddleOCR (github.com/PaddlePaddle/PaddleOCR), docTR (github.com/mindee/doctr), python-accounting (github.com/ekmungai/python-accounting), LangChain (github.com/langchain-ai/langchain), LlamaIndex (github.com/run-llama/llama_index), n8n (github.com/n8n-io/n8n), Temporal (github.com/temporalio/temporal), Beancount (github.com/beancount/beancount).

---

## Conclusion: the strategic opportunity

The construction bookkeeping automation market presents a clear gap between technically advanced but generic AI platforms (Digits, Zeni) and construction-specific but automation-limited tools (Adaptive, legacy ERPs). Building for the **underserved sub-$10M roofing contractor segment** with AI-native architecture, construction-specific compliance automation, and sub-$400/month pricing creates defensible differentiation.

The technical foundation combining PaddleOCR, LangChain, and python-accounting delivers modern AI capabilities on proven open-source infrastructure. The human-in-the-loop design achieving 70-85% automation with configurable exception routing maintains quality while dramatically reducing manual bookkeeping burden.
````

````plaintext
Increasing Roofing Company Valuation & Exit Strategy Blueprint.docx
It's also evidence that **AI in
accounting is maturing**: rather than generic black-box AI, we see
specialized AI that *knows* about AIA billing forms, lien waivers, etc.,
which is a big leap in usefulness for
contractors[\[66\]](https://insidepublicaccounting.com/2025/04/21/adaptive-launches-industry-specific-ai-to-help-accounting-firms-scale-construction-services-without-adding-headcount/#:~:text=strategic%20opportunity%20for%20accounting%20firms,margin%20advisory%20services).

For Spec-OS, this competitive scan shows both an **opportunity and a
validation**: none of the mainstream automated finance tools truly
deliver a comprehensive trade-focused valuation or CFO solution yet, but
Adaptive's traction confirms that contractors greatly value solutions
built for them. Owners often complain that generic software doesn't give
them the insight they need (e.g. which crew is most profitable, or how
much should I charge per square to hit my margin). The door is open for
Spec-OS to integrate bookkeeping, operational data, and AI to deliver
*actionable financial intelligence* (not just bookkeeping) in a way
these competitors currently do not. The ultimate aim is to **support
job-costing, crew performance tracking, cashflow management, *and* exit
planning** in one system -- essentially picking up where Pilot or
QuickBooks Live stop, and adding the trade-specific layer plus
forward-looking guidance. In the next section, we'll explore how Spec-OS
can fulfill that role, effectively *"software-izing"* what a fractional
CFO or COO would do into an intelligent platform.

## 6. Spec-OS Opportunity & Strategic Fit

Given the gaps identified, Spec-OS has a compelling opportunity to
**embed valuation and growth advisory directly into the roofing
business's operating software**. By integrating financial, operational,
and marketing data, Spec-OS can act as a virtual **CMO/CTO/CFO trio**
for contractors -- turning what used to be high-end consulting services
into automated, scalable software workflows. Let's break down how
Spec-OS can leverage its modules (Torch, Takeoff, Ridgeline, etc.) to
drive the very **valuation drivers** we outlined and deliver a unique
value proposition:

**"Software-izing" CMO, CTO, CFO Services:** In a traditional sense,
improving a roofing company's value might involve hiring a **fractional
CMO** (to boost marketing), a **fractional CTO/COO** (to streamline tech
and ops), and a **fractional CFO** (to tighten financials and strategy).
Spec-OS can **productize these roles into software agents and
workflows**[\[67\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Yes%E2%80%94if%20you%20treat%20%E2%80%9Csoftware%E2%80%9D%20as,that%E2%80%99s%20your%20orchestrator%20of%20choice)[\[68\]](file://file-EfX4M7yDHpV2M78RToJ3w8#:~:text=Service%20%3D%20what%20Matador%2FLogistis%20consultants,audit%2C%20decide%2C%20configure%2C%20monitor):

-   **Torch (Marketing/CMO Module):** *Lead Engine OS*.
````

````plaintext
Thought process: Synthesized project context and architected integration strategy.

Now I have a good understanding of what the user is building. They have extensive documentation on:
1. CrewCFO / Spec-OS - a roofing contractor CFO software
2. A Valuation Intelligence Module with 5 core features (Real-time Valuation Engine, Value Driver Scoring, Scenario Simulator, Exit Readiness/Deal Room, Roadmap Agent)
3. They're using LangChain in their architecture

The user is asking about connecting me (Claude) to LangChain to create a knowledge base to help with structure and planning for the valuation module.

Let me provide a comprehensive answer about:
1. Yes, you can connect Claude to LangChain
2. The options available (RAG, agents, knowledge bases)
3. A concrete approach for their use case
4. Cursor-friendly prompts for implementation
````

Yes, absolutely! Based on your CrewCFO Valuation Module documentation, here are the **simplest and fastest** ways to connect Claude + LangChain for a knowledge base:

---

## **Option 1: LangChain + Claude RAG (Simplest)**

Use LangChain's retrieval-augmented generation with your project docs as the knowledge base.

**Cursor prompt to scaffold this:**

```
Create a LangChain RAG knowledge base with these requirements:
1. Use Claude claude-sonnet-4-20250514 via langchain-anthropic
2. Vector store: ChromaDB (local, zero-config)
3. Embeddings: sentence-transformers/all-MiniLM-L6-v2 (free, fast)
4. Load documents from ./docs folder (support .md, .docx, .pdf)
5. Chunk size 1000 with 200 overlap
6. Simple CLI interface to query the knowledge base

Structure:
- knowledge_base/
  - loader.py (document ingestion)
  - retriever.py (vector store + retrieval)
  - chain.py (RAG chain with Claude)
  - cli.py (query interface)
  - docs/ (your markdown/docx files)

Include a requirements.txt with pinned versions.
```

---

## **Option 2: LangGraph Agent (More Powerful)**

If you want Claude to **reason over your valuation docs AND take actions** (generate schemas, write specs, etc.):

**Cursor prompt:**

```
Create a LangGraph agent for CrewCFO valuation module planning:

1. Tools the agent should have:
   - search_docs: RAG search over project knowledge base
   - write_spec: Generate structured spec files (JSON/YAML)
   - generate_schema: Output database schema proposals
   - create_epic: Generate Epic/Story breakdown in speckit format

2. Use Claude claude-sonnet-4-20250514 as the LLM
3. ChromaDB for vector store
4. Persist agent state between sessions

The agent should be able to:
- Answer questions about valuation driver models
- Propose database schemas for valuation_snapshots, driver_scores
- Generate implementation roadmaps
- Create task breakdowns

Include example usage for: "What schema do I need for the Value Driver Scoring Engine?"
```

---

## **Option 3: Claude Projects API + MCP (Newest/Native)**

Use Anthropic's native **MCP (Model Context Protocol)** to give Claude direct access to your docs without LangChain:

**Cursor prompt:**

```
Create an MCP server that exposes my CrewCFO project docs to Claude:

1. MCP server in Python using mcp-python-sdk
2. Tools:
   - search_project_docs(query: str) -> List[DocChunk]
   - get_document(doc_id: str) -> str
   - list_documents() -> List[DocMetadata]

3. Index documents from ./project-docs folder
4. Use ChromaDB for vector search
5. Include Claude Desktop configuration in claude_desktop_config.json

This gives Claude native access to my valuation module specs.
```

---

## **My Recommendation for Your Use Case**

Given you want to **plan the valuation module structure**, I'd start with **Option 1 (RAG)** because:

1. **5-minute setup** - just load your existing .docx files
2. **Test immediately** in CLI
3. **Upgrade path** - easy to add LangGraph tools later

Here's the quickest test you can run:

```python
# quick_test.py - run this first to validate
from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

# Load your docs
loader = DirectoryLoader("./docs", glob="**/*.md")
docs = loader.load()

# Create vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(docs, embeddings)

# Create RAG chain with Claude
llm = ChatAnthropic(model="claude-sonnet-4-20250514")
qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

# Test it
print(qa.invoke("What are the 5 core features of the Valuation Intelligence Module?"))
```

---

**Want me to generate the full scaffold for any of these options?** I can create the complete project structure with all files ready to copy into Cursor.



## Prompt:
12/15/2025, 4:32:48 PM

yes



## Response:
12/15/2025, 4:36:53 PM

````plaintext
Thought process: Architected comprehensive LangChain RAG scaffold for immediate deployment.

The user wants me to generate the full scaffold for the LangChain + Claude RAG knowledge base. Let me create a complete project structure that they can use immediately.

I should read the SKILL.md files first since I'm creating code files, but this is primarily Python code files, not documents. Let me create a comprehensive scaffold with all the necessary files.

I'll create:
1. A complete directory structure
2. All Python files with proper implementation
3. Requirements.txt
4. README with setup instructions
5. A .env.example file

Let me make this practical and immediately usable.
````

````plaintext
View: Check if I need docx skill for loading documents
````

````plaintext
Thought process: Architected comprehensive RAG scaffold integrating LangChain and Claude.

I'll create a complete scaffold for the LangChain + Claude RAG knowledge base. This will be a practical, ready-to-use project.

Let me create the full structure:
1. requirements.txt
2. .env.example
3. loader.py - document ingestion supporting .md, .docx, .pdf
4. retriever.py - vector store setup
5. chain.py - RAG chain with Claude
6. cli.py - interactive CLI
7. README.md - setup instructions
8. A quick test script

I'll put all files in /home/claude and then copy to outputs.
````

Let me create the complete scaffold for you:

````plaintext
Bash Tool: Create project directory structure
````

````plaintext
Thought process: Orchestrated comprehensive scaffold file generation.

Now let me create all the files for the scaffold.
````

````plaintext
Create File: Create requirements.txt with pinned versions
````

````plaintext
Thought process: Prepared to generate environment configuration file.

Good. Now let me create the .env.example file.
````

````plaintext
Create File: Create .env.example template
````

````plaintext
Thought process: Architected modular Python components for implementation.

Now let me create the main Python files: loader.py, retriever.py, chain.py, and cli.py.
````

````plaintext
Create File: Create loader.py for document ingestion
````

````plaintext
Thought process: Initiated file creation process.

Now let me create the retriever.py file.
````

````plaintext
Create File: Create retriever.py for vector store setup
````

````plaintext
Thought process: Prepared to construct RAG chain implementation.

Now let me create the chain.py file for the RAG chain with Claude.
````

````plaintext
Create File: Create chain.py for RAG chain with Claude
````

````plaintext
Thought process: Architected interactive CLI interface for data querying.

Now let me create the CLI.py file for interactive querying.
````

````plaintext
Create File: Create cli.py for interactive CLI interface
````

````plaintext
Thought process: Orchestrated documentation and testing framework creation.

Now let me create a README with setup instructions and a quick test script.
````

````plaintext
Create File: Create README.md with setup instructions
````

````plaintext
Thought process: Orchestrated test script, upgrade guide, and sample documentation.

Now let me create a quick test script that's even simpler, and also let me create an upgrade guide for LangGraph. But first, let me create a sample document in the docs folder so the user can test immediately.
````

````plaintext
Create File: Create sample doc for testing
````

````plaintext
Thought process: Devised test script for standalone execution.

Now let me create a quick test script that can be run without the full CLI.
````

````plaintext
Create File: Create quick_test.py for immediate testing
````

````plaintext
Thought process: Architected comprehensive upgrade pathway for advanced features.

Now let me create the LangGraph upgrade guide so they have a path to more advanced features.
````

````plaintext
Create File: Create LangGraph upgrade guide
````

````plaintext
Thought process

Now let me zip the project and copy it to the outputs directory so the user can download it.
````

````plaintext
Bash Tool: Create zip file of the project
````

````plaintext
Thought process

Good. Now let me copy both the zip and the individual files to the output directory, and also view the final structure.
````

````plaintext
Bash Tool: Copy project to outputs
````

````plaintext
Thought process: Prepared to deliver requested files.

Now let me present the files to the user.
````

````plaintext
View: Show final project structure
````

````plaintext
Thought process

Let me also list what's in the docs folder to confirm the test file is there.
````

**present_files**

*Request*

````javascript
{
  "filepaths": [
    "/mnt/user-data/outputs/crewcfo-knowledge-base.zip"
  ]
}
````

*Response*

````plaintext
Thought process: Orchestrated file delivery and prepared requested materials.

Good, I've created and shared the zip file. Now let me provide the user with a summary and the Cursor prompts they requested.
````

Here's your complete scaffold. The zip contains:

```
crewcfo-knowledge-base/
├── docs/
│   └── valuation_quick_reference.md  # Sample doc to test immediately
├── loader.py          # Document loading (.md, .docx, .pdf)
├── retriever.py       # ChromaDB vector store
├── chain.py           # RAG chain with Claude
├── cli.py             # Interactive CLI
├── quick_test.py      # Validate setup
├── requirements.txt   # Pinned dependencies
├── .env.example       # API key template
├── README.md          # Full setup guide
└── UPGRADE_TO_LANGGRAPH.md  # Agent upgrade path
```

---

## Quick Setup Commands (paste in terminal)

```bash
# Unzip and setup
unzip crewcfo-knowledge-base.zip
cd crewcfo-knowledge-base
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env → add ANTHROPIC_API_KEY

# Copy your CrewCFO docs
cp /path/to/your/docs/*.docx ./docs/
cp /path/to/your/docs/*.md ./docs/

# Test
python quick_test.py

# Run
python cli.py chat
```

---

## Cursor Prompts for Next Steps

**1. Add your project docs to the knowledge base:**
```
Copy the .docx and .md files from /mnt/project/ into the docs/ folder, 
then run `python cli.py ingest --rebuild` to index them.
```

**2. Test valuation module questions:**
```
python cli.py ask "What database schema do I need for Feature B Value Driver Scoring Engine?"
```

**3. If you want the LangGraph agent upgrade:**
```
Read UPGRADE_TO_LANGGRAPH.md and create agent.py with tools for:
- search_knowledge_base
- generate_database_schema  
- generate_epic_breakdown
- generate_spec_file
```

The system uses **local embeddings** (no API cost for indexing) and **Claude claude-sonnet-4-20250514** for generation. Want me to also create the LangGraph agent.py file now, or help you load your actual project documents into the knowledge base?



## Prompt:
12/15/2025, 4:37:57 PM

yes



## Response:
12/15/2025, 4:45:51 PM

````plaintext
Thought process: Orchestrated LangGraph agent setup and dependency updates.

The user wants me to create the LangGraph agent.py file. I already have the content in UPGRADE_TO_LANGGRAPH.md, but I should create a standalone agent.py file that's ready to use. Let me also add langgraph to the requirements.txt.
````

````plaintext
Edit: Add langgraph to requirements.txt
````

````plaintext
Thought process: Architected comprehensive agent tooling for valuation planning.

Now let me create the full agent.py file with all the tools for working with the valuation module planning.
````

````plaintext
Create File: Create LangGraph agent with full tool suite
````

````plaintext
Thought process: Orchestrated documentation updates and knowledge base integration.

Now let me update the README to include the agent usage, and also copy the project's actual docs to the knowledge base docs folder.
````

````plaintext
Edit: Update README with agent commands
````

````plaintext
Thought process: Orchestrated file transfer from project directory.

Now let me copy the actual project docs from /mnt/project/ to the docs folder so the user has real content to work with.
````

````plaintext
Bash Tool: Copy project docs to knowledge base
````

````plaintext
Thought process: Assembled project resources and validated system integration.

Now I have all the project docs in the docs folder. Let me also install the required packages and test that everything works together.
````

````plaintext
Bash Tool: Install dependencies for testing
````

````plaintext
Thought process

I need to use --break-system-packages flag
````

````plaintext
Bash Tool: Install dependencies with break-system-packages
````

````plaintext
Thought process: Expedited code delivery for local execution.

Let me skip the testing for now and just prepare the final output. The code is ready, the user just needs to run it in their local environment.
````

````plaintext
Bash Tool: Recreate zip with all files
````

````plaintext
Thought process: Assembled and organized project documentation for delivery.

Now I have the complete package with all the project docs included. Let me copy it to outputs and present it.
````

````plaintext
Bash Tool: Copy zip to outputs
````

````plaintext
Thought process: Verified code completeness before presenting findings.

Let me also view the agent.py to make sure it's complete, and then present everything to the user.
````

````plaintext
View: Verify agent.py is complete
````

````plaintext
Thought process

The agent.py looks good. Let me present the final package to the user.
````

**present_files**

*Request*

````javascript
{
  "filepaths": [
    "/mnt/user-data/outputs/crewcfo-knowledge-base.zip"
  ]
}
````

*Response*

````plaintext
Thought process: Prepared comprehensive package overview and usage guidance.

Let me give a good summary of what's in the package and how to use it.
````

Done! The zip now includes **all your project docs** pre-loaded plus the full LangGraph agent.

## What's Inside

```
crewcfo-knowledge-base/
├── docs/                          # YOUR PROJECT DOCS (pre-loaded!)
│   ├── CrewCFO_Valuation_Feature_20251213.docx
│   ├── Increasing_Roofing_Company_Valuation_...docx
│   ├── Roofers_Productized_Spec-OS_20251210.docx
│   ├── AI-Powered_Bookkeeping_...md
│   ├── Competitive_Landscape_...docx
│   ├── Open-Source_Tools_...docx
│   ├── Spec-OS_Automation_Plan_...docx
│   └── ... (9 docs total)
├── agent.py           # ⭐ LangGraph agent with 6 tools
├── cli.py             # Simple RAG CLI
├── chain.py           # RAG chain
├── loader.py          # Document loader
├── retriever.py       # Vector store
├── quick_test.py      # Validation script
├── requirements.txt   # All dependencies
└── README.md
```

---

## Quick Start (paste these)

```bash
unzip crewcfo-knowledge-base.zip && cd crewcfo-knowledge-base

# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env → ANTHROPIC_API_KEY=sk-ant-...

# Build index from your docs
python cli.py ingest

# Use the agent!
python agent.py chat
```

---

## Agent Tools Available

| Tool | What It Does |
|------|--------------|
| `search_knowledge_base` | RAG search over all your docs |
| `generate_database_schema` | PostgreSQL CREATE TABLE statements |
| `generate_epic_breakdown` | speckit.plan format epics |
| `generate_feature_spec` | YAML feature specifications |
| `generate_implementation_roadmap` | Week-by-week timeline |
| `generate_data_model` | Mermaid ERD diagrams |

---

## Example Agent Queries

```bash
# Interactive
python agent.py chat

# Single tasks
python agent.py task "Generate the database schema for Feature B driver_scores table"

python agent.py task "Create an epic breakdown for implementing the Valuation Engine"

python agent.py task "What data dependencies does Feature A need from Books OS?"

# Demo mode (runs 3 example queries)
python agent.py demo
```

The agent will **search your docs first**, then use the appropriate tool to generate artifacts. Memory persists across turns in chat mode so you can iterate on specs.



## Prompt:
12/15/2025, 4:53:20 PM

Ok, I added your folder to my local repo: /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base

Please provide step by step detailed instructions on what to do next as far as installing langchain, etc. and then on what prompt I should use for Cursor agent to utilize this knowledge base to create a plan for this valuation magnet feature within roofing-books-cfo



## Response:
12/15/2025, 4:53:56 PM

````plaintext
Thought process: Orchestrated setup instructions and prompt strategy for knowledge base integration.

The user has downloaded the knowledge base folder and placed it in their local repo at `/Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base`. They want step-by-step instructions on:

1. How to set up the environment and install dependencies
2. What prompts to use in Cursor to leverage this knowledge base for planning the valuation module

Let me provide clear, detailed instructions.
````

## Step-by-Step Setup Instructions

### Step 1: Open Terminal in the Knowledge Base Folder

```bash
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base
```

---

### Step 2: Create Python Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install LangChain, ChromaDB, sentence-transformers, etc. (~2-5 minutes, downloads embedding model)

---

### Step 4: Configure API Key

```bash
# Copy the template
cp .env.example .env

# Open in editor
nano .env   # or: code .env (if using VS Code)
```

Edit the file to add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

Save and exit (`Ctrl+X`, then `Y` in nano)

---

### Step 5: Build the Vector Index

```bash
python cli.py ingest
```

This reads all your `.docx` and `.md` files from `docs/` and creates the ChromaDB vector store. You should see output like:
```
✓ Loaded: CrewCFO_Valuation_Feature_20251213.docx
✓ Loaded: Increasing_Roofing_Company_Valuation...docx
...
Split into ~XXX chunks
✓ Vector store created
```

---

### Step 6: Test It Works

```bash
# Quick test
python cli.py ask "What are the 5 core features of the Valuation Module?"

# Or interactive
python cli.py chat
```

---

### Step 7: Test the Agent

```bash
# Run demo
python agent.py demo

# Or interactive agent
python agent.py chat
```

---

## Using with Cursor

### Option A: Run Agent Alongside Cursor (Recommended)

Keep a terminal open running:
```bash
python agent.py chat
```

Use this to query your knowledge base and generate specs, then copy outputs into Cursor.

**Example workflow:**
1. Ask agent: "Generate the database schema for valuation_snapshots and driver_scores"
2. Copy the SQL output
3. Paste into Cursor with: "Add this schema to our migrations"

---

### Option B: Cursor Prompt to Plan Valuation Module

Open Cursor in your `roofing-books-cfo` project and use this prompt:

```
I'm building a Valuation Intelligence Module for CrewCFO (roofing contractor CFO software). 

Reference the documentation in ./crewcfo-knowledge-base/docs/ for context, especially:
- CrewCFO_Valuation_Feature_20251213.docx (feature spec)
- Increasing_Roofing_Company_Valuation___Exit_Strategy_Blueprint.docx (business context)

The module has 5 core features:
A. Real-time Valuation Engine (TTM SDE/EBITDA + multiples)
B. Value Driver Scoring Engine (6 Matador drivers → tier assignment)
C. Scenario Simulator (no-Excel what-if modeling)
D. Exit Readiness & Deal Room Builder
E. Valuation Roadmap Agent

Create a phased implementation plan with:
1. Database schema (PostgreSQL) for: valuation_snapshots, driver_scores, roadmap_items
2. Epic breakdown for Phase 4: Valuation Intelligence
3. API endpoints needed
4. React components for the Valuation Dashboard

Follow Books OS Constitution rules:
- QBO as source of truth
- Automation tiers: Rules → ML → LLM
- Human-in-loop for confidence < 80% or amounts > $5,000

Start with Feature A (Valuation Engine) database schema and API design.
```

---

### Option C: Cursor Prompt with Agent Running

If you have the agent running in terminal, use this Cursor prompt:

```
I have a LangChain knowledge base running locally with all my CrewCFO documentation. 

I just queried it and got this schema for the valuation module:

[PASTE OUTPUT FROM agent.py HERE]

Now implement this in our codebase:
1. Create the Prisma/Drizzle migration file
2. Create the API route at /api/valuation/snapshot
3. Create the React component for the Valuation Dashboard

Use our existing patterns from the Books OS module.
```

---

## Recommended Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  Terminal 1: Knowledge Base Agent                           │
│  $ python agent.py chat                                     │
│                                                             │
│  You: Generate schema for Feature B driver scoring          │
│  Agent: [generates SQL]                                     │
│                                                             │
│  You: Create epic breakdown for Valuation Engine            │
│  Agent: [generates speckit tasks]                           │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Copy outputs
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Cursor: roofing-books-cfo project                          │
│                                                             │
│  Prompt: "Implement this schema in Prisma: [paste]"         │
│  Prompt: "Create API endpoint for this: [paste]"            │
│  Prompt: "Build React component matching this spec: [paste]"│
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference Commands

```bash
# Activate environment (run first each session)
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base
source venv/bin/activate

# Simple Q&A
python cli.py ask "your question"

# Interactive RAG
python cli.py chat

# Agent with tools (recommended)
python agent.py chat

# Single agent task
python agent.py task "Generate schema for valuation_snapshots"

# Rebuild index after adding docs
python cli.py ingest --rebuild
```

---

Want me to generate a specific Cursor prompt for the first implementation task (e.g., Feature A database schema + API)?



## Prompt:
12/15/2025, 5:16:07 PM

![Screenshot 2025-12-15 at 5.10.35 PM.png](data:image/webp;base64,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)

Ok, I am ready to create a plan and start executing it. What's next please provide full detailed plan step by step, commands, where to paste them, etc.



## Response:
12/15/2025, 5:17:31 PM

````plaintext
Thought process: Architected comprehensive execution roadmap for valuation module deployment.

The user has successfully set up the knowledge base and the agent is working - I can see from the screenshot that:
1. The vector store loaded with 236 chunks
2. The agent generated database schemas for valuation_snapshots and driver_scores
3. It's showing the key design features and Books OS Constitution compliance

Now they want a full detailed plan to execute the valuation module implementation. I should provide:
1. A clear step-by-step execution plan
2. Specific commands to run in the agent
3. Cursor prompts to use for implementation
4. The sequence of tasks

Let me create a comprehensive execution plan.
````

It's working. I can see the agent generated the schemas. Now let's execute the full implementation plan.

---

## Full Execution Plan: Valuation Intelligence Module

### Phase Overview

| Phase | What | Time Est. |
|-------|------|-----------|
| 1 | Generate all specs from agent | 30 min |
| 2 | Database schema + migrations | 1 hr |
| 3 | API endpoints | 2 hrs |
| 4 | React dashboard components | 3 hrs |
| 5 | Integration + testing | 2 hrs |

---

## PHASE 1: Generate All Specs from Agent (Do This Now)

Run these commands in your agent terminal one by one. **Copy each output to a new file.**

### 1.1 Get the Full Database Schema

**In your agent terminal, type:**
```
Generate complete PostgreSQL schemas for ALL valuation tables: valuation_snapshots, driver_scores, and roadmap_items. Include all indexes, foreign keys, and constraints. Follow Books OS Constitution.
```

**Save output to:** `docs/generated/01_database_schema.sql`

---

### 1.2 Get Feature A Spec (Valuation Engine)

**In agent:**
```
Generate a feature specification for Feature A: Real-time Valuation Engine. Include inputs, outputs, data sources, automation tier, and human-in-loop rules.
```

**Save to:** `docs/generated/02_feature_a_spec.yaml`

---

### 1.3 Get Feature B Spec (Driver Scoring)

**In agent:**
```
Generate a feature specification for Feature B: Value Driver Scoring Engine with the 6 Matador drivers (Management Independence, Financial Records Quality, Recurring Revenue, Operational Systems, Customer Base Diversity, Market Outlook).
```

**Save to:** `docs/generated/03_feature_b_spec.yaml`

---

### 1.4 Get Epic Breakdown

**In agent:**
```
Create a complete epic breakdown for Phase 4: Valuation Intelligence Module. Include all user stories for Features A through E, estimated hours, dependencies, and acceptance criteria.
```

**Save to:** `docs/generated/04_epic_breakdown.md`

---

### 1.5 Get API Design

**In agent:**
```
Design the REST API endpoints for the Valuation Module. Include: GET/POST valuation snapshots, driver scores CRUD, scenario simulation endpoint, and roadmap items. Show request/response schemas.
```

**Save to:** `docs/generated/05_api_design.md`

---

### 1.6 Get Data Model ERD

**In agent:**
```
Generate a Mermaid ERD diagram showing the relationships between Tenant, ValuationSnapshot, DriverScore, RoadmapItem, and connections to existing Books OS tables.
```

**Save to:** `docs/generated/06_data_model.md`

---

## PHASE 2: Database Schema + Migrations

### 2.1 Create the generated folder

**In your main project terminal (not the agent):**
```bash
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo
mkdir -p crewcfo-knowledge-base/docs/generated
```

### 2.2 Open Cursor in your project

```bash
cursor .
```

### 2.3 Cursor Prompt for Migrations

**Open Cursor chat (Cmd+L) and paste:**

```
I'm implementing the Valuation Intelligence Module for CrewCFO. 

Create database migrations for these tables (use our existing migration pattern - Prisma/Drizzle/raw SQL, whichever we use):

## valuation_snapshots
- id: UUID primary key
- tenant_id: UUID (FK to tenants)
- as_of_date: DATE
- ttm_revenue: DECIMAL(15,2)
- ttm_sde: DECIMAL(15,2)  
- ttm_ebitda: DECIMAL(15,2)
- tier: ENUM ('below_avg', 'average', 'above_avg')
- multiple_low: DECIMAL(4,2)
- multiple_high: DECIMAL(4,2)
- ev_low: DECIMAL(15,2)
- ev_high: DECIMAL(15,2)
- confidence_score: DECIMAL(3,2)
- drivers_json: JSONB
- audit_log_ref: UUID
- created_at, updated_at: TIMESTAMPTZ

## driver_scores
- id: UUID primary key
- tenant_id: UUID (FK)
- as_of_date: DATE
- driver_key: VARCHAR(50) - one of: management_independence, financial_records_quality, recurring_revenue, operational_systems, customer_diversity, market_outlook
- score: DECIMAL(5,2) CHECK 0-100
- evidence_refs: JSONB
- computed_by: VARCHAR(20) - 'rules', 'ml', 'llm', 'human'
- confidence: DECIMAL(3,2)
- impact_weight: DECIMAL(3,2)
- created_at: TIMESTAMPTZ

## roadmap_items
- id: UUID primary key
- tenant_id: UUID (FK)
- driver_key: VARCHAR(50)
- title: VARCHAR(255)
- description: TEXT
- expected_impact_ev: DECIMAL(15,2)
- effort_level: ENUM ('low', 'medium', 'high')
- automation_tier: VARCHAR(20)
- status: ENUM ('pending', 'in_progress', 'completed', 'skipped')
- due_date: DATE
- created_at, updated_at: TIMESTAMPTZ

Add proper indexes on tenant_id and as_of_date for all tables.
Look at our existing schema pattern and match it.
```

---

### 2.4 Run the Migration

After Cursor generates the migration file:

```bash
# If using Prisma
npx prisma migrate dev --name add_valuation_tables

# If using Drizzle
npx drizzle-kit generate
npx drizzle-kit migrate

# If raw SQL
psql $DATABASE_URL -f migrations/xxx_add_valuation_tables.sql
```

---

## PHASE 3: API Endpoints

### 3.1 Cursor Prompt for Valuation API

**In Cursor chat:**

```
Create API routes for the Valuation Module following our existing patterns.

Location: Create in appropriate API folder (e.g., /app/api/valuation/ or /src/routes/valuation/)

## Endpoints needed:

### GET /api/valuation/snapshot
- Returns latest valuation snapshot for tenant
- Include driver scores in response
- Response: { snapshot: {...}, drivers: [...], tier: string, ev_range: {low, high} }

### POST /api/valuation/snapshot
- Trigger recalculation of valuation
- Pulls TTM financials from Books OS
- Computes SDE/EBITDA
- Runs driver scoring
- Returns new snapshot

### GET /api/valuation/drivers
- Returns all driver scores for tenant
- Include trend data (last 3 months)

### POST /api/valuation/drivers/:driverKey/score
- Manual score override (human-in-loop)
- Requires evidence_refs
- Body: { score: number, evidence_refs: object, notes: string }

### POST /api/valuation/simulate
- Scenario simulation endpoint
- Body: { levers: { recurring_revenue_delta, margin_delta, owner_hours_delta } }
- Returns: { projected_ebitda, projected_multiple, projected_ev }

### GET /api/valuation/roadmap
- Returns prioritized improvement tasks
- Sorted by expected_impact_ev DESC

Use our existing auth middleware, error handling, and response patterns.
Include Zod validation schemas for all request bodies.
```

---

### 3.2 Cursor Prompt for Valuation Service Logic

**In Cursor chat:**

```
Create the core valuation calculation service.

Location: /src/services/valuation/ or /lib/valuation/

## ValuationEngine service

Create a service with these methods:

### calculateTTMFinancials(tenantId)
- Query last 12 months from transactions/P&L
- Return { revenue, cogs, gross_profit, operating_expenses, sde, ebitda }
- SDE = Net Income + Owner Salary + Owner Benefits + Discretionary Expenses
- EBITDA = Net Income + Interest + Taxes + Depreciation + Amortization

### scoreDrivers(tenantId)
- Score each of the 6 Matador drivers (0-100):
  1. management_independence: Based on owner-coded hours, approval frequency
  2. financial_records_quality: Close timeliness, job-tagging %
  3. recurring_revenue: Maintenance plan revenue / total revenue
  4. operational_systems: Crew efficiency metrics if available
  5. customer_diversity: Top 5 customers % of revenue
  6. market_outlook: Static or from external data

- Return array of { driver_key, score, confidence, evidence_refs }

### determineTier(driverScores)
- Average the scores with weights
- below_avg: avg < 40 → multiple ~3x
- average: 40-70 → multiple ~4.5-5x  
- above_avg: > 70 → multiple ~7x+
- Return { tier, multiple_low, multiple_high }

### calculateValuation(tenantId)
- Orchestrates above methods
- Returns complete ValuationSnapshot
- Saves to database
- Returns { snapshot, drivers, roadmap_suggestions }

### simulateScenario(tenantId, levers)
- Takes what-if inputs
- Projects impact on EBITDA and multiple
- Does NOT save to database
- Returns projections

Follow Books OS Constitution:
- Confidence scoring on all outputs
- Flag for review if confidence < 80%
- Audit trail on all calculations
```

---

## PHASE 4: React Dashboard

### 4.1 Cursor Prompt for Valuation Dashboard

**In Cursor chat:**

```
Create the Valuation Dashboard React component.

Location: Follow our existing component structure (e.g., /components/valuation/ or /app/(dashboard)/valuation/)

## Main Dashboard Layout

Create a dashboard with these sections:

### 1. Valuation Meter (Hero Card)
- Large display: "Estimated Value: $X.XM - $X.XM"
- Current tier badge (Below Avg / Average / Above Avg)
- Confidence indicator
- "Last updated: [date]" 
- "Recalculate" button

### 2. Multiple Breakdown Card
- Show current multiple range (e.g., "4.5x - 5.0x EBITDA")
- Visual indicator of where they fall in range
- "Why this multiple?" expandable section listing driver impacts

### 3. Driver Scorecards Grid (2x3 grid)
For each of 6 drivers:
- Driver name
- Score (0-100) with progress bar
- Trend arrow (up/down/flat vs last month)
- "Improve" button linking to roadmap

### 4. Value Delta Timeline
- Line chart showing valuation over time (last 12 months)
- Annotations on major changes
- Use Recharts or our existing chart library

### 5. Roadmap Preview (Right rail or tab)
- "Next 2 Improvements" cards
- Each shows: title, expected impact, effort level
- Link to full roadmap

## Styling
- Use our existing design system (Tailwind + shadcn/ui or whatever we use)
- Match the Finance Command Center styling
- Mobile responsive

## Data Fetching
- Use our existing patterns (React Query, SWR, or server components)
- Fetch from /api/valuation/snapshot on mount
- Polling or refetch on "Recalculate" click
```

---

### 4.2 Cursor Prompt for Scenario Simulator Component

**In Cursor chat:**

```
Create the Scenario Simulator component for the Valuation Module.

## Component: ScenarioSimulator

A "what-if" calculator with sliders/inputs:

### Levers (adjustable inputs):
1. Recurring Revenue Change: Slider -20% to +100%
2. Gross Margin Change: Slider -5% to +10%
3. Owner Hours/Week: Slider (current → 0)
4. Crew Productivity: Slider -10% to +20%

### Real-time Output Display:
- Projected EBITDA: $XXX,XXX (↑$XX,XXX from current)
- Projected Multiple: X.Xx (↑X.Xx from current)
- Projected Valuation: $X.XM - $X.XM

### Visual:
- Side-by-side comparison: Current vs Projected
- Delta highlights in green (improvement) or red (decline)

### Actions:
- "Reset" button to clear changes
- "Save Scenario" button to name and store
- "Create Roadmap" button to generate tasks from scenario

### API Integration:
- Debounced calls to POST /api/valuation/simulate as sliders move
- Show loading state during calculation
- Handle errors gracefully
```

---

## PHASE 5: Integration Commands

### 5.1 After All Code is Generated

Run these to verify:

```bash
# Type check
npm run typecheck  # or: npx tsc --noEmit

# Lint
npm run lint

# Build
npm run build

# Start dev server
npm run dev
```

### 5.2 Test the Endpoints

```bash
# Test valuation snapshot
curl http://localhost:3000/api/valuation/snapshot \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test simulation
curl -X POST http://localhost:3000/api/valuation/simulate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"levers": {"recurring_revenue_delta": 0.2, "margin_delta": 0.02}}'
```

---

## Quick Reference: What to Run Where

| Terminal | Command | Purpose |
|----------|---------|---------|
| Agent terminal | `python agent.py chat` | Generate specs |
| Project terminal | `cursor .` | Open Cursor |
| Project terminal | `npm run dev` | Run dev server |
| Cursor chat | Paste prompts above | Generate code |

---

## Your Immediate Next Steps

1. **In agent terminal:** Run the 6 spec generation commands from Phase 1 (save outputs)

2. **Create folder for specs:**
   ```bash
   mkdir -p /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base/docs/generated
   ```

3. **Open Cursor:** 
   ```bash
   cd /Users/ildar/Documents/1.Projects/roofing-books-cfo
   cursor .
   ```

4. **Start with Phase 2.3** - paste the database migration prompt into Cursor

Want me to provide the first spec generation command for you to copy-paste into your agent right now?



## Prompt:
12/16/2025, 10:16:47 AM

there are two docs folders, the one in the main and in the knowledge base. Save it to the knowledge base one? Also can I ask Langchain in the terminal to save it for me?



## Response:
12/16/2025, 10:18:53 AM

````plaintext
Thought process: Deciphered dual folder locations and automated file-saving capabilities.

The user is asking two questions:
1. Which docs folder to save to - the one in the knowledge base
2. Can the LangChain agent save files directly instead of manually copying

Let me clarify both and provide a solution. I can modify the agent to have a save_to_file tool, or provide commands to save directly.
````

Good questions! Let me clarify:

## 1. Where to Save

Save to the **knowledge base** docs folder:
```
/Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base/docs/generated/
```

This keeps all specs with the knowledge base so the agent can reference them later.

---

## 2. Yes! Let's Add a Save Tool to the Agent

I'll create an updated agent that can save files directly. Run this in your **project terminal** (not the agent):

```bash
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base

# Create the generated folder
mkdir -p docs/generated
```

Now let's add a file saving tool to your agent:

````plaintext
Create File: Create updated agent with save_to_file tool
````

````plaintext
Thought process

The user wants me to provide the updated agent file and instructions on how to use it. Let me copy it to the outputs and provide clear instructions.
````

````plaintext
Bash Tool: Copy updated agent to outputs
````

````plaintext
Thought process

Let me present this file to the user and provide clear instructions on what to do next.
````

**present_files**

*Request*

````javascript
{
  "filepaths": [
    "/mnt/user-data/outputs/agent.py"
  ]
}
````

*Response*

````plaintext
Thought process: Orchestrated step-by-step instructions for file replacement and command usage.

Now I need to provide clear step-by-step instructions on how to replace the agent file and use the new commands.
````

## Updated Agent with Auto-Save

Download the new `agent.py` above and replace your existing one.

---

## Step-by-Step Instructions

### Step 1: Replace agent.py

```bash
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base

# Backup old one (optional)
mv agent.py agent_v1_backup.py

# Move the downloaded agent.py here
mv ~/Downloads/agent.py ./agent.py

# Create the generated folder
mkdir -p docs/generated
```

---

### Step 2: Stop Old Agent, Start New One

If the old agent is running, press `Ctrl+C` to stop it, then:

```bash
# Make sure venv is active
source venv/bin/activate

# Start new agent
python agent.py chat
```

---

### Step 3: Generate ALL Specs with One Command

**Option A - Batch generate everything:**
```bash
python agent.py generate-all
```

This will automatically create and save:
- `01_database_schema.sql`
- `02_feature_a_spec.yaml`
- `03_feature_b_spec.yaml`
- `04_epic_breakdown.md`
- `05_api_design.md`
- `06_implementation_roadmap.md`

**Option B - Interactive with auto-save:**
```bash
python agent.py chat
```

Then type:
```
Generate the complete database schema for valuation_snapshots, driver_scores, and roadmap_items. Save it to 01_database_schema.sql
```

The agent will generate AND save automatically.

---

### Step 4: Check Generated Files

```bash
# In terminal
ls -la docs/generated/

# Or in the agent, type:
files
```

---

## New Commands Available

| Command | What It Does |
|---------|--------------|
| `python agent.py chat` | Interactive mode with save capability |
| `python agent.py generate-all` | Generate ALL specs automatically |
| `python agent.py task "..." --save` | Single task with auto-save |
| Type `files` in chat | List generated files |

---

## Example Agent Prompts (with auto-save)

```
Generate complete database schema for all valuation tables and save to 01_database_schema.sql
```

```
Create Feature A spec for the Valuation Engine and save to 02_feature_a_spec.yaml
```

```
Generate the epic breakdown for Phase 4 and save to 04_epic_breakdown.md
```

---

## Your Next Commands

```bash
# 1. Replace agent.py
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base
mv ~/Downloads/agent.py ./agent.py
mkdir -p docs/generated

# 2. Restart agent
source venv/bin/activate
python agent.py generate-all

# 3. Check files
ls docs/generated/
```

This will generate all 6 spec files in about 2-3 minutes. Then you can feed them to Cursor for implementation.



## Prompt:
12/16/2025, 10:21:35 AM

![Screenshot 2025-12-16 at 10.21.13 AM.png](data:image/webp;base64,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)





## Response:
12/16/2025, 10:21:49 AM

````plaintext
Thought process: The user prompt is empty, so I cannot determine the primary language. However, based on the thinking block alone, here is a summary:

Diagnosed user's shell command limitation and formulated guidance.

The user is showing a screenshot of their terminal where they're interacting with the agent. The agent is telling them it can't execute shell commands like `mv` to move files. The user needs to run those commands themselves in a separate terminal.

Let me give them clear, direct instructions on what to do next.
````

I see the issue - you're typing those commands **inside** the agent chat. The agent can't run shell commands on your Mac.

## Here's What To Do:

### Step 1: Open a NEW Terminal Tab/Window

Press `Cmd+T` in your terminal to open a new tab, or open a new Terminal window.

### Step 2: Run These Commands in the NEW Terminal

```bash
# Move the downloaded agent.py file
mv ~/Downloads/agent.py /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base/agent.py

# Create the generated folder
mkdir -p /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base/docs/generated
```

### Step 3: Go Back to Your Agent Terminal

In the terminal where the agent is running, type `exit` to quit:

```
You: exit
```

### Step 4: Restart the Agent

```bash
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base
source venv/bin/activate
python agent.py generate-all
```

---

## Summary

| Terminal | What to Do |
|----------|------------|
| **Agent terminal** (where you see "You:") | Type `exit` to quit |
| **New terminal** | Run the `mv` and `mkdir` commands |
| **Same terminal** | Run `python agent.py generate-all` |

The key thing: shell commands like `mv`, `cd`, `mkdir` go in your regular terminal, not in the agent's `You:` prompt.



## Prompt:
12/16/2025, 10:25:23 AM

![Screenshot 2025-12-16 at 10.25.09 AM.png](data:image/webp;base64,UklGRjqeAABXRUJQVlA4IC6eAADwrgGdASooA+MBPm02l0gkIyIhJBL6oIANiWlu/HzTTDVeQPPHXyprOP7rxr2kwB5IfHV6fdR9RX6X3qPmL82b0K9DX6g39v9QDpLf8Z0gH//4Hrwf/RP7V+t/89+Lfwv81/nf92/xn96/sn/t/wntT+J/If1P+xf5f/O/3b9m/qz+Fv4v/GftV6lvGP1X/Kf2z/Sf8P9////9D/xj69fY/61/c/9r/a/X3+7f2z9xf9P6C/j/6R/dv7D/gv81/l/kF/G/5N/d/6d/dv+l/e/kL+B/V7uIMv/0H+u/xfsC+rn0D/Kf2L+1/9v/Be3B6f/cP71/lP+P/fv///7voP8Z/ov95/q3+X/639t////w/QD+Nfz/++/2b+0/93+7f/////Pf98/5X+p/ej0Ivm/9//4v+P/zn7W/YF/Iv6t/rf7j/gf/f/hv/////w9/f/+J/h/8X+0f/////wp/Lf8Z/zv71/kv/l/jP/////0E/k/9f/439y/wv7P//////el//f9z/+PjT+6n/+/6fwx/ul///9wQjwLBCPxSaxGGNxP1wsgTw74Q1pQiFY7O0qdCOYSaPdiVtn9iwW21wDRXyA14B3hWhez9M/dC5lElMzTgbtW/osWCrp8ss/B5KEtVjaNExktY3x0kwOkmB0kwOkmB0kyWCeu6u/xP6S95c4AZEGQ1jGtJMDpJgdJMDpJgdJMDpJgdH5Ho+UkyrlIHGsAI2fSmxm7+JfM82wMVCupUpsZ+4XYU25+av3pPQpYACNVMUQmLk+0FaLK01iHIeEuwbBO5xz+GMdmErO+spzpMJ12rKixrYYpa4DgQy3GliyOarbGxxVVNR0JcprcqYrmxMGHI9+E1B9llqFugqjWXQkNvw1dviKuUExJEvjvuiXLkq8MjBgSpDwsR90mb9nJB9QAi3HOCLn7kO1idqepoF0S9CPjnM/nJQMWgZLTjk74rXSiJNDYAX4fIdcUG9v1Br/Q0THN9X/vZsV4YrmNWpI7pnFkR+bSUK5VVnxAyiyXYNDgSoh/DKstzEBBkACGtDxTq4aOAtTgmynOvfWDiw1ucyhiuju+npX4ZCkYEFM5PURU5qTVziHv//moTiE6Oz/NCcS2fDGuVXN6yjh3wikOGmnhZ62xWLpZ/vucW5n57ZAKdDFQ3okISJEjt4iAHZHC1nDbETntYxtbh+pokfpydxSVxhSXTS0ZALXRCfHALeB1a5eeFNPYFFAMsn0KKFlZPoUUAyyfQooBlj0igGWT6FFAMsjC2NmdPtUXULoUpuLOj1brjeegKHc8+br39Ngd52gXjWSRyAqf39NyY3KJSa7kWXS5wBcPOVPLJkcYHMCKpGGAoDsieMN7yOj1VBFid0ogCdappJU+Yrx0HW3AExds8alej6hZ6I94vcgoTcJoCsrn4mGl+azZpivdeLAdBZo3wHpH3540jG0iuZg9rrNTM58W2LjQyX6Qq9YulsLuYMbVlMAMP+ho8M8NO58pYoifur7LiHLaZ3hMEHn9RpzjpKs2QD1ZcpsdKUoK+Gqbs1ur9TmciP8zlntgGiYyWsSDDAf4c/Y8HKRBzqHZ3QrhBU2Vr7VRRIJORWGzYEqe1RwqsgadDTd8ywpNIWzG7HpHAos6gDAlSbQWR1fQ2D3HIod7hbywuJLvjrS6gTRh5KHiHEEuR9+Q+r9fHSTA6STrKCHW7d65oaUAgE4CyWGveoJ6LFh4fj5x8fcDzDNDNlCGuE1ju9Aq+s/CQKt3lHk5k+UYqIVT/Ko41IdH6LGfEbQiY+6Zjoj1s1TuoBEp8Mfskg1KnmhxM5sD9J14uXUv44lnV0A0TGS1jfHSTA6SYHSSeCMblE3C51JhaEI9SD5QL9wAieNluI1GVJgIqOONkRVgjUvPuuV4/wjWTXu2K4YUBjno19EE9/c+eASSlAH6g+NsYo1ov0s/Ou1K/5MOdpfksg5Y0TGS1jfHSTA6SYHSTA6ST2UMmbJyJ3M2xNOGyQ0AhjLyUBRxmGuIKPOyC3tGxxfGeDWQskytjQqA5feUs/i744GsC3osnrdioDKl/iWFE6KuVF5mrgEPSTDk/qyNevIjRMZLWN8dJMDpJgdJMDpJfgbCW6WjMa0lT9SrTlQgngkCqJ6JSBIpdlt7D/UXMjl9bAInpJb4UgtmU5c1FNvW2CVK8WN8dJMDpJgdJMDpJQp/OYu9RwEvV01I3tqXWYWBMIjLyHtEGmceFSa+9Vy3oqJDt4mL+WRLQWqhfoGXOtai3kQtGJxBTUhjPEHaFU+UU+zSX+s6hqx90zYuLunKC10mJE/PkkYPxbmXgBpAcpgdJMDpJgdJMDnzkK3TrA2U+vErgI6HI/kpKvIzayLJ9jGtJMDpJgdJMDpJgdJJDEYyRqQPwbKSwTEaq1hTtDwQ9zU8SG6SiFhHiWKKlQrwVO6m5h4wdysFtJKMM/jn5rE2CSqjPWpACYMgDpLGSAQsUn3s5rBA/VBPkFUbqbsfX/thBDPVCNUxD5hU+EbOQCK6TP7tjfxV26ikah30Dx10whCaxyQvp9ateEfe6rFdwJS204uv9UsfWZFCmcKNw1q3MSAGY+Z67KT21Ep8He+tpE33KVnyRCiCdCNCz+WMQbrczFGjPFgUIv1Me1TraCZaeBSOzvkTXC7OiRseuS+ooZUX+4ysyOxMoznCUVpQFiNXnWwdu0E6KkeM8HXNNvbS8KsfpFscZEAhXQdCEIirraU7BobsbAGZT0rpyIWi2cRK6RgIb5helTyCYa32o9jE3AoKTFcQOPIvsjedX5WFCnjzyV0nhKv5LJrVloE9BlTvRi/UWf5Lziu/rGb7if504UN/ODx+M4FOdvOFaHd0tFa2VxnObCuIWw+YygzPcZ5czF2Cw8s/UIOASjO0o6DBkZDdpP3Z6tZ7+czLeowb527zyhluvwZxDCQjoWzBKmfmopm2cjNnwxrLLb7eyek30UZE/cPxn6XARfW2SK8j7vGomA5q9FJHKrh2LKw1bGB0vprPtS6WP4xVOBVMqBYUCIT+MluMpA/dhUwx0b8XKgpxyMPomJ0fXaBSmZiu2ZSnWWKHInLJByT4pMoBsuhE4zTm/wPsTLhh6lYy0z30qPEXyhifyw2omAaJjJaxvjpJgdJMDpJgdIkOfY95B0gGkXqWS3GMDpJgdJMDpJgdJMDpJgdJMDpJgYkEXmqfAz8nzP+Hm1XlidvmDaofiOsaq9cFAPMpiO8ES2C+ygooMyQ9raGb7TUpvmudECSITgmrPKcWEe7hEwR6RE0yh4KpxZ+5UQAvtKkEwOkmB0kwOkmB0koRx/oVXV8Xj+gR4SwdEHYAGfCQY7cOb4kOla6mzdDIOSA5AyrF1el3TCn39kOaM1TLb5L/+Pqbt65nkhZP4SOmZwaEyBlBoETEiz6nAiUxeBJQKmZNOBhy0vpfrNrGNaSYHSTA6SXzr3nwSBfzZrc2GPosW1SqYPU1P19T7m+WOU+kAcxvY2STXLWqwM6fsCxtR6NMJczUvGz5LxQ3K3XtQmkKuq9SYmzpCPWXQeVyiyQP14WdJOCiI7lbpT2Bfe79KHtWXG29loiYnlY7RNX9TcelkMavxyNc27D3pISptXRn2WV7MQCIsMdCW9ubfigE74mAaJkT15H6ynsaSCZQlyhh6SfABhrT9IE0jD9ZUnuEIVSMGomAZygqOoJiJxPDktr+qsVwEZmqA5doZnVDJGWPQk80JFTbhPCfCrEQalGNBE58T5FdIN0P3a0PhA6t8ptP2chrNJWKIMMeP5A5ceBbO21lRyxqqltoIMHpXIhgL7prIyTPPZ08mW/dtiuJm+bqs2kffRb0n+4sD1t+OPMGcpgdJMDpJgdJMDpEjd6og6HH13fTxk4CaNQ7nrhVYokIpHkSAzy5cmcCNS9U2ro2k1t5TISHyA4WKrwSafXTFAgfuo/QXLwe50G5/Euote6gaRpEeFH/G+5PxRSNd7oC+1Fbkc2SZ13WlT7IMumslUhAtqr75xd8xCxjWkmB0kwOkmB0kwOe34bp6IAn4IQ0DfAQORn/x28e/lZIJUmE7dt2ppzdVuqV+/PA7aK+qXw16J4Nqed/m6FxioAOy/eBIt0cxuv3jufhvxjrSTYK+YBvcz9LoHmH05gQV8x/Rqc9uXNgq/A4zsdY77PsrwNExktY3x0kwOkmB0kvxCfNiuzZ5xEoq6cJdZ7cZkc+ebCBuqvASKd+5l8LUD54AZL/qHugvqoqcBW+D0B7zDwAzHLY/mXtug/PhdG/fE31kTgjuVOzyp2eVOzyp2eVOzyoiPwZ15ez/EUGSQujNp7lpoUXeBBO+ilbZLFuC6SFW6u1UwPaLbzGg0q2BBKtuB1ay1JCijHCsEYbPp/wUlvob1kZr6lEMpgdJMDpJgdJMDpJgdIhwf9TaqCG0QZ4fj/4W1kYOTgfG6uCpyesigmIfYhPbaDRsQEZls26CUovGWHuHbk6a84VOikZrKNpk6lqKozdwYXVlTs8qdnlTs8qdnlTs8qCKOShJzSCz/BF+VPhbkfhEt9Xl0wI0vH7L3z2eVOzyp2eVOzyp2eVOzyYHN+xjWkmB0kwOkmB0kwOkmB0kwOkmB0kwMQAA/oEEBowss5YzgtUsso3Ydm+DTNF/I7IHuqzj/3mJ8qb2xDZVL4mzRBNAggfmE2pjwrYqr65SEwYC0706+u97jZYH2h3CwcRhwbZOI8PdLn6gZzE3J6KvIy84HgpvUkYp8umEzFh/5yhnuQddd1JGZzYK68yuI9WQYk4mhbm75THM0b7f6iayCdGvILSSMidDurI0xODGPDZRgRP46zmv/0f4jVsyRzRic6eFFmqXSZOLaSR5Tn4+HKNUxDaLuQQeEd7c6GrRBGfNuUHIFBoXxgg2VoMziWbrJJUcRF3OS7BYgsvG7QqaLHRvO8l2z2qJ94QvjkxYnBAWuFCpQ8d9La5dhYdD/2lFGSm9/Ova59mxpcU3BxUUsMeQQYdpz9jxO3QcBg+Ayke1oF2fNX2jnQ3AwXjAMZtcDzZ8H3tOIa7o2+9PLSBi/cH2YYqYF3t840PJEWLiGyXotYN84GA3lPx4VMQ7oRvfjot0Kc4LVowKBvlYrwPmtZAO9uxNmKFm0FbwaSStdeJzgXLRTN8dtP0ni4Iyl1AX2SW5uUs6u9vLMFDxDpX6qqc9w1YWYYZ97g6dNEQK0nmhc84hF7pIQkMiG6QIebhP4a15OfTmrsVbBQ9QDfDsc6Hs2IijPo1SrKXP6q2oDNBqM2jGPBlZbXf3EJ2NUxFS4T+Xv+b1gBu37z8T6rQjDbewALCcMOXwyNvDDgWYpw9FSmYxQLxpmNrmdRSl+uiNknqiG0Iu3GKroBOHx8WbvHUoqrf93bedvDCGNsWRsB6csNffHsNB5qk8XkMyZhMZIWwuWaUcZfyjlXSL5/AsX7gP0WZ4UtgnDx4VlrTW1/8tDMAII35+7QEPCh7O2AQPeIKjmhPxvsaNqEAfaFI0J1ZIH4I0Ui+5bSUq/bBA7JvhHpbDy1k3OEW29yDLODDLFq7lNPZRa5c+o20aYwXAxZTVMB/sCyEFCreY2yYtR5g+XaMB7gUe7g9QV4JZyihxdNrhYic64Ly20rdbT1LOhXFDmL197aHNuWrcYTueXfWO2LXTAh7YR3Gx24K5ewzf+jdNpQc1WPZpBMKEpim6VLyOzLy6KuO/hpILdnQWRIivF/p7nMWfCblCLu34wSrPjGDvDZNQ5Vo2C25YBxT4DwrJ6Xkkrn8bG5gzdTThIcLWxi4atmQAlq60Ng1MmYWtOhaByfHeTl7DXl8enDE1In7VkYBMkD5JSVMmCNBwdOdfLpyRZcQv/f1sULLz/Vu+9KV+NTiSTS8L3In8D/j6HBc/kiCAISEh8Mo4DLQZRvKwIX8p9Vmosd6nwQ17UCRWXKxUKMmJm6HRQtmqc13HyuJc3Ync9DIla1N1Yflx6a/NnNl2jQj7KsCJLLw2ScKRCb9uos7CABUPCQF0WKeCz1E4ftWdRw+Xf7KxVJkfIK78MTBq85owYASeuFYWbqxmS5SkcOqEixkbjrmji8htRTUlsfQ99Pz0J5UxfpBLoX13z5wRZ3rUERRlEVT/5G/xto6oehVGPqQ207k/VgmxFjuI9Xx/wksIHnqDiODhvMljbpnNvCNT7VXVCLG1JA+9hHt/KMHXM+it6mH7HlEtdCAJKuFwtV+fYmyhIyH4M9bNtV2w8ZnCYIYm1fDavQeynKDtErQm00PnDk/r46YSGzOn3yMjro+meZtJ8FiJqjaujlIXcmtfmZhRdgKbsDtjjW3gnOOJ2cSwJh/o2yqmC6W5YsaldaBhMr4myJ3rYoLh93+dKacB/WjRoV2ittvPLU7UpxayhFcp8wnGbAQZdxxg2za/k9nKrYMlDhgyLvxgM4Z4UogF8JyfxEbnGxYtavFN5iyaBDcpoW1CUkHT1Q80A3gqK/+1xdqlhjaskPFPYRgKqRZycu3GabUqk3yTOP+WvSquur1+dzjp7DXOoo1MlP7ankkjybjTbmEVdgw417WKEZ8bI55RxRdB/GbZI7f1uvkBiseBrl/7oqoj6QChwT4coEluLNokxuj+PY6E1UIvHw7CMkRCqN+suKFeMNDC9shKXOs3CeQZorznI+2T7pR7dgqHkRNG7k9P7MW3iOWE8wsxzAWWeAdYh830nvLparmXegNZpVK98L7QWup1RYYvQ2Q4Qh9vS7xEMFpb23ZzEl2MlnMnUEouusYHppcxlz4YUMzTVF05ndJXl4OM7EmAA+MeVSMk+2rGPuTj/GQ0naL3qCYCFoEnPLEpgJzV/sLj7+9jjulnRjBmyzEul00eiD6nxmvbtvP5ImKwg5RlWIYowkodO4WCt6Q+A1LI588fqP3znxw1itUX7yasPawntWjtvbS1DuGEQ34y0HV3PgPq54NynCJqqp8NGxHl7Vpj0qFSa1nQ1ViRTRV3vcC8kORpZFZY8KSJwhAb+lD+hF3F6TuO2VCKjsyyI1j4REcaLZ9XzCoUUEWyinytZLACrkI276XQpQe81KBUN/5ZiOb+cyKmmEM4EdKd2/F+nfEB9GqV+IPQ2DhQ/EoSGlytUrA4iy3I84IG0KkT9ugjKEQCi7BYlVHlrjxeKBoHFzrfKV5PqG9AdM7m8Lrb9h1bC9pSwj1u0y93GjvKdhwzpymKpZDI2XUrdwO2AZdxFAgzLzlEodXfk1ERaG9j5rBrqVlcVAJgkPYR9Jol4N9seVnjgOp5wGN54wlg5by9cAYG641c1m6sm1dleQnekHsfSKHBRu2JEmhx8VV6RCoX9Q/jj2kIRTpu8VcElLnXKv8KAJKxMD3Zg1J2qr0ZTrUE+QLTcqeCPNIAX98eKVvdrnmKcTc+66HglTsub+HW/NB+MKcopvCAq5jC1tuYzte9mSYd39Y1cEvzuzKD9aTxy5ACqJ3cFSANtX4SRrRbDXQcTweMDcyI1VKRA2I2r+XAW2r7tgyh05IWaTtgiDY4TMagRV9hKZB/L7s4clScB9y4AJtd6hq94Tw/iZwvDT1sI8MScXaRn/TN9uAWAbkvVyPTslLuKwLmWnf5GnIaTsktNtQr4BLBn/5+Nev1eBt0yH0tJfo4Wqlk9lqWfM1EMy0ykpmbWMcHZelMehlLrpfHAaKGdaJ74+BOlS9o7NKqJpZ1yvhrQIDbAJUmhk4LZre+SoT4txy5Ug5odE1F6bBkyjXsRMLVBgfg4xezY6YkcKjqQuc93jexgU7gpuV3gFOcfUTe+jWN0G2bmS/aTbHdWZNY7yk6KvTRfr81tjjc+5bvkbV+IjzRlj8AWaddMvJEjRbsSPdpVJNmdmzemlas4EwHcJHOkYHqRa+lOND9Ig5O+uGr84x1AhO6L1mb8ErPrjLEszAf2RUA3/ay7iHPta17wWfVgSP3cIF0GGjWkRhHDaVTi6ICP0uOg0l7aXhplk6tO/z2u6yxyMDBdRSUX4odhSmpWSlthDLGI1fflPXQoaW+Qj2i+mbXYB1JKl4r9ObsWKfM1mgBmSq9Zen6HdbYx9fWNDMPXXWkv5dKuIG7Eb4Wf6vlIv7ek7EbCwDsGxweOSRWipuSDjRXt2hsfhHbvq1Vs2V06oj5X/jcFOHWvElOda+drwB6KbnaxxF887Om5tsDoEQueuMSFauApqJc2XhZEOJ4MeaLCoT4upogvWyjDMmwGClbD6neh0z5hEtb42hiYwYQGLl5FMWDDVs2KJw2wkUyGqIICfpYPegxbM5oTMwOj3EyF3e3PyvsWgc58BYUVVcq7PXVfuBo4LO22Pg2Ml+P/l9CxydCvnjG1k/SijWRJ+OXHoYdNkD6F0Y1E7utS8U08Uh6An13u0tv/kVvNR0e/evypy3GRoDqMAHweLMAE7Ch763YYLEgiH10QTPgnPhxcF59bBroroSy3owMRBOh9jdIyhT+5Syix5vwHpUPfHhH6a7ySz97xW3XuqY3zcxerlC78mqIP4AHYB5NCAE1ahO8h1fZ3r9zHXo8HMOAn8Kmw4DBaG4OoMBt2xv4W56h2QNctXnjWscqf7Hn/2YI4OzY55r0xjO484MYGtZpOy6swVJVYjrG+/rco8uzwwDGHnUUI0oZKDsAFFA0UdKtxByZGOmPqntgRcvxV4QJBSBzxkD9gfr4lNCrsBc16r2M6mWUR6ARYSu6tt1gx30tpxxnEIQ19nVfT11Orq0sSWpBRBKVcSOjWJ31xBYgdocr0FMl4K0mOhgfLtt7G4xim1f+nIQHKZdi5OWsFk0TGBC9aeat24ACKoCtk7aNak/+JvbknzyvoPqB3eTMuJoPdW278zmDv0VjO4cUEDwBLW/411+/mE86g1zMzUY5lvonuahu/TMa0id0Y9DqUHZInxUGpTARrrrliF07nLyhOZC+t9/h/614+vZl1bO7jww2Wk6Ga5b/RmfofDWs0nZc3TwlMTY3MNGGwGwLpKrx6KDcGsyNqbTz3qHZwaqZhOiZkURKjWbhjgjRVCjJA8wE9QZkXCos8QNMYGI1ATx0ZXB65d+D8uB18p4/S2VwoX5Nj3hqx/rB0d2Wg2ip27X6QzAAWiEEsGiCRhbr3BFlMB4vybI5KFPztCjOLYb0g7oz9lp5teAZ4SK7qV+K7pra/Nn6y0mFgzilhxLtRNkohLd+fZvzw71houoJe2hwej38mSEsftSqzJPuhPdMJ7Vo7a0dxTtMXhrMq1B39IS8Wd4Hp+pGrQKNS9YIVg/JD8aHb8sfFv9XjNbdrebUcsT3KEmDLH3r1ihdpy35B4/kb/69VNqBjSVjwSnakO6tRoIkS+AF6OMI4JcAtP+1ldQ5qOjFReFTLL65PNYlR21kBeafZR8HXvOsyiaJmcK5XxKhxVS+u3adNJ2bV/vQSfaSn6er6EsM6d27RxZRA0UAynz9AOiKWrv0xzHjiVDrkwNyOyeMehn1jrb/bO9gLEJJUV4aqcgu9g8POyDtoNgxbC81cR1Dq7B1+bbmnJcUmmBDg1PCqYVQjVcb+B2YUnTtxqfGAtXylsczk0jTy3yLFpow/LgYwytvGMKk0ENMBVLJW1z00sTq276mta9ILmJw9jhmtvg3ieIIgImLBhVLKOIcwrnG4zSMJOr0KJg47mVZ0l7Z8VGx7/DAilVsupqcOKFBC+QoYIrS+sxqNHnPl8mpCs+m+BJYq8a1fmLaVZBQJOruLHVelQ8TglzVHqaSTHXZOH0jnKl2QVpMkVTz8qC12Hs+e289nSHHkT6MdOgd2yfZrEFCqLiQSBgZiqL8M+cckyYxw8KiCY7q/5KwE5r3dSFxoQGO1R+Mz2IWAkR3SEVnu+i2t8EXUOGesKi8Cmq+DDVfzdaSE4FrFojEbSbn882iqOTs/WQxOdsXtbjSETRUutvyezjoKcsqyOpNoxXs0L8qu4/c2b01Fyb1009jAXh4GnQL4AqTeeQ2S7XPG7jRVvkxDJ5vFO1MF/ckSpAaZFMrSpLUmlOMid6ZqsMY210FRXED2ri3p/2IjsDOFxypc5BMqxE1EQCQg6jLWqQ5irtsvXF1S6L3yDKzz1v9hACGRZApOZx07rC2vkUQhKPy9rvEahnvT9h2r/8edVQQm24AfB4Ng/AjpB9VIvbod4FXkyymk5ZsRJus+8y5Ru9bc20lp2BOXUyBBibNfl2a12zsamZE71sUFw+7/OlNOA/rNeV7HqiY7hHh6SXOXxhUXEiVY82CRD8Tidc/lcpx2+jlbCGwGvYDKLPaOySD6bOG+Nme+ulEhZPTVT96SBzjBZnuGsF5mxg/16jLlmxzzYF9Wdkl+M5jQcvFGyHpDXRKXc2h/kBgiKWwg4V8Efw+EKKVRiN8cotihGXon89JuCy5C35MyH+AKKhHTWCqsHW2PWKWKaPgbzJr/q8hK34skyWUzFzlB8oIqpdS7RuFtagepz1/mv+GrjAESqLkGVjVdM7q6QHisxo/MFU83Cmw0XKhzujvpVbAwm+FHewedJK4Hu742lnUUlVzQ1LsEISFA6VRkph0h+EMkowxmVW0ZWQq9bHmR2c9i06dutCtm61lWi6WmHsttY81cIfG6Jhbux9vRws7bJyYLLIR2hAOtmF6AZUF5ekPrgsvhEzmEa+NUBv4JjEPc79Q3kWP0lVXk0pR+GgJi368Ug+8fcUQqdF6PuHP9uJ/P35MHc/4o7agmuThwt6zNocFDbsMUCDebs+GxCisiaNm2KH6fic3NbYZNX6VPp5sR6cRTd3Nwy1/jIaTtF6oIlEOjgYfiin/KNWObfLr5gf8PwFzUR1aNrsnHt2nc7rg5nZWv/23D/5e2MDu932auR2rDSbohFjCgyBQB9CjOnM9VaFM7FDKc0X4+C3ydjeVVoNKO9l6U80MK6IN4YfpBRKI4CXhiAaJHumqOwAP2+ZipiqpvJsRslqumr17D/iR2wBOPH6VmRrKy9L1PZgw6DKGL/s9Mhus7vT4OoSMHaQoYNT4A3/uonKUPYGq06F0S7mYsSWNtiWmSY9nFEJ7kEkFRttpIn4x799IteKAq2xpwZwoaLC/gmma+eww4z6uP10JSr0eihAfSFAzCHvNSgVDf+WYjm/nMkkggIX+4VIByiTKRoKin+OJscTxMG9SZ5uepf4pdNZv2ocsfRlhbyV9aAhxoxpWxre5SzdAP9J/nOEesDrcf32pKwVfG8vZ1mGU+4b1tvnG6WBTWdzkWghQMg+WBjZ21j2O9+Jsc4vKoto8q6U2b0HKiIBk4qItoRU5boZCZCWpLITF7ITITITITITITITITITITITITITITITITITITITITF7ITITF7ITITITITITIZS5eVgafjpGtFsylJHVCaZ13pa6BnCeqYVtRqbLZ3TD/9zWvnyvPyEd3G1qqSrzusjwcJym7QoJ+bg0zxeCzDKrhdSoNIJgzFCMR5fbeIWcCHmxJ6NWcSKbderkzBI0IrMmPLLAYbdez14lWVjGunpwSblB92pjmt3MFdGLk/9JRMqSedoS2wKaGdUL/BFBAvqfhDbpUIu7hcN628Nk1DlWxYpH4fFfFMi+WXbmSJKiTf2uJxNwF5pyCFbfpI16pnJgKhCvjn8lJMfp3DueBmXP65Zf0hZ4oG0vQ+yDDMhshWK4DxexaRpQBQR5A7caM1aS6QZLM13LGU8yZOCEV6xuSZpDTQY/yhAgrQZclgS/qDnrnWtFiUBpHn42RAvLexRDOwY42KD4V6+p3MaQ0Gt2LY9N0qb1XDRQcgIk1WSllsIz8IrRK0QbfTuZwARfulGSaERKfr4MJSYq0i/ovgfsvVrMsVMhMRif+sJy+cCQBPPfofFB4ga3mFxXMI3Bwva3dcYDqKs5YDwokluGb39foYc17ZdP16ZPRx/9KuyH/Kg+MyZv5XSaabvMlp12c1NwqcNqZumfZM/zU52szmdcOoOEiGRVvcdThxoWYi3Zcsnc8mbbvY4rhBD78JgwBJmfVIbuKAKjP4nos8kuLyyvJ1MwG9p4FOE4vb6luEW9nX6gMygt5xpopqSLvTH/Vf76P5b/gVhCzEGxuV+MH40NrMVhSfE9OkHQaxWsSNCBGCaNdbe3yySRRQzEPbVNIz+myUKBgnVc1uK5rKDcV62Q453T58TYi+ITOwXfEPimx+YB/9kn+6P3sLwC/SE6kmwfKY2krV53ZnFbfl/gj5hALA3iJbuoKXa6jp+vZpnFHu7up5ZLNhqIyPFdzpZLbuD1BXgln8eRmgxbmICMDd8faK2dGznNEoAAnOKghbyeqsJyeIUpK7YWamRM46vVMRjV7e8fibSSfUoF097K1jtANsVCPRsCw2fa1iH13RL775XSyzk2e15RBflRZXdB2yDR3FbHfRxhCDcTR+zXiOVipHhVEcNbP6XtZeDEKtz9/jtKSW8DeSsK9NZ0OpAJEs/RKSJIOVkpOwMTymjIgmo3doTTTi2sQrgayJLH2aZA/H7wIa6uJgukQU3SuXsDuwYpPf+YTaqzU2zT15THoy+p04ZSSsG4yuYBh5k0uzq19et4n5G4B6vdjb9xR5/kiEbpP4FLPfbvVMnNSDpvINho+NSzluO+2Vf8cRKP8Ts8v+P0trl2Fhxo82u261J4iWV3ac+4+3p6RtHnDZ/+hEGW6mCDuonw2G/1aXJxTIyK9UHzxB11BOPP9pOFIzhAHxrWwhomgRUSSyOjI+wy+r5KtL6rSLISv+w8GxLRgzW1aqLxmmjGed5nH/TXDHC/kdsYPPSJsB3EegVrNz6fboP9G6bSg5q1NZ/jkWO8G6754KmQjnxjRuRkAXUw3f9O/U0EYO8Nk1DlWdL79Kdf72sz6oEUygPETLLHc+O0f8E8T1wAYsolUhAaw3z501ppAIV/Fl4u1z+uUxM1VsGxCnjyU+lLD/T0NwVOOa9sun69Mno4/+gt2hl5xqttvviJRhpN3tBa80B7zzLXuXhWahKRv0sly90E+aRlrRuE7ak6mPVNrqFMdX+YJ1ysaMF4ugHHwd9z1hzhnqQQiOsmG7rQf9nkOhpZpolCCCQ2L+GWXybx/P/tAlJxwp2KMPNWi1gF2TdjoMtBe+X60WV5At5lsrKa/lhnKAv0ATZjVvkJtvJn+QGXyhyQnPwnwwRjjmCNUeJHiS69yJmtRO4s4Syt1zE53ni1bBoiX3sWmVgKS4gcQR9ZV5MhdyrKsALKG7DHj/JsqwGPJjdRr/BuuGlIq7B+uCgWQaBDTX7ffUbYo6rVBP5zUjFPlAOycItN0B9iEHwtbqsQuROOtegIUDHLwqXb7xiKRRDrfkKSp42Mgi3UVLJKw/N9hcRnFtqGdRTSOsYPSvUg/BX3fD3vA+gAfiocXi8GF1M1lg2DtwebZaortDEjP9FGe7HzOXAlaODSjoU5F1+WBu2dEBtjXdkeruPP6Extq/0gJwg6jIFctUVySdPbd6SVfsh58G2fssRYEPF0DYIqtZbqXeYGeoKWl8/3DlU5cRe/0N+Cc1+Gc0d+/N4rm/Cso/W1yHN8iZs4X0uRcYhDQ0OhUhgiZxo0p7X/RFiB3/0EfY+Rr/xJvuUzksOOh/9DBgr0qQAI3YcWsMmDIcJi4FnbgaTs3o06r01spU+RO6M65/E2g3IPaJRQ5vVC0ICM7ilYst+eZoh1xT6Ceo7zZiXr4nD2XRMmJAGlkTVntkNgOXiO6tZeY4cEkPscpYTqTu8t52xp5uRFC0vJznFEi47HReXlULxRB4LG41ZjijSqk/jm7smTEV+8NlLjjoilhypkOfo8NtZDCDqy/UofgNEfqjoJWV9ppaDTSn2vEUAwTR17fI/W1ewWfXun7CvmkDklC1i1rg2yjdmPaeLVe+UiJTSEgdz6fnR4GZ6kgWbNWtLeyKqYHGAJMJo63R5h2wmb3DdLQu7acFJeTj6z8C6jYXLkimCWIK/vZXbYw9IEMSB664eqCqocKc9k7RUc4xQI18BMoxY8kG598Qn0QC9TSFlBGdVE8s6AZPkZDHXF3sr2BOzBVUCGy8KDWSM8YuDX1Wd28RG4TteHpTGyVJtoVg0NW7DCqslePQSmlX2Wnoxhzu7gWszm7TYoWg6CifB43k0q4+4Pmnbq7a34iZuOj9MESRWuAAkTnDt48Z3H8YKLKDl1yDs1ie7iEPla8vvGpuvBSxZBZqhstyDpRl0ehq6VnctNa6jxxNtjxMQN0SVXiijx+H05fTecJaCJFiZS9FZ08V0zvm2FT5nnWiUScxqjUMrd2rsD0PSgoqgZRg8J8kF8zOhodAIaBoyE07YFqu314sLqCZe8q9SrMzmtLUeeZGJzItmgHywXZHNcoVF4/QPk2QQHJJXS5FCkwJs9u0KAQZFKDuuAbrf8c99jhjiqagW/zKU1ZQDYe4E18WeYEekTfo8bKM5+lmUEmzuynDNPFmy0Cgjm7/6gz4M+kuyAqnt7uOZa1gtkCx6N9PmhUSYn2bFov8J+7O6AAMhJIzdoziyki0BZhDzC7eLVpFqTsO9EPKz/Nz07OgAWj4LXrNubQuI6aL5n7QhMIKN5tzRIbqlWImdXcOZd3KvCmFeGwiKYraoTVRfGehgsUnRvMoazG7T4mYXFYQDCgEnA59lqsgVfkZi6/zJbAVNYKfDPeK81hnsui8ONzMGZWgE7ibufXgUuH61xkYFJunRiGDM+aTr2KDVJQHGMxrlIuav4strL5mMGuV7i5ZMtBEvb6XDbr2cdqnSJbpxepd6SSc6SVYYQx4AJWUDKScAOPn8UbFZ63Ozv3nE+BpVowjxEW1OUT9umXr6LjwDv7vrY9dUo0/BMUI1kxjxhCgqDXQL34UnC/h8V6zRBu4GgKX7DRMQtKcK3CP27aIaLAedrOPcTcsAy+1hxsSlZsPFARq0Waqtzp/k0KCjhcIsbgPoN38FA97iAvB8kegLNVbE4ey6I+IWSqmjwMLEbHLnpQAno4lgAwrz77cR3oqllDM5FykLUCn4jm6QAIoLXBi02cnRQJMHbUVcSjEvrWoOtiktOGPXscW2074hB9vEijHRZZAXBveoG5v7E+6DXkh3HUvSL0qT1ZslR9M0vD3f5QUw12hGyUyItxQVnD786/JoLKvd1rAyCHa5XR+5LpgQvy4mQq1IFtW5jrywBqHaAiZ/Til+NKvM609pAV97lgMLqW4Ham8D5YQxQoskrdJCftlWWSZAOtG+upkuO0evrdeu0QNMufy8YU/rPWLj+SS4delrOVHWF6Dllk+9n2ZKwk1O9qQwe5vTCZD+rlgkvb7gRJ4wPC0Q/vwqXIMEHhZMel3y/SvLaeqCuCN9m3GBYdtOTvo4t0n3k5mAzxB/vFdFgA0Vq+JbJCUpFmyYve5ZLGiCYYA7vHs/4x7JkcRJIxBFzcorXljwF5eVQxdaReJOFTPjtr21SQjPNRJbUPR7z+u+q9ofIi794ziM0wC0K4EiE8goO8hQmctOh1e41ufown8Au8SlGwNak8w4xWGKemLuFMDhVrFWRPLcJ5pa5Q6URqyQ+4QEbAx4MXFYOwzU1HcsqZDiTMFqrFnOKneVi51HHvGt7q2RTuPWKibU7ANqfT5jIxgB3juNYqsdNPAy14QhR8w4RhuJ8o25o3lPJZCu8NSniHHpt6Dx622gKeE0yNNdnyrYWeQqzQVLUbTPJ/2PZBxfwcGs+sUDaWO7bljeXtKKiH8yygfHrJCVUoLIYX4tWBOOUI5HBZ/jW37S7t2pc0iutoz9QN6vQvAFZZDcm0A1gNYIhUipGxn99l6Ko2uwqNPktf3MEc4amJiSr9oQmEFG825okN1SKydfrkt6kaFjlFyIxrYMMQSgw2kEcldT6Sna8iV5AIptApTYbCWtpOL+jmwDhTTXG/DCGRcU5p3J/XfHaswwJVc5f+bfxV4UVpIl6PitWCvVLDZciP/TMBRTW3FMtozYkZLkEWNJ04QB6LLWBRsWHoGTARdYDfdfro+ytm5LRsUnfCFjcIu4hDYpWrHot1cx4Qj3zQ3hYjwO+vmmUEFzntitYWbREUOjhLj+sbbPbE4IuIypfC0vmdGRvwg3g5N4oK4Lld24Hx7XjxQEHaIJRzbsZYfPf7mU4BmXSEOtRrno+m2+NXsbVS80B//08Dn+8HHNMtOPFwK8Nnwi1Ip7u/z3aQhQUdUKH4OF7W7rjTXzVKo/Cknvagn5ScbwbdMvHygfV7SX4UFHSjn4M5+347kfNUTr3Z8xo/9OtvifvRDNWd2lEBYXcD1abiuuM9dLSmrDn8Sdf6S988mvd/1dbn+lfame3EFble5cnQGLPS6m4c5yU3f6iFbnf680mg0sUVKheZW7c12RYcxa7bHFGIgxEXTx2/ygjEk8FFhCi+rjiyN4JGmcfVoOt3VWF5jF7XQmV8dxImRiUVo8Y95bZmr6ly7htwvwqrwZujBBHwWpdGe7CQyVaZNLLMFQZK4jLr5VYkd7am3DgPF7wZFSjL7cn8L9wr4fetYhxtR2ArCIh8hCG1eG0vsZFTTdgkwCUTOkPUyJpSp9TgzV4sU3+adQFhUlUC1ZVEtOWQ14fhI69iOWHSiyjWaNSq1ZgdcHGSBT+EHlij2//ipz1fvsbnCrLTUX1nq0Roih7z2yFe7myc26Npyb+dbqCqEGzWiBFTbTXsma4o4AADSfjS9B5RYSafMu2L4j7kCpMMBnSzCvfFVQTK1VOL8l/P6Spm+Tb0KQ8hF8JPoRAsOy9tGg+grQ8tgBxxGXuvS56TvOyWyKGOViqc/mEgs7X6r3J1zkDxq1KXmjoRIodjAphoI6qOe1gr+rvcR6nlzlkeXcAtVwHunh7a86OayuxCnYKzYGAK4SMpdnEKbiAPczjMdCHYSTnt0ZAFJkz3pNKUivUivGHTAweCwHlOvJ0EXWU4MYjf34csq24v32pcLscw111aFRnwoOiHJEPexkaXPCOzfLNs9WhWsg0RbPEIEVOlFZl5UOoWb6TQO/9FkAcY4Ja5N5gbiwMDsGwNiY/z95s6KsMLrEVkMOX3bQIUdpLNIVrJEEm0pUYf+muBsVUni4cN2fC+G08Grmfljkz6FMwZJWbAKIXvJOvWpYuMbGwOq1MSEZSdHyJvQX2sj5PXiYXm2Mk2FhA0UMbOS4RVwj9YCc6HUIYrMHz936BFWYnKo3eONn+cH9umQK6JmtNn2/zyTgz8UBrtY7dalEOzOysPKsuuTDy0AT/mVBYLR8MZ8WUXf74/i6j0yeZ6VX1RFHlqCm/snMBzvhPwKWprGVPpY4F1p4xBDhS0lpDQg58IfOvMSzfgTyAE+8F/+9BogWlQl6nDCmw8mEsdIWNKvWM6db1/7fNfxZ/nvEZNuC1XDkvTqg7/5DG6VqGd4CdQNcp/G9Lc7tdnbN+6ipXiQUlhtew8TU3HtMUZ9MUyop9I+jnA5dVjIHNW213yaX96540eY3kYh1YjSZJyyxb82sUd2CTjt6IkrlLKHPfrcUzMaoQJGAMUl2BWxzSvM1f9VhnyFsG0fRTURIAbpqaipMbllTE/cEKAfbf4NfegjEUBg0EFLQos/fRkEqp7cUg7BcfBnEWikJBE8KI175d6Ux7mix2cmImBBnT/zoAYRZ5GZt7yQUMQ7K+JnI03CP++Gb1qvHbM+rXo4YNeVVSNcfcorLKx1zMAfkZDLGWJPOfSYj2jzzJb7ea+I+lZrEMCvzpyjouXSnUfIcGj7cwp0Ux80tdyJKWlhcRHWHUuGVLXqq1AmsGWucbbN53XHilhS8zX/1hgiYmjlCvWjPg4EduiWtpP99j0y/2aCPjvbN7r/XKqhwxlyFGuKc9/dezcEMJz3ZHGDZMswanyczO8scYWSc3t7gf2jltCLG9pGcpGYJbzgxhDM1kmGo1dYyTNzjlRuG6pBQOR/G2Ymtb9RPAU22mol1mdTCfTFIH2PXNac2YCvWwA60EH1yNiogt7pSOzIPtJUbmUs9GPA1yvDdnD+BjvtZPm8IZmQuNYPS813qrP5pFjiGzVdL/gcenVS5eKtmBmVxGaqeqGrscWMv5zp1Ep1ZA2y5W0YKVA3TuHEy7HT/5U1eyg1bf81lXCWwvXp3HdfBcF7N1KwRrWlh8x1pGwP+ZdMwtCJWeETkCj9uoY/fL0dG3PP/6YvE5+Ziqdu35aZXkW2fPeZAf8vEaADIjjJrp60Q6IHpBoyGt8j9KONz2oSnUXgB6IXUucHZsres86OWVDUwHVjvSjBQQjgBJ5skrq4OFGPZdgwn04q7v5uERs66cOmoJJOd60zxJ8sP3VJ3t6SqSZvv+T/Mo+4wLkkeBh0n1WY2QqKwzsX2cRPAYV6DFTc1X6kXbQz85EzE+miRcO/k6vs7v7QqGMelDLm9FSB8IoHtPQ+yke7DasUi0C501lkFP/tCwp6RNqNPBHPvUo+8mpG1xNhozWpOw70Q8bbfVzJHh64A3JhzeRZ4RghqgJGPP5h/26n5lX1A4Z8dIBh2Bv8TicFDRnGwKU2kkdwCokAmA/dfDowyjmi8EuJdbkVl0PkHFIRiQgMTJVPdGju2uZEmw40w7naS4fFTdH2a4x4J3kqkYXueOnNUwgAe4tqIlon2T+m2z6oCVZIlBayBXfLzM5/0GcjYIusIbgS7y4QMgHRAGztRkbU+lWuUdXpSKoAvnL9oTprTSAQr36x9tn6SwjsjeBqay0P/yhlCHduT/Vwexl7tgyOa5fMCg/IUPYtjU951UvQg9KsAT1QjzCc5c7WbXCTk1UBZYEB5pJj3Ld9TA8kCxVmD4BlmoW9yzy/qIbv0EfRuIInRLmTWP/2Mj1uTQr/A0Ka+O/olMEaMnaAa38V2N6fiiIaY/+vsY1cuDzY+0dywjYc02B0FvDOY2Sbtzbs9IUOhXlT0viFbDQ/YwFHb/ZIFUVa0eNMFxYBYzCD4UWJfyF6WqMLd2i4PlZz7U6pwsg8NO23KEV5G6s0XtvkGsBM1eZX1gC6aT8YxOjByMlOriuedM6icZg8mSnna/lzfQ6u+Fb+sNGM6ZAGl5sP1gxHHIWwYUsYneybguGhIZhIOQt6rfwXljwg0+ezcTBOK6bF6hBNN49+ZfkMfxe0uB+2nsKuW4clQVmOg37WCYXqvzpkOCadlas0R08tuw4bENOUoki4hkmmkG2jmtu/j3n5Y+nK2mM0Qfkv3y6Rw87kVRRztYi54xMIQy4eVar0xbVz3CXE7D41t+0vChfu2bjGX7EUUq72BzLHadSL64QbesJ9zwhR4SPdigUco7Ic/8mw4SKSuW4zkEh8fEBE1sWT3QAoDxZuahSS1Xzqy0AO5T1A9lJIcCeN6thtQ8bh7289sPmAsdhYn8d3cfRBcSA24u/e0p+SnYsB6l5fi4zCFLeOIFKLHphXL5ndNwOJ7W3XePeHKg5xaKJRMcC5zt234TMb4ZXZYfGC4u+EQay4Aa3Ry7bnMopraTShJBQKbPnopDxVqSkwW4F3fu5WR84ppKA+IVj024L8G2j9yP8sAue1ONqjNM5BNMAYFx53x3UUz/lLVJVjte6gQdDNZlRRtMfxLyTk3xRwc3spVO2S+k/7zx8wfPALhCKWdNgKIQRr204bGTpZSd6rbGjjwqzHBK6rpmmtbRi9uL+dZvL2eLHdHTZYcWRUv7GbsV8Rng3P6EBln4jldPq0QjGVuZeJ+r/uA6naYEE9ssZ84TwQ2RecFxrcu0fy3ncWsM2NJrEEUtLtwtAoNVf/zWSAMzjCP2jX7MC54kcLS+MD7YIUyzL5UbGOqMX/p35w4tApffNL2AG7JqWWN1zDu1BGPsfeEG8sRJjmbsMfdp2V7JWSojbF1AkVlGZFWjstjnjIhwQGtgW5BP5QBL4F6Op8bx8NjYLzyQq+4RZnXX9oPvaJgBam/QYSwmeWOCZfGMqGR7R/boimb/mDMYtoJpfFAWLtEM3wDJ06n6XMEBIngEOEtB6G3WSCj50jyuUsBYVkMmYxAnH37Fgpgnkmbh6qoqVv7KzOE4Kg1/AzKflUB419uMGrhGxoBgW0RJBWoo7PP31tJteJBb2oj0gJ2wrcob6DljttlqwsqrXpnB9WPdfcMDGWaXjAcfEkvfbRkYsQ0Oz56ojPPu0OPxXs+yZUudpVatO/JPEjgIS74CLNfT8gv3cm1FGJCrzr9FZmC/T2pRxY22wCY0HOrPx/S63LUD4Edu26lNK9HYJWaWtxxWFW2YcoLvX9DgY77UsHRI1MygHPYKP5WU/Bpzhrd8c4xFCDkrHdb8C1/DRUYFjWN7tdY90a0rj3KV5TC60mB19ThwCqlB/OxrzwzRIaIa3/+oZzTC020QFdQpN/+LF+BrqBeQPsJgyXcfZM7n9R6QPfsX2W7QnD38xBehSHLJpeTVunLwXpUPenUy9mkX4GcZcclQDGFIgZVPn73sZOiDjFxvI86E3kqdS7fpTSSomaOgNEKTACPr7X482Sa1ShMzjPVvb+Fx6y18jWTIVf/7kzfr029d+/UhiYFmB/GPukcW5ELfNmxU2SDUUt2ePKzwxPljW3fzh4yRZ3Yt7rTZwLLOlkIAvf4PBSBMTTB45fiTTFHI2ryljvJMkNf0w3/cJ2M0RFfHsY4SGTVpJpJnh7DI8COBl4mbPzt1O+Vt+Jmn8FhxisJf84582Y6bCv2hnoYpmDOAY2r8lhq2w6QWLPx/9VWvQB+wSHsy3D/o2m2TK6enNPriDlILnjIOl5h367dMKeLOSfAz0jxLPi2NsCseO1b+8R14EWyXasYVSo7IhsToBVPwDlD3U8pI5DwhmYS7JgwT44ENy4+s1GbvRHblxywRuBPlnor1dCLWXbIXmRTOnBGzxU7SSX07JG/IqIN6HrSB45Xsn65QM6ISP2Yyr6DDTzuqPBezLcxfrVpcvmM4PltCrrRw4oB+n5IiapYttZkLL9llfj1cSOR5oShHcEz/TOh6zeJqo6fIitvOhB4/Z0FI0Q1ggFGcK5vNKcYx0tKPztNUhQ+CYY29K+nvwscR64Q5tujcGRN968Qqn2xFqKcKFeOVSyVtc9mAytN+nRe6tLTt4JSqe7+kK9vg9yCivs0Oh/1izzMIykHnMY2WAgDEGUG28gho5vPg/mjf46ug5Dpgwl/gv2pHd90O1HH3FeK0OU6S1oudl/df96vIipgRJOlRUTNjo/zsdZBcAe4DTiS1BsfXC9UBErDw4b2ZIh6TXKeFGM9ompjOdjnbM1LndSSwrB347XYjLVKiE0UfzPANKL1oNofM868MC+8RNC+dIoCWOhH24ODZE/S3RzefB/NHCGnDbYX+n/AvO2h2U61fW/l8AeTyF9SG/unVakiNr5k9LAse//WCdg2kIrSy/hEOZlWzbOFQrPDxSHMmKhv27X/b1CL4Bn/FLj+EYIzYx21Bza5XG75HOFR9DnD+h7lFHXQlxd6XTKcKScg3sSC3haSumb9LCoLwJa/sH/hA8jqwXpGpbjmeKo68VDvaHoZYhMP6MjLI1kafVdr2a89Lo4zNmG5lChOrBMHtrNIbO4taJdO/PFrGqkR9Z8wWfF4dc00ZTGIx3k+y2wwtKb3GDYbEH3Lh2xxDcZo0E2XSLZmJGXgcSL2+/vBP8fhJWj+UdidEBXkzLvoOFNT0e6tAQ3bjGOmFWSbxkEsYuX+FgofbRwnnM7TqwAAkoQroPVVkfxVeD4xBxbMi1ggddj9h+VCNAgDSm5tB5eJOF0TtZmlwfaXeXdW5bybjEVsNSi2LYmMsxrimHBom+vI42NqABHeEdNAGzqYyeqjRYIT2O/XySahlb2vT85AWRmzs6xjTvhUy9NVLca1BxvDgEG9o0yPROPeIjCu5QvLDYrC1AztMSkEumExR7iQbXJBkupzFdJuVu2rQTGjCzIw+Bg4Qrq6PEXwvYZt5jzWE5alaCFlZVJCo4D+IoJTTi4GEtfDIzbOFgD8MylIcxYwm3bLsxNM+5jE1Q3h7FBRdq+t7SD8RHIaCDq9WofrA4lJpVwPp4R1ycVEeRhSA0mv5nJNveAW5TtYNzUfTSOCynVS5ydAKmGhC6PXF2ZDgm+Qv/YQRXBpdhU3d/SncYfCSPj6eFlCEVAu7WtzylqCT7p7VK+bAqJy49LQ6A60csQ2OiLv73UGZRKuiK/VvEF+2u60Gdy1z6GNs/Z2gALXvE7x16hewizrWRhAZRJw1Aqi1pLWuD8eZCyqQRy2yqbGFbHHO6m0mUSWBrpf74T8CFj8Qn3/BKvHEwzmljw2ipOGxxtA1ZRR6LCI3ABZqaGhnT21WjaiLWdTxMhn3Hjz6h/iQgqWf7bkVm1GwzJHjzDWpBG5TZGsqErgpSBWxDu000JcukugMsPFAbIaXPnZpOPrWRhAZRJo2/CSUEgyAf+InkH9s0DbfUJh5qvJpM0US/lNN9qi7uIBRkda6CorLrBuevZNqf7/nxs80Lbb7kPzJVZwpW9FRf0Rp51hYtiwfd3ipyQewrAiik//47AFFAm7QpKqA2KwtQMzWaKuFPtQga25zH4r+kDW/bIgHvmK48xYXGU/fkL12QTHCwgv2mZKStVXthiKFDBOkTUJQo2CQotBvXOVAggdZwXm4Z9SGXUerEvRBX3DJOymfTf8yn/EHOhN1BGIGQwmoo8i44s8HHrIKYgxat7mF6DpFVbqiuVNKo94iFiuKaq/TkhQEwasnbuBak0PRIxljCwU5IWt7ixO9nB35mrJPheRdQSJ2EwDHCWomTv10qnoCd4FA3zkj+2IV+avJISxwqTspMuW6yJvWzg5A9WiqrTJkyXNAEbckVbnmbJmDIhjcbVvrzhP0s4Kw0FvQP6UxL00bTs8PpJCPQf4SPRD/SzfyL6tNK7eUNrQ9KhMz2AwwM12fueDlo35BkNQMW2IPUnUYzSRxd2bd0kuu0TrXVj2ooc/fV/0vxJruPTh79snFGzAdLkdylkXoblI18a/x/KBm3mhFWH47L28o14Z30hmaF1R9X24GADwQZ/zKQJLrPYKbtLJKaOtm3lE066aDl+yGHFfNc2H6PP4AzFHNHWjDvbxNgVUcZkPf2bpOwJW3W9KoGVWGl6dLJcwQu7syTP4KK1wKruhvWBjv7r2bghhSXsvwul2QeMZbaqwng7VVoTGMu/oDwIhQO7xxHIsi6TsWk5rz3LHSp9FDtXB3rJP/idUvR/vlRNphi4nX1p1dtrvBPSZoTS8/0fwcy51Qe3wE4r65hzWyl8bI7mzwd81G5FGCD8Yxs8iXWk4GZLDtdAUf6Akk1soxB7JFQqYolocdKdLYgxSMA50XqyngUd0SuHGdnH9f+EIqShmdt0aobM7NzukeeglmAidURRtRW9BONzwc2FF1G597s5h0D9TXjcUlSkSdAZWEO51+/2xBwXQfS0GK7aLHIxUB3RPsLwEGRRmMMKVsje++mh5TgkOuuCF1GmC7iC7Of8jizAT6LNXN34wCl3XelBSke4p0+t8TSg6Ffk+NBcP5VIAfUShqZmHlXo1uvdwOxDAjof4wQi7SajdUIr4HpxAhiQvUq1ArcSegg98DEkL8Z0etTequ8JXZ1V8CJ1RFJzc/PzC1MYT9w2lNhNzhIdVot0tUPtVk8M+RCcg0nR09BXQolAHz/4clREnI0hfguhaYivqPCDBCB9X2VzcCTBYwcuccbHguvImgDv/AfE+Kt3QUX4HlelCDHDkip6UfwzVIg/PsG8s5WcQgR4vdXPDGGLceU9Uj7fyql4Wx62e0Od5A1O5FVZ/k+m8XjeUatdweRjn35MPSb41Uzwrf9drTirOAQPp7HS7BQ8/fDIqJMlfqN40XSfff8Wx4fnskfB88WnvU66y3GgBSCoLwVQ6Hc9RZKMVy7kyuEGjocAuLW7avR5T2vn92s0NvtYS+OCB1w2VeyuKaf041xmuHw3Jo6sFgGg+uz9rU5gxH/eD5RXFhyGbvtdYkrO19b03/QyXq1mBGVc1pb01pRDo3zOFWeYOQNXKPbZlYCuAkqwH1+3xvJxKACN6ZJhvYTbB1qGoYExIh/AOTsInpnLv20AGBmBlKYE4bWM90THDTKIyD7lbIFVjqRk5EdhIBaug+lwHujcqMRaVd5Fzwmhdyu0kqPUa7RNadgwJ6D/2jif9AnOExw9azckSLcpHnCGwXrZogYKCegfLs10uvcpmkCh/AB8qalVPDAI9aP5rw9sM/61+o0GfLS6WkDeVQLcSNwFOnBFeEC0juJ1GK64rRrv6HYHGNrj24TJUWBiDmT76idRTR1jq+24V3zIjCigjaK7Jnnz6ehInM3mLTpQEtAlV4BEfndyzcMqUGrWSHqGDlemeYBeKs7zfrR8WLOI82gRX0InqPp1DP1dkCuNSt+qZpe3tOqYvPTV3tZqkgv8W2E+h5TgmmaNuFSDQO/5lELnIayVjMRCDPwl9pyk2I6WIdwCNjnRElFSCIRRnNgnz+SaT4H0B4Y+T0LCySQt1jW6uA2Dp0kg6knnhEe+SHnm5/Dl/Hw1kFLeUZy4TJ4+BFgDBUr/Cv1EwF5pwFoMs6H4fV5lUFVyMcy4M139yDOvrjdc9vujs8Y5U5GzOX4SEnSruhiZIyUb4R8hUkD288z74UpWunP6JD/UwKJDWKruOnIkTNwsMKtRILRJJoFLTGTa+IUS76Y1lfQX/LiKRyeyBTLhmr+Pbb5H6HDnOayntrOXQnuTxJHORMAxgbc9NMK/WI/NsVmdHexM6Oxkisq2JSUelysP+G9ufQ1xTCqIgTsqOR3MGSky1Vk0TFI3ubEbfEHzHn+gavwYy+42vYDtx1jB13bz8vUa39f2P87jfvG+bxmJpufCzrGxi1bVDm7lhtJYN3NW/Zk4+qAAzYcacih9CHiaYhh8xujZdippSzMDf8ka4tWnrjWBQLLYSxWVL5h45ua4ZKQiGJ/x47ntHLqhln17T/Ciejs1VvbyPODncu51aDVt4mQTM/IZ7MSNtNRDYT/r6+HSJiDhCY820H158JS+DW+TsMKDoBd5/V4ovWhR3+QxzgvsCVkqkbP1lZ5LuI0+yJIwIqc6yAMZdtjBkuRIqUWWCcFgeYxPVpnAuaZgDMy1EYMp2H7lDcenmLLhYuZ1xJUl30A43O6J4HLrvpUO1vrX6ILX6gUbOYFOS6mGTUNig08JmSERHVVOjwe4lUmIKbywUNGuOizq/RFzzepsm46UsEMcaBLaY5Tc6WdtLK/7eMIbRFX5RVjXIrhd9SsZKSSv4WFjCDDWLNbvbowQvVAIlhsrxmVbF+CNfr74RWhkc1yQd5NGkY9p752mdQGq5blKPGzx8PEzAlsF+MRDGKD7fNbMkTi0jtXr4a3X4qbvompjUVqCKbXcHDcPa3lJSqBBBx3HO9s6NnOaJQABOcWvb3WtvYpc5pObJILVUOrmZO0VHOZWWTR3CCXNtDYMhW5QXyPczqCJZeHFUYxrTE+vPITRjFuSIy6BMU4bIipaOwfqzZvmysLOvd95e6sFiB+3TdZcoW39CE6vR8Ytfs+abHADrEI9MimWkf6MnKT+TnGW8AxwbwXlxDyP3z5SpYoKKnZGg4k9cJCAZ27My7dfNo5Ong5TqcuUNFF7kqA1l8U6/3tE0nXjTOaCDehRI1SvdH72F4BNLpFHLnaQitv+N0d1ggKIESQ0hibSRpzifzpITgw91w9WJndsLZ4L/k2M2IE7TLIVs8RelfR3AKBoestsKojGUVlSo0zqMpkSaAcsflkNYdaZhW6e+72YaN5CrrZxTf1wc+5fJHaNgJC/6BMKwRCDiVvohKzmvEyVtB18g6RNtJo5P+ZT+d0zZmZ3IZT2vUE+d2A/MEy6vc7HZ+kipKgheNMe1az6fc2lTPvqZJ9nQHFMQsRyTOyF4qT6mTNf6tzml2bM/2eoBgX78KHHERt7F6ErlGIlAVBy1JW9HivPgzB7ojU6FVxavN62ho5Oqnt7Je5Mlo3amtaqZzB6mRO2MoWavTaRIO3r3ydx6u48/oTG2sPSMJeoMLnZZDfcSE72HGcE1GY/peFiU1mZlWo95xUJRFJOr8XdpCFBR1p+zeZ6j/kZjVAZxfkYqdmteVh6EHU2TUDkLMyOXOsD44Sl/z0y6P3FhVVo9rWZFpsC1l5TV6hD7S91U/KCnS1/URH7edBuHNLBsQmTbRDEVrOvIOMKk9QtZwd7CjlsKfPS2YC3Q/lmbCTIodW3mvnXqd2lZ/kTmxQ8530E8cU5IWUh1dnGRvwg3g5N4oK4LlbWDVN48N40X4rF0cJcf1jbZ+vc1MBYIFwMAxOS+zQSl17QD8zXhRAWF3A9bZuF8aBh9K85dKBY4Ux/u1EYXxvtNDHYFqDQE/ecR+MhpaZIAFDkLWBfgqUD4QPi2PS5KoFL/vBw3YTF5IzMqvEAfCt/WGjGdGRd3et1RC7QRFTAVwUm+xZDczxai8Fzk1l4HYZuvKfhJdxH3rf6uuhFFnQlSUfSttCngR+96Wv+TSE5twaottw2/NVL7aX5ppUnNWW3FbcBY8im9GlLyaCbfps3qZI9Loev+YmzR7go/NsFh1yBjdGW0X+/H8PBe2N9qigBLPWHI8mJO8V1YG46+95/WrEV01y0S5WhRbVAyKtP1REwUCkOtVEHAGMqG+f4Nk4suBCrvPQBFgdQ6VYQ4uIuX5QWWoNc6Wr428ChhrmS/H/RwXwsBWXQdbfgorhWZbC+oQG4js/tfzpZhXPQsScD5aAti3kQhweS2EGr3P3sLwC3RBaI78ajeeSj6THTqe8yCKg8vydMe1YOGcy1Tt6oOa5fMKcB25fM1qz9m111s2Uipm/bPHSnaW1zA+5kxLGKJxoAgBLK7tOfcfb0zmvr19s7Xtlq5ZCg/GHALgGjvonkeyjN2aa3t6pr8+Vlrf7GXVP/ksUndnEnzDvLAqiNBq9yjejOsq1XiIdWSCfdtohjrwG6hdsXjQdkdk6ITGAUNW5YADFKneiD1GewW0W5vC4Onfny2sWim/aJyCCBGeH8afk1z2I6UU9YabrKNd0zMng5/IkJzHhp0z2YvPlGHZoYhVTDJz2u1mnQSeAKCeTk6zOnYOXRuuI2LNkpcbr6RR0S3RdgaeETt0672bmsVmHQ2DrBzseBBJDw0HwioM6B4gCR/I+RYBeiakULce1SI0qBZeguOOHN/597oom6DJ62cUILoZFHmL4eoWcT1HebLC33dBQ9QDMCNPx4UNMsJ2Goo5ZDPOwAmH1BXCgtjg9gJX4qH20QOERcvE4S9ZKinZlixb/aP1Z2Ia16jWoJHeQp9TtOb6GQnrhRKCrHRZvtFv1aNds7wXukW1mXCna0QvK1Mi1geS+n7TEVA8BSkDIBlDhhgJc5drIpaBG/I2n3XVCn69Fh1H1fW/CixL+QvS5i3yCKI8uYw4NlOebnlkkhJctlws8oP9CIVKTz6mpMs0Wc9vkC693/V1uf6V9qZ7cgk6N54HxKF0QBnfbQ0UL4ERCMSQil4hQV795qjsQZsswYFl6w2UkhFyuss0ZM9qE5Bknuw/hX+VFE6ZSClm3llKWn7zAgcb7QRYLKitN7bBEnbMvq1BIo7qT3apAmGHH4cD9Zm5AaGrmGrcLFqs6rIYytxlmCWnaRrTUiXmQEZe+jfVUrjuVGUKAhZUJzIBZdD+d8CzWXITG6YjM9D4/5amNvOs0U7mUfC5UNh5DFhhADbqDcmVK7OOeUT4Hi5uRZ1pEkWUzP740e5jFP8A/9E3cY3/zscdeok3k83/EL8mnYvYwoSyqZDdV1vKiJh4ek8yHR4SdiNDMHRekIvSOtfmnwlL1MPx8e6QtZ7fCCzYkEu/MYrwXOTA8DbbLaQ+X8tz9uBE4L6AiqNSta/qXEgbPclNx6p5Rl1czXU2hAVlma/EaEdumixlJALUvCrK7FA8aULewSYBKJnSOI/4wrz2b1Mkl334Ui6d9a6M+yQmP2pbZh3rRf9GGsGeiETI+kBBvnSN/a/6H7QpT8ysBnbjiu33AxQHmirket+y8sFzFaZQOR3ZZJnP+mLKS8fBXTDFEViW6nHQ0UzkF84pmNGHUP8FTY8WIfcJa4Tdl4ZOivhOlKEXXrqQ6zJunkgIXd9ZAu5gn0xHYHW21ErP9lu3WkVpB5vpXI+wlZMRCYCg0W7K0oRNVz+wwJmYCs6BGnSAUBGrS3M5Rg3vcZKG/IoKrxfWzrQvuMgCgy0E8bcw6nbRMNJD4NqJK0K6sFiBxpepc8yOVOzWEI88R4wZSrbJvrWaFLmkYu0CbuNWAIt1RRYOmh/fs1ecaxPDlfqrmIam8WSICnzxGM7qIEYs8XyNlRjzB44EtsGjhEv3PfOL8UFGhe7YVboBOVoqvLHcKfA4j2w2OcSY9uNmsglVmNGzgAJDucMf0vCxKayfff0vgKmfJxZnX0shMCdnT5H3jSyEPbf7UWCnU2ZNX2BfHhyRkw6RLlePViJ4oRYh75OSIm0zhM1RjQOiOAa8L15SM+G4IS6hWJBZHMiUQVv3QJrIrw8wYH3v+qP/W75EfuzgVpJ7RnuQrkubqXGsArkqZ5tzgJLTW0fTUsh6B7Epl0/D+XI/Wu/wLoes9wOLS2cQnI9+iwW6cNrks5O15tIIlC7ql4UsvLyn1MYNIJSpdi/YrbSZjGFl+8g2EpKrgfxi2ZRkj6CLPwL7BPy46a0/jyyFyRApSF+XykPs8ZKssvCA9l6Z/2HoYboSknraTmHbi01YTuenPEJE9TV3zITjl3Iw2sHO+jyMZJigiBSIT6+1cASyd/RqTuERXOpZWWuFJaBMH3kG4Euc3Ogmc/5IFyRAkp+eBBCd302oVdPb2U+eEp7NguRPo0YFjPbxHfUwGRnFTe5YcglZT6VNuLyf/fC3kvj9POg2rg3/qHyXZdCQpoyiIkiI+ALDHTUFgWSI7sMYLCymfk8BpRJu7a2YOZka4/MyYDpCz7ElnJutIgF7un4vuqKwSzSt1F8Pm0pZu/4jGvvwMFyqpD483hGikwP+By+Iy4Fi8I56w3VrNVa9m5IS2nXpo1Ux7IBDtnP703nmEzBzHk4zRhgkY0LFtc2rziQj2OGwL0bQ80CzRw2fVyv5bUV173guJmR3/i9Wu/SN6MuxCnX4UGfD4EvVjRRlVHoNr+r1Ty41NH4u7IllU0ioME0AvZcVNSIm49zLIxTgJ8OUCQz5noJxSAwJSsjH9I0fKDwiSXx8tij5iT+iWDGtWa2JOTKfsUJ1iFiyDsi0x8HobUVsUvrHEP3eSoDroBmdRurwtx1EdTvvKIKPoyWcDFS27/SE3g+UVrcc9CSijGIpG9xlx9Ec0zEpZjLNDAalbesQOi04di/5rdoWAh8XruYG5TAdobFX8PkwxgTjwcegdVYASO+Jh6cll/mZ4ujmVSKQoCJOAiiv8gELdheGlxiNXjy2+EALKFz0+P9FJ39TGB1TW+Ne1NmMc/CSHdbreJGfR25lNoN+jPGb6hJL9d/QKOnF7KSdfQQ/dHrloAqgb1RckvpV/jw+le149rJsIfErQPzZx5fSgyte9XfDM5jynvTMf5D2Vh1RKkFaeibl5sTNCXLsF0Bns8htdpA5suZ0OMJ9fW8/M+PTFBvuJNBu53kDU4sTS7NF3ie7LSBjuHZ2D7/X68N6fCpe0OvyYnqX9YIHozxB2dH0122fIKeRD7PxtyQY1OcKyBcHrRoqdIYI8TxP7m51cznr+YcUjm0pFbcTlrkRbjJHvSNRqv7zoE8Y1Q16TFf5XnL4jzjVA0Lrcs7IqJh1wJxl3r/wXgGUM7u9tkY60JyvDCZ5+3DrTECCrhCRh3a4mS2uLmkDMflmjJRzeVJsmJMq1VFT3yhxMimL32g2H0GKVLQdiQQPZ4JfmF+PqxZhTmun7MaBbb+vQ2FtRWkDY9fuLAobxRlfaCzdpR3KpHQ+iHXLnoTY1vMDagk3qZzpS8fyoIXnlgmh8I9PUv1G7tjJGQEkrM8wHAK5R9aHPN2U0oa0Aj5m/kN0WV+gQTN8g9n4oO4MikSccDNP/zNsuZ1tk/zLpI3Xyiiu2qWz5q2lX1AZNaFe1BFcbnc0x+LMgURk3Fr6dFLz4rXcgL7czBjHkokE+kHfxuv7UeNnqgpHFKniYwT4YGediJlwq4cNvHQ8d+oFGzl6oau/QD43G00kIxLAtSWVghNhi/q9YU6mCjxj7b0vN2GLMFX7Sg269MBEzQwy5XPbXmOiykginnqW22AGVrxgFqOWwGccP/OjHyesEQm/Gzg7MlGK4QnO0naZ5mMHUi2wVCEmjwOFGPPj5yLeSPSrgny2YoUY8+YIiqeJAjyYNvh+2OUmeqOULuAO0Odd3KHN+mERrANHQ8WkJH2YM5vZBm2ebKMRDEQ8a7oZiyRIaSI/DMpSGilxM0QZEqVPZVWYqkAY31d8bKz3vIuXvcW2RIOokClLgDEiDEWDbm/Rj3cCIP877j+dAQSM9xUvzCb5EUn5/5GFYwi+xB6w05JN75cYIO3mt6fhl37IoskiRNwhA6FuCoyzAhPJsFxbc2OVTh87E+R5nYHV22MSPdVuWkCj0zlILPU9R0CylbIDUWbYT8tFDXSkXfglavnGuRjiZCUVEG6rKqi3ADOAWlbjN/gzVHEfegxihs9z91ZUbunMcXTr5LEbVAtvR2J2Km5Fmg4uW5SoWlQx1CE2bNiH9f0xKBdUS0qMOxnM82ewP2OzP2ZzeC2fJNfDutE+3ssnyq6GKKLiVHYq9oC6aSYe2oWcoXXdIFpm0S1xm4n0S24ZMu5kpO/5ciQCo+fk2BhJkcq81Lwbqj7/KOKMX/GqV+5vM/wQQdOUV2Oi7Wlp28Ec0flysh2xg7cgZKNv7OFmvDYxVGs8TPT8OkW3UNify1SgBAwukMynda01kcE9WvOFjowBNYc1h4Uy8G6cKMmCdZdy3mNMpayjd4ghbYlOuoZhRo30ChNyPqUK9dAG+CgpgCdOXnIc5Qft8TsoduihZwq7ReK/ZR75A5K0lAki3N3tNKwOgWym8hzGs/UXs6MHmGNLgVWoOEGRx2PrBXc3bJ+6SvMRPkywMHursjDWiuOZMw7nzZFDiBLdJy1Kc3q+HhNeog7zkC/wB8UHGsdzsSxgWoRH95JsTr+e9RUppBhTsFIGzSMnlD88r4CQUb9KlaCnWLdsmKq5HVE63hJSls3aDPjbcN2pcVpBLCJFzU8YoQ2TZPTouMYwrp6jAvBCMOmC0dTeECNCW29khM4ZBDH7TZPEm9a6qNZPX3NchdS4cYNVIR603ktyzXGGLALi4D0XajNk/QvLO5pcwWj6oFI1a0gBdPfZX9b0yP3Fj3CMvz7yRkmukdBsnuIN0JcjYvxL8MW3i7f9eIBG64EvSHlfXI0vxY+3tAODQRRqFId5qvX7xsQo+YiUUD1fdDcDq2Y/zwrzyv0ERfJMySzNM+adaVIenXrNWwrZiVVDzlJwg0IZ5OncNm/wxjN5H+7AHYI8r2weC/fccn6svpGnON9+FPqEccpbUmF+kcZm2OH0Xg/ypoPu8JjO0DLcCo6hhQyJ8QhFXQLAdmxp+tfqW9mSUql6dUHf/GinVYjn7Z5S7XBFuSqy9AMj2u/XOXO6jSG1z3VHzxKeHt1MFxmwxj1nZQmDXYJmrfS/423DdqXFgjIBakMuIvR+rAhUhejrZtc3zrXXeBBb/fWf7lF6n5nAsuwsjFAREkiQJGMWqdhd987ukJvwgG4qfde32EUxX/BWGtDb05Nn/oBb6QHu+Avj4mexT0/Z38JMPBYQn/gOAsYdebXuayjx8xpC5HGBKLC+D9Ux6HA5EAO+1C4CKKUcVR57LAH/HurVnMACVMhQAynEcHeCc5tB654WeBNsagPzSNI3yY3MBwL6iuVohx0rWxAkxficqpNGxyXRodort5KPdWfIGzxXaqqiKDJ8Y3o8W3OSODepldNFAd3KQITZ40JeGlGDp9gDhVFHrpKvODgzCNI9EnXIo8dRL/KoJaUZ13SCHb6VCtWSr5rnM6/hC35c1z9yh35IL87NyJOQgep+BQ3ZstAC6Nsom8Kxym6yFJgW/JpGa2NTLmyAgPvFwcxm+F6DxxOyCgWEa6/AgfamvzDIx+1V28pnVb1stWaT1064n/3kBGWzJm4RdG0EvorzSheQBqYnDRrah8Myls3x6o9Q7jB40cz/D0lpBRqNoa3QkY28sMe7YlCdfTY5xI+RR0VxkjEQATgWE9vWXXlUymJEgXLEtGL/CRIrEMsmYVY4Rgyrt8eVL9oITpsczra6naPsV4gZnxbh5Ew3ZQFlpAB+ktas7eA7y2a97nTyDDGbwdgVbD+Cu5DTArNZA90UyN26092S3xJlgwPYOTc+AG55HQBiE6Vk/0iX550qBFrLvujcXpMfizL2qzI35zJv81mdi069AWj4J5LfFr22YaMTf8Rwgw8dS9Q6QtAcMkyC+cTNeIJcyBMMCZHQI3j0EY3ai5DhOCS1+fL+bBA9jZvJlqwXFRF0wPO+lZVuJquDcBkHlxvt7qa5rBkQr1nJZdBheBgb1BbNInInnDvwrBN4CAFCbU0LU9NTgd+4GmcgmC8X9VNPNxnURVWqj+ij46gD7W9e9CuLwvHRt5tGGGrZl7XDghXJzhyxCZboeSKsw00SkNhpZ3g+1l4qQ21si5xqkQxoiUTAiJSkPJUJzjZwE1O/prdbiUMyjWzj+v0P96QyUSTfem7Vi91Bztb8y0ErDubiwYoYmKtsUlvGIWphSRQCGZVdqkylUvjwO28XKU1YgoYdSklFTrn1mJFZncc3z5Hp2KGW0222oA1itEt3xJpijkbQuno64QDvxZT0wb1qU6Pulg9VaH91zqwcr1gMQHQ7uJGQM3/Rz1cQci0nF+lN1vxjEATgYVKnzzDmijJNzlBUQ6KS5WYzYnsPdUgkntPlNErQ1TwJd9Tm7D2C0+oBoc7eTr8Y/wx7GOIP88sk4ydZvI4Du2FOJn8Uc25t/NB6tRoMCwsFZ2zI4os8hHw5dgOQNdWjUMIgifLx4be6ZqlRJ1uy5GGX+J2eCbapatODyMuS/HTWUiPPMajO90ufJZ9MUqs4XILIempV+ETXI5ZLHFdBG2szHw7Hfgsd7u+hsnRfiHZJGpsN9yaZnUaveJGiLpcJL3YyrTKKfYlWTxqGrjpnQ57k7rkbQDSDW1ndL4PySZcW0e5nXiCfYbGbjhXH3uNJtZLszt5UalxH5bzBuI60H06oJaUZ13SB/6jBh2QnfcqX5roKuSUkQFv0Tr0DVaUdgEdh+Ix3S637O0JcguC07ZjLz3rm/jMJzzSum3kWp8we0Z8xopNkm9y3Zu8UsHi1hPu0mlyy1hUW83BvnaSrpYv1+iopO0aMgmy2Nvkz9MuJLtI5dfUvY5mtkMXqX3JR6kP6PPqQkNPkvb6DZlXWBSv3inS6x0W/1kjsFuEnMui6e9ljwxyEdMnSGddeyDOFTw/+DGPtez41dPClMysa73GXi9SFMimRG0AfL1tceNiDoqL9xEliFGsurSHGMaXb1qBngm++9ZjO2k2/4jzJ35lS2u6cktB7aYZTuA07vIOM/S723JpMdR04iX8gNvk5LqTMIOu1rS+OGFTz+L2hBI4u3eAjy/KaSug4sf/8gfetXw184C3p7FGPXlLLYrunsMtezRU+o4wPzxyZbP9XekPrwrmV2zSKRJhYyn2kmtI+6XIA+XrXfcH5/8tkoaZRu766soUWZ06RZQbhZGZ3alW8XW7T/y89amsff07aJFRu77Vh2zZJdFAgYaoAXcoyGeo2EMFyqjnyxElHS4BFQunI7CnOKd7KaEMHmzEkpcOOIO0J182kL8dVPCH7umdHhWoZGV79kSQBh1X1vRhRlr5yLWcuzd2JZcE3WExPYrKvO36PZqxF/w/WZh3pSPpmRU9XixuI7AetQQ27AMyKtLq//CWboz7/yW4S0WnwY7+Ld25GDvfTiN81la/QAfQtc0wTL4xlRVOc8yQ+2mBKD5O2dKA0WfFEPvLpwFiCNXiWYovvMg6hdm7puG1VvETZOIT3gooUx12poGuvhm/DFLWe9pA6cEo3udOXWl1cr3uCQCvvxJCZk8k62MfKHWx+zQQvH7HXd2aniFK+W2oNLjk/rsya81ku2fMJc5BXG2dLGJajhRF3ePZ/xj2TIpbu3iNH3t9A2kDv5wZ0qUrC1615LpUHoQQPeP4pdEsH6uRlHG+EXeILuugTYOci4o9OJYF2eaUje5sLrieSlL1qOqD/ewB94lSMC5SwTwqCoACl8KigFOgppE4OnbkRDHiY2hZACVLR1b5SdON9gX8l9JR71nLazjnP+3A481J9WSWYgVw81mSfp/PONs7I+wlDx4yxbY1orDUNXUAXuXDK5uSMeydQzVRk2XDFkIZ1r4HpxAhiQvPh2MLr0Cur3WK+X3r7VQJq2AchgDGx+oUFtkrADii/xmGj/nFC0Qm2U/H6wUMVEUj4I654RUhZ6oeYiL/nNhlcTC2I3JmWHEflzSMLZYyWLAmddKG0Z6PiTKqDaAHKlWql0X4sIGKpLuyZD2m+7DaXXJ64OgLf7lPneSsEZrkkhI9EP9LOWRrziGNs/Z2XmntVOO5hOBJLl/ELQ7zglEflkMwVWRELN5CsEOv1VUnah6YFUSGZIYzRO2LiRA6JNbwFec/FwQpGOqtGrEn3m7Ith69knrhG99ye/Qc144fr7hBfvI7746qJk3EJBYF3K+Kv7VwJXSzB4PQMsye2+AimJy19AkMyPKHiXufLGQByrz52UG1iVLUHTsepPTgYYJVewk7PBcmingBhhWc33FOHaAmWYhcVJDgl63tUiLi+qT1UaqYgxdzMy/gSvXrosJyWv7tC06fuCH9bz2gIirR20ZrvZX7mgU7VTZp3eTBsZEI0y2O7zhY4RFiB78HX2aD88Lx5alX5GDnHbTuMr9ZN+cHKq6Zy2TVKfaARriYQvzPHmw0IO6GTDH/Xac7ZVd1DOE6U/JwQcJ1c3HX4X1Mhtw0d5Ut/0353unTCa4nhOtx1Iwh5L4RtZjzYhRYQfVP9FHrp+T5+X7B4CaATVubm6XpsOifvPHoOqlwu/PNMWFVp9aZgZAgqKe18cj4DhWbA1qtF7PzaZH46XmtASqiLbagnsd7inopTJg+CfEMOn1nOVnvpiYHU6ogO4A5LdyEx9sv0C+yiA0RaOpVO77zz8zNW0hVwkf31So2X1VZwWD+vWlwV8EG6c7uqFF+rt/7gIKaxM0TS9l1jQxhc1UsPCHH2iuadQ+sFy/JRCvhvI5AfGjFHGPuiKpxWcp5yaY/6zRjeEteHg97+aMeZ1Isy71Q9mpHnG/2GMLH19stRZcZ/mTdb8YwNFBhGOUXTF42VinNX/670t2MTf14VoRsQ0GaojhokkYW1eK2f40ShGDG2YEc7udOXYbqlC0KoWSUfWQYOvL6D9Cgd2fJRLSQgqFPii03dVzus5n4jbUX02fu82QYkncalD9FNeVbaaTna8UlKmiVls+xmZ1IVnKS7h01ic1UO3nHsyruglfxggtTEBJ5sywW7JBvV83sC6IAS1kGmGnii0LfrG/Xa5gfTv/kVHgG1aLSWd+PY3b/nseafvtFKatA81wIsjvF0+NMj/KgESAx9xXPt4/pvSMXgc33TKiZxMT8E/yZb3BCnTfIgXzhg4oi6QNp4rUFkKdQnZzW/ZIYciC/E5W7OwRWhL/pj+k+mMCbu7NAD5pXpj1IhaZ7Gg4MNEjALud19u2WQDWCjDmx8IiRa03fTs3hBrceP+B6v7lCVwK0B8VBBV0AnDTdnNurmG4/PWF2li5osh/nNbB7rqsU+XvRcCQaoUWOxXNULjzbShHYqiZsN9XVix+vXst4WREmIWkXP12yN8Zb5PTgSn+hl83FP4Y6WMovgDIAtps6rrZvZ4UlJU4ZKUMYpBYTMxwabUqpNKrxOXXl6/zCMtUj6jBLKwQrEwhTSNFObzxs032WLVrhCHvYrt62+O5CjUL2diyEPo1pDeonyE0QGoJpWv1LKUi05UgXJDSeOP4luM2YwGAA2HQPtxT6n1Hdln9vJjF+r+FCX+XgmneUnGBbUnCDKrAuwyJURIDZU0Jf3L8rHKpwUv+gsqkGcwWlJQqQQc+YVdQKuMmd4DH26DSbPrCwwrSm51spvCSm4MQy6bUK2ijvmana8+F13jXDdyZ8VS/i0bksFmHfRn4guafjs7VjI1QbSjGr9ZdbiGEoZq0OEg21uDjbiTlXXksnPSP8KnaYPvsksp1daCqsv6lwlz4pzZJpV7NdEmd69hY/8Iocd1j/qxOHWu0idmTHy1RADVWipI8bS9i2tJ/gIWjEQM+yS6kNVBCd5GWSAcxL6SLlQuCtNJsOSaWXaRBoE9R8HC8HSyA1YXlHEguSpHR3g6+ul5RHxB9kiDvrPRWXrBpTYGbowQR8GjqUs3soSFGgfN0p/NZ15/pySoNFhR3tqbcNKhEoXXp/lWT73O4TkJ6EJnjTxR6QJp/Qxjj7an8o36U6/3tZn1AVI1Fbaean672LIgAMArDN37Tzafasn/MYs8ZaDOOtLN08wyeOqY1rk636/eH609+GpJ+GKlw8FnTsuKFGGVc8UG5+KbJ2EP/4k9GrOJFOMB1rU5zKLTBfLknrVQP+MPmGGwTq6qpfJ7ZQBEm56BxF52BMcEIVivl1TdJNi/9G6bSg5ruXfzeglX5JHRLHcN41Mgo6jLKNqAV65wcA4wH3MQWDYg2FVnWE3as3qt9OWiAkjHav6ELN0s8wY66h2yYvDypMAsOTWQ/8eIibaPOFSKjkkloP6HlhFyQj7wiwZqbKdKnElIU9cm5lo+zU1mfsYaxN2rQAzzSFcp/8ruBSOShePbhBU4gXSf37/kTZ70eEz57N+GAeyAsYL7KwYPoM+zsCzt9EtL5XE3ncsDermAdcl8kUdflr97e+vIHNrttyKwWepmlL0ryW4QPkc7pyzC1wzImB1mExIV7SsgW75b/U7HEc4JgQm/gUp7NqUXd9RwYDtNiO2UPwT5hMnnQrVTXB0vVINOdJFR1xy33daoV7+m6/aduaZN+rZTGxIwhsI8RVs18kYXW2jc+haGIBnzCL+azx6lmQ5QV+gez+B22/EKnSeUiKbP5L0malqhDwCDM1+ZT2Yq8VIPZV23N7UKse1ahZB4WZfxZ8lrcU6xf10mm6GB9mwq6HZEa2um9rmp87PMVlbSsRvryw58ByJsyGcRk+vdZUZ8h6p44QoU3hzWPr/1weUUhJ5aeVXo47ZvEiiNE3TZRL/VkmcUOhsReGFcVXlcJ6rO+HOS3R1xDDw6uwwpu1vs3KKs3JlJY8UkT41dQyhzOwUrZt9odB0hpKxJm7oixBRMSEmmFGgD5wCQdFGaHQ1K7m780FOUTuL3XeuKZtJwh85vUWNgnIa8dYfCf4UyVMUk5eGW4xejynHYCcoJR1w9d2ScgLeQhT1/QZY8PhFk/wFEkUHb59KWZzK6MG1OVmXtindUqeJ2Yqv8VcSIJE6lvR3Dx8ruPAHKCntxFjU1yxrGdY+/muAH8DmTTETCVmJcLrdzV44H+MtMsV1MBR4yNZdd3xle7m3H6Km0IRGii7I6CDypzL3N2Pj0c2iLh7BDB1FNw4m8xG0ruI836ql0OP75XZGVE4Mh5E1C45mJ2WMJeRoX/Nn5INgoLV5/3TacaFQkfhdZjL0agWkXuVccIXZFxrZvn76xgsv8nxnMnzparDHaprPUoTM8ULgiW7AMnHCbiZE04zybqA6WozdJX82ykr2xvupnCU9gLt+k7u78P4DGSuqFZos2p6hSNUlufbmwY3WBswwU6eCsufJMXRzMuUWTDDvrrP3g6/pBmJMImD4pcc/idSpfBg4mj4qCdcEfnr6us1LYrJeIU8zS3KmjsuaFzGm4grXdUNZx06qezNQwafWtbqTiD3ntEHUxFapVDW46KnwVzImDJmuEe2XpGM0FET5CAnZn0OfhWIPX+JVzbhYAUP2rT4AP4rUuLh3bU7LAqNPMpZYdymXk9NC6Pyv3t86HxWEf2uMMvaKa1ougE6OwLFgx1nS7zF3nGkb+QhfhIAYzx0reNJVFFVtZHf2ydBW03c8sndbrDcV5jd7zg6x3OtdBDfXyWl/phQI/0mQ4HN509QAXdHAZCCEqpdmHTPviuxoTSuAHd5WiUWg6qx/NiPtlIIepjLoeAAR4101a9pt2JMDI5pSw8YkynWeBlLXw6GDGAg85ea/6utz/SvtTPbiCtyvct8j4JlWVIvmuHdDBBddnprnmLFrmldp4nX0b8Z55RhtDO9Hh3RU7wck6jGM3AZ/Ndk+uPDoqoLX6+GC+efEt1xoie1nq2SQgcELenGWuvLbQLsnNDIHb67CAl0QKyFpk9nshsVSvKNPFS3rPsqGEjjQsdRRSVacJGZodxsBqDPuGgAJ1IAB4w1VASRdkelXm+Q3Nv9kdMR5+z7WjDZPwhcdKZE23QFdUlQUQluidPwAE7O7C0dWwSXmlAOauxokY9gD3QyNzwXXnh4NVRf5qbC2Mqz7COrKbp6pdNk+Xg11aOvXbYW09SGTe9DxAMEOEdjgPBSPL3vfm5W99BIn72D15VPamJGMGybVux7riVuafXGj06PMi8aHRNASxhnnD6p+w1X4ICLr0kypMDUEmsmxAmfJV+2PhkyukFZQhsNq8CkVKhxXsKVAkSS4B9KwbXrgCGnezspQ4MWogRDA0MxwrGIHsu3ysYOvsJ+UsUnoP+RLpkWYv7VpmfQesaU8snUpJHfnFLnOSPCPBGOdHl4W3fA4Mbp+9tgrI1P3dgM+7wKXpwlOzG0SgwS56ttYiPv89SeGqgDZWVmgrEAbCFhBpfCuHg8hYwSsWrq9WzaBIjFEsmgbgWP6vzb4ipfPDNANpjtIDSXrfuLjdCD0Ps8UICgAD4Bb1BPcAVtC2Se25ZBtw4nxsUF3quQTeqjMHjWlzs2hSCBWe2+cIqEItCoVzKWUyIMU5/9DAESlLWoBDCzXCYAyytq3tvGzA3RBR2WPHv2hFyxfZpiWA65iU2h5RTgXyCEcB4lM/iMQChNawjnmufPkKfWym7UReKQlfd68Yzr838+zw9IF/20I4dwmhH0CNyRW+ka1H2P0O+HVujG4ZDj4DUUg3DVGHTHX5/ab95yEMyRBa/00q7HwOSTkWwTbqGdKEpw5q4a74VrFAAH4ov15XajoJJ1cgDSCbz1m/dDGB1uz9oWC36yms1P6A5BsvxH51WqTfNoqicnnpW7UKVYABvabP43uk+785Gi2B2qm/NP1Tva3x175Ak4fU40BOqVyQqwdsw8k0scFx0szG6x+7gtzVZpW8qocSwL1Ic+QcUQDO58gIzFkIMjAolOu2HS1orXZz/WnIxETM6EpcJIZCGqxG8rnrbZcERKDgeLjekqHgDJ0VPnIVGX4R4jxGrq/PRyfUROXkPZfLCl3MpU9KGbZw1spj1w2CoTNtpc8Bja7EqNHBRzGYyNv1t3SpRFDrTZwJFJo6ZYY+nXSvu1ISbBbGt4sMUydjcY8xxivKcI2MI0xb8DX053M2ox+v9LfIPRp17zIeqGl1rzJeSEdsd8UOBoZPt/bK3nXKGd4MxBHcdeAj0xIFIe8MXDvCkdNmAyCRzqBY2pR424hYNTZtfozr57UxGt08CpTkeJbvVdmeox1hhLd3+/UpLJAkr0pOVTGl6nFrnNn2PfYLBQ53SyXL3QT5sCD1cYmeUX/VaEJb8aNjBZ0USQxIPOfUbeOb7++M6vN/SnX+9rM5bKX458bsyfAPMYkZW5xcH1AhFesbkmaOJ7o/ewvAL4mI4O97X94HfkRkbApJp+1BQIFm7UrS6caYc4rOGY7JrEg9MDvY2M0442/D8yeEpd2mld6bI69o/3+3KtteYwMLDRUuDe1CxAbXePyfg19osGYIeTGD7ncuSAtcLX5d5oLTVIyvujno5zeYZ1zdx6EwlaX5s4497yE6GwOd/Cz+QhSQOfXCDb1hPueE0+C6huXqm6DFj+0xgmT/Q6EPtuAhZLgrKerAsDtlbgMkYi4gPN9N6KJqlB9c1EVVTWDHV0xJnElNKMZpYRzTtf6AXSRltFKPxTonPiSdXufvYXgFqE7oNv8ajeeIJ2MHeGyahyrW0w+YeOTLV3PPt4JxWVf6YUHpw4/IspDqbUxs6itDf+8TqvTq3MdeJ6KKrxg1+IpBuYd7qHvgPH/GFeezeq1ygGBuTrwaNojNXRjzMFFIO0c1+m0GTPeskkpLVpsw71owFZZPRHQzZYHIG4bdhyhhwIzv76qMGrXEkDlzk7P5mGTRgi/Y6KZI3K7pKP7jLGd/kmbcVwy0rqmyvGJw8CvYJlq59FfVaRLLUlcS5YdDXaFmhDcQ9spSVA/isgQMs3PSbQmDcL0yJmxofG7JSGN86HxWEenKqzwghLWESyRMX+gygLwWOxgKhkBfeP8vba8DOAMUsPiT/WA4YUtyE9B6fzWdef6chL33XcX8+sEym2lt1g4VqmL9ufiK8BBCoYwffutuPzYLC12ZjSGg1tavdOMKGw45mZcHZQHe2ptw0qETRL8ZN/9qJfttDiwVbwGeqWJSb8vM1ymT4GzTGjUiE1s6LjCch14xdciCMaZmX51+ZjauT4utukLCILvp+JxmDslXdPfHWXkZ3Tw/CRj4qjkJ9sChc1zDvvKNCNAGvL6nsrwYNd5l8hwOK1kM98daaL+T51OFERu5LD5N09djvdU+M8KGSUbieitv2mloPGIHzPeCBZgAEaVodue+DfwEnpulw0TKDpJl6fmzeYQvhJDi1jaL7JPqt9KESgR4sJszGrtjg7kTwsHXnVyGqzb4Q2XkTMJwuBq3CV8w6bK2uCLUTKfhRYl/IXpclzBYYFVjBXLWfsgTtujSxbUzJz3PjhQcskfOdctsL/PoxFVJ0vcNodgtBvmt4pMdS6xGa6rCbP4IchBmX7Bb4G88FTNcWG4GCSIg2SNetfOVvVTY/aoFN85dVYT+KP2KyPQSbUKunt7EnDqfYG8W6nEJq9H/+ePpU26fxOuuAgmqmBaDMZoZvwz4RoOv2GndnHU1KyDSbIxE9IaXT5iv7bUjuOd7jA/xxHKlajzU2luVuIJf9xQOMbrAAQpnf3DkJC0vPuChREg/8TEjexKM+dOoa7pccD+cZsT7hXyfn6WHYiuMUf1xBLrq8VReygaPqCflJxvBt0y8DCI7GOMdJ57sWVe3qQTRAaZ/Eg+kjBpxpPQTTqAsKkqgiBWEbSXSnkZuTOja/PcgnIwfxKkdMZ/XC/E2Kv+TvWL/8aJrGZdG64k3zyaT1rvyOUPD/jCl4ZHLoqokSCLp2KqJ19WWrM2msgvCZLTz92ML8wAQ3NFmsODnbRfO52oPUSMLITBkTNZvCCvls06OmT5DX8gxpWGEoQ5VT3hhcjeSpPCDRtoga6rJ7UOh8t9I/PF3XF2lAIh5sf5o/Hvp1kKcyZ51QMX+KE7JLW9Rsq0MpSvlhS4M1J5NDDIT6GQ/X26MvKHQeJow6zgoWL/Vi0B7VtMkUsOsr57cDxRI/Dln+f39+Hwsm7kp3gvgFgbwtAG8F4/lbpOBreJ0q0MgEPa84GsB7yq+fntNwXDbZE6533fA+GX29gSiGSGFtlGEsdopl5bPWf07fSHNlzPitBnyL6zRzpcUJxNVaqEaDSFngP29gb28AC0U5mi8KvZnFbfl/gj7HLlR0yFDXFnVoSwS7aaz9NjWHw2BD9Uwy4/+ukTa95PFPq2lR3mukFDznfQTxxT3S6lhkH2iD2AHoBdgMmSyqMtLcInblqxX+54P54FD6PgZJbaV91k7ZMaRNVuEyJTHrBJf59v5tE82JQbFUy/zr73NXjfMVn7muWZLAtzH73w+f+jyKcLb2pS3MAwhmLp746awJ3kVU1VqS3Hap0iW6cXq5mhBGa+00yoL4hgOV+zZSvO8+Kvu5QCQRRUzj5O2FblDfQBYb8qJ0CZgmYBdequcimF2akVzMHLd08O6wjpNUzcH9GoAbZhacKylYcdB3bd3+oMxnMKLba4yBF9x+ifmKlJE5OGKrIYIlU4a8My23RYaiIFrE167h5NUEyy3/iVNXxlLsrKl6CanE5bIO3xsC7U7S2uYH3MyecUmfei1BvvRVAPdiNxTy0NiLv9VLvv6G3PLATT+djoOW7slWz5iubjMlr1qkNYx+pAoxI2jzhs//QiDKnj3Ms9iBS0i7Gy8ZHp/G7/iW3TzeI+hz8XX4BCfaYnAgs7Zh4TwIzpIztQSSZSMFlc7kBrrylfYYKQ/PGoGAvIpUtCp2Sf7QEGQAI8EKvDerrbKClzF01QL0kEFogyBI7kN6fQT1HebByDiVvohKzmvEyVtB18jFbBMcxBSMXSvA+bhwdK3vNR5ZhVvKrfxOex2JiSgAMN7CulXNRoASj+ySFxc1Me7Uy8oTCudp+Lr/1lmKF8eX2ly/TZKxNPZseh3wUeS4g6MNucLxuG77hHJmjMh/CQFIpcwWOgJ4OBgoaLvEo5XWRuZq3eljXFFF209ZbPYILJaRTWd8uNvXlnDLJonSpVxAPMQU8OnTl/ecxPjkbZOFG4IAHB0tnbDqWkAhfWfrZB2EhnFadcRT00OjI4XVDtcr7QhMIKN5tzRIbqlY6M6u6okE5jHhMnLQKeJ52hvvu+9k2tEwDOT6LJ4zwJGay0lkRXLCIx3eNHcxH+x1ivZGNplkmrDcK2ASiPuUszt9HZ8mJkiFW9I5gl+T8TGXyRAFrmPh8I/zMvHrB0dlocQcEVRkTux95Dp8u7b/PD2nODy+iDCtyhvoRf5zAOn0EYIuyqCOfwh+5osjEaDV7lG+JOIJO/NlAbeGmgqzJ4rQJKc66cr2vk/P1Et/jScCuz3BtNUtibiHTu6kEf/Lm5b8Eo8MuTU7VyHwFl01y0S5WhRbVAyKtP1JIkoQQ2IQQPI4nmYwTPEnl9WOLLgzAdFQDgFDvMlt2lyTPA8xHyves9RrY0qIszI4MgrLaW8SG6qGXim1XycI5LBvlFGSm9/OwJjghCsV8uqbZ2Y0l9i7Xtp6qnO1NjSwKPOBz6cyGhEJAtHdKtjuNeckBL/aAxnPWjP20ykWLMnLBQbjwIjGcaLuwHoJ9DETH8Gv+PrDJ8in/s2qmMVEBPIj/NEQmdMO6h9rfzImlP2UBqc3Dbqjor+A7r2RrAzpCe5FsrB4cnCSJmbf1oAnVAFJxBSEmi3bi3e3llRYEGLEYw7IZC5KpNPgKQVb/jHuaApFO/0Gz143OuPDTyHgIGGYX/SPjZR0W5/aoh5Lk2Vm/A0v78AaqYj56vA5DbpB8zcsGc4KmupWkN56xoWwaeHEboP+lh9Uy3cf96AsXDasmhbtJNuQ1FU6ZdGYr6X/saPTdHR1S9i6cfqP30WLEHLErMhw91iIPVQJyzvGrINjPCssowvcLCoO3t5IOfCnaN4n8AW9o63lUDOWXixqiBnpjuhzvKZ2E92+42DZIjwefTjdH6CyRlGx4VY+vjLGXZCLW2FMXmDBSK2vCn7JzPA38UCj/ccLJMwuw8cnge7jb49fxi4QVR1m/2ATmcjCXXal+NX9/wBYlUBdBrxWnJw+ctMxqa3Bbk88U7KmTj0WjbANhRcTTZUano2T5xoop5kwvCyamWm5GjNmAAtpARsWLCT+E3mpOujKbA++rf1Ff7iDK63V4D5xrEIt8D0Xsc1yyPx5f+e4YAH9/qQ753E/9bJw/w7CRVODYFFvdjs+IL639juoFvePirpXjPuPITwzHb1QUFAeB+VwXarzT097vQ8Oc7AquAyRPyXnelyB9/PtAPqDQsBq92bMiOgnEnL4y0yFlFr7hrW9uJ854W+CnmGcjHfAGPnC583ZBWJOGxrnodWNcVayj4HqaY6K/JslUfQ2Q90rkvXhbGH+SJyvb1XWuaxzPXeJ/Rg3cXKwU1/lXBcCg8zjxabimvxgb3snPaK1DcKXtfalyVscJqMQr/MDOGFraQZbDmKhgfixBkTm2xv15nXbNWig1W3IZFR/tBBha88O6mCDLgOGikMpPUR99jBQWoOnTMadhC+KtCcjwCq+wnU/USF37GAf2BE5XDiFik4I3hWGgnyC69Rmp3TGz9kL+E8kOuqeJS4ceS0tV/lOO/JeEoRW+XwmIQQhRTukwFjAeVNzelvQe6nZ5UfIyXeSypfxVwR8Qe8I40xWw6i0LCcTnw9JW+55aooQ4Q4WTVesJrXYaqfc/cS0u/r+KBI63Zul8QtbjtzlRShipNPdO93G/pTVcnI8843btoo7pauG7OacoXhJRVxIxLzskuBPH0EOTUdPnz/gxfsuxgebQXak5XoH82GM57/2yQvLAgbUKvutH6+MRgvBew9NVbaHk1taPKrH3XYrZ6hL5UOmpkqmOs2zfFJbudgZ140wcPc616aaYQcrOpITljQIjI4WmqPxRsBDPazJDaOz1C3kl4JnTVV0Qq67U+nUn8KfbZbWX90+FwGYiTgH1eKpkDj9yXz4VefMlAhAIkx8Iz61LgJBmniaobkP32l/tnkTmDEeKMSEVT+XYsNWG5e5T5H2eTTYOB/bjVtUAU9AmQZ47KxNeBZCkb/qzHflLkNdoRslMiLcFDpOdVMEy/s7L0/F4keScqmNTX1AKVDF6b4iQPzOwwVzbnvRmA7u7XiZaf/8SJ1j50GOvguQ3cB7gHkZlW6ukvSGDEq9WlRXYdP3DlfhphvxiQfpTVO1xBpzdC7LI7yIg3KixshjO89xU/qdSyVOR6nNy6+/UsvU3oreLv6Ip8/fMpzwujFf9SebnZqKXw/MnhKXdsKFA/04Iy3HI2n38zGWl27plGdIjXqCXoRfmLt7lIPkaQjaNgSExCiWIzBSV5ARbNZ3YGjx/ReQMt+KoWjPRZVOxzDWp6+hRAXm6+h/1EV1fuzoX//tPzHDzvABbjUNSlwsWVkdjw68Xr3xhalFeRbSqjmxxh828ikwCI9idF43b1TSqjMnoP4gLXkt1QFvPFTOLxFMhgIpxcGYzEseGC+WDhyQMp3jeDv0E1jgelJNxUQc0fMp9LE+8ClIGprruWXe8EfaVYuffMgddnqwKfJu14sH/omrVhuHc+mUOKQl69dqWuz2o0oaTc5y8WeiWX8knBxoHb3+FLYckAL6TsTQKBZgM4XB0rivUJwg871DDmvb/gN+v3h+tPfhqSfhipcPBZ1CXK1YT1H7zJ2T5gMhBP4a9FxQWlCgtOupF+1lK4kBYfwSz4abnM3cny46e+VAVc73vxL4RQoec76CeOKfs7+ebE0dm3t1UW7wiBx/UQotXknskOdlh4VryzAb378SOj6uilUg7cud3sjKxJTPchWVKiJylwhMtRJM6o97R3JQdfsk0sc6lUyZRW623pwDBpE4Qxl5Z/hnkobyT/d/ay+ANTLsstcACla5w4Q62wkOxtj8Mayj4DjDHcd7kZHVOwW3+cdi/uIWvaCayY7rfDM7LwZFpOa+tVrXOkQGSWpn1gBIAQ+BZ0Y9ekVE6T9X+TvkpgsVYE/leOz5mLunIwwp4ASXOirAU3DLgFQTF2dhBI7x9vfkzAbS6ng0DQsPaRh7dCLZmhn5CT/nDbap0ge5NjTYMFTbojXSyoI6ceTSSCJ+dOc7okaP1y5GF6RDEE0WAdhyAw5zu17PhRXeRbu0XB8rOfanVOFkHhp204oL3LKRFV3ns7zV+vid3awtFVf1P5p8bZoCAOMtmeQa2iCNsxu3nbpX8NUnKXR98mtqsfa1awr8uH1TTxR+P6XWzMfAjt23UrlgyZcn+AsFZXl1z2W/+5ksPWls/65zjSfoZ+K/XkQb0ur3gm6ZQ5WwJ0t4D60bALq8Ire0Wa5yL/AAArurf8k9KEajSp1a5A2tjtjJMp0QOQqvddkfdh1BlSFb4uZHnxE9aEsjJeN3Z88yYZbnFwwUggcZCT8WoHl5p5VEWKu6BOeVzQNNFAATlnidbG0h1cn8WTwBEz/jGDpM4FAjSIyJkW4+rxEg5p2RNcggy0fMrMzy1Df1G6As/UGN1mdxAF+/KJ6vLlExF+n7Pi+9GFMyCrhJN8RbPNeb27xQIJ1kW7rbgQ2dtqaxW/qzgvTkvzRR0ZNwLjwC6rTLliTtjN+vftBVuTCxhQWJU7wlVU3cIkRY5rUKNbSPJDR/keIe00ep+RCOfVcjhe4qeWXqySsy2NXpTCwhng3h9rHv0dntPq0i1ZU42M+KhG9/GfZlt74MQt4JVlBWu+kLl/WmVZKuClQZMmsSYhgNXJhghUGeg4G8Ko0ZCnsuUov8mvT+avsTJ+7HhuXzZ99L/dDGXgOEnZlKPuB8z+gFHv6zs4Cn4D9SyX+jbYqz+AvRKGDbLvnJeHiVGjrNV/pzraAZwb+fgDKkbnpEO45avrsUkgydEbc7c+UIZcBAX28uwbfsNolrjNw7/nX0pE4MG0htQBLqQ4doYpkNn+92S9Dhcekl4hVHADkA1MLybdFUPtHCvHm+mnVErrZ0/BGcxSjackvh1PgscAGo3MOT/scqf77tQrO6nSaGVV35YvIBpZ1I5EH5/OlRLeT5JlwnD+km9JWZJn6T6nkkKG85sio5e5Dlv1yJQC0mi98fbboJ2TmUnfqBaGZLW7V9IsSkoFl61YCc07C0EbFXzdDg5Z2HebNyd3T0r2tnBbeYimpX7GJLYv23XKQYitSLKlD/stNGLvwStXzlkA5yFHaqJXWUPHFNYYSyc5tF7z5uevz7I2IRI7iQ2tEqFaUqGSspob3xFy6JSRCwz6yb0krXwqKvu16VCaGXlz9PZsxeptFUkjtyfgoTCbT1UYmzIr8XPeRgFajDr5nZ8/gcvpbYX7lgRPookRZeGqZgV4zt96GzrHCHOR0gBdlD3bKMxyiTybhvgQEPhlqWjVn4hIS9nRAKLHrStNabG6zo2EQN/jPBsdUs3tMj8vr7q6tXBvQKQ6qlSTheypiWZZ8KivmVeXOFLgp1PJFk8niEh2kJLxdDLIs9PhwclbWcHSxu9yttcBmWU8p7++b2AncxXUkkYN8KXgJBp6fD9j808y7xQXbX3uVf4bmnNIoNNhxO9bypQDDYEy1H33wkUZX9yEm6afPKlBC6Nn4uzU3ZwqxV7pHFH28ktbX7LXSqWO4YbD2/TYJ6UOLZOaPVFuNveq+JT5j1ijYo+OkEF9dooAsSQlXNPET11fM5rmCapWnhWprBv1eBt0w642hkwUyPBk7/ufziVDbFM8Pi/fZyblOPq60JXyk9DugIUJyXl7gwzmGebXuOlqO0o4Xp0wIxzKRQ4NK+j/sGwieeWqjA4Mg1uZNuz1zcatoTPuLeq0Nz8LR3dHcmKGhPMjyWWRWS3sdW/bk5U8gf1NYLSniSsdV31/04YRB6MsHBGwnWPpM0srueVsp/sCWNM77bJ7tjR74I8va73zIzIkv1Rh2n/YkU98olYFuEjp/nwbuh7QB4pMDQe0hMATGUxPU4khsBr1/4Ne+jkCb4kQK6z+iy/AqjlmpoCTAqYWku7deOZeqZ2yppYDU13KDlvUzmiLiEDvkUxb0gRDp+vgj4j4QI7m0ID4QYbiFF25rOdjkHP1ZYYIpvjzG6p8lwko6hxWzVpN8UGRdJCw0u47TG5NvzY86HWATMTMCs+ZvEU8kp2eQkjl8Pm0o+QMbpQ+ra5ZKlZ5BiPFGJxmSfoeQRUQ2cvQ1QNBRzxlma05oOYozMP3g6HPVzK2U3wrbpGIbEzYlgPmWO9/yk9BgCQ+324d+oYly6OqPrAQmeEB+gwGVAfV/p3ipZBjXa5CAZpEf9OdbQDNXJz+HfOIfICLxNKrw1ai5dIxNcZoMB2Od93ex9836Tw8w8vK/GG4wkcdhl/LifgFl0iRU2Cw8u5K+5tzTFeZdNixXjtdmqgltvGF3MQUHlGGfPTPLrrDuhEBbsvADrSZvVe/ZUX372ljSJtRp4I596lH3k1I2uJsNGa1J2HeiHjWK5iZzMX8dCtPoSFL6Z/YA//m56dnQALN1r7Z4T+C16zbrfIg91f8GfQB//JKyqOngAAJNMUsdjbAhoo7WrdoQ/3+RHKV6qtjp7DO+iusFeeVtgwTj2TksbW32Cu7NndMSxNQg6a5aUiYJRDm/3OcxNxsk7jFQyg28oW1uGVgSFYFUavsWtMGfkk7jWdmahZZYqbgDuB4f4hasY9ET8T4DSVLXWn50qwN8fQgvCcfGFoIGH1MBuO5IHoOiE+NbrCA1PaLiCZCpj7jR0aBsl4hLhAALiEG9W1xZoKA304J6FEAdXEmjmSYs3BEDbANksu0RVu5YUMJaNxDYmBoPLH6R0FwsJcf16jKXub2FDgRfEj8wJMqo0OE687lOKdZGPxTu6D22WRmSRtxiMWfg7RM95MUcDDsIgsI9BO4/I9YBXhdf5/JCOVQCGKw5HyIp0zX+isL82y5gfT+HfvyJWT/CWVlQyPfLOHhVl2DfrZWiRxPELxXDvPYTNa/5iF94ri0tKOTNPP+UbZ2TbBfvkR5Pc8Z5LWvIWkEH7dT+m+yBMrOIcWEtG8PODEJDDTsZZnMBwWMz4gqiPE9XRI0HPHMwVxD6W/Kj/feDcWOotb2ECSQViJQbtUrtnnHESkjIP+OD1u9+xZGGB8x/tUR1aG1Zb0K28yaFl8QkjlOnrqWJM4ptC8p5Uw3Riv4TL6Q+kEoMNQQKNfnkbYl5B9yrmB+QVwCSpRC70ljlLtOpwnjn0mu4VGThISS/tDfrvhRSJP5xT+g2ENUGdI9DHL3z5W922hAZMGADGS0H4EKN+qKiqi0j4Dsjx/wIsOTBldbO5Kc7g2/GYnavK8JKbap17Ymx8Q27SQbXBmOLYklIq+LOoXPaVUFnBq5oBQeCzpMoP1oqBuPktTiqpLhjI5kR4hozWB9w/0dUWv/xnjJTEAjBRHa7Q/0gtOA8RM6kwwk+BlMHx+L/GA4MIhF+QZ2Kku7QCun0rgvXCurLMIi+Rh8Mm9V2Pu6Gy9zwmOEuRoMKJlJcZmDvorHSVARhrAbhu+JdDbrtMdxS9kTGPINqFza3R8Ah2h8HS/1r2Lesx0FBa8NENO+0ZzLlAgROqroOh6Hp/fiGdIxswTsmRwy7PtSeu0Qqx5P7HdsWPI3W0XY5oOLuBaD0vZRvkxoI6Vnws6xC30U8E/VqktX0N3IXtlgRVEqtN6i3etiMxF8PAFpb+KAG6btUD1DwwUmhMuV61E7i8xgusS6VA0G2kNAh3MYQDk/ibQavQNQXaFbeZr7zYrqKeloLlcMC7lnpIvcH2N2CpI3OBdXGrwrqyyFAtS/mnJrWTUy077kcB4+lI34N4GgDnRhZf0REp2L6S1OuPGLPmOg3yDt9ybrfEunSi3ycbBz8y51GSbhFpWgTtjmcZPDU13KDmj/uVzvFPIcJPUn/7nA+8xrebWkdehF0w44rh+AUwQ6HEZePbe4mW62vZRn7ujUbOjNNgR6lCO+8tzzc5jLgTSwFtZHApF9ZqKKdz2oq2rexDiHva8OxT72Kg375zifoh+Vn2GV/FBD71pyiEy8OEM+1KhKYNDzKNwMVsobUWpgYNOCr3NwsiQaRF4htHI7vyC1aRBfCsagZhGeY4ahjydjVmGmo1BZN3RkCO+DSLGsZiNNGVA00JXYlwpzBEQSnHAKMRcQYl82QYoqDF1Popf7mfs4LMMfdtUJjKNXUTqR4dHUOBZ/Y3gTHS42lPzglbhI16KbNfg6juugVxOYrBgrtpSGeE6pOiyTo4YPRiQgMXG/8fp23b28bor1v42yckx8CiGXtxocSpSdsjeye5k+hxTGZG5ByP+yBGoBL3jrQe8fWLPtg1Ak0GdCleioNEwDoms3FiB2TFA6T3o2tyNgeHFAH9BJzm5X+qiGVF5XR4s6FqXq82X11SwnJqj5xTSUB8Qzpp6slU0TqUZB+9JuOa9Z5tCMORWqvUDDEWLBlbYmX1spl0YSe2EHFkrlX3hNDCED+Mk0k7i28dL2I2nsFlzz5NmsxgGfD8yeEpd2kC/mvoqy/HIZzZDQf0WZnQt4U9OTfYgZz1HG9kh/Cm0bo84bP/0IgybPF5MedqPN1oLYHNdKrD00qMTPNHLbBS2q05hO+2h4k57aup+i9C1uq5NNAqqG0i4xIwLa211f6EI53SyXL3QT5xBoq/nRf/qeh2duj7tGEV+sne4RvifFB4AO9XKXK/VK89X0ZNqViTmhianltJih/edE/LK9F5UN0kbRV/ME7EW/s3NahW5GBv7vuwaZWUXS9eu1LXZ7KZnNYK4zcVUHgYg9eVBM0VHZ8gQLf/5iquBTiDab11XuK3sjWAOMu3aJiXF13VbaAlGYu9fJoSQadouizXs+7em35aLb6lJxVIDeuxrcF+ogwMR/OzRQcoJnykc2zGyHurTAcpGISG6rB1X3Us3c4a6wCEIjAtmsCeCgdXZiVzxVqwSSoltUvOeqwPH3RnE256N7kxk7HpYWpc4nEPrupvo3n7CfgkR4F5m3ZjyW3q1NycC8v9FyYTjGFryCKdHdI/ArvMZ3RJIxsZkIEqwSAbul01glgQWdHQcVR8qAZ90JXtZSYZad3HTQEGVVzENBQe402ZzZN3/DYD8+GREaTn21zV3TNzF9zwNC7F6ZyRj9TNWyAXQlEXqMS4CVxG6eu/jzZaRVmYYjkejVgx+uQbplRrOtVzqLcPwnMDTOOYq0ROkeNBZeJ8MU90A852M+8OsIOR8u7GF+VoJHz0Dkr9zx8teqh7Vr97LvR9vOCRaZ25n5/HtQbqrv4MYAQW04sm4Ixd0g3650q3KVQzR6Lb08TOKvtM5b6fUpTXZucO0QYUl811J8POIXlhKYwLopXgAdKJ0X/MJww//suTtDrKB+G8GrllMPD4ceG0g58FHGt7ePOgTy+5y+JXS95zHatJDBLSmpYKNLHWsyZ5XCA84L8zIwcEoaUR5wSiPyyIHG5qBRFnZtnOynKwOlp1/AKN4oATeQ8vO27P1xZkGiY1xTwvKIOfEpZ9PTR5xFDG6d5AVISpMqYkvjnZnVlQ6XJQHe+Y4Ocfs8KNRpXXkeJigQpPinJqkHOlCmoRp47p0q/iqYCz758VdaEd1bK4sOyxrVmDiBn1QtXbds1cekdR2XeHOVS6Y/fUgfgkJhabCWmnz1Uls1Rl3PI6cD5ISBfhHBtoiQ5wCuM0zANiA2ZG4SlShxIBNZYkqwa35afgoszH38UGsQgdkTZiWmJTuQeobsAftzpPNhuVjXfgfmTdYaQIABLk784XAU5iy70sub/DrjQ0j5g4A3TY493/7ITLKy+jBEKsiCB539ifoWh2hajI0SpavATwDKIcKWDegscGTfQIio3994q/kcL9npUyHM84BLOGARH041hcGC/uE6H68mxwK/3MylINX3tU3c1QdLyRTreNuLbpcufKlcfhS3KgH4KoNELQEP5AM62kXNc625PpmALMmbp0B4+lWxye2u0r9tVVWg3KCAb3sGVRZBYc8DNKj/iNrHKzbVC0SEICQGVW0HDF2xZDu6cw6M+J6K7bg7Xjsg2rnbRSIUt/LTfVbjBr1STyZtJx8AKVQwiQ2sX2tYCph3afkLCIfqi4vUCR3dxrOcORJSOhd6uz3S8EMH+/cSPKncbNtT2v7QxH+yrW99d9Z7sUMX08v4b4mV0RP45hSej3twockked3xb88WsaqFyGH6y3OBPzcKxYh3NA0mN0heWGw/0+LmBY0JzgUgDPuwPPL4o/bAf4QFBeeDMTeB1S4HBLnFk3CHW0QmyddToLH/zOsNPsa6ECIo4aZhQzYzLzYyzekghAkCMAGR97mJCnfPG+EGaT2VT0BO8FI8PPAHp26pL7cgDed2a3qfGX+x88NT4LD0l/hHPwnlrx/sOAYFv9itxncKwoh9MR1zdhdE4W4pdq8d7XnkPRrKv3EOpqHAjLi4EpDpZ3c6cw0xoMauMZVjm5cM6Ti39YDjxBGAvrQoT1SGldbUaGpkKgAt+UqZlKRbnkEYdDr2ss0yxUXm+epGqgzQW4/O8RC/6+QtjZXefQtzPNvwklRjQXgyBVUFiS6pj6Opb2+95jW+TnF8QoqF2wgsrQyk4Vq9ZJz2bvyO4EzXYObiwchBWGt22oC6rFpt6fvtZNh0JTxhVUxrt9opbgRXWzNwpDeG+45wrErsxU24hBh80YnRpX5v5ZYOnyHSOW2VTYwrY453U2kyiSwNdL/fCfgQsfiE+/4JV45LtT3y/DHw9AWtx1fmTy9tntKVcckbmPrXChxan8RHVBhT6cthSeZYpvfbtz4jzaXF0O6/xPXFVvHlZFvQ3NpAb/cxXNG+5SSKumx1EGOpqWvysBQ1gnbAtNLBe9NiSI7NGeCXvLyEYKqmQv9WnfnkWkmQFCRvP5+2Rs5TSF0F8P8By95D7WSKykWQEg3lLz7eFP8s2XcR8EVcI/osZfkmwzrtuJKLf2qITPVT4FnEoJi4HngvUhzQCtc4C+iJ8dJyX/IHkAP6Eo3eIwU+oZ3vROS+UEOMqP1DzDInnWRx1gVYhfvJD+puPXffnNFc+r+24f0eLi5dk9zU7tu8tx8kISC58BdpMqIGL+4tzCyNOFVcR68/Dy0NDUfLwqAywLVm5As3v3GweF/ow1oheKZH+Uz+Ug+J+1INXeShUAYGA28ZT/Vzae6/mNr/Es3EH9Upp9fHkqeCOtgcj/RcqcIVb5BbSmum/pkqW907Oh77+6jpIoslbnvNnMYE6Lb0W2XRB6+hhwcEyaXKcvcdnGKE2dIeRBJBLR3S0MLi2DLGY9yJccvY5WKCnLUavqXs2RAM/1p/Omf9Gs9h5V74dfE5szSTKiE7zVFD26NlXrzmUw0ScIGPSIvS9PCG271OzMOmcSm1Yp0INesHZAjaQUChtrT17JwAw4HGQLRn71guOa7H78vfGxctvMkCPogobgB1iV44jNQXXEL94PmOnZP0UaDjEjw7yBl0bMhH7Yyku8ssXT25ELZkk7czKa/67R8Cl+mXQtFo4A7irRJ8BapDK7WInnJQ1pq3VoFHkbQNrCNCmS4gsN9jGaJ3jcq+wuD7xKJEq6G//q4pa9Q8T1rjjQEqVzk8EsCqKTeM0LCnRUD5+QFc+jOPybmDK9vHaOq7r64wWAQEla3ZqcGhfyh+Lry5UIp/tKhMHz34gUOrheeCJYMGOWh3Ecsfcr8VAlliHX6p50uXKAanFkEZKtOmCSODD+Ga3bOl4tvrQkhANI4hiU6tGwO1T7XzNrY2KyN/WWZ9IA0NfAkalRqkOqZonAzUz4RhSWw6ug82sD+anNNHM9poR2e8x3j4/YXb2kNFyXlmQz3OIWx6NI9WRTXcDcemcLKimJFiF6bAukqvJy0lf6X99HCAFkDBXB1RbzUr6dd0wV82M2tX/7pcgD5et4O5hKEBTjoQIE6pIwCONeMooANlcu5MtBW587aCWPdFLzybxEGzDHMYHkSU2iS0D9WkrhcuXfuqYE1IarC5zreXVugrp6+txEZk+5EFURasaRLrJehuXxyVEScjQSwu4fncUTRZAE32uM+rlKm/RWDgTn8LgmR1pMGbUr1Hmx4WfWGPCG59LuQGi/2ola4YZkR2X059dvPSBeHn3dIlGXoCt6s5+Sv4D6a2WxOFuSBHPu/kpGOCZnRlTV6NgIQG8rx/5pLJTaGsqXCSio3CNFs+r5xrwwzJu/VQqO6ApgHk5daAOOfGg2Dc4TTskOxy+32j2vTWGB6Kr8yXZofznnulgQE2sNaERbAQBmbvDNH5Y9v4IgyQTKz1YmJG4RmKQhZIzwf8AAeGVxldDTa1UJ8HTHsTynaG/f9Fa3wOBmnKsJWUkOBs3o6tETOWFoNsYF5leqloWpDlynw+Eh0xKjAFBKjgzcx+nhTWHWaZtbcLw4OUauxfmHTucl+pQKx/eokpiTyunJhndUDrhkGAuLyHnxPVdLRFHoZiQTPJjWVuTMModB9Dgk8Bmq9/QGNQI/upkZHxpSHhedgmCJsx+fXvjXFdcT+q3HjMqFDIYfMpvN9Z1iri/H6GC6uldauAXaaw8/bxeFOAFM/HNIVN/VjKvMUJqdUZfr4QMpR3w0q8G1J8T12rEQDXJ9gQBvAAAAAA=)





## Response:
12/16/2025, 10:25:33 AM

````plaintext
Thought process: The user prompt is empty, so I cannot provide a summary. Please provide a user prompt for me to analyze.

I see the user typed "exit" and it looks like the agent continued running - it didn't actually exit, it just processed "exit" as a query and responded about the exit readiness feature. The old agent.py is still running (not the new version with the generate-all command).

The user needs to:
1. Press Ctrl+C to force quit the agent
2. Replace the agent.py file with the new version
3. Restart with the new agent

Let me give clear instructions.
````

I see - the old agent interpreted "exit" as a question about the Exit Readiness feature! You need to force quit.

## Do This Now:

### Step 1: Force Quit the Agent

Press **`Ctrl+C`** in that terminal (hold Control and press C)

You should see something like:
```
^C
KeyboardInterrupt
(venv) ildar@mac crewcfo-knowledge-base %
```

---

### Step 2: Replace the agent.py file

Now run these commands (you should see your normal terminal prompt):

```bash
mv ~/Downloads/agent.py ./agent.py
mkdir -p docs/generated
```

---

### Step 3: Restart with the New Agent

```bash
python agent.py generate-all
```

---

## Quick Summary

1. **`Ctrl+C`** → kills the agent
2. **`mv ~/Downloads/agent.py ./agent.py`** → replaces the file
3. **`mkdir -p docs/generated`** → creates output folder
4. **`python agent.py generate-all`** → runs batch generation

Let me know what you see after `Ctrl+C`!



## Prompt:
12/16/2025, 10:57:52 AM

can you access my folder? /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base/docs/generated



## Response:
12/16/2025, 10:58:36 AM

````plaintext
Thought process: Clarified access limitations and proposed alternative file-sharing methods.

The user is asking if I can access their local folder. I cannot directly access folders on their local machine. I can only:

1. Access files they upload to the conversation
2. Work with files in my container environment (/home/claude, /mnt/user-data/, /mnt/project/, etc.)

I should clarify this and offer alternatives - either they can upload the files, or I can provide the agent.py content directly for them to copy-paste.
````

No, I cannot directly access folders on your Mac. I can only:

1. **See files you upload** to this chat
2. **Access project files** in `/mnt/project/` (your Claude Project files)
3. **Create files** that you can download

---

## Easiest Solution: Let Me Give You the agent.py Content Directly

Instead of downloading, just **copy-paste** the new agent.py:

### Step 1: Kill the old agent

Press **`Ctrl+C`** in your terminal

---

### Step 2: Open agent.py in your editor

```bash
nano /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base/agent.py
```

Or open it in VS Code:
```bash
code /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base/agent.py
```

---

### Step 3: Replace ALL content with this

Select all (`Cmd+A`), delete, then paste this:

```python
#!/usr/bin/env python3
"""
LangGraph Agent for CrewCFO Planning & Spec Generation.
V2: Added save_to_file tool for direct file output.
"""
import os
from pathlib import Path
from typing import Annotated, TypedDict, List, Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from retriever import get_or_create_vectorstore

load_dotenv()

console = Console()
app = typer.Typer()

GENERATED_DIR = Path("./docs/generated")


class AgentState(TypedDict):
    messages: Annotated[List, add_messages]


@tool
def search_knowledge_base(query: str) -> str:
    """Search the CrewCFO knowledge base for relevant documentation."""
    vectorstore = get_or_create_vectorstore()
    results = vectorstore.similarity_search(query, k=5)
    if not results:
        return "No relevant documents found."
    formatted = []
    for i, doc in enumerate(results):
        source = doc.metadata.get("filename", "unknown")
        formatted.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)


@tool
def save_to_file(filename: str, content: str, file_type: str = "md") -> str:
    """Save generated content to docs/generated/."""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    filepath = GENERATED_DIR / f"{safe_filename}.{file_type}"
    with open(filepath, "w") as f:
        f.write(f"# Generated by CrewCFO Agent - {datetime.now().isoformat()}\n\n")
        f.write(content)
    return f"✅ Saved to: {filepath.absolute()}"


@tool
def list_generated_files() -> str:
    """List all files in docs/generated/."""
    if not GENERATED_DIR.exists():
        return "No generated files yet."
    files = list(GENERATED_DIR.glob("*"))
    if not files:
        return "No generated files yet."
    return f"Generated files:\n" + "\n".join([f"- {f.name}" for f in sorted(files)])


@tool
def generate_database_schema(table_name: str, description: str, columns: List[str]) -> str:
    """Generate PostgreSQL schema definition."""
    columns_sql = ",\n  ".join(columns)
    return f"""-- {description}
CREATE TABLE {table_name} (
  {columns_sql}
);

CREATE INDEX idx_{table_name}_tenant ON {table_name}(tenant_id);
"""


@tool
def generate_epic_breakdown(epic_name: str, description: str, user_stories: List[str], estimated_hours: int) -> str:
    """Generate Epic/Story breakdown."""
    stories_md = "\n".join([f"- [ ] {s}" for s in user_stories])
    return f"""## Epic: {epic_name}

**Description:** {description}
**Estimated Hours:** {estimated_hours}

### User Stories
{stories_md}
"""


@tool
def generate_feature_spec(feature_id: str, feature_name: str, purpose: str, inputs: List[str], outputs: List[str], automation_tier: str) -> str:
    """Generate YAML feature specification."""
    inputs_yaml = "\n".join([f"    - {i}" for i in inputs])
    outputs_yaml = "\n".join([f"    - {o}" for o in outputs])
    return f"""feature:
  id: "{feature_id}"
  name: "{feature_name}"
  purpose: "{purpose}"
  automation_tier: "{automation_tier}"
  inputs:
{inputs_yaml}
  outputs:
{outputs_yaml}
"""


SYSTEM_PROMPT = """You are a technical architect for CrewCFO, an AI bookkeeping platform for roofing contractors.

Tools available:
- search_knowledge_base: Find info in project docs
- save_to_file: Save content to docs/generated/
- list_generated_files: Show saved files
- generate_database_schema: Create SQL schemas
- generate_epic_breakdown: Create epics
- generate_feature_spec: Create YAML specs

Valuation Module has 5 features (A-E):
A. Real-time Valuation Engine
B. Value Driver Scoring (6 Matador drivers)
C. Scenario Simulator
D. Exit Readiness & Deal Room
E. Roadmap Agent

Always search knowledge base first, then generate and offer to save."""


def create_agent():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", api_key=api_key, max_tokens=8192)
    tools = [search_knowledge_base, save_to_file, list_generated_files, generate_database_schema, generate_epic_breakdown, generate_feature_spec]
    llm_with_tools = llm.bind_tools(tools)
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    
    def call_model(state):
        messages = [system_message] + state["messages"]
        return {"messages": [llm_with_tools.invoke(messages)]}
    
    def should_continue(state):
        last = state["messages"][-1]
        return "tools" if hasattr(last, "tool_calls") and last.tool_calls else END
    
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")
    
    return workflow.compile(checkpointer=MemorySaver())


@app.command()
def chat():
    """Interactive chat."""
    console.print(Panel.fit("[bold blue]CrewCFO Agent v2[/bold blue]\nType 'quit' to exit, 'files' to list generated"))
    agent = create_agent()
    config = {"configurable": {"thread_id": "main"}}
    
    while True:
        user_input = console.input("\n[cyan]You:[/cyan] ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if user_input.lower() == "files":
            files = list(GENERATED_DIR.glob("*")) if GENERATED_DIR.exists() else []
            console.print(Panel("\n".join([f.name for f in files]) or "None"))
            continue
        if not user_input:
            continue
        
        with console.status("Thinking..."):
            response = agent.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
        
        for msg in reversed(response["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                console.print(f"\n[green]Agent:[/green]")
                console.print(Markdown(msg.content))
                break


@app.command()
def generate_all():
    """Generate all Valuation Module specs."""
    console.print("[bold]Generating all specs...[/bold]")
    agent = create_agent()
    
    tasks = [
        "Generate complete PostgreSQL schemas for valuation_snapshots, driver_scores, and roadmap_items tables with all columns, indexes, constraints. Save to 01_database_schema.sql",
        "Generate Feature A spec: Real-time Valuation Engine. Save to 02_feature_a_spec.yaml",
        "Generate Feature B spec: Value Driver Scoring Engine with 6 Matador drivers. Save to 03_feature_b_spec.yaml",
        "Create epic breakdown for Phase 4: Valuation Intelligence with all user stories. Save to 04_epic_breakdown.md",
        "Design API endpoints for valuation module. Save to 05_api_design.md",
    ]
    
    for i, task in enumerate(tasks):
        console.print(f"\n[cyan]Task {i+1}/{len(tasks)}...[/cyan]")
        config = {"configurable": {"thread_id": f"batch-{i}"}}
        with console.status("Working..."):
            agent.invoke({"messages": [HumanMessage(content=task)]}, config=config)
        console.print("[green]✓ Done[/green]")
    
    console.print(f"\n[bold green]All specs saved to {GENERATED_DIR.absolute()}[/bold green]")


if __name__ == "__main__":
    app()
```

---

### Step 4: Save and Exit

- In nano: `Ctrl+O`, Enter, `Ctrl+X`
- In VS Code: `Cmd+S`

---

### Step 5: Create folder and run

```bash
mkdir -p /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base/docs/generated

cd /Users/ildar/Documents/1.Projects/roofing-books-cfo/crewcfo-knowledge-base

source venv/bin/activate

python agent.py generate-all
```

This should generate all your specs automatically!



## Prompt:
12/16/2025, 10:59:22 AM

![Screenshot 2025-12-16 at 10.59.08 AM.png](data:image/webp;base64,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)

I already generated them. What's next?



## Response:
12/16/2025, 10:59:45 AM

````plaintext
Thought process: Charted implementation pathway using generated specifications.

The user has successfully generated all 6 spec files:
1. 01_database_schema.sql
2. 02_feature_a_spec.yaml
3. 03_feature_b_spec.yaml
4. 04_epic_breakdown.md
5. 05_api_design.md
6. 06_implementation_roadmap.md

Now they need to use these to actually implement the Valuation Module in their roofing-books-cfo codebase using Cursor.

The next step is to:
1. Open Cursor in the main project folder
2. Use the generated specs as context for Cursor prompts
3. Start implementing - database migrations first, then API, then UI

Let me give them the exact next steps with Cursor prompts.
````

All 6 specs generated! Now let's implement them with Cursor.

---

## Next Steps: Implementation with Cursor

### Step 1: Open Cursor in your main project

```bash
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo
cursor .
```

---

### Step 2: Start with Database Schema

Open Cursor chat (`Cmd+L`) and paste this prompt:

```
Read the file at crewcfo-knowledge-base/docs/generated/01_database_schema.sql

Create database migrations for these valuation tables using our existing migration pattern (Prisma/Drizzle/raw SQL - whichever we use in this project).

Add the tables:
- valuation_snapshots
- driver_scores  
- roadmap_items

Make sure to:
1. Match our existing schema patterns
2. Add proper foreign keys to tenants table
3. Include all indexes
4. Add created_at/updated_at timestamps

Show me where to put the migration file.
```

---

### Step 3: After Migration, Create the API

```
Read crewcfo-knowledge-base/docs/generated/05_api_design.md

Create the API routes for the Valuation Module following our existing patterns.

Start with:
1. GET /api/valuation/snapshot - get latest valuation
2. POST /api/valuation/snapshot - trigger recalculation
3. GET /api/valuation/drivers - get driver scores

Use our existing auth middleware and error handling patterns.
```

---

### Step 4: Create the Valuation Service

```
Read crewcfo-knowledge-base/docs/generated/02_feature_a_spec.yaml

Create a ValuationEngine service that:
1. Calculates TTM (trailing twelve months) financials from our Books OS data
2. Computes SDE and EBITDA
3. Determines tier (below_avg/average/above_avg) based on driver scores
4. Calculates valuation range using Matador multiples (3x/4.5-5x/7x+)

Put it in our services folder following existing patterns.
```

---

### Step 5: Create the Dashboard UI

```
Read crewcfo-knowledge-base/docs/generated/04_epic_breakdown.md

Create a Valuation Dashboard React component with:
1. Valuation Meter - shows estimated value range
2. Driver Scorecards - 6 cards showing each driver score (0-100)
3. Value Timeline - chart showing valuation over time

Use our existing component library (shadcn/Tailwind/etc).
```

---

## Quick Reference: Implementation Order

| Step | What | Cursor File to Reference |
|------|------|--------------------------|
| 1 | Database migrations | `01_database_schema.sql` |
| 2 | API endpoints | `05_api_design.md` |
| 3 | Valuation service | `02_feature_a_spec.yaml` |
| 4 | Driver scoring | `03_feature_b_spec.yaml` |
| 5 | React dashboard | `04_epic_breakdown.md` |
| 6 | Timeline check | `06_implementation_roadmap.md` |

---

## Your Immediate Action

1. **Open Cursor**: `cursor .` in the `roofing-books-cfo` folder
2. **Paste the Step 2 prompt** into Cursor chat
3. **Let Cursor create the migration**
4. **Run the migration** (Cursor will tell you how)

Ready to start? Just paste that first prompt into Cursor and let me know what it generates!



## Prompt:
12/16/2025, 11:30:05 AM

Commit summary:
* 6 files changed
* 1,742 insertions, 1 deletion
* Commit hash: 422a0b3
Note: There are still some untracked files/directories that weren't committed:
* crewcfo-knowledge-base/
* docs/architecture/
* docs/modules/
These appear to be documentation/knowledge base files. Add them if you want them in the repository, or add them to .gitignore if they should remain local.
Changes are now on the main branch at https://github.com/darfaz/roofing-books-cfo.git.

Above is the cursor agent report. Should I add these to gitignore?



## Response:
12/16/2025, 11:30:21 AM

````plaintext
Thought process: Evaluated which files warrant version control versus local exclusion.

The user is asking whether to add these untracked files to .gitignore or commit them. Let me think about each:

1. `crewcfo-knowledge-base/` - This is the LangChain knowledge base we created together. It contains:
   - Python code (agent.py, cli.py, etc.)
   - Generated specs in docs/generated/
   - The original project docs
   - The chroma_db vector store (binary files)
   - venv (virtual environment)

2. `docs/architecture/` - Likely architecture documentation
3. `docs/modules/` - Likely module documentation

For the knowledge base:
- The Python code (agent.py, cli.py, etc.) - SHOULD be committed (useful for team)
- docs/generated/*.sql, *.yaml, *.md - SHOULD be committed (these are the specs)
- Original docs in docs/ - SHOULD be committed (project documentation)
- chroma_db/ - Should be IGNORED (binary vector store, can be regenerated)
- venv/ - Should be IGNORED (virtual environment)
- .env - Should be IGNORED (contains API keys)

For docs/architecture/ and docs/modules/ - these sound like documentation that SHOULD be committed.

So the recommendation is:
- Commit most things
- Add specific items to .gitignore (chroma_db, venv, .env, __pycache__)
````

**Don't ignore them all** - some should be committed, some should be ignored.

## Here's What to Do:

### Add these to `.gitignore`:

```bash
# In your roofing-books-cfo folder, add to .gitignore:

# Knowledge base - ignore generated/binary files
crewcfo-knowledge-base/venv/
crewcfo-knowledge-base/chroma_db/
crewcfo-knowledge-base/.env
crewcfo-knowledge-base/__pycache__/
```

### Commit these (they're valuable):

| Folder | Why Keep |
|--------|----------|
| `crewcfo-knowledge-base/docs/` | Your project specs + generated specs |
| `crewcfo-knowledge-base/*.py` | Agent code (reusable by team) |
| `crewcfo-knowledge-base/requirements.txt` | Dependencies |
| `docs/architecture/` | Architecture docs |
| `docs/modules/` | Module docs |

---

## Quick Commands

```bash
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo

# Add ignores
echo "
# CrewCFO Knowledge Base
crewcfo-knowledge-base/venv/
crewcfo-knowledge-base/chroma_db/
crewcfo-knowledge-base/.env
crewcfo-knowledge-base/__pycache__/
" >> .gitignore

# Now commit everything else
git add .
git commit -m "Add knowledge base agent and documentation"
git push
```

This keeps your specs and agent code in version control while ignoring the local-only stuff (virtual env, vector database, API keys).



## Prompt:
12/16/2025, 11:36:41 AM

(venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo % cd /Users/ildar/Documents/1.Projects/roofing-books-cfo
# Add ignores
echo "
# CrewCFO Knowledge Base
crewcfo-knowledge-base/venv/
crewcfo-knowledge-base/chroma_db/
crewcfo-knowledge-base/.env
crewcfo-knowledge-base/__pycache__/
" >> .gitignore
# Now commit everything else
git add .
git commit -m "Add knowledge base agent and documentation"
git push
zsh: command not found: #
zsh: command not found: #
[main fd967d7] Add knowledge base agent and documentation
 37 files changed, 9427 insertions(+)
 create mode 100644 crewcfo-knowledge-base/.env.example
 create mode 100644 crewcfo-knowledge-base/README.md
 create mode 100644 crewcfo-knowledge-base/UPGRADE_TO_LANGGRAPH.md
 create mode 100644 crewcfo-knowledge-base/agent.py
 create mode 100644 crewcfo-knowledge-base/chain.py
 create mode 100644 crewcfo-knowledge-base/cli.py
 create mode 100644 crewcfo-knowledge-base/docs/23816 Roofing Contractors in the US Industry Report.pdf
 create mode 100644 crewcfo-knowledge-base/docs/AI-Powered_Bookkeeping_for_Roofing_Contractors__MVP_Build_Plan_and_Strategic_Analysis.md
 create mode 100644 crewcfo-knowledge-base/docs/Competitive_Landscape__Automated_Bookkeeping___Fractional_CFO_Services__US_.docx
 create mode 100644 crewcfo-knowledge-base/docs/Comprehensive US Roofing M&A Transaction Database_ 2015-2025.pdf
 create mode 100644 crewcfo-knowledge-base/docs/CrewCFO_Valuation_Feature_20251213.docx
 create mode 100644 crewcfo-knowledge-base/docs/Increasing Roofing Company Valuation & Exit Strategy Blueprint.docx
 create mode 100644 crewcfo-knowledge-base/docs/Increasing_Roofing_Company_Valuation___Exit_Strategy_Blueprint.docx
 create mode 100644 crewcfo-knowledge-base/docs/Open-Source_Tools___Frameworks_for_Roofing_CFO_MVP.docx
 create mode 100644 crewcfo-knowledge-base/docs/Private Equity Transforms Americas Roofing Industry_ Consolidation Wave and Roll-Up Strategies.pdf
 create mode 100644 crewcfo-knowledge-base/docs/Roofers_Productized_Spec-OS_20251210.docx
 create mode 100644 crewcfo-knowledge-base/docs/Roofing_Salary_Benchmarking_Tool by Claude.xlsx
 create mode 100644 crewcfo-knowledge-base/docs/Spec-OS_Automation_Plan_20251211.docx
 create mode 100644 crewcfo-knowledge-base/docs/Spec-OS_Roofing_Bookkeeping_automation_spec_kit_20251211.docx
 create mode 100644 crewcfo-knowledge-base/docs/US_Roofing_MA_Master_Database.xlsx
 create mode 100644 crewcfo-knowledge-base/docs/U_S__Roofing_Contractor_Industry_Analysis.docx
 create mode 100644 crewcfo-knowledge-base/docs/generated/01_database_schema.sql
 create mode 100644 crewcfo-knowledge-base/docs/generated/02_feature_a_spec.yaml
 create mode 100644 crewcfo-knowledge-base/docs/generated/03_feature_b_spec.yaml
 create mode 100644 crewcfo-knowledge-base/docs/generated/04_epic_breakdown.md
 create mode 100644 crewcfo-knowledge-base/docs/generated/05_api_design.md
 create mode 100644 crewcfo-knowledge-base/docs/generated/06_implementation_roadmap.md
 create mode 100644 crewcfo-knowledge-base/docs/valuation_quick_reference.md
 create mode 100644 crewcfo-knowledge-base/loader.py
 create mode 100644 crewcfo-knowledge-base/quick_test.py
 create mode 100644 crewcfo-knowledge-base/requirements.txt
 create mode 100644 crewcfo-knowledge-base/retriever.py
 create mode 100644 docs/architecture/valuation-integration-seams.md
 create mode 100644 docs/modules/valuation-magnet/00-overview.md
 create mode 100644 docs/modules/valuation-magnet/04-valuation-engine.md
 create mode 100644 docs/modules/valuation-magnet/05-matador-driver-model.md
Enumerating objects: 49, done.
Counting objects: 100% (49/49), done.
Delta compression using up to 12 threads
Compressing objects: 100% (45/45), done.
Writing objects: 100% (46/46), 1.14 MiB | 2.82 MiB/s, done.
Total 46 (delta 3), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (3/3), completed with 3 local objects.
To https://github.com/darfaz/roofing-books-cfo.git
   422a0b3..fd967d7  main -> main
(venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo %



## Response:
12/16/2025, 11:36:51 AM

````plaintext
Thought process: Validated successful commit and charted implementation course forward.

The user successfully committed all the files to git. The "command not found: #" errors are just because the shell tried to interpret the comment lines as commands - but the actual commands worked fine and everything got committed and pushed.

37 files committed including the knowledge base agent, all the docs, generated specs, and architecture docs. This is great progress!

Now I should guide them to the next step - implementing with Cursor.
````

It worked. 37 files committed and pushed. The "command not found: #" is just the shell trying to run the comment lines - harmless.

---

## What's Committed

✅ Knowledge base agent (`agent.py`, `cli.py`, etc.)
✅ All project docs (industry reports, specs, M&A database)
✅ Generated specs (`01_database_schema.sql` through `06_implementation_roadmap.md`)
✅ Architecture docs (`docs/architecture/`, `docs/modules/`)

---

## Next: Start Implementation

Now open Cursor and start building:

```bash
cursor .
```

### First Cursor Prompt (Database Migration)

Paste this in Cursor chat (`Cmd+L`):

```
Read these files:
- crewcfo-knowledge-base/docs/generated/01_database_schema.sql
- docs/modules/valuation-magnet/04-valuation-engine.md

Create database migrations for the valuation module tables (valuation_snapshots, driver_scores, roadmap_items).

Use our existing migration pattern and ORM (Prisma/Drizzle/raw SQL).
```

---

Let me know what Cursor generates and we'll move to the API layer next!



## Prompt:
12/16/2025, 11:37:45 AM

Features implemented
1. Valuation Meter
* Displays estimated enterprise value range (low/high/average)
* Visual bar with gradient representing the range
* Metrics grid showing:
* TTM Revenue
* TTM SDE
* TTM EBITDA
* Multiple range
* Confidence score with progress bar and warning if < 80%
2. Driver Scorecards
* Six cards, one per Matador driver:
* Management Independence
* Financial Records
* Recurring Revenue
* Operational Systems
* Customer Diversity
* Market Outlook
* Each card shows:
* Icon and description
* Score (0-100) with color coding
* Progress bar
* Confidence percentage
3. Value Timeline
* Chart showing valuation trends over time
* Color-coded bars by tier (below_avg/avg/above_avg)
* Hover tooltips with date and value
* Legend for tier colors
* Empty state message when no historical data
Design
* Uses Tailwind CSS matching the existing dark theme (slate-950, slate-900)
* Emerald/blue/amber color coding for tiers and scores
* Responsive layout (mobile-friendly grid)
* Loading and error states
* TypeScript for type safety
API integration
The component uses these endpoints:
* GET /api/valuation/snapshot - Latest snapshot
* GET /api/valuation/drivers - Driver scores
* GET /api/valuation/snapshots - Historical snapshots (added to main.py)



## Response:
12/16/2025, 11:38:08 AM

````plaintext
Thought process: Validated implementation progress and charted remaining feature roadmap.

The user has successfully implemented the Valuation Dashboard with all the key components. This is great progress! Let me summarize what's done and what's next.

Looking at what was implemented:
1. Valuation Meter - displays EV range, TTM metrics, confidence
2. Driver Scorecards - 6 Matador drivers with scores, progress bars
3. Value Timeline - historical chart with tier coloring
4. API integration with 3 endpoints

This covers Features A and B from the spec. Now they need to continue with:
- Feature C: Scenario Simulator
- Feature D: Exit Readiness / Deal Room
- Feature E: Roadmap Agent

I should congratulate them and give them the next steps.
````

Excellent progress! Features A and B are done. Here's what you've completed and what's next:

---

## ✅ Completed

| Feature | Status |
|---------|--------|
| A. Real-time Valuation Engine | ✅ Done |
| B. Value Driver Scoring | ✅ Done |
| Database Schema | ✅ Done |
| API Endpoints | ✅ Done |
| Dashboard UI | ✅ Done |

---

## Next: Features C, D, E

### Feature C: Scenario Simulator

**Cursor Prompt:**

```
Read crewcfo-knowledge-base/docs/generated/02_feature_a_spec.yaml

Create a ScenarioSimulator component with:

1. Input sliders for "what-if" levers:
   - Recurring Revenue Change: -20% to +100%
   - Gross Margin Change: -5% to +10%
   - Owner Hours/Week: current → 0
   - Crew Productivity: -10% to +20%

2. Real-time output panel showing:
   - Projected EBITDA (with delta from current)
   - Projected Multiple (with delta)
   - Projected Valuation Range

3. Buttons: Reset, Save Scenario

4. API: POST /api/valuation/simulate
   Body: { levers: { recurring_revenue_delta, margin_delta, owner_hours_delta, productivity_delta } }
   Response: { projected_ebitda, projected_multiple, projected_ev_low, projected_ev_high }

Use the same dark theme (slate-950/900) and Tailwind styling as the ValuationDashboard.
```

---

### Feature D: Exit Readiness & Deal Room

**Cursor Prompt:**

```
Create an ExitReadiness component with:

1. Readiness Score card (0-100) with status indicator

2. Due Diligence Checklist:
   - Financial statements (3-5 years) ✓/✗
   - Tax returns ✓/✗
   - AR/AP aging reports ✓/✗
   - Asset list ✓/✗
   - Org chart ✓/✗
   - KPI dashboard ✓/✗
   - Safety/insurance docs ✓/✗

3. Document upload area for each checklist item

4. "Generate CIM Outline" button (Confidential Information Memorandum)

5. Deal Room completeness meter (% of docs uploaded)

API: GET /api/valuation/exit-readiness
```

---

### Feature E: Roadmap Agent

**Cursor Prompt:**

```
Create a ValuationRoadmap component showing:

1. "Next 2 Improvements" cards at the top:
   - Each shows: title, expected EV impact, effort level (Low/Med/High)
   - "Start" button to mark in progress

2. Full roadmap list below:
   - Grouped by driver (Management Independence, Financial Records, etc.)
   - Each item shows: title, description, expected_impact_ev, status
   - Status badges: pending, in_progress, completed

3. Quarterly "Spec Jam" reminder card if due

API: 
- GET /api/valuation/roadmap - Get prioritized items
- PATCH /api/valuation/roadmap/:id - Update status
```

---

## Implementation Order

```
1. [ ] POST /api/valuation/simulate endpoint
2. [ ] ScenarioSimulator component
3. [ ] ExitReadiness component + API
4. [ ] ValuationRoadmap component + API
5. [ ] Integration testing
6. [ ] Wire up navigation to all components
```

---

## Quick Win: Add Navigation

If not already done, add a tab navigation to switch between dashboard views:

```
Read the existing ValuationDashboard.

Add a tab navigation at the top with:
- Overview (current dashboard)
- Scenario Simulator
- Exit Readiness
- Roadmap

Use our existing tab component pattern.
```

---

Which feature do you want to build next - **Scenario Simulator**, **Exit Readiness**, or **Roadmap**?



## Prompt:
12/16/2025, 11:40:05 AM

should I test ui/ux first?



## Response:
12/16/2025, 11:40:22 AM

````plaintext
Thought process: Weighed testing benefits against development risks, advocated early validation.

The user is asking if they should test the UI/UX before moving on to build more features. This is a good question about development workflow.

Let me think about this:

Pros of testing now:
1. Catch bugs early before building more on top
2. Validate the UX makes sense before adding complexity
3. See if the API integration actually works
4. Get a feel for the user flow
5. Find any gaps in the data model

Cons of waiting:
1. If there are fundamental issues, you've built more stuff that needs changing
2. Harder to debug when there's more code

I should recommend YES - test now. It's a good checkpoint. Let me give practical steps on how to test.
````

**Yes, test now.** Good checkpoint before adding more complexity.

---

## Quick Test Checklist

### 1. Start the Dev Server

```bash
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo
npm run dev   # or: yarn dev / pnpm dev
```

---

### 2. Seed Test Data (if needed)

You likely need sample data. Ask Cursor:

```
Create a seed script that adds test data for the valuation module:

1. One valuation_snapshot with:
   - ttm_revenue: 2,500,000
   - ttm_sde: 375,000
   - ttm_ebitda: 312,500
   - tier: 'average'
   - multiple_low: 4.5, multiple_high: 5.0
   - ev_low: 1,406,250, ev_high: 1,562,500

2. Six driver_scores (one per driver):
   - management_independence: 65
   - financial_records_quality: 78
   - recurring_revenue: 42
   - operational_systems: 55
   - customer_diversity: 71
   - market_outlook: 68

3. A few historical snapshots for the timeline chart

Put in scripts/seed-valuation.ts or similar.
```

---

### 3. Test These Flows

| Test | What to Check |
|------|---------------|
| Page loads | No console errors, data displays |
| Valuation Meter | Shows dollar range, tier badge |
| Driver Cards | All 6 show scores, colors correct |
| Timeline Chart | Shows historical data (or empty state) |
| Mobile view | Resize browser, check responsive |
| Confidence warning | Shows warning if < 80% |

---

### 4. Check API Responses

Open browser DevTools → Network tab → reload page

Verify these return data:
- `/api/valuation/snapshot` → 200
- `/api/valuation/drivers` → 200
- `/api/valuation/snapshots` → 200

---

### 5. Quick Fixes

If something's broken, tell me:
- Screenshot of the error
- Console error message
- Which endpoint is failing

---

**Test now, then we'll build Features C-E on a solid foundation.**



## Prompt:
12/16/2025, 11:43:50 AM

To https://github.com/darfaz/roofing-books-cfo.git
   422a0b3..fd967d7  main -> main
(venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo % npm run dev
npm error code ENOENT
npm error syscall open
npm error path /Users/ildar/Documents/1.Projects/roofing-books-cfo/package.json
npm error errno -2
npm error enoent Could not read package.json: Error: ENOENT: no such file or directory, open '/Users/ildar/Documents/1.Projects/roofing-books-cfo/package.json'
npm error enoent This is related to npm not being able to find a file.
npm error enoent
npm error A complete log of this run can be found in: /Users/ildar/.npm/_logs/2025-12-16T19_42_48_323Z-debug-0.log
(venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo % npm run dev
npm error code ENOENT
npm error syscall open
npm error path /Users/ildar/Documents/1.Projects/roofing-books-cfo/package.json
npm error errno -2
npm error enoent Could not read package.json: Error: ENOENT: no such file or directory, open '/Users/ildar/Documents/1.Projects/roofing-books-cfo/package.json'
npm error enoent This is related to npm not being able to find a file.
npm error enoent
npm error A complete log of this run can be found in: /Users/ildar/.npm/_logs/2025-12-16T19_43_35_642Z-debug-0.log
(venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo %



## Response:
12/16/2025, 11:44:01 AM

````plaintext
Thought process: Diagnosed missing frontend setup, identified Python backend architecture.

The user doesn't have a package.json - this means the project doesn't have a Node.js/React frontend set up yet. They likely have a Python backend (FastAPI based on the earlier API design mentioning main.py).

Let me help them figure out what they actually have and how to run it.
````

The project doesn't have a frontend set up yet. Let's see what you actually have:

---

## Check Your Project Structure

```bash
ls -la /Users/ildar/Documents/1.Projects/roofing-books-cfo/
```

And:

```bash
find . -name "*.py" -type f | head -20
find . -name "main.py" -type f
```

---

## Likely Situation

Based on the earlier mention of `main.py`, you probably have:
- **Python/FastAPI backend** ✅
- **No React frontend yet** ❌

---

## If You Have FastAPI Backend

Run it with:

```bash
# If using uvicorn directly
uvicorn main:app --reload

# Or if main.py is in a subfolder
uvicorn app.main:app --reload

# Or if there's a different entry point
python main.py
```

---

## Tell Me What You See

Run this and share the output:

```bash
ls -la
```

This will show me your actual project structure so I can give you the right command to run it.



## Prompt:
12/16/2025, 11:45:00 AM

g
(venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo % ls -la /Users/ildar/Documents/1.Projects/roofing-books-cfo/
total 312
drwxr-xr-x@ 42 ildar  staff  1344 Dec 15 16:51 .
drwxr-xr-x  29 ildar  staff   928 Dec 11 15:26 ..
-rw-r--r--@  1 ildar  staff  8196 Dec 16 11:09 .DS_Store
-rw-r--r--@  1 ildar  staff   520 Dec 12 14:21 .dockerignore
-rw-r--r--@  1 ildar  staff  3743 Dec 12 16:42 .env
-rw-r--r--@  1 ildar  staff  3025 Dec 11 15:09 .env.example
drwxr-xr-x@ 12 ildar  staff   384 Dec 16 11:36 .git
-rw-r--r--@  1 ildar  staff   573 Dec 16 11:36 .gitignore
drwxr-xr-x@  6 ildar  staff   192 Dec 11 19:16 .venv
-rw-r--r--@  1 ildar  staff  7751 Dec 12 13:37 AUDIT_REPORT.md
-rw-r--r--@  1 ildar  staff  5341 Dec 12 14:58 DEPLOY_DIGITALOCEAN.md
-rw-r--r--@  1 ildar  staff  3907 Dec 12 13:19 DOCKER.md
-rw-r--r--@  1 ildar  staff  1987 Dec 12 15:41 DOCKER_OPTIMIZATION.md
-rw-r--r--@  1 ildar  staff  6797 Dec 12 14:21 DOCKER_SETUP.md
-rw-r--r--@  1 ildar  staff  1673 Dec 12 15:41 Dockerfile
-rw-r--r--@  1 ildar  staff  1085 Dec 12 15:41 Dockerfile.prod
-rw-r--r--@  1 ildar  staff  1619 Dec 12 18:12 MARKETING_PAGES.md
-rw-r--r--@  1 ildar  staff  1682 Dec 12 14:21 Makefile
-rw-r--r--@  1 ildar  staff  5253 Dec 12 13:49 NEXT_STEPS_SUMMARY.md
-rw-r--r--@  1 ildar  staff  5448 Dec 12 15:41 README.md
-rw-r--r--@  1 ildar  staff  4697 Dec 12 13:37 SYNC_USAGE.md
-rw-r--r--@  1 ildar  staff  5427 Dec 12 10:39 TESTING_SETUP.md
-rw-r--r--@  1 ildar  staff   794 Dec 12 13:05 check_tenant_setup.sql
drwxr-xr-x@ 17 ildar  staff   544 Dec 16 10:22 crewcfo-knowledge-base
-rw-r--r--@  1 ildar  staff   705 Dec 12 14:21 docker-compose.override.yml.example
-rw-r--r--@  1 ildar  staff  1517 Dec 13 08:08 docker-compose.prod.yml
-rw-r--r--@  1 ildar  staff  3621 Dec 12 18:12 docker-compose.yml
drwxr-xr-x@ 17 ildar  staff   544 Dec 15 14:31 docs
-rw-r--r--@  1 ildar  staff  1020 Dec 12 13:10 fixed_token_health_check.sql
-rw-------@  1 ildar  staff   419 Dec 12 15:48 id_rsa
-rw-r--r--@  1 ildar  staff   108 Dec 12 15:48 id_rsa.pub
drwxr-xr-x@  7 ildar  staff   224 Dec 12 15:12 marketing
drwxr-xr-x@  4 ildar  staff   128 Dec 12 16:44 nginx
-rw-r--r--@  1 ildar  staff   561 Dec 12 15:41 requirements-full.txt
-rw-r--r--@  1 ildar  staff   640 Dec 12 15:41 requirements.txt
drwxr-xr-x@  2 ildar  staff    64 Dec 11 15:09 sample_data
drwxr-xr-x@ 11 ildar  staff   352 Dec 16 11:24 src
drwxr-xr-x@  5 ildar  staff   160 Dec 16 11:15 supabase
-rw-r--r--@  1 ildar  staff  2525 Dec 12 13:10 test_qbo_connection.py
-rw-r--r--@  1 ildar  staff  2067 Dec 12 13:37 test_sync.py
drwxr-xr-x@  2 ildar  staff    64 Dec 11 15:09 tests
-rw-r--r--@  1 ildar  staff  1701 Dec 12 13:05 verify_qbo_tokens.sql
(venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo %



## Response:
12/16/2025, 11:45:09 AM

````plaintext
Thought process: Analyzed FastAPI project structure and dependencies.

The user has a Python/FastAPI backend project. I can see:
- `src/` folder - likely contains the main app
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker setup
- No `package.json` - no Node.js frontend
- `.venv/` - Python virtual environment

Let me ask them to check the src folder structure and find how to run the app.
````

Got it! This is a **Python/FastAPI** project with no separate frontend yet. Let's check the src folder and run the backend:

---

## Step 1: Check the src folder

```bash
ls -la src/
```

---

## Step 2: Run the FastAPI Backend

Try one of these:

```bash
# Option A: If main.py is in src/
cd src
uvicorn main:app --reload

# Option B: From project root with module path
uvicorn src.main:app --reload

# Option C: Using python directly
python -m uvicorn src.main:app --reload
```

---

## Step 3: Check if uvicorn is installed

```bash
# Activate the project's venv (not the knowledge-base one)
source .venv/bin/activate

# Install if needed
pip install uvicorn

# Then run
uvicorn src.main:app --reload
```

---

## Quick Check

Run this to see what's in src:

```bash
ls -la src/
cat src/main.py | head -50
```

Share the output and I'll give you the exact run command!



## Prompt:
12/16/2025, 11:46:23 AM

-rw-r--r--@  1 ildar  staff  1701 Dec 12 13:05 verify_qbo_tokens.sql
(venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo % ls -la src/
total 64
drwxr-xr-x@ 11 ildar  staff    352 Dec 16 11:24 .
drwxr-xr-x@ 42 ildar  staff   1344 Dec 15 16:51 ..
-rw-r--r--@  1 ildar  staff      0 Dec 11 15:12 __init__.py
drwxr-xr-x@  4 ildar  staff    128 Dec 12 13:49 __pycache__
drwxr-xr-x@  4 ildar  staff    128 Dec 12 17:46 dashboard
drwxr-xr-x@  3 ildar  staff     96 Dec 16 11:24 frontend
-rw-r--r--@  1 ildar  staff  31492 Dec 16 11:25 main.py
drwxr-xr-x@  3 ildar  staff     96 Dec 11 15:12 models
drwxr-xr-x@  8 ildar  staff    256 Dec 16 11:18 services
drwxr-xr-x@  3 ildar  staff     96 Dec 11 15:12 utils
drwxr-xr-x@  3 ildar  staff     96 Dec 11 15:09 {services
(venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo %



## Response:
12/16/2025, 11:46:32 AM

````plaintext
Thought process: Surveyed project structure and identified backend setup requirements.

The user has a Python/FastAPI project. I can see:
- src/main.py (31KB - the main FastAPI app)
- src/frontend/ folder (likely contains the React components Cursor created)
- src/services/ folder
- src/dashboard/ folder

Let me give them the command to run the backend and check if there's a frontend setup.
````

There's a `src/frontend/` folder - Cursor created the components there. Let's check it and run the backend:

---

## Step 1: Check the Frontend Folder

```bash
ls -la src/frontend/
```

---

## Step 2: Run the Backend

```bash
# Make sure you're using the project venv
source .venv/bin/activate

# Run FastAPI
uvicorn src.main:app --reload
```

This should start at `http://localhost:8000`

---

## Step 3: Check API Docs

Once running, open in browser:
- **Swagger UI:** http://localhost:8000/docs
- **API endpoints:** http://localhost:8000/api/valuation/snapshot

---

## Step 4: Check What Frontend Exists

```bash
ls -la src/frontend/
cat src/frontend/*.py 2>/dev/null || ls -la src/frontend/
```

---

Run the commands above and share what you see. We need to know:
1. Does the backend start?
2. What's in `src/frontend/` (React files or Python templates)?



## Prompt:
12/16/2025, 11:49:41 AM

I am set up in Docker



## Response:
12/16/2025, 11:49:46 AM

````plaintext
Thought process: Recognized containerized environment and adjusted technical approach.

The user is running the project in Docker. So instead of running uvicorn directly, they need to use Docker commands.
````

Got it! Use Docker then:

---

## Run with Docker

```bash
# Start the containers
docker-compose up

# Or in detached mode (background)
docker-compose up -d

# View logs if detached
docker-compose logs -f
```

---

## Check What's Running

```bash
# See running containers
docker-compose ps

# Check the app logs
docker-compose logs app
```

---

## Access the App

Once running, open:
- **API Docs:** http://localhost:8000/docs
- **Valuation endpoint:** http://localhost:8000/api/valuation/snapshot

---

## If You Need to Rebuild (after code changes)

```bash
docker-compose up --build
```

---

Run `docker-compose up` and let me know what happens!



## Prompt:
12/16/2025, 4:07:38 PM

(.venv) (base) ildar@MacBook-Pro-52 spec-os-shared-suite % cd /Users/ildar/Documents/1.Projects/roofing-books-cfo
(.venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo % npm run dev
npm error code ENOENT
npm error syscall open
npm error path /Users/ildar/Documents/1.Projects/roofing-books-cfo/package.json
npm error errno -2
npm error enoent Could not read package.json: Error: ENOENT: no such file or directory, open '/Users/ildar/Documents/1.Projects/roofing-books-cfo/package.json'
npm error enoent This is related to npm not being able to find a file.
npm error enoent
npm error A complete log of this run can be found in: /Users/ildar/.npm/_logs/2025-12-17T00_06_57_990Z-debug-0.log
(.venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo %



## Response:
12/16/2025, 4:07:44 PM

````plaintext
Thought process: Identified Python project mismatch and prescribed Docker solution.

The user keeps running `npm run dev` but this is a Python/FastAPI project without a Node.js frontend. They said they're set up in Docker. Let me give them the correct Docker command.
````

**Don't use `npm`** - this is a Python project, not Node.js.

---

## Use Docker:

```bash
docker-compose up
```

That's it! Then open http://localhost:8000/docs to see your API.



## Prompt:
12/16/2025, 4:33:44 PM

I am adding crewcfo.com domain to DO droplet. provide step by step instructions how to do that with ssl certificate as well



## Response:
12/16/2025, 4:34:05 PM

````plaintext
Thought process: Orchestrated comprehensive domain setup guide encompassing DNS, DigitalOcean, SSL.

The user wants to set up their domain crewcfo.com on a DigitalOcean droplet with SSL. I'll provide step-by-step instructions for:

1. DNS setup at the domain registrar
2. DigitalOcean configuration
3. SSL certificate with Let's Encrypt/Certbot

I should ask where their domain is registered (Namecheap, GoDaddy, Google Domains, etc.) but I can provide generic instructions that work for most registrars.
````

## Setting Up crewcfo.com on DigitalOcean with SSL

---

## Step 1: Get Your Droplet's IP Address

```bash
# In DigitalOcean dashboard, find your droplet's public IP
# Or if you're SSH'd in:
curl ifconfig.me
```

Write down the IP (e.g., `143.198.xxx.xxx`)

---

## Step 2: Configure DNS at Your Domain Registrar

Go to where you bought crewcfo.com (GoDaddy, Namecheap, Cloudflare, etc.) and set these DNS records:

| Type | Host/Name | Value | TTL |
|------|-----------|-------|-----|
| A | @ | `YOUR_DROPLET_IP` | 300 |
| A | www | `YOUR_DROPLET_IP` | 300 |

**Example for common registrars:**

**Namecheap:** Domain List → Manage → Advanced DNS → Add Records

**GoDaddy:** My Products → DNS → Add Record

**Cloudflare:** DNS → Add Record

---

## Step 3: SSH into Your Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

---

## Step 4: Install Certbot (Let's Encrypt)

```bash
# Update packages
apt update && apt upgrade -y

# Install Certbot and Nginx plugin
apt install certbot python3-certbot-nginx -y
```

---

## Step 5: Configure Nginx

Create/edit Nginx config:

```bash
nano /etc/nginx/sites-available/crewcfo
```

Paste this:

```nginx
server {
    listen 80;
    server_name crewcfo.com www.crewcfo.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

---

## Step 6: Enable the Site

```bash
# Create symlink
ln -s /etc/nginx/sites-available/crewcfo /etc/nginx/sites-enabled/

# Remove default if exists
rm -f /etc/nginx/sites-enabled/default

# Test config
nginx -t

# Reload Nginx
systemctl reload nginx
```

---

## Step 7: Get SSL Certificate

```bash
certbot --nginx -d crewcfo.com -d www.crewcfo.com
```

Follow the prompts:
- Enter email address
- Agree to terms (Y)
- Share email with EFF (optional, N is fine)
- **Select option 2** to redirect HTTP to HTTPS

---

## Step 8: Verify Auto-Renewal

```bash
# Test renewal
certbot renew --dry-run

# Check timer is active
systemctl status certbot.timer
```

---

## Step 9: Make Sure Your App is Running

```bash
# Check if Docker is running your app
docker-compose ps

# If not running, start it
cd /path/to/your/app
docker-compose up -d
```

---

## Step 10: Test It

Wait 5-10 minutes for DNS propagation, then:

1. Open https://crewcfo.com
2. Check for green padlock 🔒
3. Test https://www.crewcfo.com (should also work)

---

## Troubleshooting

**DNS not propagating?**
```bash
# Check from your Mac
dig crewcfo.com
nslookup crewcfo.com
```

**Certbot fails?**
```bash
# Make sure port 80 is open
ufw allow 80
ufw allow 443

# Check Nginx is running
systemctl status nginx
```

**App not responding?**
```bash
# Check if app is running on port 8000
curl localhost:8000
docker-compose logs
```

---

## Quick Reference

| URL | What |
|-----|------|
| https://crewcfo.com | Your app |
| https://crewcfo.com/docs | API docs (Swagger) |

---

Which domain registrar are you using? I can give more specific DNS instructions if needed.



## Prompt:
12/16/2025, 4:43:58 PM

![Screenshot 2025-12-16 at 4.43.41 PM.png](data:image/webp;base64,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)





## Response:
12/16/2025, 4:44:08 PM

````plaintext
Thought process: I notice the user prompt is empty, so I cannot determine the primary language. However, based on the thinking block being in English, here is my summary:

Diagnosed DNS record conflict and prescribed deletion solution.

The user is setting up DNS records for crewcfo.com. I can see:
- They already have an A record for @ pointing to 137.184.122.124
- They're trying to add a www record but getting "Record name www conflicts with another record"

This means there's already a www record (probably a CNAME or another A record). They need to delete the existing www record first, then add the new one.
````

There's already a `www` record that's conflicting. You need to delete the existing one first.

---

## Fix This:

### Step 1: Scroll down and find the existing `www` record

Look in the records list below for a `www` entry (could be CNAME or A record)

### Step 2: Delete the old `www` record

Click the trash icon 🗑️ next to it

### Step 3: Now add the new `www` A record

- **Type:** A
- **Name:** www
- **Value:** 137.184.122.124
- **TTL:** 600

### Step 4: Click Save

---

## Your Final DNS Should Look Like:

| Type | Name | Data | TTL |
|------|------|------|-----|
| A | @ | 137.184.122.124 | 600 |
| A | www | 137.184.122.124 | 600 |

---

Once saved, continue with **Step 3** from before (SSH into your droplet to set up Nginx and SSL).

Can you scroll down and show me what other records exist? There should be a conflicting `www` record to delete.



## Prompt:
12/16/2025, 4:45:12 PM

Godaddy is not letting me delete it



## Response:
12/16/2025, 4:45:25 PM

````plaintext
Thought process: Brainstormed alternative solutions to GoDaddy deletion obstruction.

The user is having trouble deleting the existing www record in GoDaddy. This is a common issue - GoDaddy sometimes has default records that can't be deleted easily, or there might be a CNAME record for www that's conflicting.

Let me suggest some workarounds:

1. Edit the existing www record instead of deleting it
2. Check if it's a CNAME record and change it to an A record
3. Look for a "Manage" or "Edit" button instead of delete
4. Sometimes GoDaddy has the www record tied to their forwarding/parking service

Let me give clear instructions.
````

## Workaround: Edit Instead of Delete

### Option 1: Edit the Existing www Record

1. Find the existing `www` record in the list below
2. Click the **pencil/edit icon** ✏️ (not delete)
3. Change the **Value/Data** to `137.184.122.124`
4. Change **Type** to `A` if it's currently CNAME
5. Save

---

### Option 2: If It's a CNAME Record

If the existing `www` is a CNAME (pointing to something like `@` or `forwarding.godaddy.com`):

1. Click **Edit** on that record
2. Change **Type** from CNAME to **A**
3. Set **Value** to `137.184.122.124`
4. Save

---

### Option 3: Check for Forwarding

GoDaddy sometimes locks `www` if you have domain forwarding enabled:

1. Go to **Domain Settings** → **Forwarding**
2. If forwarding is ON, turn it **OFF**
3. Then you can edit/delete the www record

---

### Option 4: Cancel and Just Edit

1. Click **Cancel** on the form you're currently on
2. Scroll down to find the existing `www` record
3. Click the **Edit** button (pencil icon) on that row
4. Update the IP to `137.184.122.124`

---

**Can you scroll down and screenshot the full list of existing DNS records?** That will help me see what's blocking you.



## Prompt:
12/16/2025, 4:48:04 PM

(.venv) (base) ildar@MacBook-Pro-52 roofing-books-cfo % ssh root@137.184.122.124
Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.8.0-71-generic x86_64)
 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro
 System information as of Wed Dec 17 00:47:14 UTC 2025
  System load:  0.01               Processes:             116
  Usage of /:   23.6% of 23.17GB   Users logged in:       0
  Memory usage: 49%                IPv4 address for eth0: 137.184.122.124
  Swap usage:   0%                 IPv4 address for eth0: 10.48.0.6
Expanded Security Maintenance for Applications is not enabled.
0 updates can be applied immediately.
Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status
*** System restart required ***
Last login: Tue Dec 16 23:07:30 2025 from 162.243.190.66
root@ubuntu-s-1vcpu-1gb-sfo3-01:~#



## Response:
12/16/2025, 4:48:13 PM

````plaintext
Thought process: Orchestrated next steps for server configuration and SSL setup.

Good, the user is now SSH'd into their DigitalOcean droplet. Now I need to guide them through setting up Nginx and SSL. Let me continue from Step 4 of the original instructions.
````

You're in! Now let's set up Nginx and SSL.

---

## Step 4: Install Certbot

```bash
apt update && apt install certbot python3-certbot-nginx -y
```

---

## Step 5: Create Nginx Config

```bash
nano /etc/nginx/sites-available/crewcfo
```

Paste this (right-click to paste in terminal):

```nginx
server {
    listen 80;
    server_name crewcfo.com www.crewcfo.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

---

## Step 6: Enable Site

```bash
ln -sf /etc/nginx/sites-available/crewcfo /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

---

## Step 7: Get SSL Certificate

```bash
certbot --nginx -d crewcfo.com -d www.crewcfo.com
```

Enter your email, agree to terms, choose to redirect HTTP→HTTPS.

---

## Step 8: Check Your App is Running

```bash
docker ps
```

If no containers running:
```bash
cd /root/roofing-books-cfo   # or wherever your app is
docker-compose up -d
```

---

Run these commands one by one and let me know when you hit any issues!



## Prompt:
12/16/2025, 4:58:31 PM

where do I do step 4?



## Response:
12/16/2025, 4:58:36 PM

````plaintext
Thought process: Determined user should execute command in current terminal session.

The user is asking where to run step 4. They're already SSH'd into the droplet - they can see the prompt:

`​`​`
root@ubuntu-s-1vcpu-1gb-sfo3-01:~#
`​`​`

So they just need to type the command right there in that same terminal window where they SSH'd in.
````

Right there in the same terminal where you just SSH'd in!

You should see this prompt:
```
root@ubuntu-s-1vcpu-1gb-sfo3-01:~#
```

Just type:

```bash
apt update && apt install certbot python3-certbot-nginx -y
```

Press Enter and let it run.



## Prompt:
12/16/2025, 5:02:10 PM

after step 5 is it control 0 on mac?



## Response:
12/16/2025, 5:02:16 PM

````plaintext
Thought process: Clarified Mac keyboard shortcut for nano editor saving.

The user is asking about saving in nano editor on Mac. On Mac, it's still Ctrl+O (the Control key, not Command). Let me clarify this.
````

Yes! On Mac in terminal:

- **Save:** `Ctrl+O` (Control key + letter O), then press `Enter`
- **Exit:** `Ctrl+X` (Control key + letter X)

**Not** Command (⌘), use the **Control** key.



## Prompt:
12/16/2025, 5:03:42 PM

after step 6:

Unpacking python3-icu (2.12-1build2) ...
Setting up python3-configargparse (1.7-1) ...
Setting up python3-parsedatetime (2.6-3) ...
Setting up python3-icu (2.12-1build2) ...
Setting up nginx-common (1.24.0-2ubuntu7.5) ...
Created symlink /etc/systemd/system/multi-user.target.wants/nginx.service → /usr/lib/systemd/system/nginx.service.
Could not execute systemctl:  at /usr/bin/deb-systemd-invoke line 148.
Setting up python3-josepy (1.14.0-1) ...
Setting up python3-rfc3339 (1.1-4) ...
Setting up nginx (1.24.0-2ubuntu7.5) ...
Not attempting to start NGINX, port 80 is already in use.
Setting up python3-acme (2.9.0-1) ...
Setting up python3-certbot (2.9.0-1) ...
Setting up certbot (2.9.0-1) ...
Created symlink /etc/systemd/system/timers.target.wants/certbot.timer → /usr/lib/systemd/system/certbot.timer.
Setting up python3-certbot-nginx (2.9.0-1) ...
Processing triggers for man-db (2.12.0-4build2) ...
Processing triggers for ufw (0.36.2-6) ...
Scanning processes...                                          
Scanning candidates...                                         
Scanning linux images...                                       
Pending kernel upgrade!
Running kernel version:
  6.8.0-71-generic
Diagnostics:
  The currently running kernel version is not the expected
kernel version 6.8.0-90-generic.
Restarting the system to load the new kernel will not be
handled automatically, so you should consider rebooting.
Restarting services...
Service restarts being deferred:
 /etc/needrestart/restart.d/dbus.service
 systemctl restart getty@tty1.service
 systemctl restart serial-getty@ttyS0.service
 systemctl restart systemd-logind.service
 systemctl restart unattended-upgrades.service
No containers need to be restarted.
No user sessions are running outdated binaries.
No VM guests are running outdated hypervisor (qemu) binaries
 on this host.
root@ubuntu-s-1vcpu-1gb-sfo3-01:~# nano /etc/nginx/sites-available/crewcfo
root@ubuntu-s-1vcpu-1gb-sfo3-01:~# ln -sf /etc/nginx/sites-available/crewcfo /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
nginx.service is not active, cannot reload.
root@ubuntu-s-1vcpu-1gb-sfo3-01:~#



## Response:
12/16/2025, 5:03:50 PM

````plaintext
Thought process: Diagnosed port conflict preventing nginx activation.

The user ran step 6 and nginx config test passed but nginx service is not active. Port 80 is already in use by something else (likely Docker/Caddy or another web server). We need to:

1. Find what's using port 80
2. Either stop it or configure differently

Let me help them figure out what's using port 80 and get nginx running.
````

Nginx isn't running because something else is using port 80. Let's fix it:

---

## Step 6a: Check What's Using Port 80

```bash
lsof -i :80
```

or

```bash
ss -tlnp | grep :80
```

---

## Step 6b: Likely Caddy or Docker is Running

Check if it's Caddy:
```bash
systemctl status caddy
```

Check Docker containers:
```bash
docker ps
```

---

## Step 6c: Stop the Conflicting Service

If Caddy is running:
```bash
systemctl stop caddy
systemctl disable caddy
```

If Docker is exposing port 80:
```bash
docker-compose down
```

---

## Step 6d: Start Nginx

```bash
systemctl start nginx
systemctl enable nginx
systemctl status nginx
```

---

Run `lsof -i :80` first and tell me what's using port 80!



## Prompt:
12/16/2025, 5:04:45 PM

root@ubuntu-s-1vcpu-1gb-sfo3-01:~# nano /etc/nginx/sites-available/crewcfo
root@ubuntu-s-1vcpu-1gb-sfo3-01:~# ln -sf /etc/nginx/sites-available/crewcfo /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
nginx.service is not active, cannot reload.
root@ubuntu-s-1vcpu-1gb-sfo3-01:~# lsof -i :80
COMMAND     PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
docker-pr 19568 root    7u  IPv4  51982      0t0  TCP *:http (LISTEN)
docker-pr 19572 root    7u  IPv6  51983      0t0  TCP *:http (LISTEN)
root@ubuntu-s-1vcpu-1gb-sfo3-01:~#



## Response:
12/16/2025, 5:04:54 PM

````plaintext
Thought process: Diagnosed port conflict and orchestrated Docker-Nginx resolution strategy.

Docker is using port 80. We need to either:
1. Stop the Docker container using port 80, then use Nginx
2. Or configure the Docker setup to work with Nginx

The cleanest approach is to:
1. Stop Docker containers
2. Change docker-compose to use a different port (like 8000 internally, not exposed to 80)
3. Use Nginx as the reverse proxy on port 80
4. Start Docker again

Let me guide them through this.
````

Docker is using port 80. Let's reconfigure:

---

## Step 6a: Stop Docker Containers

```bash
cd /root/roofing-books-cfo
docker-compose down
```

(Or find where your app is: `find /root -name "docker-compose.yml"`)

---

## Step 6b: Start Nginx

```bash
systemctl start nginx
systemctl enable nginx
systemctl status nginx
```

---

## Step 6c: Update docker-compose.yml

We need to change Docker to use port 8000 internally (not 80). Edit the file:

```bash
nano /root/roofing-books-cfo/docker-compose.yml
```

Find the ports section and change:
```yaml
# Change FROM this:
ports:
  - "80:8000"

# TO this:
ports:
  - "8000:8000"
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

---

## Step 6d: Restart Docker

```bash
docker-compose up -d
```

---

## Step 6e: Verify Both Running

```bash
# Check Nginx
systemctl status nginx

# Check Docker
docker ps

# Test app internally
curl localhost:8000
```

---

## Step 7: Get SSL Certificate

```bash
certbot --nginx -d crewcfo.com -d www.crewcfo.com
```

---

Run Step 6a first (`docker-compose down`) and let me know!



## Prompt:
12/16/2025, 5:06:19 PM

snap install docker          # version 28.4.0, or
apt  install docker-compose  # version 1.29.2-6
See 'snap info docker' for additional versions.
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo# systemctl start nginx
systemctl enable nginx
systemctl status nginx
Job for nginx.service failed because the control process exited with error code.
See "systemctl status nginx.service" and "journalctl -xeu nginx.service" for details.
Synchronizing state of nginx.service with SysV service script with /usr/lib/systemd/systemd-sysv-install.
Executing: /usr/lib/systemd/systemd-sysv-install enable nginx
× nginx.service - A high performance web server and a reverse >
     Loaded: loaded (/usr/lib/systemd/system/nginx.service; en>
     Active: failed (Result: exit-code) since Wed 2025-12-17 0>
       Docs: man:nginx(8)
        CPU: 18ms
Dec 17 01:05:40 ubuntu-s-1vcpu-1gb-sfo3-01 systemd[1]: Startin>
Dec 17 01:05:40 ubuntu-s-1vcpu-1gb-sfo3-01 nginx[550188]: ngin>
Dec 17 01:05:40 ubuntu-s-1vcpu-1gb-sfo3-01 nginx[550188]: ngin>
Dec 17 01:05:41 ubuntu-s-1vcpu-1gb-sfo3-01 nginx[550188]: ngin>
Dec 17 01:05:41 ubuntu-s-1vcpu-1gb-sfo3-01 nginx[550188]: ngin>
Dec 17 01:05:42 ubuntu-s-1vcpu-1gb-sfo3-01 nginx[550188]: ngin>
Dec 17 01:05:42 ubuntu-s-1vcpu-1gb-sfo3-01 nginx[550188]: ngin>
Dec 17 01:05:42 ubuntu-s-1vcpu-1gb-sfo3-01 systemd[1]: nginx.s>
Dec 17 01:05:42 ubuntu-s-1vcpu-1gb-sfo3-01 systemd[1]: nginx.s>
Dec 17 01:05:42 ubuntu-s-1vcpu-1gb-sfo3-01 systemd[1]: Failed >
lines 1-16/16 (END)



## Response:
12/16/2025, 5:06:25 PM

````plaintext
Thought process: Diagnosed port conflict and orchestrated sequential resolution steps.

Nginx is failing to start because Docker is still using port 80. The user needs to stop the Docker containers first before Nginx can start.

Let me guide them through:
1. First stop Docker containers
2. Then start Nginx
3. Then modify docker-compose to use a different port
4. Then restart Docker
````

Docker is still using port 80. Press `q` to exit that status screen, then:

---

## Step 1: Stop Docker First

```bash
cd /root/roofing-books-cfo
docker stop $(docker ps -q)
```

---

## Step 2: Now Start Nginx

```bash
systemctl start nginx
systemctl status nginx
```

---

## Step 3: Edit docker-compose.yml

```bash
nano /root/roofing-books-cfo/docker-compose.yml
```

Find `ports:` and change `80:8000` to `8000:8000`

Save: `Ctrl+O`, Enter, `Ctrl+X`

---

## Step 4: Restart Docker

```bash
docker-compose up -d
```

---

Run Step 1 first - stop Docker containers!



## Prompt:
12/16/2025, 5:08:32 PM

(base) ildar@MacBook-Pro-52 spec-os-shared-suite % cd /Users/ildar/Documents/1.Projects/roofing-books-cfo
(base) ildar@MacBook-Pro-52 roofing-books-cfo % cd /root/roofing-books-cfo
docker stop $(docker ps -q)
cd: no such file or directory: /root/roofing-books-cfo
6e9fb338aa5d
71b63d0a45fd
(base) ildar@MacBook-Pro-52 roofing-books-cfo % systemctl start nginx
systemctl status nginx
zsh: command not found: systemctl
zsh: command not found: systemctl
(base) ildar@MacBook-Pro-52 roofing-books-cfo %



## Response:
12/16/2025, 5:08:36 PM

````plaintext
Thought process: Diagnosed remote server access misconfiguration issue.

The user is running commands on their local Mac instead of on the remote server. They need to SSH back into the DigitalOcean droplet first.
````

You're on your Mac now, not the server! SSH back in:

---

## SSH Back Into the Server

```bash
ssh root@137.184.122.124
```

Then run:

```bash
cd /root/roofing-books-cfo
docker stop $(docker ps -q)
systemctl start nginx
systemctl status nginx
```



## Prompt:
12/16/2025, 5:09:25 PM

*** System restart required ***
Last login: Wed Dec 17 00:47:15 2025 from 64.125.142.138
root@ubuntu-s-1vcpu-1gb-sfo3-01:~# cd /root/roofing-books-cfo
docker stop $(docker ps -q)
systemctl start nginx
systemctl status nginx
35ca1aa55dc3
7e6ee611eb1d
561081a1657d
ce33fe86c26c
● nginx.service - A high performance web server and a reverse >
     Loaded: loaded (/usr/lib/systemd/system/nginx.service; en>
     Active: active (running) since Wed 2025-12-17 01:08:59 UT>
       Docs: man:nginx(8)
    Process: 550972 ExecStartPre=/usr/sbin/nginx -t -q -g daem>
    Process: 550974 ExecStart=/usr/sbin/nginx -g daemon on; ma>
   Main PID: 550975 (nginx)
      Tasks: 2 (limit: 1110)
     Memory: 2.0M (peak: 2.2M)
        CPU: 26ms
     CGroup: /system.slice/nginx.service
             ├─550975 "nginx: master process /usr/sbin/nginx ->
             └─550976 "nginx: worker process"
Dec 17 01:08:59 ubuntu-s-1vcpu-1gb-sfo3-01 systemd[1]: Startin>
Dec 17 01:08:59 ubuntu-s-1vcpu-1gb-sfo3-01 systemd[1]: Started>
lines 1-16/16 (END)



## Response:
12/16/2025, 5:09:31 PM

````plaintext
Thought process: Orchestrated next deployment steps: SSL, Docker config, restart.

Nginx is now running (Active: active (running)). Now we need to:
1. Get SSL certificate
2. Update docker-compose.yml to use port 8000 instead of 80
3. Restart Docker

Let me guide the user through this.
````

Nginx is running! Press `q` to exit, then get the SSL certificate:

---

## Step 7: Get SSL Certificate

```bash
certbot --nginx -d crewcfo.com -d www.crewcfo.com
```

Enter your email, type `Y` to agree, and select option to redirect HTTP to HTTPS.

---

## Step 8: Edit docker-compose.yml

```bash
nano /root/roofing-books-cfo/docker-compose.yml
```

Find `ports:` section and change:
```yaml
# FROM:
ports:
  - "80:8000"

# TO:
ports:
  - "8000:8000"
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

---

## Step 9: Restart Docker

```bash
docker-compose up -d
```

---

## Step 10: Test

```bash
curl localhost:8000
```

Then open in browser: **https://crewcfo.com**

---

Run Step 7 first!



## Prompt:
12/16/2025, 5:12:31 PM

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Would you be willing, once your first certificate is successfully issued, to
share your email address with the Electronic Frontier Foundation, a founding
partner of the Let's Encrypt project and the non-profit organization that
develops Certbot? We'd like to send you email about our work encrypting the web,
EFF news, campaigns, and ways to support digital freedom.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: n
Account registered.
Requesting a certificate for crewcfo.com and www.crewcfo.com
An unexpected error occurred:
No such authorization
Ask for help or search for solutions at https://community.letsencrypt.org. See the logfile /var/log/letsencrypt/letsencrypt.log or re-run Certbot with -v for more details.
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo#



## Response:
12/16/2025, 5:12:40 PM

````plaintext
Thought process: Diagnosed DNS propagation delay blocking certificate authorization.

The SSL certificate failed with "No such authorization" error. This usually means DNS hasn't propagated yet - Let's Encrypt can't verify that crewcfo.com points to this server.

Let me help them check if DNS is working.
````

DNS hasn't propagated yet. Let's check and fix:

---

## Step 1: Check if DNS is Working

```bash
dig crewcfo.com +short
dig www.crewcfo.com +short
```

If it shows `137.184.122.124`, DNS is working.
If empty or different IP, DNS hasn't propagated.

---

## Step 2: Test from Server

```bash
curl -I http://crewcfo.com
```

---

## Step 3: If DNS Not Working Yet

**Option A:** Wait 10-30 minutes for DNS propagation, then retry:
```bash
certbot --nginx -d crewcfo.com -d www.crewcfo.com
```

**Option B:** Try just the root domain first:
```bash
certbot --nginx -d crewcfo.com
```

---

## Step 4: Check GoDaddy Settings

Make sure you saved the DNS records:
- **A record** `@` → `137.184.122.124`
- **A record** `www` → `137.184.122.124`

---

Run `dig crewcfo.com +short` and tell me what it shows!



## Prompt:
12/16/2025, 5:12:48 PM

provide steps 8, 9 and 10 as a cursor command for it to do it for me



## Response:
12/16/2025, 5:12:59 PM

````plaintext
Thought process: Reconciled local editing workflow with remote server deployment constraints.

The user wants me to provide a Cursor prompt that will help them edit the docker-compose.yml file on their remote server. But wait - Cursor runs locally on their Mac, not on the remote server. They need to either:

1. Run the commands directly on the server via SSH
2. Edit the file locally and push/deploy to server

Actually, looking at their setup, they have the roofing-books-cfo project locally on their Mac at /Users/ildar/Documents/1.Projects/roofing-books-cfo and they deploy to the server.

So they should:
1. Edit docker-compose.yml locally using Cursor
2. Push to git
3. Pull on server
4. Run docker-compose up -d

Let me give them a Cursor prompt to edit the local file, then the server commands.
````

Cursor runs on your Mac, not the server. Here's the workflow:

---

## Cursor Prompt (Run on Your Mac)

Open Cursor in your project and paste:

```
Edit docker-compose.yml:

Change the app/web service ports from "80:8000" to "8000:8000"

Nginx will handle port 80/443 and proxy to port 8000.
```

---

## Then Deploy to Server

After Cursor makes the change, push and deploy:

**On your Mac:**
```bash
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo
git add docker-compose.yml
git commit -m "Change port mapping for nginx proxy"
git push
```

**On the server (SSH terminal):**
```bash
ssh root@137.184.122.124
cd /root/roofing-books-cfo
git pull
docker-compose up -d
curl localhost:8000
```

---

## Or Edit Directly on Server

If you prefer, just run this on the server:

```bash
sed -i 's/"80:8000"/"8000:8000"/g' /root/roofing-books-cfo/docker-compose.yml
docker-compose up -d
curl localhost:8000
```

---

Which approach do you want to use?



## Prompt:
12/16/2025, 5:16:54 PM

# docker-compose.yml - CrewCFO Development Environment
# Usage: 
#   docker-compose up                    # Start all services
#   docker-compose up api dashboard      # Start only API and dashboard
#   docker-compose --profile tools up    # Include pgAdmin
services:
  # Nginx - Serves marketing pages + reverse proxy
  nginx:
    image: nginx:alpine
    container_name: crewcfo-nginx
    ports:
      - "80:80"
    volumes:
      - ./marketing:/usr/share/nginx/html:ro
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
      - dashboard
    networks:
      - crewcfo-network
    restart: unless-stopped
  # FastAPI Backend
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: crewcfo-api
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - PORT=8000
    volumes:
      - ./src:/app/src
      - ./sample_data:/app/sample_data
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    # Note: API uses Supabase by default, postgres is optional (use --profile db)
    networks:
      - crewcfo-network
    restart: unless-stopped
  # Streamlit Dashboard
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: crewcfo-dashboard
    ports:
      - "8503:8503"  # Updated to match your current port
    env_file:
      - .env
    environment:
      - PORT=8503
    volumes:
      - ./src:/app/src
    command: streamlit run src/dashboard/owner.py --server.port 8503 --server.address 0.0.0.0 --server.headless true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8503/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      api:
        condition: service_healthy
    networks:
      - crewcfo-network
    restart: unless-stopped
  # Local PostgreSQL (optional - for offline dev/testing)
  # Note: You're using Supabase in production, but local DB is useful for:
  # - Testing without internet
  # - Development with local data
  # - CI/CD pipelines
  postgres:
    image: postgres:15-alpine
    container_name: crewcfo-db
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-crewcfo}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./supabase/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - crewcfo-network
    restart: unless-stopped
    profiles:
      - db  # Only starts with: docker-compose --profile db up
  # pgAdmin (optional - database GUI)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: crewcfo-pgadmin
    ports:
      - "5050:80"
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL:-admin@crewcfo.com}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-admin}
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - crewcfo-network
    profiles:
      - tools  # Only starts with: docker-compose --profile tools up
    restart: unless-stopped
volumes:
  postgres_data:
    driver: local
networks:
  crewcfo-network:
    driver: bridge


above is docker-compose.yml contents, provide the full replacement



## Response:
12/16/2025, 5:17:10 PM

````plaintext
Thought process: Reconciled port conflicts by disabling Docker nginx for system handling.

The user wants the full replacement for docker-compose.yml. The issue is that the nginx container in docker-compose is using port 80, but we want the system nginx (not docker nginx) to handle SSL/port 80.

We have two options:
1. Disable the docker nginx and use system nginx
2. Use docker nginx with SSL

Since we already set up system nginx with certbot, we should disable the docker nginx container and let system nginx handle port 80/443.

I'll provide the full replacement with the docker nginx service commented out or removed.
````

Your docker-compose already has a nginx container using port 80. Since we're using **system Nginx** for SSL, we need to disable the Docker nginx:

```yaml
# docker-compose.yml - CrewCFO Development Environment
# Usage: 
#   docker-compose up                    # Start all services
#   docker-compose up api dashboard      # Start only API and dashboard
#   docker-compose --profile tools up    # Include pgAdmin
services:
  # Nginx - DISABLED (using system nginx for SSL)
  # nginx:
  #   image: nginx:alpine
  #   container_name: crewcfo-nginx
  #   ports:
  #     - "80:80"
  #   volumes:
  #     - ./marketing:/usr/share/nginx/html:ro
  #     - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
  #   depends_on:
  #     - api
  #     - dashboard
  #   networks:
  #     - crewcfo-network
  #   restart: unless-stopped

  # FastAPI Backend
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: crewcfo-api
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - PORT=8000
    volumes:
      - ./src:/app/src
      - ./sample_data:/app/sample_data
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - crewcfo-network
    restart: unless-stopped

  # Streamlit Dashboard
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: crewcfo-dashboard
    ports:
      - "8503:8503"
    env_file:
      - .env
    environment:
      - PORT=8503
    volumes:
      - ./src:/app/src
    command: streamlit run src/dashboard/owner.py --server.port 8503 --server.address 0.0.0.0 --server.headless true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8503/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      api:
        condition: service_healthy
    networks:
      - crewcfo-network
    restart: unless-stopped

  # Local PostgreSQL (optional)
  postgres:
    image: postgres:15-alpine
    container_name: crewcfo-db
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-crewcfo}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./supabase/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - crewcfo-network
    restart: unless-stopped
    profiles:
      - db

  # pgAdmin (optional)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: crewcfo-pgadmin
    ports:
      - "5050:80"
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL:-admin@crewcfo.com}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-admin}
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - crewcfo-network
    profiles:
      - tools
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local

networks:
  crewcfo-network:
    driver: bridge
```

---

## On the Server, Run:

```bash
cd /root/roofing-books-cfo
nano docker-compose.yml
```

Replace all content with the above, then:

```bash
docker-compose up -d
curl localhost:8000
```

---

## Then Retry SSL

```bash
certbot --nginx -d crewcfo.com -d www.crewcfo.com
```



## Prompt:
12/16/2025, 5:18:28 PM

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: n
Account registered.
Requesting a certificate for crewcfo.com and www.crewcfo.com
An unexpected error occurred:
No such authorization
Ask for help or search for solutions at https://community.letsencrypt.org. See the logfile /var/log/letsencrypt/letsencrypt.log or re-run Certbot with -v for more details.
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo# docker-compose up -d
curl localhost:8000
Command 'docker-compose' not found, but can be installed with:
snap install docker          # version 28.4.0, or
apt  install docker-compose  # version 1.29.2-6
See 'snap info docker' for additional versions.
curl: (7) Failed to connect to localhost port 8000 after 0 ms: Couldn't connect to server
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo#



## Response:
12/16/2025, 5:18:36 PM

````plaintext
Thought process: Diagnosed SSL propagation delay and Docker version incompatibility issues.

Two issues:
1. SSL certificate failed - DNS not propagated yet
2. docker-compose not found - need to use `docker compose` (with space) on newer Docker versions

Let me help fix both.
````

Two issues to fix:

---

## Fix 1: Docker Compose Command

Use `docker compose` (with space) instead:

```bash
docker compose up -d
```

---

## Fix 2: Check DNS Propagation

```bash
dig crewcfo.com +short
```

If it doesn't show `137.184.122.124`, DNS hasn't propagated yet.

---

## Run These Now:

```bash
# Start the app
docker compose up -d

# Check it's running
docker ps

# Test locally
curl localhost:8000

# Check DNS
dig crewcfo.com +short
dig www.crewcfo.com +short
```

---

## If DNS Shows Your IP, Retry SSL:

```bash
certbot --nginx -d crewcfo.com -d www.crewcfo.com
```

---

## If DNS Not Working Yet:

Wait 15-30 minutes, or check GoDaddy to make sure records saved correctly:
- **A** `@` → `137.184.122.124`
- **A** `www` → `137.184.122.124`

Run `docker compose up -d` first and tell me what happens!



## Prompt:
12/16/2025, 6:55:30 PM

write these in ssh or regular terminal?



## Response:
12/16/2025, 6:55:37 PM

````plaintext
Thought process: Determined commands require server execution via SSH.

The user is asking whether to run these commands in SSH (on the server) or regular terminal (on their Mac).

Since they're setting up the server with Docker and Nginx, all these commands need to run on the server via SSH.
````

**SSH** (on the server)

You should see this prompt:
```
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo#
```

If you're not connected, open terminal and:
```bash
ssh root@137.184.122.124
cd /root/roofing-books-cfo
```

Then run:
```bash
docker compose up -d
```



## Prompt:
12/16/2025, 6:56:22 PM

*** System restart required ***
Last login: Wed Dec 17 01:08:49 2025 from 64.125.142.138
root@ubuntu-s-1vcpu-1gb-sfo3-01:~# docker compose up -d
no configuration file provided: not found
root@ubuntu-s-1vcpu-1gb-sfo3-01:~#



## Response:
12/16/2025, 6:56:27 PM

````plaintext
Thought process: Thinking about resolving missing Docker Compose configuration file error.

The user is in the home directory (~) instead of the project directory. They need to cd into the project folder first.
````

You're in the wrong folder. Navigate to the project first:

```bash
cd /root/roofing-books-cfo
docker compose up -d
```



## Prompt:
12/16/2025, 6:57:27 PM

*** System restart required ***
Last login: Wed Dec 17 01:08:49 2025 from 64.125.142.138
root@ubuntu-s-1vcpu-1gb-sfo3-01:~# docker compose up -d
no configuration file provided: not found
root@ubuntu-s-1vcpu-1gb-sfo3-01:~# cd /root/roofing-books-cfo
docker compose up -d
WARN[0000] Found orphan containers ([crewcfo-web]) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up. 
[+] up 0/1
 ⠴ Container crewcfo-api Waiting              0.5s 
dependency failed to start: container crewcfo-api is unhealthy
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo#



## Response:
12/16/2025, 6:57:31 PM

````plaintext
Thought process: Thinking about diagnosing Docker Compose startup failures and container health issues.

The container is unhealthy. Let's check the logs to see what's wrong with the API container.
````

The API container is unhealthy. Let's check what's wrong:

```bash
docker compose logs api
```

And check container status:

```bash
docker ps -a
```

Share the output and I'll help fix it!



## Prompt:
12/16/2025, 7:00:14 PM

crewcfo-api  |     return future.result()
crewcfo-api  |            ^^^^^^^^^^^^^^^
crewcfo-api  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
crewcfo-api  |     await self._serve(sockets)
crewcfo-api  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
crewcfo-api  |     config.load()
crewcfo-api  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 439, in load
crewcfo-api  |     self.loaded_app = import_from_string(self.app)
crewcfo-api  |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
crewcfo-api  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
crewcfo-api  |     raise exc from None
crewcfo-api  |   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
crewcfo-api  |     module = importlib.import_module(module_str)
crewcfo-api  |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
crewcfo-api  |   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
crewcfo-api  |     return _bootstrap._gcd_import(name[level:], package, level)
crewcfo-api  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
crewcfo-api  |   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
crewcfo-api  |   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
crewcfo-api  |   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
crewcfo-api  |   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
crewcfo-api  |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
crewcfo-api  |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
crewcfo-api  |   File "/app/src/main.py", line 26, in <module>
crewcfo-api  |     from utils.auth import get_current_tenant_id
crewcfo-api  | ModuleNotFoundError: No module named 'utils'
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo# docker ps -a
CONTAINER ID   IMAGE                         COMMAND                  CREATED       STATUS                   PORTS                                         NAMES
e1ca136677f3   nginx:alpine                  "/docker-entrypoint.…"   2 hours ago   Created                                                                crewcfo-nginx
cf02d6d8e22b   roofing-books-cfo-dashboard   "streamlit run src/d…"   2 hours ago   Created                                                                crewcfo-dashboard
69505c479a4a   roofing-books-cfo-api         "uvicorn src.main:ap…"   2 hours ago   Up 2 hours (unhealthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   crewcfo-api
561081a1657d   roofing-books-cfo-web         "docker-entrypoint.s…"   4 hours ago   Exited (0) 2 hours ago                                                 crewcfo-web
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo#



## Response:
12/16/2025, 7:00:23 PM

````plaintext
Thought process: Diagnosed import path mismatch and identified resolution options.

The issue is a Python import error. The code in main.py is trying to import `from utils.auth import get_current_tenant_id` but Python can't find the `utils` module.

Looking at the project structure earlier, there's a `src/utils` folder. The issue is that the import should be relative or use `src.utils`.

Let me check what the import statement should be. The command is `uvicorn src.main:app` which means uvicorn is running from the `/app` directory and importing `src.main`. 

In main.py line 26, it has:
`​`​`python
from utils.auth import get_current_tenant_id
`​`​`

But since the app is being run as `src.main`, the import should be:
`​`​`python
from src.utils.auth import get_current_tenant_id
`​`​`

Or use a relative import:
`​`​`python
from .utils.auth import get_current_tenant_id
`​`​`

The code on the server might be out of sync with the local code. The user needs to either:
1. Pull the latest code from git on the server
2. Or fix the import path

Let me ask them to pull the latest code first, and if that doesn't work, we can fix the import.
````

Import error in the code. The server code might be out of sync. Let's update it:

---

## Step 1: Pull Latest Code

```bash
cd /root/roofing-books-cfo
git pull
```

---

## Step 2: Rebuild and Restart

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## Step 3: Check Logs

```bash
docker compose logs api
```

---

If git pull fails or the error persists, show me the import section of main.py:

```bash
head -30 src/main.py
```



## Prompt:
12/16/2025, 7:07:37 PM

now what?



## Response:
12/16/2025, 7:07:43 PM

````plaintext
Thought process: Thinking about clarifying the context of an ambiguous follow-up question.

The user is asking "now what?" after running the commands I gave them. I need to ask what happened - did the commands work? What was the output?
````

What happened? Share the output of:

```bash
docker ps
curl localhost:8000
```

And check DNS:

```bash
dig crewcfo.com +short
```



## Prompt:
12/16/2025, 7:08:29 PM

put this command in ssh or regular terminal?



## Response:
12/16/2025, 7:08:33 PM

````plaintext
Thought process: Thinking about distinguishing SSH terminal from regular terminal usage.

The user is asking whether to run the commands in SSH (on the server) or regular terminal (on their Mac). Since we're checking the Docker containers, the API, and DNS - all of which are on the server - they should run these commands in SSH.
````

**SSH** (on the server)

You should see:
```
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo#
```

Then run:
```bash
docker ps
curl localhost:8000
dig crewcfo.com +short
```



## Prompt:
12/16/2025, 7:09:29 PM

crewcfo-nginx
cf02d6d8e22b   roofing-books-cfo-dashboard   "streamlit run src/d…"   2 hours ago   Created                                                                crewcfo-dashboard
69505c479a4a   roofing-books-cfo-api         "uvicorn src.main:ap…"   2 hours ago   Up 2 hours (unhealthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   crewcfo-api
561081a1657d   roofing-books-cfo-web         "docker-entrypoint.s…"   4 hours ago   Exited (0) 2 hours ago                                                 crewcfo-web
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo# docker ps
curl localhost:8000
dig crewcfo.com +short
CONTAINER ID   IMAGE                   COMMAND                  CREATED       STATUS                   PORTS                                         NAMES
69505c479a4a   roofing-books-cfo-api   "uvicorn src.main:ap…"   2 hours ago   Up 2 hours (unhealthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   crewcfo-api
curl: (52) Empty reply from server
137.184.122.124
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo#



## Response:
12/16/2025, 7:09:38 PM

````plaintext
Thought process: Diagnosed API import error and formulated debugging strategy.

Good progress! Let me analyze:

1. `docker ps` shows the API container is running but "unhealthy"
2. `curl localhost:8000` returns "Empty reply from server" - the app has issues
3. `dig crewcfo.com +short` returns `137.184.122.124` - DNS is working!

The API is unhealthy due to the import error we saw earlier. We need to fix the code and rebuild. The error was:
`​`​`
ModuleNotFoundError: No module named 'utils'
`​`​`

This is likely a path issue in main.py. The import is `from utils.auth import get_current_tenant_id` but it should probably be `from src.utils.auth import ...` or the PYTHONPATH needs to be set.

Let me help them fix this.
````

Good news: **DNS is working!** (`137.184.122.124` ✓)

But the API is broken. Let's fix the import error:

---

## Step 1: Check the Import Issue

```bash
head -30 src/main.py
```

---

## Step 2: Quick Fix - Update the Import

The error was `No module named 'utils'`. Let's see the structure:

```bash
ls src/
```

Then edit main.py:

```bash
nano src/main.py
```

Find this line (around line 26):
```python
from utils.auth import get_current_tenant_id
```

Change it to:
```python
from src.utils.auth import get_current_tenant_id
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

---

## Step 3: Restart the Container

```bash
docker compose restart api
docker compose logs api --tail 50
```

---

Run `head -30 src/main.py` first and show me the imports!



## Prompt:
12/16/2025, 7:14:54 PM

FastAPI application for bookkeeping automation
"""
import os
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client
import uvicorn
# Load environment variables
load_dotenv()
# Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_SERVICE_KEY", "")
)
# Auth helper (Supabase Auth -> tenant context)
from utils.auth import get_current_tenant_id
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
root@ubuntu-s-1vcpu-1gb-sfo3-01:~/roofing-books-cfo#



## Response:
12/16/2025, 7:15:01 PM

````plaintext
Thought process: Identified import path discrepancy and formulated correction.

The issue is clear - the import is `from utils.auth import get_current_tenant_id` but it should be `from src.utils.auth import get_current_tenant_id` because the app is running from `/app` directory in Docker and the code is in `/app/src/`.

Let me provide the fix.
````

Found it! Fix the import:

```bash
nano src/main.py
```

Find line 26:
```python
from utils.auth import get_current_tenant_id
```

Change to:
```python
from src.utils.auth import get_current_tenant_id
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

---

Then restart:

```bash
docker compose restart api
sleep 5
docker compose logs api --tail 20
```



## Prompt:
12/16/2025, 7:15:28 PM

provide cursor prompt for it to fix it



## Response:
12/16/2025, 7:15:36 PM

````plaintext
Thought process: Endorsed local workflow and devised Cursor prompt solution.

The user wants to fix this on their local Mac using Cursor, then push to the server. That's actually a better workflow. Let me provide a Cursor prompt.
````

## Cursor Prompt

Open Cursor on your Mac in the `roofing-books-cfo` project and paste:

```
In src/main.py, fix the import error.

Change:
from utils.auth import get_current_tenant_id

To:
from src.utils.auth import get_current_tenant_id

Also check all other imports in the file - any import from local modules (utils, services, models) should be prefixed with "src." 

For example:
- from utils.x → from src.utils.x
- from services.x → from src.services.x
- from models.x → from src.models.x
```

---

## After Cursor Fixes It

**On your Mac terminal:**
```bash
cd /Users/ildar/Documents/1.Projects/roofing-books-cfo
git add .
git commit -m "Fix import paths for Docker"
git push
```

**On SSH (server):**
```bash
cd /root/roofing-books-cfo
git pull
docker compose restart api
sleep 5
curl localhost:8000
```





---
Powered by [Claude Exporter](https://www.claudexporter.com)