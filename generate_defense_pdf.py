import os
import sys
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
        
        # We don't draw running header on cover page (Page 1)
        if self._pageNumber > 1:
            self.drawString(45, 11 * inch - 28, "CCA EXAMINATION MANAGEMENT SYSTEM (EXAM_MANAGEMENT)")
            self.setFont("Helvetica", 7.5)
            self.drawRightString(8.5 * inch - 45, 11 * inch - 28, "Capstone Technical Defense Dossier")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(45, 11 * inch - 32, 8.5 * inch - 45, 11 * inch - 32)

        # Running Footer (on all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(45, 34, 8.5 * inch - 45, 34)
        self.setFont("Helvetica", 7.5)
        self.drawString(45, 22, "CONFIDENTIAL - PREPARED FOR CAPSTONE FINAL DEFENSE & TECHNICAL ADVISORY")
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
        spaceBefore=7,
        spaceAfter=4,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='SubSecHeader',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=secondary_color,
        spaceBefore=5,
        spaceAfter=3,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='CustomBody',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=body_text_color,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name='BulletItem',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=body_text_color,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2.5
    ))

    styles.add(ParagraphStyle(
        name='QAQuestion',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=primary_color,
        spaceBefore=3,
        spaceAfter=2,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='QAAnswer',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=body_text_color,
        leftIndent=6,
        spaceAfter=4
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

    # =============================================================
    # PAGE 1: TITLE BANNER, ABSTRACT, TOPOLOGY & AUTH FLOWS
    # =============================================================
    banner_content = [
        [Paragraph("CCA EXAMINATION MANAGEMENT SYSTEM", styles['DocTitle'])],
        [Paragraph("Comprehensive System Architecture, Algorithmic Engine & Capstone Defense Dossier", styles['DocSubTitle'])],
        [Paragraph("<b>Author / Candidate:</b> Capstone Engineering Team &nbsp;|&nbsp; <b>Institution:</b> City College of Angeles &nbsp;|&nbsp; <b>Cloud Target:</b> 165.22.100.18 (cca-exam.duckdns.org)", styles['MetaText'])]
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

    abstract_text = (
        "<b>Executive Technical Abstract:</b> This dossier documents the architectural foundations and engineering decisions "
        "of the CCA Exam Management System (EXAM_MANAGEMENT). Developed for academic institutional operations, it encompasses "
        "a defense-in-depth security perimeter, robust session management, MySQL connection pooling, a deterministic "
        "Constraint Satisfaction Problem (CSP) scheduling engine with tiered relaxation, and an enterprise deployment stack "
        "on DigitalOcean utilizing Nginx, Gunicorn, Systemd, and DuckDNS."
    )
    abstract_box = Table([[Paragraph(abstract_text, styles['CustomBody'])]], colWidths=[7.4 * inch])
    abstract_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('LINELEFT', (0,0), (-1,-1), 3.5, secondary_color),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(abstract_box)
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. System Overview & Architectural Topology", styles['SecHeader']))
    story.append(Paragraph(
        "The system adheres to a decoupled 5-tier web architecture engineered for high concurrency, deterministic "
        "security, zero timetable conflicts, and high availability:",
        styles['CustomBody']
    ))

    arch_layers = [
        [Paragraph("<b>Layer</b>", styles['TableHeader']), Paragraph("<b>Component & Technology</b>", styles['TableHeader']), Paragraph("<b>Core Architectural Responsibilities</b>", styles['TableHeader'])],
        [
            Paragraph("<b>1. Client Layer</b>", styles['TableCellBold']),
            Paragraph("Desktop & Mobile Browsers<br/>(HTML5, Vanilla JS, Bootstrap, CSS)", styles['TableCell']),
            Paragraph("Delivers responsive role-based interfaces; includes CSRF tokens on all mutating requests; polls unread notifications via an asynchronous ticker without resetting session idle timers.", styles['TableCell'])
        ],
        [
            Paragraph("<b>2. Edge & DNS</b>", styles['TableCellBold']),
            Paragraph("DuckDNS Dynamic DNS &amp;<br/>Nginx 1.18+ (Reverse Proxy)", styles['TableCell']),
            Paragraph("Binds cca-exam.duckdns.org to droplet IP (165.22.100.18). Terminates SSL/TLS. Enforces 50MB request buffering and a 300s proxy timeout to allow uninterrupted batch processing.", styles['TableCell'])
        ],
        [
            Paragraph("<b>3. WSGI Server</b>", styles['TableCellBold']),
            Paragraph("Gunicorn 21.2.x<br/>(Pre-fork Worker Model)", styles['TableCell']),
            Paragraph("Hosts 3 dedicated worker processes on loopback (127.0.0.1:9999) under Linux Systemd supervisor (cca_exam.service) with automatic crash revival.", styles['TableCell'])
        ],
        [
            Paragraph("<b>4. App & Logic</b>", styles['TableCellBold']),
            Paragraph("Flask 3.1.x Framework<br/>(app.py, logic.py, scheduler.py)", styles['TableCell']),
            Paragraph("Implements ProxyFix middleware, Flask-Limiter, Bcrypt hashing, NIST password checks, RBAC route guards, rolling 20-min session expiry, and the CSP scheduling engine.", styles['TableCell'])
        ],
        [
            Paragraph("<b>5. Persistence</b>", styles['TableCellBold']),
            Paragraph("MySQL 8.x InnoDB<br/>(database.py, Connection Pool)", styles['TableCell']),
            Paragraph("Managed by MySQLConnectionPool (size: 10, pool_reset_session=True) with graceful fallback to direct connections; autonomous schema updates and audit logging.", styles['TableCell'])
        ],
    ]
    t_arch = Table(arch_layers, colWidths=[1.1 * inch, 2.0 * inch, 4.3 * inch])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, subtle_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. End-to-End User Authentication & Session Security", styles['SecHeader']))
    story.append(Paragraph(
        "Authentication is protected by defense-in-depth measures against brute-forcing, session fixation, and CSRF:",
        styles['CustomBody']
    ))
    story.append(Paragraph("<b>&bull; Step 1: Request Intake & Rate Limiting:</b> POST requests to <code>/login</code> are throttled by <code>Flask-Limiter</code> at 15 req/min per IP. Attacks are stopped immediately with HTTP 429.", styles['BulletItem']))
    story.append(Paragraph("<b>&bull; Step 2: Cryptographic Password Verification:</b> <code>verify_login()</code> queries the user via parameterized SQL. Passwords are verified against stored hashes using <code>bcrypt.checkpw()</code> (Blowfish salt, cost factor 12).", styles['BulletItem']))
    story.append(Paragraph("<b>&bull; Step 3: Account State Verification:</b> If <code>is_active = 0</code>, authentication is blocked with <code>'inactive'</code>, keeping unapproved registrations locked out.", styles['BulletItem']))
    story.append(Paragraph("<b>&bull; Step 4: Session Cleansing (Anti-Fixation):</b> When credentials pass, <code>session.clear()</code> wipes pre-existing session cookies, neutralizing session fixation vectors.", styles['BulletItem']))
    story.append(Paragraph("<b>&bull; Step 5: Session Hydration:</b> Injects <code>user_id</code>, <code>role</code>, <code>instructor_id</code>, <code>section</code>, <code>institute_id</code>, and float epoch <code>_last_active</code>.", styles['BulletItem']))
    story.append(Paragraph("<b>&bull; Step 6: Role Redirection:</b> <code>_redirect_by_role()</code> routes the user: Admin &rarr; <code>/dashboard</code>, Proctor &rarr; <code>/proctor/dashboard</code>, Secretary &rarr; <code>/secretary/dashboard</code>, Student &rarr; <code>/student/timetable</code>.", styles['BulletItem']))

    # Force clean page break to Page 2
    story.append(PageBreak())

    # =============================================================
    # PAGE 2: ROLE WALKTHROUGH & BACKEND/DATABASE ARCHITECTURE
    # =============================================================
    story.append(Paragraph("2.1 Detailed Walkthrough of the 4 User Roles", styles['SecHeader']))
    story.append(Paragraph(
        "Access control is enforced strictly across all four institutional user classes:",
        styles['CustomBody']
    ))

    role_data = [
        [Paragraph("<b>Role</b>", styles['TableHeader']), Paragraph("<b>Access Controls &amp; Data Scoping</b>", styles['TableHeader']), Paragraph("<b>Primary Capabilities &amp; System Flows</b>", styles['TableHeader'])],
        [
            Paragraph("<b>Student</b>", styles['TableCellBold']),
            Paragraph("Guarded by <code>require_role('student')</code>.<br/>Data scoped strictly to the student's assigned <code>section</code> and <code>institute_id</code>.", styles['TableCell']),
            Paragraph("Read-only access to published timetables (gated by <code>is_schedule_published()</code>). Official PDF timetable export. Irregular students access the <b>Irregular Student Portal</b> to verify cross-section schedules and review subject conflicts.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Proctor<br/>(Faculty)</b>", styles['TableCellBold']),
            Paragraph("Guarded by <code>require_role('proctor')</code>.<br/>Linked via <code>session['instructor_id']</code> to instructor master records.", styles['TableCell']),
            Paragraph("Timetable hidden until published. Submits time availability windows (<code>proctor_availability</code>) used as hard constraints by the scheduler. Inspects assigned rooms and monitors cumulative duty hours against institutional caps.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Secretary</b>", styles['TableCellBold']),
            Paragraph("Guarded by <code>require_role('secretary', 'admin')</code>.<br/>Departmentally scoped by <code>session['institute_id']</code>.", styles['TableCell']),
            Paragraph("Monitors test paper custody via <code>exam_collection</code> (Pending &rarr; Collected &rarr; Returned). Tracks proctor attendance, records absences (<code>proctor_absence</code>), and executes one-click dispatch of standby invigilators from the <code>relievers</code> pool.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Administrator<br/>&amp; Super Admin</b>", styles['TableCellBold']),
            Paragraph("Guarded by <code>require_role('admin')</code> and <code>require_super_admin()</code>.<br/>Global access across all institutes.", styles['TableCell']),
            Paragraph("Full institutional governance: batch imports curriculums, rooms, and proctors; executes automated CSP scheduler; adjusts dates/rooms with live conflict checking; manages dual-authorization schedule reset requests; manages user credentials.", styles['TableCell'])
        ],
    ]
    t_role = Table(role_data, colWidths=[1.0 * inch, 2.2 * inch, 4.2 * inch])
    t_role.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, subtle_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_role)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Rolling Inactivity Watchdog (20-Minute Inactivity Timeout):</b>", styles['SubSecHeader']))
    story.append(Paragraph(
        "To comply with NIST SP 800-63B and institutional data protection guidelines, an application-level watchdog "
        "<code>@app.before_request check_session_inactivity()</code> executes on every incoming request. If "
        "<code>time.time() - session['_last_active'] > 1200 seconds (20 minutes)</code>, the session is cleared, an "
        "<code>AUTH_SESSION_TIMEOUT</code> event is written to <code>audit_logs</code>, and the user is redirected to <code>/login</code>. "
        "Polling endpoints (such as <code>/api/notifications/unread-count</code>) are specifically exempt from refreshing "
        "<code>_last_active</code>, ensuring background JavaScript tickers do not keep unattended sessions active.",
        styles['CustomBody']
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3. Backend & Database Architecture (app.py & database.py)", styles['SecHeader']))
    story.append(Paragraph(
        "The backend service layer is engineered around connection resilience, thread safety, and strict separation of concerns:",
        styles['CustomBody']
    ))

    story.append(Paragraph("<b>MySQL Connection Pooling & Burst Fallback:</b>", styles['SubSecHeader']))
    story.append(Paragraph(
        "Opening raw database connections for every request causes high socket latency and risks database connection "
        "exhaustion under peak student traffic. In <code>system/database.py</code>, we implement a persistent connection "
        "pool via <code>mysql.connector.pooling.MySQLConnectionPool</code> initialized with <code>pool_size = 10</code> and "
        "<code>pool_reset_session = True</code>. When connections return to the pool via <code>db.close()</code>, "
        "all user variables, active transactions, and temporary states are cleared automatically. If extreme traffic "
        "spikes exhaust the 10 pooled connections, <code>open_db()</code> captures the pool exception and immediately "
        "spawns a direct database connection, ensuring requests never fail with 500 server errors.",
        styles['CustomBody']
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Autonomous Database Schema Synchronization:</b>", styles['SubSecHeader']))
    story.append(Paragraph(
        "To eliminate migration errors when deploying across environments, <code>ensure_database_schema()</code> runs automatically "
        "upon application launch. It dynamically inspects existing table definitions and non-destructively adds required "
        "structures, including <code>audit_logs</code>, <code>exam_archives</code>, and <code>schedule_reset_requests</code>, "
        "as well as essential operational columns (<code>schedule_published</code>, <code>max_daily_proctor_hrs</code>).",
        styles['CustomBody']
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Non-Repudiation Audit Logging:</b>", styles['SubSecHeader']))
    story.append(Paragraph(
        "All state-changing actions—such as timetable modifications, user promotions, schedule resets, and student approvals—are "
        "permanently recorded in the <code>audit_logs</code> table with the actor's <code>user_id</code>, <code>user_role</code>, "
        "client <code>ip_address</code>, action type, and detailed description. This provides forensic accountability and full "
        "compliance with institutional security standards.",
        styles['CustomBody']
    ))

    # Force clean page break to Page 3
    story.append(PageBreak())

    # =============================================================
    # PAGE 3: THE SCHEDULING ENGINE (SCHEDULER.PY & CSP)
    # =============================================================
    story.append(Paragraph("4. The Scheduling Engine (scheduler.py & Constraint Satisfaction)", styles['SecHeader']))
    story.append(Paragraph(
        "Examination scheduling is mathematically categorized as the <b>Examination Timetabling Problem (ETP)</b>, "
        "a proven <b>NP-Hard Combinatorial Optimization Problem</b>. A brute-force search over all combinations of "
        "exams, rooms, dates, and proctors is computationally intractable. To generate a 100% conflict-free timetable "
        "in seconds, we engineered a deterministic <b>Constraint Satisfaction Problem (CSP) Heuristic Engine with a Tiered Relaxation Ladder</b>.",
        styles['CustomBody']
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Hard Constraints (Mathematically Invariant - Zero Violations Allowed):</b>", styles['SubSecHeader']))

    hard_constraints = [
        ("1. Zero Room Double-Booking", "Ensured by interval collision checks room_cal[r_id] against candidate [start, end]. No two exams ever occupy the same physical room at overlapping times."),
        ("2. Zero Proctor Double-Booking", "Ensured by inst_cal[i_id]. A proctor can never be scheduled for two concurrent examinations."),
        ("3. Zero Student Overlap + 1-Hour Rest Buffer", "section_free(sec, s, e) checks interval [s - 1 hour, e + 1 hour] against section_cal. Students never have simultaneous exams, and a mandatory 1-hour rest window is guaranteed between exams to eliminate cognitive fatigue."),
        ("4. Sister-Section Synchronization", "Exams are pre-grouped by content_group_id or subject_id. All class sections enrolled in the same course take the exam at the exact same time slot across parallel rooms. This completely eliminates test question leaks."),
        ("5. Strict Anti-Self-Proctoring", "Faculty members are strictly barred from proctoring examinations for subjects they teach. Pre-tokenized subjects_taught sets are matched against the exam group tokens before candidate evaluation."),
        ("6. Proctor Availability Windows", "O(1) dictionary lookup against proctor_availability ensures instructors are only assigned during time windows they officially submitted."),
        ("7. PWD Accessibility Matching", "Faculty members with physical disabilities (is_pwd = 1) are strictly assigned to rooms marked as wheelchair-accessible (is_pwd_accessible = 1) on ground floors or elevator-serviced wings."),
        ("8. Seating Capacity Bounds", "The engine verifies that room.capacity >= section_student_count (or institute default capacity).")
    ]

    for title, desc in hard_constraints:
        story.append(Paragraph(f"<b>&bull; {title}:</b> {desc}", styles['BulletItem']))

    story.append(Spacer(1, 5))
    story.append(Paragraph("<b>Soft Constraints & The 4-Tier Relaxation Ladder:</b>", styles['SubSecHeader']))
    story.append(Paragraph(
        "In dense exam periods, rigid daily proctor limits can cause artificial scheduling deadlocks. The engine resolves "
        "this by dynamically evaluating candidate slots across a progressive 4-tier relaxation ladder:",
        styles['CustomBody']
    ))

    tier_table_data = [
        [Paragraph("<b>Tier</b>", styles['TableHeader']), Paragraph("<b>Daily Major Cap per Section</b>", styles['TableHeader']), Paragraph("<b>Daily Proctoring Cap per Faculty</b>", styles['TableHeader']), Paragraph("<b>Operational Purpose</b>", styles['TableHeader'])],
        [
            Paragraph("<b>Tier 1</b>", styles['TableCellBold']),
            Paragraph("Max 2 Major Exams", styles['TableCell']),
            Paragraph("Max 4.0 Hours", styles['TableCell']),
            Paragraph("Ideal institutional balance; standard target load.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Tier 2</b>", styles['TableCellBold']),
            Paragraph("Max 2 Major Exams", styles['TableCell']),
            Paragraph("Max 5.0 Hours", styles['TableCell']),
            Paragraph("Absorbs minor bottlenecks while preserving student study balance.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Tier 3</b>", styles['TableCellBold']),
            Paragraph("Max 3 Major Exams", styles['TableCell']),
            Paragraph("Max 6.5 Hours", styles['TableCell']),
            Paragraph("High-density periods with limited faculty inventory.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Tier 4</b>", styles['TableCellBold']),
            Paragraph("Max 3 Major Exams", styles['TableCell']),
            Paragraph("Max 8.0 Hours (Absolute Ceiling)", styles['TableCell']),
            Paragraph("Emergency fail-safe; ensures 100% placement rather than unassigned exams.", styles['TableCell'])
        ],
    ]
    t_tier = Table(tier_table_data, colWidths=[0.8 * inch, 1.8 * inch, 2.0 * inch, 2.8 * inch])
    t_tier.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, subtle_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_tier)
    story.append(Spacer(1, 5))

    story.append(Paragraph("<b>Fair Rotation & Campus Travel Heuristics:</b>", styles['SubSecHeader']))
    story.append(Paragraph(
        "Candidate proctors are sorted using a multi-attribute comparator: (1) fewest proctoring hours worked on that day, "
        "(2) fewest cumulative hours worked across the exam period, and (3) a round-robin assignment counter. This guarantees "
        "equitable workload distribution. Additionally, when a proctor moves between different buildings, the engine enforces "
        "a mandatory <code>15-minute inter-building travel buffer</code> (<code>travel_buffer_min = 15</code>).",
        styles['CustomBody']
    ))

    # Force clean page break to Page 4
    story.append(PageBreak())

    # =============================================================
    # PAGE 4: DEPLOYMENT/INFRASTRUCTURE & CAPSTONE DEFENSE Q&A
    # =============================================================
    story.append(Paragraph("5. Deployment & Cloud Infrastructure", styles['SecHeader']))
    story.append(Paragraph(
        "The production system is hosted on an enterprise Linux Virtual Private Server (VPS) on DigitalOcean, "
        "architected for high availability and automated recovery:",
        styles['CustomBody']
    ))

    infra_items = [
        ("DigitalOcean Ubuntu Droplet (165.22.100.18)", "Provides high-performance compute and isolated memory, operating in the Asia/Manila (+08:00) timezone to match institutional schedules."),
        ("DuckDNS Dynamic DNS (cca-exam.duckdns.org)", "Binds the droplet's public IP to a persistent domain name, enabling automated SSL/TLS certificate renewal via Let's Encrypt Certbot."),
        ("Nginx Reverse Proxy & SSL Gateway", "Listens on ports 80 and 443. Terminates SSL/TLS; forwards authenticated traffic to Gunicorn on 127.0.0.1:9999. Configured with client_max_body_size 50M for batch file uploads and proxy_read_timeout 300s to handle long-running batch scheduling without 504 timeouts."),
        ("Gunicorn WSGI Application Server", "Runs 3 pre-forked worker processes. If one worker process is computing a complex schedule, the remaining workers continue to serve student schedule inquiries without degradation."),
        ("Linux Systemd Supervisor (cca_exam.service)", "Controls the Gunicorn process daemon with Restart=always. If the process encounters a fatal exception or the host reboots, Systemd revives the service within milliseconds. Environment variables (DB credentials, FLASK_SECRET_KEY) are securely isolated in the service definition."),
        ("1-Click Automated Deployment Pipeline", "Executed via update_server_now.bat and deploy_remote.sh. The script packages source files into cca_exam_deploy.zip, transfers them via SCP, purges stale .pyc bytecode, verifies database settings, and issues a zero-downtime reload to Gunicorn and Nginx.")
    ]

    for title, desc in infra_items:
        story.append(Paragraph(f"<b>&bull; {title}:</b> {desc}", styles['BulletItem']))

    story.append(Spacer(1, 6))

    story.append(Paragraph("6. Capstone Defense: Panelist Anticipated Questions & Answers", styles['SecHeader']))
    story.append(Paragraph(
        "Be prepared to deliver these concise, professional engineering responses during your defense presentation:",
        styles['CustomBody']
    ))

    qa_list = [
        (
            "Q1: Why did you develop a custom heuristic CSP engine instead of using an off-the-shelf solver like Google OR-Tools CP-SAT directly in production?",
            "<b>Answer:</b> While commercial solvers like OR-Tools are powerful general-purpose tools, they introduce heavy C++ binary dependencies, high RAM overhead, and deployment fragility on lean VPS instances. Academic scheduling includes unique institutional rules—such as sister-section synchronization, 1-hour cognitive rest buffers, anti-self-proctoring token matching, building transit buffers, and PWD room accessibility. Our custom CSP heuristic with a Tiered Relaxation Ladder is specifically tailored to these requirements, executing in under two seconds with 100% deterministic constraint satisfaction."
        ),
        (
            "Q2: How does the system mathematically prevent test question leaks between different sections?",
            "<b>Answer:</b> We enforce Sister-Section Synchronization in <code>system/scheduler.py</code>. All exams sharing the same <code>content_group_id</code> or <code>subject_id</code> are treated as an atomic scheduling cluster. The engine locks a single synchronized timestamp for the entire cluster. All sister sections take the exam at the exact same hour and date across parallel rooms, eliminating any opportunity for questions to be leaked between sections."
        ),
        (
            "Q3: What mechanisms prevent session hijacking and cross-site scripting (XSS) cookie theft?",
            "<b>Answer:</b> We implement four layers of session security: (1) 256-bit entropy cryptographic cookie signing via Flask's secret key; (2) <code>SESSION_COOKIE_HTTPONLY = True</code>, making cookies completely inaccessible to client-side JavaScript; (3) <code>SESSION_COOKIE_SAMESITE = 'Lax'</code> with <code>Flask-WTF</code> CSRF tokens on all mutating requests; and (4) a rolling 20-minute inactivity watchdog that purges expired sessions automatically."
        ),
        (
            "Q4: What happens if all 10 pooled MySQL connections are busy when a burst of students logs in?",
            "<b>Answer:</b> In <code>system/database.py</code>, <code>open_db()</code> catches connection pool exhaustion exceptions gracefully. Instead of dropping the user's request with an HTTP 500 Internal Server Error, the system immediately spawns an on-demand direct MySQL connection to handle the burst, returning to the pool once traffic normalizes."
        ),
        (
            "Q5: How does your system prevent proctor burnout during grueling multi-day exam periods?",
            "<b>Answer:</b> Proctor assignment uses a three-tier fair rotation heuristic: (1) fewest hours worked on the scheduled date, (2) fewest total cumulative hours across the entire exam period, and (3) a round-robin assignment tiebreaker. In addition, consecutive proctoring is capped at 3 hours, daily hours are strictly constrained by the active relaxation tier, and a 15-minute inter-building travel buffer is enforced."
        )
    ]

    for q, a in qa_list:
        qa_flow = [
            Paragraph(q, styles['QAQuestion']),
            Paragraph(a, styles['QAAnswer'])
        ]
        story.append(KeepTogether(qa_flow))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built: {filename}")

if __name__ == '__main__':
    target_path = r"c:\xampp\htdocs\EXAM_MANAGEMENT\CCA_Exam_Management_Capstone_Defense_Guide.pdf"
    static_path = r"c:\xampp\htdocs\EXAM_MANAGEMENT\static\CCA_Exam_Management_Capstone_Defense_Guide.pdf"
    build_pdf(target_path)
    build_pdf(static_path)
