from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

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
            time_str = dt.strftime('%I:%M %p') if dt else 'N/A'
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
        data.append([p.get('name', ''), str(p.get('exam_count', 0)), f"{p.get('total_hours', 0.0):.2f}"])
        
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
    
    data = [['Exam Date', 'Subject', 'Section', 'Collected At', 'Returned At']]
    for c in collection_data:
        dt = c.get('exam_date_time')
        c_at = c.get('collected_at')
        r_at = c.get('returned_at')
        
        data.append([
            dt.strftime('%Y-%m-%d %H:%M') if dt else 'N/A',
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
