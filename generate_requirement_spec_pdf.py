import os
import sys
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Running Header on page 2+
        if self._pageNumber > 1:
            self.drawString(45, 11 * inch - 28, "EXAMSCHEDULER SYSTEM - REQUIREMENT SPECIFICATION ANALYSIS")
            self.setFont("Helvetica", 7.5)
            self.drawRightString(8.5 * inch - 45, 11 * inch - 28, "City College of Angeles (CCA)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(45, 11 * inch - 32, 8.5 * inch - 45, 11 * inch - 32)

        # Running Footer (on all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(45, 34, 8.5 * inch - 45, 34)
        self.setFont("Helvetica", 7.5)
        self.drawString(45, 22, "CONFIDENTIAL - ACADEMIC SPECIFICATION SPECIFICATION & SYSTEM ARCHITECTURE")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 45, 22, page_str)
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=40,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    primary_color = colors.HexColor("#1E3A8A")   # Deep Indigo/Navy
    secondary_color = colors.HexColor("#0284C7") # Ocean Blue
    dark_neutral = colors.HexColor("#0F172A")    # Slate 900
    body_text_color = colors.HexColor("#1E293B") # Slate 800
    subtle_border = colors.HexColor("#CBD5E1")

    styles.add(ParagraphStyle(
        name='DocTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.white,
        alignment=0
    ))

    styles.add(ParagraphStyle(
        name='DocSubTitle',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#E0F2FE"),
        alignment=0
    ))

    styles.add(ParagraphStyle(
        name='MetaText',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#BAE6FD")
    ))

    styles.add(ParagraphStyle(
        name='SecHeader',
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='SubSecHeader',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=secondary_color,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='CustomBody',
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=body_text_color,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name='BulletItem',
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=body_text_color,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2.8
    ))

    styles.add(ParagraphStyle(
        name='TableHeader',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=0
    ))

    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.5,
        textColor=body_text_color
    ))

    styles.add(ParagraphStyle(
        name='TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.5,
        textColor=dark_neutral
    ))

    story = []

    # Banner Table
    banner_content = [
        [Paragraph("REQUIREMENT SPECIFICATION ANALYSIS", styles['DocTitle'])],
        [Paragraph("ExamScheduler: Automated Academic Examination Scheduling System", styles['DocSubTitle'])],
        [Paragraph("<b>Target System:</b> CCA Exam Management System (EXAM_MANAGEMENT) &nbsp;|&nbsp; <b>Institution:</b> City College of Angeles", styles['MetaText'])]
    ]
    banner_table = Table(banner_content, colWidths=[7.4 * inch])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('TOPPADDING', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 2),
        ('TOPPADDING', (0,1), (-1,1), 0),
        ('BOTTOMPADDING', (0,1), (-1,1), 4),
        ('TOPPADDING', (0,2), (-1,2), 3),
        ('BOTTOMPADDING', (0,2), (-1,2), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 6))

    with open('RequirementSpecificationAnalysis_ExamScheduler.md', 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Section 1: System Overview
    m_overview = re.search(r'## 1\. System Overview\s*\n(.*?)(?=\n---|\n## 2)', md_text, re.DOTALL)
    if m_overview:
        story.append(Paragraph("1. System Overview", styles['SecHeader']))
        overview_text = m_overview.group(1).strip()
        overview_box = Table([[Paragraph(overview_text, styles['CustomBody'])]], colWidths=[7.4 * inch])
        overview_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('LINELEFT', (0,0), (-1,-1), 3.5, secondary_color),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        story.append(overview_box)
        story.append(Spacer(1, 6))

    # Section 2: Stakeholders and User Roles
    m_roles = re.search(r'## 2\. Stakeholders and User Roles\s*\n(.*?)(?=\n---|\n## 3)', md_text, re.DOTALL)
    if m_roles:
        story.append(Paragraph("2. Stakeholders and User Roles", styles['SecHeader']))
        roles_raw = m_roles.group(1).strip()
        role_lines = re.findall(r'(\d+)\.\s*\*\*([^*]+)\*\*:\s*(.*)', roles_raw)
        
        roles_table_data = [
            [Paragraph("<b>No.</b>", styles['TableHeader']), Paragraph("<b>Stakeholder / User Role</b>", styles['TableHeader']), Paragraph("<b>Core Institutional Responsibilities & Scope</b>", styles['TableHeader'])]
        ]
        for num, r_name, r_desc in role_lines:
            roles_table_data.append([
                Paragraph(f"<b>{num}</b>", styles['TableCellBold']),
                Paragraph(f"<b>{r_name.strip()}</b>", styles['TableCellBold']),
                Paragraph(r_desc.strip(), styles['TableCell'])
            ])
        t_roles = Table(roles_table_data, colWidths=[0.4 * inch, 2.1 * inch, 4.9 * inch])
        t_roles.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('GRID', (0,0), (-1,-1), 0.5, subtle_border),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_roles)
        story.append(Spacer(1, 6))

    # Section 3: General & Core Authentication Modules
    m_core = re.search(r'## 3\. General & Core Authentication Modules\s*\n(.*?)(?=\n---|\n## 4)', md_text, re.DOTALL)
    if m_core:
        story.append(Paragraph("3. General & Core Authentication Modules", styles['SecHeader']))
        core_raw = m_core.group(1).strip()
        bullets = re.findall(r'^\*\s+\*\*([^*:]+):?\*\*:?\s*(.*)$', core_raw, re.MULTILINE)
        for b_name, b_desc in bullets:
            story.append(Paragraph(f"<b>&bull; {b_name.strip()}:</b> {b_desc.strip()}", styles['BulletItem']))
        story.append(Spacer(1, 6))

    # Section 4: Functional Requirements by User Role
    story.append(Paragraph("4. Functional Requirements by User Role", styles['SecHeader']))

    # Split sub-sections 4.1 to 4.7
    subsections = re.findall(r'### (4\.\d+\s+[^\n]+)\s*\n(.*?)(?=\n### 4\.\d+|\n## 5|\Z)', md_text, re.DOTALL)
    for title, content in subsections:
        story.append(Paragraph(title.strip(), styles['SubSecHeader']))
        
        lines = content.strip().split('\n')
        intro_lines = []
        for line in lines:
            line_s = line.strip()
            if line_s.startswith('* **'):
                break
            if line_s and not line_s.startswith('---'):
                intro_lines.append(line_s)
        
        if intro_lines:
            story.append(Paragraph(" ".join(intro_lines), styles['CustomBody']))
        
        bullets = re.findall(r'^\*\s+\*\*([^*:]+):?\*\*:?\s*(.*)$', content, re.MULTILINE)
        for b_name, b_desc in bullets:
            story.append(Paragraph(f"<b>&bull; {b_name.strip()}:</b> {b_desc.strip()}", styles['BulletItem']))
        story.append(Spacer(1, 4))

    # Section 5: Non-Functional Requirements
    m_nfr = re.search(r'## 5\. Non-Functional Requirements\s*\n(.*?)(?=\Z)', md_text, re.DOTALL)
    if m_nfr:
        story.append(Paragraph("5. Non-Functional Requirements", styles['SecHeader']))
        nfr_raw = m_nfr.group(1).strip()
        bullets = re.findall(r'^\*\s+\*\*([^*:]+):?\*\*:?\s*(.*)$', nfr_raw, re.MULTILINE)
        for b_name, b_desc in bullets:
            story.append(Paragraph(f"<b>&bull; {b_name.strip()}:</b> {b_desc.strip()}", styles['BulletItem']))
        story.append(Spacer(1, 6))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF built successfully: {filename}")

if __name__ == '__main__':
    target_path = r"c:\xampp\htdocs\EXAM_MANAGEMENT\Requirement_Specification_Analysis_ExamScheduler.pdf"
    static_path = r"c:\xampp\htdocs\EXAM_MANAGEMENT\static\Requirement_Specification_Analysis_ExamScheduler.pdf"
    build_pdf(target_path)
    build_pdf(static_path)
