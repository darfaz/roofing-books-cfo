-- ============================================================
-- DEMO DATA SEED MIGRATION
-- ============================================================
-- Creates a demo tenant "Apex Roofing Solutions" with realistic
-- financials, profit leaks, and valuation data for showcasing
-- all CrewCFO dashboard features.
--
-- Demo Company Profile:
-- - Revenue: $3.5M annual
-- - 12 employees
-- - Mixed residential/commercial (70/30)
-- - Texas-based
-- - Owner-operator with key-person risk
-- - 5 identified profit leaks
-- ============================================================

-- Create demo tenant
INSERT INTO tenants (id, company_name, industry, annual_revenue, employee_count, created_at)
VALUES (
    'demo-0000-0000-0000-000000000001'::uuid,
    'Apex Roofing Solutions',
    'Roofing Contractor',
    3500000,
    12,
    NOW() - INTERVAL '2 years'
) ON CONFLICT (id) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    annual_revenue = EXCLUDED.annual_revenue;

-- ============================================================
-- VALUATION SHOCK REPORT
-- Shows the "expected vs actual" gap that shocks owners
-- ============================================================
INSERT INTO valuation_shock_reports (
    id,
    tenant_id,
    generated_at,
    -- What owner thinks (reported/expected)
    reported_revenue,
    reported_ebitda,
    reported_owner_comp,
    reported_addbacks,
    expected_multiple,
    expected_valuation,
    -- What buyer sees (defensible)
    defensible_ebitda,
    defensible_sde,
    buyer_multiple_low,
    buyer_multiple_high,
    buyer_valuation_low,
    buyer_valuation_high,
    -- The gap (the shock)
    ebitda_haircut,
    multiple_penalty,
    value_gap,
    value_gap_percentage,
    -- Detailed breakdowns
    ebitda_adjustments,
    multiple_penalties,
    driver_scores,
    -- Value recovery
    value_unlocks,
    total_recoverable_value,
    -- Tier
    tier,
    -- Data quality
    qbo_data_range_start,
    qbo_data_range_end,
    transaction_count,
    invoice_count,
    expense_count,
    confidence_score
) VALUES (
    'demo-rpt-0000-0000-000000000001'::uuid,
    'demo-0000-0000-0000-000000000001'::uuid,
    NOW(),
    -- Owner expects: $3.5M revenue, $350K "EBITDA", 10x = $3.5M valuation
    3500000,
    350000,
    180000,
    95000,
    10.0,
    3500000,
    -- Buyer sees: $245K defensible EBITDA, 3.5x multiple = $857K
    245000,
    395000,
    3.0,
    4.0,
    735000,
    980000,
    -- The shock: $105K haircut, -6.5x multiple penalty, $2.5M+ gap
    105000,
    6.5,
    2520000,
    72.0,
    -- EBITDA adjustments (what buyer rejects)
    '[
        {"type": "owner_compensation", "description": "Owner salary above market rate", "amount": 180000, "accepted": 120000, "rejected": 60000, "reason": "Market rate for GM is $120K"},
        {"type": "personal_expense", "description": "Personal vehicle through company", "amount": 18000, "accepted": 0, "rejected": 18000, "reason": "100% personal use vehicle"},
        {"type": "related_party", "description": "Wife on payroll (no clear duties)", "amount": 45000, "accepted": 15000, "rejected": 30000, "reason": "Part-time admin work valued at $15K"},
        {"type": "one_time_expense", "description": "Lawsuit settlement", "amount": 25000, "accepted": 25000, "rejected": 0, "reason": "Non-recurring, buyer accepts"},
        {"type": "discretionary", "description": "Country club membership", "amount": 12000, "accepted": 0, "rejected": 12000, "reason": "Personal expense"}
    ]'::jsonb,
    -- Multiple penalties (why 3.5x vs 7x)
    '[
        {"driver": "management_independence", "penalty": -1.5, "score": 25, "reason": "Owner IS the business - no #2, no succession plan"},
        {"driver": "recurring_revenue", "penalty": -1.0, "score": 15, "reason": "0% recurring revenue - 100% project-based"},
        {"driver": "financial_records", "penalty": -0.5, "score": 55, "reason": "Mixed personal/business, delayed reconciliation"},
        {"driver": "customer_diversity", "penalty": -0.5, "score": 45, "reason": "Top 3 customers = 42% of revenue"}
    ]'::jsonb,
    -- Driver scores (0-100)
    '{
        "management_independence": 25,
        "financial_records": 55,
        "recurring_revenue": 15,
        "operational_systems": 60,
        "customer_diversity": 45,
        "market_outlook": 75
    }'::jsonb,
    -- Value unlocks (what to fix)
    '[
        {"priority": 1, "title": "Hire Operations Manager", "ev_impact": 350000, "effort": "high", "timeline": "6-12 months"},
        {"priority": 2, "title": "Launch Maintenance Program", "ev_impact": 280000, "effort": "medium", "timeline": "3-6 months"},
        {"priority": 3, "title": "Clean Personal Expenses", "ev_impact": 175000, "effort": "low", "timeline": "1-3 months"},
        {"priority": 4, "title": "Diversify Customer Base", "ev_impact": 150000, "effort": "high", "timeline": "12+ months"},
        {"priority": 5, "title": "Document SOPs", "ev_impact": 125000, "effort": "medium", "timeline": "3-6 months"}
    ]'::jsonb,
    1080000,
    'below_avg',
    DATE '2024-01-01',
    DATE '2024-12-31',
    2847,
    342,
    1892,
    78
) ON CONFLICT (id) DO UPDATE SET
    generated_at = NOW(),
    value_gap = EXCLUDED.value_gap;

-- ============================================================
-- DRIVER SCORES (6 Matador categories)
-- ============================================================
INSERT INTO driver_scores (tenant_id, as_of_date, driver_key, score, weight, evidence_refs, computed_by, confidence, automation_tier, impact_on_multiple)
VALUES
    ('demo-0000-0000-0000-000000000001'::uuid, CURRENT_DATE, 'management_independence', 25, 1.0,
     '["Owner handles all estimates", "No operations manager", "No documented succession plan"]'::jsonb,
     'system', 85, 'hybrid', -1.50),
    ('demo-0000-0000-0000-000000000001'::uuid, CURRENT_DATE, 'financial_records', 55, 1.0,
     '["QuickBooks connected", "Monthly close delayed 15+ days", "Personal expenses mixed"]'::jsonb,
     'system', 82, 'hybrid', -0.50),
    ('demo-0000-0000-0000-000000000001'::uuid, CURRENT_DATE, 'recurring_revenue', 15, 1.0,
     '["No maintenance contracts", "100% project revenue", "No service agreements"]'::jsonb,
     'system', 90, 'rules', -1.00),
    ('demo-0000-0000-0000-000000000001'::uuid, CURRENT_DATE, 'operational_systems', 60, 1.0,
     '["Uses JobNimbus CRM", "Paper-based safety checklists", "No formal SOPs"]'::jsonb,
     'system', 78, 'hybrid', 0.00),
    ('demo-0000-0000-0000-000000000001'::uuid, CURRENT_DATE, 'customer_diversity', 45, 1.0,
     '["Top 3 customers = 42% revenue", "Builder concentration risk", "Good geographic spread"]'::jsonb,
     'system', 88, 'rules', -0.50),
    ('demo-0000-0000-0000-000000000001'::uuid, CURRENT_DATE, 'market_outlook', 75, 1.0,
     '["Strong Texas market", "PE consolidation active", "Labor shortage challenges"]'::jsonb,
     'system', 80, 'hybrid', 0.00)
ON CONFLICT (tenant_id, as_of_date, driver_key) DO UPDATE SET
    score = EXCLUDED.score,
    impact_on_multiple = EXCLUDED.impact_on_multiple;

-- ============================================================
-- ROADMAP ITEMS (Strategic action plan)
-- ============================================================
INSERT INTO roadmap_items (tenant_id, driver_key, title, description, category, priority, status, expected_impact_ev, effort_level, automation_tier, due_date)
VALUES
    -- Critical: Management Independence
    ('demo-0000-0000-0000-000000000001'::uuid, 'management_independence',
     'Hire Operations Manager',
     'Recruit and onboard an operations manager to handle day-to-day decisions, crew scheduling, and customer communication. Target: owner involvement drops from 60+ hrs/week to 20 hrs/week.',
     'strategic', 'critical', 'pending', 350000, 'high', 'hybrid',
     CURRENT_DATE + INTERVAL '6 months'),

    ('demo-0000-0000-0000-000000000001'::uuid, 'management_independence',
     'Document All SOPs',
     'Create written Standard Operating Procedures for: estimating, job scheduling, safety protocols, customer communication, and accounting processes.',
     'strategic', 'high', 'in_progress', 125000, 'medium', 'hybrid',
     CURRENT_DATE + INTERVAL '3 months'),

    -- High: Recurring Revenue
    ('demo-0000-0000-0000-000000000001'::uuid, 'recurring_revenue',
     'Launch Maintenance Contract Program',
     'Create annual roof maintenance contracts ($350-500/year residential, $0.04/sqft commercial). Target: 200 contracts in Year 1 = $70K+ recurring revenue.',
     'strategic', 'critical', 'pending', 280000, 'medium', 'hybrid',
     CURRENT_DATE + INTERVAL '4 months'),

    ('demo-0000-0000-0000-000000000001'::uuid, 'recurring_revenue',
     'Implement Extended Warranty Program',
     'Offer 10-year extended labor warranty for premium ($500-1,000 upcharge). Creates deferred revenue and customer lock-in.',
     'strategic', 'medium', 'pending', 85000, 'low', 'hybrid',
     CURRENT_DATE + INTERVAL '2 months'),

    -- High: Financial Records
    ('demo-0000-0000-0000-000000000001'::uuid, 'financial_records',
     'Clean Up Personal Expenses',
     'Remove all personal expenses from P&L: personal vehicle ($18K), country club ($12K), wife''s non-business salary portion ($30K). Transfer to owner distributions.',
     'monthly_close', 'high', 'in_progress', 175000, 'low', 'rules',
     CURRENT_DATE + INTERVAL '1 month'),

    ('demo-0000-0000-0000-000000000001'::uuid, 'financial_records',
     'Implement 5-Day Close Process',
     'Close books within 5 business days of month-end. Current: 15+ days. Required: bank reconciliation, AR/AP review, WIP adjustment.',
     'monthly_close', 'high', 'pending', 50000, 'medium', 'hybrid',
     CURRENT_DATE + INTERVAL '2 months'),

    -- Medium: Customer Diversity
    ('demo-0000-0000-0000-000000000001'::uuid, 'customer_diversity',
     'Reduce Builder Concentration',
     'Target: No single customer >15% of revenue. Current: Top 3 = 42%. Action: increase residential marketing, add 2 new commercial property managers.',
     'quarterly_review', 'high', 'in_progress', 150000, 'high', 'hybrid',
     CURRENT_DATE + INTERVAL '12 months'),

    -- Medium: Operational Systems
    ('demo-0000-0000-0000-000000000001'::uuid, 'operational_systems',
     'Implement Job Costing System',
     'Track actual vs. estimated costs per job. Integrate with QuickBooks for real-time profitability visibility.',
     'strategic', 'medium', 'pending', 75000, 'medium', 'hybrid',
     CURRENT_DATE + INTERVAL '3 months'),

    ('demo-0000-0000-0000-000000000001'::uuid, 'operational_systems',
     'Digitize Safety Checklists',
     'Replace paper safety checklists with digital forms. Improves compliance documentation for insurance and due diligence.',
     'compliance', 'medium', 'pending', 25000, 'low', 'rules',
     CURRENT_DATE + INTERVAL '1 month')
ON CONFLICT DO NOTHING;

-- ============================================================
-- VALUATION SNAPSHOT (Current state)
-- ============================================================
INSERT INTO valuation_snapshots (
    tenant_id, as_of_date, ttm_revenue, ttm_sde, ttm_ebitda,
    tier, multiple_low, multiple_high, ev_low, ev_high,
    confidence_score, drivers_json, computed_by, automation_tier
)
VALUES (
    'demo-0000-0000-0000-000000000001'::uuid,
    CURRENT_DATE,
    3500000,
    395000,
    245000,
    'below_avg',
    3.0,
    4.0,
    735000,
    980000,
    78,
    '{
        "management_independence": {"score": 25, "impact": -1.5},
        "financial_records": {"score": 55, "impact": -0.5},
        "recurring_revenue": {"score": 15, "impact": -1.0},
        "operational_systems": {"score": 60, "impact": 0},
        "customer_diversity": {"score": 45, "impact": -0.5},
        "market_outlook": {"score": 75, "impact": 0}
    }'::jsonb,
    'system',
    'hybrid'
)
ON CONFLICT DO NOTHING;

-- ============================================================
-- EBITDA ADJUSTMENTS (Detailed buyer perspective)
-- ============================================================
INSERT INTO ebitda_adjustments (tenant_id, shock_report_id, adjustment_type, category, description, amount, accepted_amount, buyer_concern, rejection_reason, is_recoverable, remediation_action, remediation_effort, remediation_impact)
VALUES
    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     'owner_compensation', 'partial',
     'Owner salary of $180,000 exceeds market rate for General Manager role',
     180000, 120000,
     'Above-market owner compensation reduces normalized earnings',
     'Market rate for GM in Texas roofing is $110-130K. Excess $60K is owner profit extraction.',
     true,
     'Document market-rate salary; treat excess as distribution',
     'low', 175000),

    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     'personal_expense', 'rejected',
     'Personal vehicle (BMW X5) fully expensed through company',
     18000, 0,
     'Personal vehicle with no business log',
     'No mileage log. Vehicle used primarily for personal transportation.',
     true,
     'Separate personal vehicle; implement mileage tracking for business vehicles',
     'low', 52500),

    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     'related_party', 'partial',
     'Spouse on payroll at $45,000 with unclear job duties',
     45000, 15000,
     'Related party transaction without clear value',
     'No job description or time records. Estimated 10 hrs/week admin work = $15K value.',
     true,
     'Document job duties; adjust salary to market rate or remove',
     'low', 87500),

    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     'one_time_expense', 'accepted',
     'Legal settlement for customer dispute',
     25000, 25000,
     NULL,
     NULL,
     false, NULL, NULL, 0),

    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     'discretionary', 'rejected',
     'Country club membership and golf expenses',
     12000, 0,
     'Entertainment expense with no documented business purpose',
     'No client entertainment log. Appears to be personal lifestyle expense.',
     true,
     'Remove from business expenses; pay personally',
     'low', 35000)
ON CONFLICT DO NOTHING;

-- ============================================================
-- MULTIPLE PENALTIES (Why not 7x)
-- ============================================================
INSERT INTO multiple_penalties (tenant_id, shock_report_id, driver_key, penalty_amount, baseline_multiple, resulting_multiple, driver_score, reason, buyer_concern, due_diligence_flag, remediation_action, remediation_timeline, remediation_effort, multiple_recovery)
VALUES
    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     'management_independence', -1.5, 7.0, 5.5, 25,
     'Owner IS the business',
     'Key person risk: owner handles all sales, estimates, and major decisions. No second-in-command or succession plan.',
     'Require transition support; earnout structure',
     'Hire operations manager; document all processes; create succession plan',
     '6-12 months', 'high', 1.0),

    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     'recurring_revenue', -1.0, 5.5, 4.5, 15,
     'Zero recurring revenue',
     '100% project-based revenue creates unpredictable cash flow and no customer lock-in.',
     'Revenue concentration risk; pipeline visibility',
     'Launch maintenance contract program; target 20% recurring within 18 months',
     '12-18 months', 'medium', 0.75),

    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     'financial_records', -0.5, 4.5, 4.0, 55,
     'Messy books',
     'Personal expenses mixed with business; monthly close delayed 15+ days; add-backs need verification.',
     'Quality of earnings study required; personal expense audit',
     'Clean up chart of accounts; implement 5-day close; separate personal expenses',
     '1-3 months', 'low', 0.5),

    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     'customer_diversity', -0.5, 4.0, 3.5, 45,
     'Customer concentration',
     'Top 3 customers represent 42% of revenue. Loss of key builder relationship could significantly impact earnings.',
     'Customer contract review; relationship durability',
     'Diversify customer base; reduce single customer to <15% of revenue',
     '12+ months', 'high', 0.25)
ON CONFLICT DO NOTHING;

-- ============================================================
-- VALUE UNLOCKS (Prioritized roadmap for value creation)
-- ============================================================
INSERT INTO value_unlocks (tenant_id, shock_report_id, priority_rank, title, description, action_type, ebitda_impact, multiple_impact, ev_impact, effort_level, timeline, related_driver, is_locked, is_preview)
VALUES
    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     1, 'Hire Operations Manager',
     'Reduce owner dependence from 60+ hours/week to 20 hours/week. Creates transferable business value and improves multiple.',
     'multiple_expansion', 0, 1.0, 350000, 'high', '6-12 months',
     'management_independence', false, false),

    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     2, 'Launch Maintenance Contracts',
     'Create recurring revenue stream with annual roof maintenance contracts. Target: 200 contracts = $70K+ recurring revenue.',
     'multiple_expansion', 70000, 0.75, 280000, 'medium', '3-6 months',
     'recurring_revenue', false, false),

    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     3, 'Clean Up Personal Expenses',
     'Remove $60K of personal expenses from P&L. Increases defensible EBITDA and signals clean books to buyers.',
     'ebitda_recovery', 60000, 0, 175000, 'low', '1-3 months',
     'financial_records', false, false),

    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     4, 'Diversify Customer Base',
     'Reduce top customer concentration from 42% to under 30%. Add new commercial property management relationships.',
     'risk_reduction', 0, 0.25, 150000, 'high', '12+ months',
     'customer_diversity', true, true),

    ('demo-0000-0000-0000-000000000001'::uuid, 'demo-rpt-0000-0000-000000000001'::uuid,
     5, 'Document All SOPs',
     'Create written procedures for estimating, scheduling, safety, and accounting. Makes business transferable.',
     'multiple_expansion', 0, 0.25, 125000, 'medium', '3-6 months',
     'management_independence', true, true)
ON CONFLICT DO NOTHING;

-- ============================================================
-- COMMENT FOR DOCUMENTATION
-- ============================================================
COMMENT ON TABLE tenants IS 'Demo tenant demo-0000-0000-0000-000000000001 = Apex Roofing Solutions for demo mode';
