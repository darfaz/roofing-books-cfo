"""
PDF Generator for Valuation Shock Reports.

Generates professional PDF reports from shock report data.
"""

import io
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class ShockReportPDFGenerator:
    """Generate PDF reports from shock report data."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#334155'),
            spaceBefore=20,
            spaceAfter=10
        ))

        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#475569'),
            spaceBefore=10,
            spaceAfter=5
        ))

        self.styles.add(ParagraphStyle(
            name='ReportBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#475569'),
            spaceAfter=8
        ))

        self.styles.add(ParagraphStyle(
            name='HighlightRed',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#dc2626'),
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='HighlightGreen',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#16a34a'),
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='MoneyBig',
            parent=self.styles['Normal'],
            fontSize=20,
            textColor=colors.HexColor('#1e293b'),
            alignment=TA_CENTER
        ))

    def generate_pdf(self, report: Dict[str, Any], company_name: str = "Your Company") -> bytes:
        """
        Generate a PDF from shock report data.

        Args:
            report: The shock report data dictionary
            company_name: Name of the company for the report header

        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        story = []

        # Title
        story.append(Paragraph("Valuation Shock Report", self.styles['ReportTitle']))
        story.append(Paragraph(f"<b>{company_name}</b>", self.styles['ReportBody']))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y')}",
            self.styles['ReportBody']
        ))
        story.append(Spacer(1, 20))

        # Executive Summary
        story.extend(self._build_executive_summary(report))

        # Value Gap Analysis
        story.extend(self._build_gap_analysis(report))

        # Driver Scores
        story.extend(self._build_driver_scores(report))

        # Multiple Penalties
        if report.get('penalties'):
            story.extend(self._build_penalties(report))

        # Value Unlocks
        if report.get('value_unlocks'):
            story.extend(self._build_value_unlocks(report))

        # Footer
        story.append(Spacer(1, 30))
        story.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#e2e8f0')
        ))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "This report is for informational purposes only and should not be considered "
            "financial or legal advice. Actual transaction values may vary based on market "
            "conditions and buyer negotiations.",
            ParagraphStyle(
                name='Disclaimer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#94a3b8'),
                alignment=TA_CENTER
            )
        ))
        story.append(Paragraph(
            "Powered by CrewCFO - AI-Powered CFO for Roofing Contractors",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#64748b'),
                alignment=TA_CENTER
            )
        ))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def _build_executive_summary(self, report: Dict[str, Any]) -> list:
        """Build executive summary section."""
        elements = []

        reported = report.get('reported', {})
        defensible = report.get('defensible', {})
        gap = report.get('gap', {})

        elements.append(Paragraph("Executive Summary", self.styles['SectionTitle']))

        # Key metrics table
        data = [
            ['Metric', "Owner's View", "Buyer's View", 'Gap'],
            [
                'EBITDA',
                f"${reported.get('ebitda', 0):,.0f}",
                f"${defensible.get('ebitda', 0):,.0f}",
                f"${gap.get('ebitda_haircut', 0):,.0f}"
            ],
            [
                'Multiple',
                f"{reported.get('expected_multiple', 0):.1f}x",
                f"{defensible.get('multiple_low', 0):.1f}x - {defensible.get('multiple_high', 0):.1f}x",
                f"-{gap.get('multiple_penalty', 0):.1f}x"
            ],
            [
                'Valuation',
                f"${reported.get('expected_valuation', 0):,.0f}",
                f"${defensible.get('valuation_low', 0):,.0f} - ${defensible.get('valuation_high', 0):,.0f}",
                f"${gap.get('value_gap', 0):,.0f}"
            ],
        ]

        table = Table(data, colWidths=[1.5*inch, 1.8*inch, 2.2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#334155')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            # Highlight gap column
            ('TEXTCOLOR', (-1, 1), (-1, -1), colors.HexColor('#dc2626')),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        # Value gap highlight
        gap_pct = gap.get('value_gap_pct', 0)
        elements.append(Paragraph(
            f"<b>Value Gap: {gap_pct:.0f}%</b>",
            self.styles['HighlightRed']
        ))
        elements.append(Paragraph(
            f"You may be leaving <b>${gap.get('value_gap', 0):,.0f}</b> on the table",
            self.styles['ReportBody']
        ))

        return elements

    def _build_gap_analysis(self, report: Dict[str, Any]) -> list:
        """Build gap analysis section."""
        elements = []

        gap = report.get('gap', {})

        elements.append(Paragraph("Why The Gap Exists", self.styles['SectionTitle']))

        if gap.get('ebitda_haircut', 0) > 0:
            elements.append(Paragraph(
                f"<b>EBITDA Adjustment:</b> Buyers typically haircut reported EBITDA by "
                f"{gap.get('ebitda_haircut_pct', 0):.0f}% due to undocumented add-backs, "
                "owner-specific expenses, and non-recurring items.",
                self.styles['ReportBody']
            ))

        if gap.get('multiple_penalty', 0) > 0:
            elements.append(Paragraph(
                f"<b>Multiple Reduction:</b> Your business receives a {gap.get('multiple_penalty', 0):.1f}x "
                "lower multiple than industry leaders due to value driver deficiencies.",
                self.styles['ReportBody']
            ))

        elements.append(Spacer(1, 10))

        return elements

    def _build_driver_scores(self, report: Dict[str, Any]) -> list:
        """Build driver scores section."""
        elements = []

        driver_scores = report.get('driver_scores', {})

        elements.append(Paragraph("Value Driver Scores", self.styles['SectionTitle']))

        driver_labels = {
            'management_independence': 'Management Independence',
            'financial_records': 'Financial Records Quality',
            'recurring_revenue': 'Recurring Revenue',
            'customer_diversity': 'Customer Diversity',
            'operational_systems': 'Operational Systems',
            'market_outlook': 'Market Outlook'
        }

        data = [['Driver', 'Score', 'Status']]

        for key, label in driver_labels.items():
            score = driver_scores.get(key, 0)
            if score >= 70:
                status = 'Strong'
                status_color = '#16a34a'
            elif score >= 50:
                status = 'Moderate'
                status_color = '#ca8a04'
            else:
                status = 'Needs Work'
                status_color = '#dc2626'

            data.append([label, f"{score}/100", status])

        table = Table(data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 1), (1, -1), colors.HexColor('#334155')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))

        # Color code status column based on score
        for i, row in enumerate(data[1:], start=1):
            score = driver_scores.get(list(driver_labels.keys())[i-1], 0)
            if score >= 70:
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#16a34a'))
                ]))
            elif score >= 50:
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#ca8a04'))
                ]))
            else:
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#dc2626'))
                ]))

        elements.append(table)
        elements.append(Spacer(1, 15))

        return elements

    def _build_penalties(self, report: Dict[str, Any]) -> list:
        """Build multiple penalties section."""
        elements = []

        penalties = report.get('penalties', [])

        elements.append(Paragraph("Multiple Penalties", self.styles['SectionTitle']))
        elements.append(Paragraph(
            "These factors are reducing your valuation multiple:",
            self.styles['ReportBody']
        ))

        data = [['Driver', 'Penalty', 'Reason']]

        for penalty in penalties:
            data.append([
                penalty.get('driver_key', '').replace('_', ' ').title(),
                f"{penalty.get('penalty_amount', 0):.1f}x",
                penalty.get('reason', '')
            ])

        table = Table(data, colWidths=[1.8*inch, 1*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef2f2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#334155')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#fecaca')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 15))

        return elements

    def _build_value_unlocks(self, report: Dict[str, Any]) -> list:
        """Build value unlocks section."""
        elements = []

        unlocks = report.get('value_unlocks', [])
        total_recoverable = report.get('total_recoverable', 0)

        elements.append(Paragraph("Value Unlock Opportunities", self.styles['SectionTitle']))
        elements.append(Paragraph(
            f"<b>Total Recoverable Value: ${total_recoverable:,.0f}</b>",
            self.styles['HighlightGreen']
        ))
        elements.append(Spacer(1, 10))

        for i, unlock in enumerate(unlocks[:5], start=1):  # Top 5 unlocks
            elements.append(Paragraph(
                f"<b>{i}. {unlock.get('title', 'Improvement')}</b>",
                self.styles['SubSection']
            ))
            elements.append(Paragraph(
                f"<i>{unlock.get('description', '')}</i>",
                self.styles['ReportBody']
            ))

            impact_text = []
            if unlock.get('ebitda_impact', 0) > 0:
                impact_text.append(f"EBITDA +${unlock['ebitda_impact']:,.0f}")
            if unlock.get('multiple_impact', 0) > 0:
                impact_text.append(f"Multiple +{unlock['multiple_impact']:.1f}x")
            if unlock.get('ev_impact', 0) > 0:
                impact_text.append(f"Value +${unlock['ev_impact']:,.0f}")

            if impact_text:
                elements.append(Paragraph(
                    f"Impact: {' | '.join(impact_text)}",
                    self.styles['ReportBody']
                ))

            if unlock.get('timeline'):
                elements.append(Paragraph(
                    f"Timeline: {unlock['timeline']} | Effort: {unlock.get('effort_level', 'medium').title()}",
                    self.styles['ReportBody']
                ))

            elements.append(Spacer(1, 5))

        return elements


def generate_shock_report_pdf(report: Dict[str, Any], company_name: str = "Your Company") -> bytes:
    """
    Convenience function to generate a shock report PDF.

    Args:
        report: The shock report data dictionary
        company_name: Name of the company

    Returns:
        PDF file as bytes
    """
    generator = ShockReportPDFGenerator()
    return generator.generate_pdf(report, company_name)
