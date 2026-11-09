import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import fitz  # PyMuPDF for verification and rendering previews

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
            self.drawString(40, 11 * inch - 26, "CCA EXAMINATION MANAGEMENT SYSTEM (EXAM_MANAGEMENT)")
            self.setFont("Helvetica", 7.5)
            self.drawRightString(8.5 * inch - 40, 11 * inch - 26, "Capstone Final Defense Master Dossier")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(40, 11 * inch - 30, 8.5 * inch - 40, 11 * inch - 30)

        # Running Footer on all pages
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(40, 32, 8.5 * inch - 40, 32)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(40, 20, "CONFIDENTIAL - PREPARED FOR CAPSTONE FINAL DEFENSE & TECHNICAL ADVISORY BOARD")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 40, 20, page_str)
        self.restoreState()

def create_defense_dossier_pdf(target_filename):
    # Total width = 8.5 inch = 612 pt. Margins = 40 pt each side -> Printable width = 532 pt = 7.388 in.
    doc = SimpleDocTemplate(
        target_filename,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=36,
        bottomMargin=38
    )

    styles = getSampleStyleSheet()

    primary_color = colors.HexColor("#1E3A8A")   # Deep Indigo/Navy
    secondary_color = colors.HexColor("#0284C7") # Ocean Blue
    accent_dark = colors.HexColor("#0F172A")     # Slate 900
    body_text_color = colors.HexColor("#1E293B") # Slate 800
    border_color = colors.HexColor("#CBD5E1")    # Slate 300
    bg_light = colors.HexColor("#F8FAFC")        # Slate 50
    alert_bg = colors.HexColor("#EFF6FF")        # Blue 50

    styles.add(ParagraphStyle(
        name='DocTitle',
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
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
        fontSize=7.8,
        leading=11,
        textColor=colors.HexColor("#BAE6FD")
    ))

    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14.5,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='SubSectionHeading',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12.5,
        textColor=secondary_color,
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='NormalBody',
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.8,
        textColor=body_text_color,
        spaceAfter=3
    ))

    styles.add(ParagraphStyle(
        name='NormalBodyBold',
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10.8,
        textColor=accent_dark,
        spaceAfter=3
    ))

    styles.add(ParagraphStyle(
        name='BulletText',
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.8,
        textColor=body_text_color,
        leftIndent=11,
        firstLineIndent=-8,
        spaceAfter=2
    ))

    styles.add(ParagraphStyle(
        name='CalloutBody',
        fontName='Helvetica-Oblique',
        fontSize=7.8,
        leading=10.8,
        textColor=colors.HexColor("#1E3A8A")
    ))

    styles.add(ParagraphStyle(
        name='TableHeader',
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.white,
        alignment=0
    ))

    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='Helvetica',
        fontSize=7.0,
        leading=9.0,
        textColor=body_text_color
    ))

    styles.add(ParagraphStyle(
        name='TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7.0,
        leading=9.0,
        textColor=accent_dark
    ))

    styles.add(ParagraphStyle(
        name='QAQuestion',
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11.0,
        textColor=primary_color,
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='QAAnswer',
        fontName='Helvetica',
        fontSize=7.6,
        leading=10.5,
        textColor=body_text_color,
        leftIndent=8,
        spaceAfter=4
    ))

    story = []

    # =========================================================================
    # HEADER BANNER
    # =========================================================================
    banner_content = [
        [Paragraph("CCA EXAMINATION MANAGEMENT SYSTEM (EXAM_MANAGEMENT)", styles['DocTitle'])],
        [Paragraph("Comprehensive Capstone Final Defense Technical Dossier & Architecture Manual", styles['DocSubTitle'])],
        [Paragraph("<b>Institution:</b> City College of Angeles &nbsp;|&nbsp; <b>Production Cloud Droplet:</b> 165.22.100.18 (cca-exam.duckdns.org) &nbsp;|&nbsp; <b>Stack:</b> Flask / MySQL / Gunicorn / Nginx", styles['MetaText'])]
    ]
    banner_table = Table(banner_content, colWidths=[7.388 * inch])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 2),
        ('TOPPADDING', (0,1), (-1,1), 0),
        ('BOTTOMPADDING', (0,1), (-1,1), 3),
        ('TOPPADDING', (0,2), (-1,2), 3),
        ('BOTTOMPADDING', (0,2), (-1,2), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 5))

    # =========================================================================
    # 1. EXECUTIVE SUMMARY & PROBLEM STATEMENT
    # =========================================================================
    callout_text = (
        "<b>The 30-Second Elevator Pitch for Your Panel:</b><br/>"
        "<i>\"The CCA Examination Management System is a specialized, web-based academic platform engineered for "
        "City College of Angeles to solve the Examination Timetabling Problem (ETP)—a proven NP-hard combinatorial "
        "optimization challenge. By replacing manual spreadsheet scheduling with a deterministic Constraint Satisfaction "
        "Problem (CSP) heuristic engine featuring a 4-tier progressive relaxation ladder, the system generates 100% "
        "conflict-free timetables in under 2 seconds. It enforces institutional academic integrity through sister-section "
        "synchronization, strict anti-self-proctoring, PWD accessibility matching, equitable faculty workload rotation, "
        "and digital test questionnaire chain-of-custody tracking across 5 dedicated stakeholder roles.\"</i>"
    )
    callout_box = Table([[Paragraph(callout_text, styles['CalloutBody'])]], colWidths=[7.388 * inch])
    callout_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), alert_bg),
        ('LINELEFT', (0,0), (-1,-1), 3.5, secondary_color),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 9),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BFDBFE")),
    ]))
    story.append(callout_box)
    story.append(Spacer(1, 4))

    story.append(Paragraph("1. Executive Overview & Institutional Problem Statement", styles['SectionHeading']))
    story.append(Paragraph(
        "Prior to the implementation of EXAM_MANAGEMENT, examination scheduling at City College of Angeles suffered from "
        "severe operational vulnerabilities inherent in manual spreadsheet coordination across departments (IBM, ICS, IEAS):",
        styles['NormalBody']
    ))
    story.append(Paragraph("<b>&bull; Resource Collisions:</b> Physical room double-bookings and faculty proctor schedule clashes caused exam delays.", styles['BulletText']))
    story.append(Paragraph("<b>&bull; Test Question Leaks (Asynchronous Exam Slots):</b> Different class sections taking the exact same subject were scheduled on different days or hours, allowing early-test takers to leak exam items to peers in later sections.", styles['BulletText']))
    story.append(Paragraph("<b>&bull; Academic Bias & Conflicts of Interest:</b> Instructors frequently proctored exams for subjects they personally taught.", styles['BulletText']))
    story.append(Paragraph("<b>&bull; Faculty Burnout & Inequity:</b> Proctoring duties were unevenly allocated, with some professors exceeding 6 continuous hours while others had zero shifts.", styles['BulletText']))
    story.append(Paragraph("<b>&bull; Logistical Friction & Security Breaches:</b> Physical exam questionnaires and completed answer booklets lacked chain-of-custody tracking, creating custody confusion during proctor changeovers.", styles['BulletText']))
    story.append(Paragraph("<b>&bull; Student Fatigue:</b> Students faced back-to-back major examinations without cognitive rest periods.", styles['BulletText']))

    story.append(Spacer(1, 4))

    # =========================================================================
    # 2. ARCHITECTURAL TOPOLOGY & TECH STACK
    # =========================================================================
    story.append(Paragraph("2. Technical Stack & 5-Tier Decoupled Architecture", styles['SectionHeading']))
    story.append(Paragraph(
        "The system employs a 5-tier decoupled topology engineered for high concurrency, zero timetable deadlocks, "
        "and resilient Linux cloud operations:",
        styles['NormalBody']
    ))

    arch_layers = [
        [Paragraph("<b>Layer</b>", styles['TableHeader']), Paragraph("<b>Component & Stack</b>", styles['TableHeader']), Paragraph("<b>Architectural Responsibilities & Configuration Parameters</b>", styles['TableHeader'])],
        [
            Paragraph("<b>1. Client / Presentation</b>", styles['TableCellBold']),
            Paragraph("Responsive Web UI<br/>(HTML5, Vanilla JS, Bootstrap 5, CSS)", styles['TableCell']),
            Paragraph("Role-specific interfaces; dynamic CSRF token attachment on mutating requests; asynchronous notification ticker (<code>/api/notifications/unread-count</code>) designed to bypass session idle timer refresh.", styles['TableCell'])
        ],
        [
            Paragraph("<b>2. Edge & DNS Gateway</b>", styles['TableCellBold']),
            Paragraph("DuckDNS Dynamic DNS &amp;<br/>Nginx 1.18+ Reverse Proxy", styles['TableCell']),
            Paragraph("Points <code>cca-exam.duckdns.org</code> to <code>165.22.100.18</code>. Terminates TLS/SSL; enforces <code>client_max_body_size 50M</code> (for batch CSV uploads) and <code>proxy_read_timeout 300s</code> to prevent HTTP 504 timeouts during heavy CSP batch generation.", styles['TableCell'])
        ],
        [
            Paragraph("<b>3. WSGI Server</b>", styles['TableCellBold']),
            Paragraph("Gunicorn 21.2.x<br/>(Pre-forked Worker Model)", styles['TableCell']),
            Paragraph("Runs 3 worker processes on loopback (<code>127.0.0.1:9999</code>). Supervised by Linux Systemd (<code>cca_exam.service</code>) configured with <code>Restart=always</code> for sub-second crash revival.", styles['TableCell'])
        ],
        [
            Paragraph("<b>4. Application & Logic</b>", styles['TableCellBold']),
            Paragraph("Python 3.12 / Flask 3.1.x<br/>(app.py, scheduler.py, logic.py)", styles['TableCell']),
            Paragraph("Executes the CSP scheduling engine, role-based access control (RBAC), Bcrypt password validation, 20-minute rolling session timeout watchdog, ReportLab PDF generators, and SMTP mail dispatchers.", styles['TableCell'])
        ],
        [
            Paragraph("<b>5. Persistence & Data</b>", styles['TableCellBold']),
            Paragraph("MySQL 8.x InnoDB<br/>(database.py, Connection Pool)", styles['TableCell']),
            Paragraph("Managed by <code>MySQLConnectionPool</code> (size: 10, <code>pool_reset_session=True</code>) with on-demand direct-connection fallback under burst conditions. Auto-schema migration on startup.", styles['TableCell'])
        ],
    ]
    t_arch = Table(arch_layers, colWidths=[1.1 * inch, 1.9 * inch, 4.388 * inch])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_arch)

    # Force Page Break to Page 2
    story.append(PageBreak())

    # =========================================================================
    # 3. DATABASE ARCHITECTURE & 16-TABLE DATA MODEL
    # =========================================================================
    story.append(Paragraph("3. Database Architecture & Complete 16-Table Data Model", styles['SectionHeading']))
    story.append(Paragraph(
        "The relational database schema is normalized to 3NF and structured to enforce referential integrity, "
        "audit compliance, and historical record archiving across academic terms:",
        styles['NormalBody']
    ))

    db_tables = [
        [Paragraph("<b>Table Name</b>", styles['TableHeader']), Paragraph("<b>Core Entity & Key Columns</b>", styles['TableHeader']), Paragraph("<b>Relational Role & Operational Purpose</b>", styles['TableHeader'])],
        [
            Paragraph("<code>users</code>", styles['TableCellBold']),
            Paragraph("id, email, password_hash, role, is_active, institute_id, section", styles['TableCell']),
            Paragraph("Stores user profiles for 5 roles; credentials hashed using Bcrypt; gates platform access via <code>is_active</code> verification.", styles['TableCell'])
        ],
        [
            Paragraph("<code>institutes</code>", styles['TableCellBold']),
            Paragraph("id, code, name, default_room_capacity", styles['TableCell']),
            Paragraph("Academic units (e.g. IBM, ICS, IEAS); establishes baseline capacity rules for classroom allocation.", styles['TableCell'])
        ],
        [
            Paragraph("<code>instructors</code>", styles['TableCellBold']),
            Paragraph("id, name, email, institute_id, subjects_taught, is_pwd", styles['TableCell']),
            Paragraph("Faculty invigilator directory; stores teaching subjects (tokenized) and physical disability flags for accessible room placement.", styles['TableCell'])
        ],
        [
            Paragraph("<code>subjects</code>", styles['TableCellBold']),
            Paragraph("id, code, name, subject_type, institute_id, content_group_id", styles['TableCell']),
            Paragraph("Course curriculum catalog; differentiates Major vs Minor subjects; assigns <code>content_group_id</code> for cross-section sync.", styles['TableCell'])
        ],
        [
            Paragraph("<code>rooms</code>", styles['TableCellBold']),
            Paragraph("id, name, building, floor, capacity, is_pwd_accessible", styles['TableCell']),
            Paragraph("Physical exam inventory; distinguishes Main Building and PAGCOR Building; tracks wheelchair accessibility.", styles['TableCell'])
        ],
        [
            Paragraph("<code>exams</code>", styles['TableCellBold']),
            Paragraph("id, subject_id, room_id, instructor_id, section, exam_date_time, duration", styles['TableCell']),
            Paragraph("Core timetable entries; binds subject, room, proctor, and section into a verified, conflict-free scheduling slot.", styles['TableCell'])
        ],
        [
            Paragraph("<code>exam_settings</code>", styles['TableCellBold']),
            Paragraph("id, academic_year, exam_term, exam_semester, period_start, period_end", styles['TableCell']),
            Paragraph("Defines global academic milestones (e.g., 2026-2027 Midterm) and active date windows for the scheduler.", styles['TableCell'])
        ],
        [
            Paragraph("<code>system_settings</code>", styles['TableCellBold']),
            Paragraph("day_start, day_end, slot_interval, max_proctor_hrs, schedule_published", styles['TableCell']),
            Paragraph("Global operational thresholds, SMTP mail server parameters, and timetable visibility gate (<code>schedule_published</code>).", styles['TableCell'])
        ],
        [
            Paragraph("<code>proctor_availability</code>", styles['TableCellBold']),
            Paragraph("id, instructor_id, date, start_time, end_time", styles['TableCell']),
            Paragraph("Stores faculty-submitted availability windows used by the scheduler as O(1) hard constraints.", styles['TableCell'])
        ],
        [
            Paragraph("<code>proctor_absence</code>", styles['TableCellBold']),
            Paragraph("id, instructor_id, exam_id, date, reason, reported_at", styles['TableCell']),
            Paragraph("Logs emergency faculty absences on exam days with timestamps and formal justifications.", styles['TableCell'])
        ],
        [
            Paragraph("<code>relievers</code>", styles['TableCellBold']),
            Paragraph("id, instructor_id, date, time_slot, status", styles['TableCell']),
            Paragraph("Standby proctor inventory available to department secretaries for immediate 1-click emergency substitution.", styles['TableCell'])
        ],
        [
            Paragraph("<code>exam_collection</code>", styles['TableCellBold']),
            Paragraph("id, exam_id, proctor_id, status, collected_at, returned_at", styles['TableCell']),
            Paragraph("Paper custody tracking: logs handover of test questionnaires and return of student answer booklets.", styles['TableCell'])
        ],
        [
            Paragraph("<code>audit_logs</code>", styles['TableCellBold']),
            Paragraph("id, user_id, user_role, ip_address, action, details, timestamp", styles['TableCell']),
            Paragraph("Non-repudiation audit trail compliant with ISO/IEC 27001 and NIST SP 800-53; captures all sensitive system modifications.", styles['TableCell'])
        ],
        [
            Paragraph("<code>schedule_reset_requests</code>", styles['TableCellBold']),
            Paragraph("id, requested_by_id, reason, status, reviewed_by_id, reviewed_at", styles['TableCell']),
            Paragraph("Dual-authorization governance table; requires two independent administrators to approve full timetable resets.", styles['TableCell'])
        ],
        [
            Paragraph("<code>exam_archives</code>", styles['TableCellBold']),
            Paragraph("id, academic_year, exam_term, archive_title, snapshot_data, archived_at", styles['TableCell']),
            Paragraph("Permanent historical snapshots containing complete JSON dumps of finalized exam periods for multi-year accreditation audits.", styles['TableCell'])
        ],
        [
            Paragraph("<code>notifications</code>", styles['TableCellBold']),
            Paragraph("id, user_id, message, is_read, created_at", styles['TableCell']),
            Paragraph("Broadcast alerts and role-specific updates displayed dynamically in the top navigation bar.", styles['TableCell'])
        ]
    ]
    t_db = Table(db_tables, colWidths=[1.15 * inch, 2.3 * inch, 3.938 * inch])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_db)

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Autonomous Database Schema Synchronization (Zero-Migration Deployment):</b>", styles['SubSectionHeading']))
    story.append(Paragraph(
        "To prevent runtime crashes during environment migrations (e.g., from local XAMPP to production Linux Droplets), "
        "<code>ensure_database_schema()</code> in <code>system/database.py</code> executes upon application launch. It programmatically "
        "inspects MySQL table catalogs, creates missing relational tables (<code>audit_logs</code>, <code>exam_archives</code>, "
        "<code>schedule_reset_requests</code>), and dynamically alters tables to add missing columns without manual SQL scripting.",
        styles['NormalBody']
    ))

    # Force Page Break to Page 3
    story.append(PageBreak())

    # =========================================================================
    # 4. THE CORE SCHEDULING ENGINE (SCHEDULER.PY & CSP)
    # =========================================================================
    story.append(Paragraph("4. The Scheduling Engine (system/scheduler.py & CSP Heuristics)", styles['SectionHeading']))
    story.append(Paragraph(
        "Academic examination timetabling is mathematically categorized as the <b>Examination Timetabling Problem (ETP)</b>, "
        "a proven <b>NP-Hard Combinatorial Optimization Problem</b>. A brute-force search over all permutations of courses, "
        "rooms, faculty invigilators, and timeslots is computationally intractable ($O(N!)$). To generate a verified, 100% "
        "conflict-free timetable in under two seconds, we designed a deterministic <b>Constraint Satisfaction Problem (CSP) "
        "Heuristic Engine with a Tiered Relaxation Ladder</b>.",
        styles['NormalBody']
    ))

    story.append(Paragraph("<b>4.1 Hard Constraints (Zero Violations Permitted):</b>", styles['SubSectionHeading']))
    hard_rules = [
        ("1. Zero Room Double-Booking", "Ensured via interval collision check <code>room_cal[r_id]</code> against candidate <code>[start, end)</code>. No two exams can occupy the same physical room simultaneously."),
        ("2. Zero Proctor Double-Booking", "Ensured via <code>inst_cal[i_id]</code>. A proctor can never be scheduled for two concurrent examination rooms."),
        ("3. Zero Student Overlap + 1-Hour Rest Buffer", "The function <code>section_free(sec, s, e)</code> checks extended interval <code>[s - 1 hr, e + 1 hr)</code> against <code>section_cal</code>. Students are guaranteed zero concurrent exams and at least 60 minutes of cognitive rest between tests."),
        ("4. Sister-Section Synchronization", "Sections enrolled in common courses or sharing a <code>content_group_id</code> are treated as an atomic scheduling cluster. The engine locks a single synchronized timestamp for all sections across parallel rooms, eliminating test question leaks."),
        ("5. Strict Anti-Self-Proctoring", "Faculty members are barred from invigilating exams for subjects they teach. Pre-tokenized subject sets (name, code, ID) in <code>inst_subs_map</code> are checked against candidate exam tokens before proctor assignment."),
        ("6. Proctor Availability Windows", "O(1) dictionary lookup against <code>proctor_availability</code> ensures instructors are only assigned during their declared working hours."),
        ("7. PWD Room Accessibility Matching", "Instructors with physical disabilities (<code>is_pwd = 1</code>) are strictly paired with classrooms flagged <code>is_pwd_accessible = 1</code> (ground floor or elevator-serviced wings)."),
        ("8. Seating Capacity Bounds", "The engine verifies <code>room.capacity >= section_student_count</code> (or the institute default capacity).")
    ]
    for title, desc in hard_rules:
        story.append(Paragraph(f"<b>&bull; {title}:</b> {desc}", styles['BulletText']))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>4.2 Soft Constraints & The 4-Tier Progressive Relaxation Ladder:</b>", styles['SubSectionHeading']))
    story.append(Paragraph(
        "In dense exam periods with limited proctor inventories, rigid daily thresholds cause artificial scheduling deadlocks. "
        "The engine dynamically evaluates candidate slots through a 4-tier relaxation hierarchy:",
        styles['NormalBody']
    ))

    tier_data = [
        [Paragraph("<b>Relaxation Tier</b>", styles['TableHeader']), Paragraph("<b>Daily Major Cap per Section</b>", styles['TableHeader']), Paragraph("<b>Daily Proctoring Cap per Faculty</b>", styles['TableHeader']), Paragraph("<b>Operational Function</b>", styles['TableHeader'])],
        [
            Paragraph("<b>Tier 1 (Strict Baseline)</b>", styles['TableCellBold']),
            Paragraph("Max 2 Major Exams", styles['TableCell']),
            Paragraph("Max 4.0 Hours", styles['TableCell']),
            Paragraph("Ideal institutional distribution; prevents student and proctor fatigue.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Tier 2 (Minor Absorption)</b>", styles['TableCellBold']),
            Paragraph("Max 2 Major Exams", styles['TableCell']),
            Paragraph("Max 5.0 Hours", styles['TableCell']),
            Paragraph("Absorbs minor faculty shortages while protecting student balance.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Tier 3 (Dense Period)</b>", styles['TableCellBold']),
            Paragraph("Max 3 Major Exams", styles['TableCell']),
            Paragraph("Max 6.5 Hours", styles['TableCell']),
            Paragraph("Accommodates high curriculum density during peak exam cycles.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Tier 4 (Fail-Safe Ceiling)</b>", styles['TableCellBold']),
            Paragraph("Max 3 Major Exams", styles['TableCell']),
            Paragraph("Max 8.0 Hours (Absolute Ceiling)", styles['TableCell']),
            Paragraph("Final fallback ensuring 100% placement rather than leaving unassigned exams.", styles['TableCell'])
        ],
    ]
    t_tier = Table(tier_data, colWidths=[1.15 * inch, 1.8 * inch, 1.8 * inch, 2.638 * inch])
    t_tier.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_tier)

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>4.3 Fair Workload Rotation & Campus Transit Heuristics:</b>", styles['SubSectionHeading']))
    story.append(Paragraph(
        "Candidate proctors are sorted using a multi-attribute comparator: <code>(daily_hours_worked, cumulative_term_hours, round_robin_counter)</code>. "
        "This guarantees equitable workload balance across faculty ranks. Furthermore, proctors cannot exceed 3 consecutive hours without a rest period. "
        "To prevent campus transit delays, the engine locks proctors to their assigned building (Main Building vs. PAGCOR Building) for that day, "
        "or enforces a mandatory <code>15-minute inter-building travel buffer</code>.",
        styles['NormalBody']
    ))

    # Force Page Break to Page 4
    story.append(PageBreak())

    # =========================================================================
    # 5. SECURITY, RELIABILITY & ENTERPRISE COMPLIANCE
    # =========================================================================
    story.append(Paragraph("5. Security Architecture, Resilience & Compliance", styles['SectionHeading']))
    story.append(Paragraph(
        "The application layer implements multi-tiered defense-in-depth security aligned with OWASP Top 10, "
        "NIST SP 800-63B, and ISO/IEC 27001 standards:",
        styles['NormalBody']
    ))

    sec_items = [
        ("Cryptographic Password Storage", "Passwords are salted and hashed using Bcrypt with Blowfish cost factor 12. Plaintext credentials are never persisted."),
        ("NIST SP 800-63B Password Validation", "Enforces strict length, character diversity, and dictionary checks against common breached passwords."),
        ("Rolling 20-Minute Inactivity Watchdog", "Monitored via <code>@app.before_request check_session_inactivity()</code>. If idle time exceeds 1,200 seconds, the session is invalidated, an <code>AUTH_SESSION_TIMEOUT</code> event is logged, and the user is redirected to login. AJAX notification endpoints are explicitly exempted so background tickers do not falsely reset the idle clock."),
        ("Anti-Session Fixation & Leak Protection", "Upon successful login, <code>session.clear()</code> purges previous session tokens. Cookies are set with <code>HttpOnly=True</code> (blocks XSS theft), <code>SameSite='Lax'</code>, and <code>Secure=True</code> in production."),
        ("CSRF Protection on All Mutating Requests", "Flask-WTF CSRF tokens protect all POST/PUT/DELETE forms and AJAX calls via <code>static/js/csrf.js</code>."),
        ("Flask-Limiter Brute-Force Rate Limiting", "Throttles <code>/login</code> to 15 requests per minute per IP address, stopping automated credential stuffing with HTTP 429."),
        ("MySQL Pool Resiliency & Burst Fallback", "Configured with <code>MySQLConnectionPool(pool_size=10, pool_reset_session=True)</code>. If traffic bursts exhaust pooled sockets, <code>open_db()</code> captures the exception and immediately spawns a direct on-demand connection, preventing 500 server crashes."),
        ("Dual-Authorization Schedule Reset", "Clearing master schedules requires dual-admin validation: one administrator submits a formal justification, and a second administrator reviews and approves the request in <code>schedule_reset_requests</code>."),
        ("Non-Repudiation Audit Trail", "All critical modifications (timetable generation, manual edits, user role changes, student approvals) are logged in <code>audit_logs</code> with actor IDs, roles, IP addresses, and timestamps.")
    ]
    for title, desc in sec_items:
        story.append(Paragraph(f"<b>&bull; {title}:</b> {desc}", styles['BulletText']))

    story.append(Spacer(1, 4))

    # =========================================================================
    # 6. USER ROLES & LIVE DEMO SCRIPT
    # =========================================================================
    story.append(Paragraph("6. Stakeholder Roles & Capstone Live Demonstration Script", styles['SectionHeading']))
    story.append(Paragraph(
        "Demonstrate the system to the defense panel in this logical 5-stage workflow:",
        styles['NormalBody']
    ))

    demo_steps = [
        [Paragraph("<b>Role</b>", styles['TableHeader']), Paragraph("<b>Route & Scope</b>", styles['TableHeader']), Paragraph("<b>Live Demonstration Actions & Key Defense Talking Points</b>", styles['TableHeader'])],
        [
            Paragraph("<b>1. Super Admin</b>", styles['TableCellBold']),
            Paragraph("<code>/super_admin</code><br/>Global Access", styles['TableCell']),
            Paragraph("Show the User Account Directory; approve pending student registrations; highlight the <b>Audit Logs Table</b> and the Dual-Authorization Schedule Reset approval queue.", styles['TableCell'])
        ],
        [
            Paragraph("<b>2. System Admin</b>", styles['TableCellBold']),
            Paragraph("<code>/dashboard</code><br/><code>/schedule</code>", styles['TableCell']),
            Paragraph("Import rooms, subjects, and instructors via CSV. Click <b>'Generate Schedule'</b> (point out sub-2s CSP execution). Open the <b>Interactive Conflict Resolver</b> to verify 0 overlaps. Demonstrate the <b>Publish Schedule</b> toggle.", styles['TableCell'])
        ],
        [
            Paragraph("<b>3. Faculty / Proctor</b>", styles['TableCellBold']),
            Paragraph("<code>/proctor/dashboard</code><br/>Faculty Scoped", styles['TableCell']),
            Paragraph("Submit availability windows. Show assigned proctoring shifts and room assignments. <b>Highlight anti-self-proctoring:</b> show that the professor is never assigned to subjects they teach.", styles['TableCell'])
        ],
        [
            Paragraph("<b>4. Dept Secretary</b>", styles['TableCellBold']),
            Paragraph("<code>/secretary/dashboard</code><br/>Institute Scoped", styles['TableCell']),
            Paragraph("Demonstrate <b>Chain-of-Custody Tracking</b>: transition test papers from <i>Pending &rarr; Collected &rarr; Returned</i>. Simulate a proctor absence and execute a <b>1-Click Standby Reliever Dispatch</b>.", styles['TableCell'])
        ],
        [
            Paragraph("<b>5. Student &amp; Guest</b>", styles['TableCellBold']),
            Paragraph("<code>/student/timetable</code><br/><code>/public_timetable</code>", styles['TableCell']),
            Paragraph("Log in as a student to view personalized schedules and download the <b>Official Printable Examination Slip (PDF)</b>. Open Incognito to <code>/public_timetable</code> to show cross-section lookups for irregular examinees.", styles['TableCell'])
        ],
    ]
    t_demo = Table(demo_steps, colWidths=[1.15 * inch, 1.6 * inch, 4.638 * inch])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_demo)

    # Force Page Break to Page 5
    story.append(PageBreak())

    # =========================================================================
    # 7. PANELIST DEFENSE Q&A MASTER GUIDE
    # =========================================================================
    story.append(Paragraph("7. Panelist Defense Q&A Master Guide (Anticipated Questions & Winning Answers)", styles['SectionHeading']))
    story.append(Paragraph(
        "Deliver these concise, authoritative technical responses during the panel questioning period:",
        styles['NormalBody']
    ))

    qa_master = [
        (
            "Q1: Why did you develop a custom heuristic CSP engine instead of integrating an off-the-shelf solver like Google OR-Tools?",
            "While Google OR-Tools is a capable solver, it introduces heavy C++ binary dependencies, high RAM consumption, and deployment fragility on lean cloud instances. Academic scheduling at CCA includes unique institutional constraints—such as sister-section synchronization, 1-hour cognitive rest intervals, anti-self-proctoring token matching, PWD room pairings, and inter-building transit buffers. Our custom CSP heuristic with a Tiered Relaxation Ladder was engineered specifically for these constraints, executing in under 2 seconds with 100% deterministic constraint satisfaction."
        ),
        (
            "Q2: How does the system mathematically prevent test question leaks between different sections?",
            "Through Sister-Section Synchronization in <code>system/scheduler.py</code>. The engine groups all sections taking the same course or sharing a <code>content_group_id</code> into an atomic scheduling cluster. It assigns all sections to the exact same date and timeslot across parallel classrooms. Because exams take place concurrently, early test-takers cannot leak questions to other sections."
        ),
        (
            "Q3: How does the platform handle emergency faculty absences on examination day?",
            "The Department Secretary dashboard features an emergency dispatch system. If a proctor reports an illness or fails to arrive, the secretary logs the absence in <code>proctor_absence</code> and dispatches a replacement from the <code>relievers</code> pool with a single click. The timetable immediately updates, and the replacement event is permanently logged in <code>audit_logs</code> without disturbing other testing rooms."
        ),
        (
            "Q4: What happens if 500 students access the portal simultaneously when timetables are released?",
            "The system is architected for high-concurrency bursts: (1) Nginx acts as an edge reverse proxy handling SSL termination and static asset caching; (2) Gunicorn utilizes 3 pre-forked worker processes to handle dynamic requests; (3) database connections are managed via a persistent 10-socket MySQL pool with automatic on-demand direct-connection fallback to prevent pool exhaustion; and (4) student schedule queries are read-optimized indexed SQL lookups."
        ),
        (
            "Q5: How do you prevent accidental schedule deletion or malicious tampering by rogue administrators?",
            "We engineered a Dual-Authorization Schedule Reset workflow. A System Administrator cannot clear active timetables on impulse. They must submit a formal request with a documented reason into <code>schedule_reset_requests</code>. The reset remains pending until a second administrator reviews and approves it, at which point an automated archive snapshot is stored in <code>exam_archives</code>."
        ),
        (
            "Q6: Why are there separate Super Admin and System Admin roles?",
            "This adheres to the Principle of Least Privilege and Separation of Duties. System Administrators manage day-to-day academic scheduling operations (subjects, classrooms, proctor assignments, timetable publishing). Super Administrators govern global security parameters, user account provisioning, role promotions, SMTP credentials, and dual-authorization approvals. This ensures no single operational admin can unilaterally compromise the system."
        ),
        (
            "Q7: What are the current limitations of your system and what are your recommendations for future research?",
            "Currently, proctor substitutions require a secretary to manually select from the available reliever pool; future enhancements could incorporate automated push notifications and geolocation dispatch. Additionally, while the system generates official PDF passes, integrating direct SMS gateway alerts would enhance student notification during severe weather disruptions or emergency campus closures."
        )
    ]

    for q, a in qa_master:
        qa_block = [
            Paragraph(q, styles['QAQuestion']),
            Paragraph(f"<b>Answer:</b> {a}", styles['QAAnswer'])
        ]
        story.append(KeepTogether(qa_block))

    story.append(Spacer(1, 4))

    # =========================================================================
    # 8. DEFENSE DAY CHECKLIST & CONTINGENCY
    # =========================================================================
    story.append(Paragraph("8. Defense Day Operational Checklist & Contingency Strategy", styles['SectionHeading']))
    checklist_items = [
        "<b>Cloud VPS Verification:</b> Verify DigitalOcean Droplet status via SSH (<code>systemctl status cca_exam.service nginx</code>).",
        "<b>Offline Local Fallback:</b> Keep local XAMPP Apache/MySQL and Flask running on your laptop (<code>run.bat</code>) in case venue Wi-Fi drops.",
        "<b>Role Credentials Card:</b> Have test logins ready for Super Admin, System Admin, Department Secretary, Proctor, and Student.",
        "<b>Pre-Loaded Browser Windows:</b> Open distinct browser windows or profiles for each role beforehand to avoid demo login delays.",
        "<b>Panel Grace Strategy:</b> If panelists suggest a new constraint, answer: <i>'That is an excellent institutional consideration. In our architecture, that rule can be seamlessly added as an evaluation filter in our CSP heuristic ladder.'</i>"
    ]
    for item in checklist_items:
        story.append(Paragraph(f"&bull; {item}", styles['BulletText']))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Master Dossier PDF built successfully at: {target_filename}")

    # Generate page preview images using PyMuPDF (fitz)
    try:
        pdf_doc = fitz.open(target_filename)
        # Determine the project root directory
        base_dir = r"c:\xampp\htdocs\EXAM_MANAGEMENT"
        static_dir = os.path.join(base_dir, "static")
        os.makedirs(static_dir, exist_ok=True)
        for i, page in enumerate(pdf_doc):
            pix = page.get_pixmap(dpi=150)
            img_path = os.path.join(static_dir, f"defense_dossier_page_{i+1}.png")
            pix.save(img_path)
    except Exception as img_err:
        print(f"Notice generating page preview images: {img_err}")

if __name__ == '__main__':
    root_pdf = r"c:\xampp\htdocs\EXAM_MANAGEMENT\CCA_Exam_Management_Capstone_Final_Defense_Master_Dossier.pdf"
    static_pdf = r"c:\xampp\htdocs\EXAM_MANAGEMENT\static\CCA_Exam_Management_Capstone_Final_Defense_Master_Dossier.pdf"
    guide_pdf = r"c:\xampp\htdocs\EXAM_MANAGEMENT\CCA_Exam_Management_Capstone_Defense_Guide.pdf"
    static_guide_pdf = r"c:\xampp\htdocs\EXAM_MANAGEMENT\static\CCA_Exam_Management_Capstone_Defense_Guide.pdf"
    
    create_defense_dossier_pdf(root_pdf)
    create_defense_dossier_pdf(static_pdf)
    create_defense_dossier_pdf(guide_pdf)
    create_defense_dossier_pdf(static_guide_pdf)
