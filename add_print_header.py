import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

html_replacement = '''
            <div class="print-only">
                <div class="print-header">
                    <div class="print-logo-section">
                        <i class="fa-solid fa-graduation-cap"></i>
                        <div class="print-univ-info">
                            <h2>City College of Angeles</h2>
                            <p>Arayat Blvd, Angeles, Pampanga, 2009</p>
                            <p>info@cca.edu.ph</p>
                        </div>
                    </div>
                    <div class="print-title-section">
                        <h1>MASTER EXAM SCHEDULE</h1>
                        <p>Midterm/Final term examination test</p>
                        <p>School Year: 2025-2026</p>
                        {% if filter_section %}
                        <p style="margin-top:5px; font-size:16px; color:#111;"><strong>Section: {{ filter_section }}</strong></p>
                        {% endif %}
                    </div>
                </div>
            </div>
            
            <div class="timetable-wrapper mb-8">
'''

content = content.replace('<div class="timetable-wrapper mb-8">', html_replacement)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'w', encoding='utf-8') as f:
    f.write(content)
