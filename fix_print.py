import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\student_timetable.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add print styles
css_replacement = '''
        /* PRINT */
        @media print {
            .hero, .controls-bar, .ctrl-btn-logout, .info-strip, .main-content, .page-footer, #studentPwModal { display:none !important; }
            body { background:#fff; margin: 0; padding: 0; font-family: "Inter", sans-serif; }
            .print-container { display: block !important; width: 100%; max-width: 100%; padding: 20px; }
        }
        @media screen {
            .print-container { display: none !important; }
        }

        /* Print Table Styles */
        .print-header { text-align: center; margin-bottom: 30px; }
        .print-logo-section { display: flex; align-items: center; justify-content: flex-start; margin-bottom: 20px; border-bottom: 2px solid #668054; padding-bottom: 15px; }
        .print-logo-section i { font-size: 40px; color: #668054; margin-right: 15px; }
        .print-univ-info h2 { margin: 0; font-size: 22px; font-weight: 700; color: #111; }
        .print-univ-info p { margin: 2px 0 0; font-size: 12px; color: #555; }
        
        .print-title-section h1 { font-size: 24px; font-weight: 800; color: #668054; margin: 0 0 5px; text-transform: uppercase; }
        .print-title-section p { margin: 3px 0; font-size: 14px; font-weight: 600; color: #333; }
        
        .print-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }
        .print-table th, .print-table td { border: 1px solid #ddd; padding: 10px; text-align: center; }
        .print-table th { background-color: #668054 !important; color: white !important; font-weight: 600; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .print-table td { color: #333; }
        .print-table tbody tr:nth-child(even) { background-color: #f9f9f9 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .print-table .text-left { text-align: left; }
'''

# Replace the existing print block
import re
content = re.sub(r'/\*\s*PRINT\s*\*/[\s\S]*?@media\s+print\s*{[\s\S]*?}', css_replacement, content)

print_html = '''
<!-- PRINT CONTAINER -->
<div class="print-container">
    <div class="print-header">
        <div class="print-logo-section">
            <i class="fa-solid fa-graduation-cap"></i>
            <div class="print-univ-info text-left">
                <h2>City College of Angeles</h2>
                <p>Arayat Blvd, Angeles, Pampanga, 2009</p>
                <p>info@cca.edu.ph</p>
            </div>
        </div>
        <div class="print-title-section">
            <h1>EXAM SCHEDULE</h1>
            <p>Midterm/Final term examination test</p>
            <p>School Year: 2025-2026</p>
        </div>
    </div>
    
    <div style="margin-bottom: 15px; font-size: 14px; display: flex; justify-content: space-between;">
        <div><strong>Student:</strong> {{ full_name }}</div>
        <div><strong>Section:</strong> {{ section }}</div>
    </div>

    <table class="print-table">
        <thead>
            <tr>
                <th rowspan="2">Subject</th>
                <th rowspan="2">Date</th>
                <th colspan="2">Time</th>
                <th rowspan="2">Location</th>
                <th rowspan="2">Duration</th>
            </tr>
            <tr>
                <th>Start Time</th>
                <th>End Time</th>
            </tr>
        </thead>
        <tbody>
            {% if grouped %}
                {% for date_str, exams in grouped %}
                    {% for exam in exams %}
                    <tr>
                        <td class="text-left"><strong>{{ exam.subject_name }}</strong></td>
                        <td>{{ date_str.split(', ')[1] }}</td>
                        <td>{{ exam.time }}</td>
                        <td>{{ exam.time_end }}</td>
                        <td>{{ exam.room_name or 'TBA' }}</td>
                        <td>{{ exam.duration_minutes }} Hours</td>
                    </tr>
                    {% endfor %}
                {% endfor %}
            {% else %}
                <tr>
                    <td colspan="6" style="padding: 20px;">No exams scheduled.</td>
                </tr>
            {% endif %}
        </tbody>
    </table>
</div>

<header class="hero">
'''

content = content.replace('<header class="hero">', print_html)

# wait, duration is in minutes, but the UI shows "1 Hours". I will change it to convert minutes to hours if possible, or just keep it "min". The reference shows "1 Hours". Let's use "{{ (exam.duration_minutes / 60)|int }} Hours".
content = content.replace("{{ exam.duration_minutes }} Hours", "{% if exam.duration_minutes == 60 %}1 Hour{% elif exam.duration_minutes == 120 %}2 Hours{% elif exam.duration_minutes == 90 %}1.5 Hours{% else %}{{ exam.duration_minutes }} min{% endif %}")

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\student_timetable.html', 'w', encoding='utf-8') as f:
    f.write(content)
