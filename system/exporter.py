from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
from datetime import datetime, timedelta

def export_schedule_pdf(grouped_schedule, conflict_ids=None):
    """Returns bytes of a PDF with the full exam schedule.
    grouped_schedule is a list of (date_str, [exam_dicts]) sorted by date.
    Conflict rows are highlighted in red."""
    if conflict_ids is None: conflict_ids = []
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph("Exam Schedule Report", styles['Title']))
    elements.append(Spacer(1, 12))
    
    for date_str, exams in grouped_schedule:
        elements.append(Paragraph(f"Date: {date_str}", styles['Heading2']))
        
        data = [['Time', 'Subject', 'Section', 'Type', 'Room', 'Proctor']]
        
        for e in exams:
            dt = e.get('exam_date_time')
            dur = int(e.get('duration_minutes') or 60)
            if dt:
                if isinstance(dt, str):
                    try:
                        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pass
                if isinstance(dt, datetime):
                    end_dt = dt + timedelta(minutes=dur)
                    time_str = f"{dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
                else:
                    time_str = str(dt)
            else:
                time_str = 'N/A'
            data.append([
                time_str,
                e.get('subject_name', ''),
                e.get('section', ''),
                e.get('subject_type', ''),
                e.get('room_name', ''),
                e.get('instructor_name', '')
            ])
            
        if len(data) > 1:
            t = Table(data, repeatRows=1)
            
            tStyle = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ])
            
            for i, e in enumerate(exams):
                if e.get('exam_id') in conflict_ids or e.get('id') in conflict_ids:
                    tStyle.add('BACKGROUND', (0, i+1), (-1, i+1), colors.lightpink)
                    
            t.setStyle(tStyle)
            elements.append(t)
        else:
            elements.append(Paragraph("No exams scheduled for this date.", styles['Normal']))
        elements.append(Spacer(1, 20))
        
    doc.build(elements)
    return buffer.getvalue()

def export_proctor_report_pdf(proctor_hours, absence_report):
    """Returns bytes of a PDF proctor assignment + absence report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph("Proctor Report", styles['Title']))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("Proctor Hours Summary", styles['Heading2']))
    
    data = [['Instructor Name', 'Total Exams', 'Total Hours']]
    for p in proctor_hours:
        tot = float(p.get('total_hours') or 0.0)
        tot_str = str(int(tot)) if tot.is_integer() else f"{tot:.1f}"
        data.append([p.get('name', ''), str(p.get('exam_count', 0)), tot_str])
        
    if len(data) > 1:
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No proctor data available.", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Proctor Absences", styles['Heading2']))
    if absence_report:
        data2 = [['Date', 'Instructor', 'Exam', 'Reported By']]
        for a in absence_report:
            dt = a.get('reported_at')
            dt_str = dt.strftime('%Y-%m-%d %H:%M') if dt else ''
            data2.append([
                dt_str,
                a.get('instructor_name', ''),
                a.get('subject_name', ''),
                a.get('reported_by', '')
            ])
        t2 = Table(data2)
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t2)
    else:
        elements.append(Paragraph("No absences reported.", styles['Normal']))
        
    doc.build(elements)
    return buffer.getvalue()

def export_collection_report_pdf(collection_data):
    """Returns bytes of a PDF exam collection tracking report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    elements.append(Paragraph("Exam Collection Tracking Report", styles['Title']))
    elements.append(Spacer(1, 12))
    
    data = [['Exam Date & Time', 'Subject', 'Section', 'Collected At', 'Returned At']]
    for c in collection_data:
        dt = c.get('exam_date_time')
        dur = int(c.get('duration_minutes') or 60)
        c_at = c.get('collected_at')
        r_at = c.get('returned_at')
        if dt:
            if isinstance(dt, str):
                try:
                    dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass
            if isinstance(dt, datetime):
                end_dt = dt + timedelta(minutes=dur)
                dt_str = f"{dt.strftime('%b %d, %Y')} ({dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')})"
            else:
                dt_str = str(dt)
        else:
            dt_str = 'N/A'
        
        data.append([
            dt_str,
            c.get('subject_name', ''),
            c.get('section', ''),
            c_at.strftime('%Y-%m-%d %H:%M') if c_at else 'Pending',
            r_at.strftime('%Y-%m-%d %H:%M') if r_at else 'Pending'
        ])
        
    if len(data) > 1:
        t = Table(data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No exam collection data available.", styles['Normal']))
        
    doc.build(elements)
    return buffer.getvalue()

def export_archive_pdf(archive):
    """Returns bytes of a PDF for an archived exam schedule."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=28
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ArchiveTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#27361b')
    )
    subtitle_style = ParagraphStyle(
        'ArchiveSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#668054')
    )
    meta_style = ParagraphStyle(
        'ArchiveMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#374151')
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1f2937')
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=cell_style,
        fontName='Helvetica-Bold'
    )
    cell_th = ParagraphStyle(
        'CellTH',
        parent=cell_style,
        fontName='Helvetica-Bold',
        textColor=colors.whitesmoke
    )

    elements = []

    # Header
    elements.append(Paragraph("CITY COLLEGE OF ANGELES", subtitle_style))
    elements.append(Paragraph(f"Exam Archive: {archive.get('archive_title', 'Archived Schedule')}", title_style))
    elements.append(Spacer(1, 6))

    ay = archive.get('academic_year') or 'N/A'
    sem = archive.get('exam_semester') or 'N/A'
    term = archive.get('exam_term') or 'N/A'
    total_exams = archive.get('total_exams', len(archive.get('exams', [])))
    total_proctors = archive.get('total_proctors', 0)
    total_sections = archive.get('total_sections', 0)
    arch_at = str(archive.get('archived_at', ''))[:19]
    arch_by = archive.get('archived_by_name') or 'System'

    meta_line1 = f"<b>Academic Year:</b> {ay} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Semester:</b> {sem} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Term:</b> {term} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Total Exams:</b> {total_exams} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Proctors:</b> {total_proctors} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Sections:</b> {total_sections}"
    meta_line2 = f"<b>Archived On:</b> {arch_at} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Archived By:</b> {arch_by}"
    elements.append(Paragraph(meta_line1, meta_style))
    elements.append(Paragraph(meta_line2, meta_style))
    if archive.get('notes'):
        elements.append(Paragraph(f"<b>Notes:</b> {archive.get('notes')}", meta_style))
    elements.append(Spacer(1, 10))

    headers = ['Date', 'Time', 'Code', 'Subject Name', 'Section', 'Room', 'Proctor', 'Institute']
    data = [[Paragraph(f"<b>{h}</b>", cell_th) for h in headers]]

    exams = archive.get('exams', [])
    if exams:
        for ex in exams:
            d_str = ex.get('formatted_date') or (ex.get('exam_date_time', '')[:10] if ex.get('exam_date_time') else 'N/A')
            t_start = ex.get('formatted_time', '')
            t_end = ex.get('formatted_time_end', '')
            t_str = f"{t_start} - {t_end}" if (t_start and t_end) else (t_start or t_end or 'TBA')
            code = ex.get('subject_code') or '-'
            subj = ex.get('subject_name') or '-'
            sec = ex.get('section') or '-'
            r_name = ex.get('room_name') or 'TBA'
            bldg = f" ({ex.get('building')})" if ex.get('building') else ''
            room_str = f"{r_name}{bldg}"
            proc = ex.get('instructor_name') or 'Unassigned'
            inst = ex.get('institute_code') or ex.get('institute_name') or '-'

            data.append([
                Paragraph(d_str, cell_style),
                Paragraph(t_str, cell_style),
                Paragraph(code, cell_bold),
                Paragraph(subj, cell_style),
                Paragraph(sec, cell_style),
                Paragraph(room_str, cell_style),
                Paragraph(proc, cell_style),
                Paragraph(inst, cell_style)
            ])

        col_widths = [80, 85, 55, 175, 65, 100, 140, 70]
        t = Table(data, colWidths=col_widths, repeatRows=1)

        t_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#668054')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                t_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9fafb')))
        t.setStyle(TableStyle(t_style))
        elements.append(t)
    else:
        elements.append(Paragraph("No scheduled exam records found in this archive snapshot.", styles['Normal']))

    def _draw_page_footer(canvas, d):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#6b7280'))
        canvas.drawString(24, 14, "City College of Angeles • Examination Management System")
        footer_text = f"Page {d.page}"
        canvas.drawRightString(841.89 - 24, 14, footer_text)
        canvas.restoreState()

    doc.build(elements, onFirstPage=_draw_page_footer, onLaterPages=_draw_page_footer)
    return buffer.getvalue()



def export_proctor_duty_slip_pdf(proctor_name, exams, exam_term='Midterm', exam_semester='1st Semester', total_hours=0.0):
    """Generates an official A4 portrait Faculty Proctoring Duty Schedule / Invigilation Slip PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=28,
        bottomMargin=28
    )
    styles = getSampleStyleSheet()
    elements = []
    
    univ_style = ParagraphStyle(
        'UnivStyleP',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        textColor=colors.HexColor('#27361b')
    )
    sub_univ_style = ParagraphStyle(
        'SubUnivStyleP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#475569')
    )
    doc_title_style = ParagraphStyle(
        'DocTitleStyleP',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#3d5c2e'),
        alignment=1
    )
    doc_sub_style = ParagraphStyle(
        'DocSubStyleP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )
    meta_label = ParagraphStyle(
        'MetaLabelP',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#334155')
    )
    meta_val = ParagraphStyle(
        'MetaValP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0f172a')
    )
    th_style = ParagraphStyle(
        'THStyleP',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1
    )
    td_style = ParagraphStyle(
        'TDStyleP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        alignment=1
    )
    td_left = ParagraphStyle(
        'TDLeftP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        alignment=0
    )
    td_bold = ParagraphStyle(
        'TDBoldP',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#2d4a22'),
        alignment=1
    )

    # University Header
    elements.append(Paragraph("CITY COLLEGE OF ANGELES", univ_style))
    elements.append(Paragraph("Arayat Blvd, Barangay Pampang, Angeles City, Pampanga &bull; info@cca.edu.ph", sub_univ_style))
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("FACULTY PROCTORING DUTY SCHEDULE", doc_title_style))
    elements.append(Paragraph(f"{exam_term} Examination &bull; {exam_semester}, Academic Year 2025-2026", doc_sub_style))
    elements.append(Spacer(1, 10))

    # Proctor Metadata Box
    tot_hrs_str = f"{total_hours:.1f}".rstrip('0').rstrip('.') if isinstance(total_hours, float) else str(total_hours)
    meta_data = [
        [
            Paragraph("<b>Faculty Proctor:</b>", meta_label),
            Paragraph(str(proctor_name or 'N/A'), meta_val),
            Paragraph("<b>Total Duty Hours:</b>", meta_label),
            Paragraph(f"{tot_hrs_str} hrs", meta_val)
        ],
        [
            Paragraph("<b>Institution:</b>", meta_label),
            Paragraph("City College of Angeles", meta_val),
            Paragraph("<b>Assigned Sessions:</b>", meta_label),
            Paragraph(f"{len(exams)} Exam Session(s)", meta_val)
        ]
    ]
    meta_t = Table(meta_data, colWidths=[90, 180, 100, 169])
    meta_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(meta_t)
    elements.append(Spacer(1, 12))

    # Exam Table
    headers = [
        Paragraph("<b>#</b>", th_style),
        Paragraph("<b>Subject / Course</b>", th_style),
        Paragraph("<b>Section</b>", th_style),
        Paragraph("<b>Exam Date</b>", th_style),
        Paragraph("<b>Time Window</b>", th_style),
        Paragraph("<b>Dur.</b>", th_style),
        Paragraph("<b>Room / Venue</b>", th_style),
    ]
    table_data = [headers]

    for idx, e in enumerate(exams, 1):
        dt = e.get('exam_date_time')
        dur = int(e.get('duration_minutes') or 60)
        date_str = 'TBD'
        time_str = 'TBD'
        if dt:
            if isinstance(dt, str):
                try:
                    dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass
            if isinstance(dt, datetime):
                end_dt = dt + timedelta(minutes=dur)
                date_str = dt.strftime("%b %d, %Y")
                time_str = f"{dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
            else:
                date_str = str(dt)

        subj = e.get('subject_name', '')
        if e.get('subject_code'):
            subj_cell = Paragraph(f"<b>{subj}</b><br/><font color='#64748b' size=6>{e.get('subject_code')}</font>", td_left)
        else:
            subj_cell = Paragraph(f"<b>{subj}</b>", td_left)

        table_data.append([
            Paragraph(str(idx), td_style),
            subj_cell,
            Paragraph(str(e.get('section', '')), td_style),
            Paragraph(date_str, td_style),
            Paragraph(time_str, td_bold),
            Paragraph(f"{dur}m", td_style),
            Paragraph(str(e.get('room_name') or 'TBA'), td_style)
        ])

    if len(table_data) > 1:
        t = Table(table_data, colWidths=[20, 155, 60, 74, 125, 35, 70], repeatRows=1)
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3d5c2e')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ]
        for r in range(1, len(table_data)):
            if r % 2 == 0:
                t_style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#f8fafc')))
        t.setStyle(TableStyle(t_style))
        elements.append(t)
    else:
        elements.append(Paragraph("No proctoring assignments found for this period.", styles['Normal']))

    elements.append(Spacer(1, 14))

    # Instructions & Signatures
    reminders_style = ParagraphStyle(
        'RemindersP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor('#475569')
    )
    elements.append(Paragraph("<b>PROCTOR GUIDELINES:</b><br/>"
                              "1. Claim exam test papers from Department Secretary 15 minutes prior to start.<br/>"
                              "2. Verify student permits and CCA ID cards before admitting examinees.<br/>"
                              "3. Return all collected test papers and discrepancy forms directly after the session.", reminders_style))
    elements.append(Spacer(1, 24))

    sig_data = [
        [Paragraph("________________________________________", td_style), Paragraph("________________________________________", td_style)],
        [Paragraph("<b>Faculty Proctor Signature</b>", td_style), Paragraph("<b>Dean / Department Chair Signature</b>", td_style)]
    ]
    sig_t = Table(sig_data, colWidths=[269, 270])
    sig_t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(sig_t)

    doc.build(elements)
    return buffer.getvalue()


def export_student_permit_pdf(student_name, section, exams, exam_term='Midterm', exam_semester='1st Semester'):
    """Generates an official A4 portrait Student Examination Permit PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=28,
        bottomMargin=28
    )
    styles = getSampleStyleSheet()
    elements = []
    
    univ_style = ParagraphStyle(
        'UnivStyleS',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        textColor=colors.HexColor('#27361b')
    )
    sub_univ_style = ParagraphStyle(
        'SubUnivStyleS',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#475569')
    )
    doc_title_style = ParagraphStyle(
        'DocTitleStyleS',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#3d5c2e'),
        alignment=1
    )
    doc_sub_style = ParagraphStyle(
        'DocSubStyleS',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )
    meta_label = ParagraphStyle(
        'MetaLabelS',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#334155')
    )
    meta_val = ParagraphStyle(
        'MetaValS',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0f172a')
    )
    th_style = ParagraphStyle(
        'THStyleS',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1
    )
    td_style = ParagraphStyle(
        'TDStyleS',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        alignment=1
    )
    td_left = ParagraphStyle(
        'TDLeftS',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        alignment=0
    )
    td_bold = ParagraphStyle(
        'TDBoldS',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#2d4a22'),
        alignment=1
    )

    # University Header
    elements.append(Paragraph("CITY COLLEGE OF ANGELES", univ_style))
    elements.append(Paragraph("Arayat Blvd, Barangay Pampang, Angeles City, Pampanga &bull; info@cca.edu.ph", sub_univ_style))
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("OFFICIAL STUDENT EXAMINATION PERMIT", doc_title_style))
    elements.append(Paragraph(f"{exam_term} Examination &bull; {exam_semester}, Academic Year 2025-2026", doc_sub_style))
    elements.append(Spacer(1, 10))

    # Student Metadata Box
    meta_data = [
        [
            Paragraph("<b>Student Name:</b>", meta_label),
            Paragraph(str(student_name or 'N/A'), meta_val),
            Paragraph("<b>Class Section:</b>", meta_label),
            Paragraph(str(section or 'N/A'), meta_val)
        ],
        [
            Paragraph("<b>Institution:</b>", meta_label),
            Paragraph("City College of Angeles", meta_val),
            Paragraph("<b>Permit Status:</b>", meta_label),
            Paragraph("<font color='#15803d'><b>Officially Validated</b></font>", meta_val)
        ]
    ]
    meta_t = Table(meta_data, colWidths=[90, 180, 90, 179])
    meta_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(meta_t)
    elements.append(Spacer(1, 12))

    # Exam Table
    headers = [
        Paragraph("<b>Subject / Course</b>", th_style),
        Paragraph("<b>Exam Date</b>", th_style),
        Paragraph("<b>Start Time</b>", th_style),
        Paragraph("<b>End Time</b>", th_style),
        Paragraph("<b>Room</b>", th_style),
        Paragraph("<b>Dur.</b>", th_style),
    ]
    table_data = [headers]

    for e in exams:
        dt = e.get('exam_date_time')
        dur = int(e.get('duration_minutes') or 60)
        date_str = 'TBD'
        start_str = 'TBD'
        end_str = 'TBD'
        if dt:
            if isinstance(dt, str):
                try:
                    dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass
            if isinstance(dt, datetime):
                end_dt = dt + timedelta(minutes=dur)
                date_str = dt.strftime("%b %d, %Y")
                start_str = dt.strftime("%I:%M %p")
                end_str = end_dt.strftime("%I:%M %p")
            else:
                date_str = str(dt)

        subj = e.get('subject_name', '')
        if e.get('subject_code'):
            subj_cell = Paragraph(f"<b>{subj}</b><br/><font color='#64748b' size=6>{e.get('subject_code')}</font>", td_left)
        else:
            subj_cell = Paragraph(f"<b>{subj}</b>", td_left)

        table_data.append([
            subj_cell,
            Paragraph(date_str, td_style),
            Paragraph(start_str, td_bold),
            Paragraph(end_str, td_bold),
            Paragraph(str(e.get('room_name') or 'TBA'), td_style),
            Paragraph(f"{dur}m", td_style)
        ])

    if len(table_data) > 1:
        t = Table(table_data, colWidths=[184, 85, 75, 75, 75, 45], repeatRows=1)
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3d5c2e')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ]
        for r in range(1, len(table_data)):
            if r % 2 == 0:
                t_style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#f8fafc')))
        t.setStyle(TableStyle(t_style))
        elements.append(t)
    else:
        elements.append(Paragraph("No scheduled exams found for this section.", styles['Normal']))

    elements.append(Spacer(1, 14))

    # Examinee instructions & Signatures
    reminders_style = ParagraphStyle(
        'RemindersS',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor('#475569')
    )
    elements.append(Paragraph("<b>EXAMINEE REMINDERS:</b><br/>"
                              "1. Present this permit and your valid CCA Student ID to the room proctor upon entry.<br/>"
                              "2. Arrive at designated examination rooms at least 15 minutes before the start time.<br/>"
                              "3. Strictly uphold academic integrity. Any form of cheating results in immediate failure.", reminders_style))
    elements.append(Spacer(1, 24))

    sig_data = [
        [Paragraph("________________________________________", td_style), Paragraph("________________________________________", td_style)],
        [Paragraph("<b>Student Signature</b>", td_style), Paragraph("<b>College Registrar / Dean Signature</b>", td_style)]
    ]
    sig_t = Table(sig_data, colWidths=[269, 270])
    sig_t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(sig_t)

    doc.build(elements)
    return buffer.getvalue()
