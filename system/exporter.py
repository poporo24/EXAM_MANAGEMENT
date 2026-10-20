from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
from datetime import datetime, timedelta

def _build_cca_report_header(elements, doc_title, exam_term='Midterm', exam_semester='1st Semester', prepared_by=None, is_landscape=False):
    styles = getSampleStyleSheet()
    univ_style = ParagraphStyle(
        'UnivStyleR', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=13, leading=16,
        textColor=colors.HexColor('#27361b')
    )
    sub_univ_style = ParagraphStyle(
        'SubUnivStyleR', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=10.5,
        textColor=colors.HexColor('#475569')
    )
    doc_title_style = ParagraphStyle(
        'DocTitleStyleR', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        textColor=colors.HexColor('#3d5c2e'), alignment=1
    )
    doc_sub_style = ParagraphStyle(
        'DocSubStyleR', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=colors.HexColor('#475569'), alignment=1
    )
    meta_label = ParagraphStyle(
        'MetaLabelR', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=9.5,
        textColor=colors.HexColor('#334155')
    )
    meta_val = ParagraphStyle(
        'MetaValR', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=9.5,
        textColor=colors.HexColor('#0f172a')
    )

    elements.append(Paragraph("CITY COLLEGE OF ANGELES", univ_style))
    elements.append(Paragraph("Arayat Blvd, Barangay Pampang, Angeles City, Pampanga, 2009 &bull; info@cca.edu.ph", sub_univ_style))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(doc_title.upper(), doc_title_style))
    elements.append(Paragraph(f"{exam_term} Examination &bull; {exam_semester}, Academic Year 2025-2026", doc_sub_style))
    elements.append(Spacer(1, 8))

    # Metadata Box with Prepared By
    prep_name = str(prepared_by or 'Office of Academic Affairs')
    gen_time = datetime.now().strftime("%B %d, %Y %I:%M %p")
    w1, w2 = (140, 645) if is_landscape else (110, 429)
    meta_data = [
        [
            Paragraph("<b>Report Prepared By:</b>", meta_label),
            Paragraph(f"<b>{prep_name}</b>", meta_val),
            Paragraph("<b>Generated On:</b>", meta_label),
            Paragraph(gen_time, meta_val)
        ],
        [
            Paragraph("<b>Institution:</b>", meta_label),
            Paragraph("City College of Angeles", meta_val),
            Paragraph("<b>Document Type:</b>", meta_label),
            Paragraph(doc_title, meta_val)
        ]
    ]
    col_widths = [110, 280, 95, 300] if is_landscape else [90, 180, 85, 184]
    meta_t = Table(meta_data, colWidths=col_widths)
    meta_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(meta_t)
    elements.append(Spacer(1, 10))

def _append_cca_signatures(elements, prepared_by=None, is_landscape=False):
    styles = getSampleStyleSheet()
    td_style = ParagraphStyle(
        'SigTextR', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=10, alignment=1
    )
    elements.append(Spacer(1, 14))
    prep_name = str(prepared_by or 'Office of Academic Affairs')
    sig_data = [
        [Paragraph("________________________________________", td_style), Paragraph("________________________________________", td_style)],
        [Paragraph(f"<b>Prepared by: {prep_name}</b><br/><font color='#64748b' size=6.5>Examination In-Charge / Administrator</font>", td_style),
         Paragraph("<b>Certified &amp; Approved by:</b><br/><font color='#64748b' size=6.5>College Dean / Academic Affairs Head</font>", td_style)]
    ]
    w = 392 if is_landscape else 269
    sig_t = Table(sig_data, colWidths=[w, w])
    sig_t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(sig_t)

def export_schedule_pdf(grouped_schedule, conflict_ids=None, exam_term='Midterm', exam_semester='1st Semester', prepared_by=None):
    """Returns bytes of a PDF with the full exam schedule with official CCA header."""
    if conflict_ids is None: conflict_ids = []
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=28, leftMargin=28, topMargin=28, bottomMargin=28)
    elements = []
    styles = getSampleStyleSheet()

    _build_cca_report_header(elements, "Official Examination Master Schedule", exam_term, exam_semester, prepared_by, is_landscape=True)
    
    th_style = ParagraphStyle('THStyleS', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white, alignment=1)
    td_style = ParagraphStyle('TDStyleS', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=1)
    td_left  = ParagraphStyle('TDLeftS', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=0)
    td_bold  = ParagraphStyle('TDBoldS', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#2d4a22'), alignment=1)

    for date_str, exams in grouped_schedule:
        elements.append(Paragraph(f"<b>Date: {date_str}</b>", ParagraphStyle('DateH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#27361b'))))
        elements.append(Spacer(1, 4))
        
        headers = [
            Paragraph("<b>Time Window</b>", th_style),
            Paragraph("<b>Subject / Course</b>", th_style),
            Paragraph("<b>Section</b>", th_style),
            Paragraph("<b>Type</b>", th_style),
            Paragraph("<b>Room &amp; Venue</b>", th_style),
            Paragraph("<b>Faculty Proctor</b>", th_style)
        ]
        table_data = [headers]
        
        for e in exams:
            dt = e.get('exam_date_time')
            dur = int(e.get('duration_minutes') or 60)
            if dt:
                if isinstance(dt, str):
                    try: dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                    except Exception: pass
                if isinstance(dt, datetime):
                    end_dt = dt + timedelta(minutes=dur)
                    time_str = f"{dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
                else:
                    time_str = str(dt)
            else:
                time_str = 'TBA'
            
            table_data.append([
                Paragraph(time_str, td_bold),
                Paragraph(f"<b>{e.get('subject_name', '')}</b>", td_left),
                Paragraph(str(e.get('section', '—')), td_style),
                Paragraph(str(e.get('subject_type', 'General')), td_style),
                Paragraph(str(e.get('room_name') or 'TBA'), td_style),
                Paragraph(str(e.get('instructor_name') or 'Unassigned'), td_left)
            ])
            
        if len(table_data) > 1:
            t = Table(table_data, colWidths=[120, 220, 75, 75, 110, 185], repeatRows=1)
            tStyle = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3d5c2e')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('LEFTPADDING', (0,0), (-1,-1), 5),
                ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ])
            for idx, e in enumerate(exams):
                if e.get('exam_id') in conflict_ids or e.get('id') in conflict_ids:
                    tStyle.add('BACKGROUND', (0, idx+1), (-1, idx+1), colors.HexColor('#fee2e2'))
                elif (idx + 1) % 2 == 0:
                    tStyle.add('BACKGROUND', (0, idx+1), (-1, idx+1), colors.HexColor('#f8fafc'))
            t.setStyle(tStyle)
            elements.append(t)
        else:
            elements.append(Paragraph("No exams scheduled for this date.", styles['Normal']))
        elements.append(Spacer(1, 10))

    _append_cca_signatures(elements, prepared_by, is_landscape=True)
    doc.build(elements)
    return buffer.getvalue()

def export_proctor_report_pdf(proctor_hours, absence_report, exam_term='Midterm', exam_semester='1st Semester', prepared_by=None, report_type='both'):
    """Returns bytes of a PDF proctor assignment + absence report with official CCA header and prepared_by."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=28, leftMargin=28, topMargin=28, bottomMargin=28)
    elements = []
    styles = getSampleStyleSheet()

    doc_title = "Official Proctor Absence Report" if report_type == 'absence' else ("Official Proctor Assignment Report" if report_type == 'assignment' else "Official Proctor Duty & Absence Report")
    _build_cca_report_header(elements, doc_title, exam_term, exam_semester, prepared_by, is_landscape=False)

    th_style = ParagraphStyle('THStylePR', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white, alignment=1)
    td_style = ParagraphStyle('TDStylePR', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=1)
    td_left  = ParagraphStyle('TDLeftPR', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=0)
    td_bold  = ParagraphStyle('TDBoldPR', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#2d4a22'), alignment=1)

    if report_type in ['both', 'absence']:
        elements.append(Paragraph("<b>Proctor Absence Records</b>", ParagraphStyle('AbsH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#27361b'))))
        elements.append(Spacer(1, 4))
        if absence_report:
            data2 = [[
                Paragraph("<b>Date &amp; Time</b>", th_style),
                Paragraph("<b>Instructor</b>", th_style),
                Paragraph("<b>Subject / Section</b>", th_style),
                Paragraph("<b>Reported Reason</b>", th_style)
            ]]
            for a in absence_report:
                dt = a.get('reported_at')
                dt_str = dt.strftime('%b %d, %Y %I:%M %p') if dt and hasattr(dt, 'strftime') else str(dt or '—')
                data2.append([
                    Paragraph(dt_str, td_bold),
                    Paragraph(f"<b>{a.get('instructor_name', '')}</b>", td_left),
                    Paragraph(f"{a.get('subject_name', '')} ({a.get('section', '')})", td_left),
                    Paragraph(str(a.get('reason') or 'No reason specified'), td_left)
                ])
            t2 = Table(data2, colWidths=[110, 130, 140, 159], repeatRows=1)
            t2_style = [
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3d5c2e')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 5),
                ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ]
            for r in range(1, len(data2)):
                if r % 2 == 0:
                    t2_style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#f8fafc')))
            t2.setStyle(TableStyle(t2_style))
            elements.append(t2)
        else:
            elements.append(Paragraph("No proctor absences recorded for this period.", styles['Normal']))
        elements.append(Spacer(1, 14))

    if report_type in ['both', 'assignment']:
        elements.append(Paragraph("<b>Faculty Proctor Assignment &amp; Load Summary</b>", ParagraphStyle('LoadH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#27361b'))))
        elements.append(Spacer(1, 4))
        data = [[
            Paragraph("<b>#</b>", th_style),
            Paragraph("<b>Faculty Proctor Name</b>", th_style),
            Paragraph("<b>Assigned Exams</b>", th_style),
            Paragraph("<b>Total Duty Hours</b>", th_style)
        ]]
        for idx, p in enumerate(proctor_hours, 1):
            tot = float(p.get('total_hours') or 0.0)
            tot_str = f"{tot:.1f}".rstrip('0').rstrip('.') if tot % 1 != 0 else str(int(tot))
            data.append([
                Paragraph(str(idx), td_style),
                Paragraph(f"<b>{p.get('name', '')}</b>", td_left),
                Paragraph(f"{p.get('exam_count', 0)} Session(s)", td_style),
                Paragraph(f"{tot_str} hrs", td_bold)
            ])
            
        if len(data) > 1:
            t = Table(data, colWidths=[25, 274, 120, 120], repeatRows=1)
            t_style = [
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3d5c2e')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('LEFTPADDING', (0,0), (-1,-1), 5),
                ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ]
            for r in range(1, len(data)):
                if r % 2 == 0:
                    t_style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#f8fafc')))
            t.setStyle(TableStyle(t_style))
            elements.append(t)
        else:
            elements.append(Paragraph("No proctor assignment data available.", styles['Normal']))
        elements.append(Spacer(1, 10))

    _append_cca_signatures(elements, prepared_by, is_landscape=False)
    doc.build(elements)
    return buffer.getvalue()

def export_collection_report_pdf(collection_data, exam_term='Midterm', exam_semester='1st Semester', prepared_by=None):
    """Returns bytes of a PDF exam collection tracking report with official CCA header."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=28, leftMargin=28, topMargin=28, bottomMargin=28)
    elements = []
    styles = getSampleStyleSheet()

    _build_cca_report_header(elements, "Exam Paper & Envelope Collection Tracking Report", exam_term, exam_semester, prepared_by, is_landscape=True)
    
    th_style = ParagraphStyle('THStyleC', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white, alignment=1)
    td_style = ParagraphStyle('TDStyleC', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=1)
    td_left  = ParagraphStyle('TDLeftC', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=0)
    td_bold  = ParagraphStyle('TDBoldC', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#2d4a22'), alignment=1)

    headers = [
        Paragraph("<b>Exam Date &amp; Time Window</b>", th_style),
        Paragraph("<b>Subject / Course</b>", th_style),
        Paragraph("<b>Section</b>", th_style),
        Paragraph("<b>Claimed / Collected</b>", th_style),
        Paragraph("<b>Returned / Received</b>", th_style)
    ]
    data = [headers]
    for c in collection_data:
        dt = c.get('exam_date_time')
        dur = int(c.get('duration_minutes') or 60)
        c_at = c.get('collected_at')
        r_at = c.get('returned_at')
        if dt:
            if isinstance(dt, str):
                try: dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                except Exception: pass
            if isinstance(dt, datetime):
                end_dt = dt + timedelta(minutes=dur)
                dt_str = f"{dt.strftime('%b %d, %Y')} ({dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')})"
            else:
                dt_str = str(dt)
        else:
            dt_str = 'TBA'
        
        c_str = c_at.strftime('%b %d, %Y %I:%M %p') if c_at and hasattr(c_at, 'strftime') else (str(c_at) if c_at else 'Pending')
        r_str = r_at.strftime('%b %d, %Y %I:%M %p') if r_at and hasattr(r_at, 'strftime') else (str(r_at) if r_at else 'Pending')

        data.append([
            Paragraph(dt_str, td_bold),
            Paragraph(f"<b>{c.get('subject_name', '')}</b>", td_left),
            Paragraph(str(c.get('section', '—')), td_style),
            Paragraph(f"<font color='{'#15803d' if c_at else '#b45309'}'>{c_str}</font>", td_style),
            Paragraph(f"<font color='{'#15803d' if r_at else '#64748b'}'>{r_str}</font>", td_style)
        ])
        
    if len(data) > 1:
        t = Table(data, colWidths=[200, 225, 80, 140, 140], repeatRows=1)
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3d5c2e')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ]
        for r in range(1, len(data)):
            if r % 2 == 0:
                t_style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#f8fafc')))
        t.setStyle(TableStyle(t_style))
        elements.append(t)
    else:
        elements.append(Paragraph("No exam collection tracking records found.", styles['Normal']))

    _append_cca_signatures(elements, prepared_by, is_landscape=True)
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



def export_proctor_duty_slip_pdf(proctor_name, exams, exam_term='Midterm', exam_semester='1st Semester', total_hours=0.0, prepared_by=None):
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
        status_note = ""
        if e.get('has_reliever'):
            status_note = f"<br/><font color='#1d4ed8' size=6><b>[Relieved &bull; Sub: Prof. {e.get('reliever_name', 'Reliever')}]</b></font>"
        elif e.get('is_absent_reported'):
            status_note = "<br/><font color='#b45309' size=6><b>[Absence Reported &bull; Pending Reliever]</b></font>"

        if e.get('subject_code'):
            subj_cell = Paragraph(f"<b>{subj}</b>{status_note}<br/><font color='#64748b' size=6>{e.get('subject_code')}</font>", td_left)
        else:
            subj_cell = Paragraph(f"<b>{subj}</b>{status_note}", td_left)

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
