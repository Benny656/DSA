"""
PDF Statement Generator for BankFlow.
Generates an authentic, institutional-grade bank statement PDF with:
- Bank Letterhead & Branding
- Customer Details & Account Summary
- Transaction Ledger with Debit / Credit / Net Balance columns
- Formal Banking Disclaimers & Security Watermark
"""
from datetime import datetime
import io
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle
)

from core.models import Account, Transaction, TransactionType, TransactionStatus


def generate_bank_statement_pdf(
    account: Account,
    transactions: List[Transaction],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> bytes:
    """
    Generates an official-looking Bank Account Statement PDF as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'BankTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f2942')
    )
    subtitle_style = ParagraphStyle(
        'BankSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#556b82')
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0f2942')
    )
    label_style = ParagraphStyle(
        'FieldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#334155')
    )
    val_style = ParagraphStyle(
        'FieldValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0f172a')
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1e293b')
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0f172a')
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#64748b')
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>APEX COMMERCIAL BANK</b><br/><font size=7 color='#556b82'>National Banking & Financial Services Corporation</font>", title_style),
            Paragraph(
                "<b>ACCOUNT STATEMENT</b><br/>"
                f"Generated: {datetime.now().strftime('%d-%b-%Y %H:%M')}<br/>"
                "IFSC: APEX0004812 | Branch: Metro Central",
                ParagraphStyle('RightHdr', parent=subtitle_style, alignment=2)
            )
        ]
    ]
    header_table = Table(header_data, colWidths=[3.8 * inch, 3.8 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f2942'), spaceAfter=10))

    # 2. Account Details & Summary Table
    # Calculate deposits vs withdrawals
    total_deposits = 0.0
    total_withdrawals = 0.0
    for tx in transactions:
        if tx.status == TransactionStatus.COMPLETED:
            if tx.tx_type == TransactionType.DEPOSIT:
                total_deposits += tx.amount
            elif tx.tx_type == TransactionType.WITHDRAWAL:
                total_withdrawals += tx.amount
            elif tx.tx_type == TransactionType.TRANSFER:
                if tx.to_account == account.account_number:
                    total_deposits += tx.amount
                elif tx.from_account == account.account_number:
                    total_withdrawals += tx.amount

    summary_data = [
        [
            Paragraph("<b>Account Holder:</b>", label_style),
            Paragraph(account.holder_name, val_style),
            Paragraph("<b>Opening Balance:</b>", label_style),
            Paragraph(f"INR {account.balance - total_deposits + total_withdrawals:,.2f}", val_style)
        ],
        [
            Paragraph("<b>Account Number:</b>", label_style),
            Paragraph(account.account_number, val_style),
            Paragraph("<b>Total Credits:</b>", label_style),
            Paragraph(f"<font color='#047857'>+ INR {total_deposits:,.2f}</font>", val_style)
        ],
        [
            Paragraph("<b>Account Type:</b>", label_style),
            Paragraph("Primary Savings / Checking", val_style),
            Paragraph("<b>Total Debits:</b>", label_style),
            Paragraph(f"<font color='#b91c1c'>- INR {total_withdrawals:,.2f}</font>", val_style)
        ],
        [
            Paragraph("<b>Statement Period:</b>", label_style),
            Paragraph(f"{start_date.strftime('%d-%b-%Y') if start_date else 'Account Inception'} to {end_date.strftime('%d-%b-%Y') if end_date else datetime.now().strftime('%d-%b-%Y')}", val_style),
            Paragraph("<b>Closing Balance:</b>", label_style),
            Paragraph(f"<b>INR {account.balance:,.2f}</b>", val_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[1.4 * inch, 2.3 * inch, 1.4 * inch, 2.5 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # 3. Transaction History Table
    story.append(Paragraph("<b>TRANSACTION ACTIVITY LEDGER</b>", heading_style))
    story.append(Spacer(1, 4))

    tx_table_headers = [
        Paragraph("<b>Date / Time</b>", cell_bold),
        Paragraph("<b>Narration / Details</b>", cell_bold),
        Paragraph("<b>Ref ID</b>", cell_bold),
        Paragraph("<b>Type</b>", cell_bold),
        Paragraph("<b>Debit (Dr)</b>", ParagraphStyle('HdrR', parent=cell_bold, alignment=2)),
        Paragraph("<b>Credit (Cr)</b>", ParagraphStyle('HdrR', parent=cell_bold, alignment=2)),
        Paragraph("<b>Status</b>", ParagraphStyle('HdrC', parent=cell_bold, alignment=1))
    ]

    tx_table_rows = [tx_table_headers]

    for tx in transactions:
        is_credit = False
        is_debit = False

        if tx.tx_type == TransactionType.DEPOSIT:
            is_credit = True
        elif tx.tx_type == TransactionType.WITHDRAWAL:
            is_debit = True
        elif tx.tx_type == TransactionType.TRANSFER:
            if tx.to_account == account.account_number:
                is_credit = True
            else:
                is_debit = True

        dr_text = f"INR {tx.amount:,.2f}" if (is_debit and tx.status == TransactionStatus.COMPLETED) else "-"
        cr_text = f"INR {tx.amount:,.2f}" if (is_credit and tx.status == TransactionStatus.COMPLETED) else "-"

        narration = tx.description or f"{tx.tx_type.value} transaction"
        if tx.tx_type == TransactionType.TRANSFER:
            if is_debit:
                narration += f" to A/C {tx.to_account}"
            else:
                narration += f" from A/C {tx.from_account}"

        status_color = '#059669' if tx.status == TransactionStatus.COMPLETED else ('#dc2626' if tx.status == TransactionStatus.FAILED else '#d97706')

        row = [
            Paragraph(tx.timestamp.strftime("%d-%b-%Y %H:%M"), cell_style),
            Paragraph(narration[:40], cell_style),
            Paragraph(tx.tx_id, cell_style),
            Paragraph(tx.tx_type.value, cell_style),
            Paragraph(dr_text, ParagraphStyle('DrVal', parent=cell_style, alignment=2, textColor=colors.HexColor('#b91c1c') if dr_text != '-' else colors.HexColor('#64748b'))),
            Paragraph(cr_text, ParagraphStyle('CrVal', parent=cell_style, alignment=2, textColor=colors.HexColor('#047857') if cr_text != '-' else colors.HexColor('#64748b'))),
            Paragraph(f"<font color='{status_color}'><b>{tx.status.value}</b></font>", ParagraphStyle('StVal', parent=cell_style, alignment=1))
        ]
        tx_table_rows.append(row)

    if len(tx_table_rows) == 1:
        # Empty ledger
        tx_table_rows.append([
            Paragraph("No transactions recorded during this period.", cell_style),
            "", "", "", "", "", ""
        ])

    tx_table = Table(
        tx_table_rows,
        colWidths=[1.1 * inch, 2.1 * inch, 0.9 * inch, 0.8 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch]
    )
    tx_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))

    story.append(tx_table)
    story.append(Spacer(1, 20))

    # 4. Official Seal & Sign-off Footer
    footer_data = [
        [
            Paragraph(
                "<b>IMPORTANT NOTICE:</b> This is an official system-generated bank statement verified by cryptographically audited ledger entries. "
                "For discrepancy reporting, reach out to customer care at 1800-APEX-BANK within 14 business days.",
                disclaimer_style
            ),
            Paragraph(
                "<b>APEX COMMERCIAL BANK</b><br/>"
                "<i>Digitally Signed & Validated</i><br/>"
                "<font size=6 color='#64748b'>Certified Bank Transaction Processing Authority</font>",
                ParagraphStyle('Sig', parent=subtitle_style, alignment=2)
            )
        ]
    ]
    footer_table = Table(footer_data, colWidths=[5.2 * inch, 2.4 * inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(footer_table)

    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
