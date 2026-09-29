import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

css_replacement = '''
        @media print {
            .no-print { display: none !important; }
            body { background: white !important; margin: 0; padding: 0; font-family: "Inter", sans-serif; }
            main { margin-left: 0 !important; padding: 0 !important; max-width: 100% !important; }
            .timetable-wrapper { box-shadow: none; border: 1px solid #ddd; width: 100%; margin-top: 20px; }
            .timetable-wrapper th { background-color: #668054 !important; color: white !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
            .timetable-wrapper .time-cell { background-color: #f9f9f9 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
            .timetable-wrapper td, .timetable-wrapper th { border-color: #ddd !important; }
            
            .print-only { display: block !important; }
            .print-header { text-align: center; margin-bottom: 20px; padding: 20px 20px 0 20px; }
            .print-logo-section { display: flex; align-items: center; justify-content: flex-start; margin-bottom: 15px; border-bottom: 2px solid #668054; padding-bottom: 10px; }
            .print-logo-section i { font-size: 36px; color: #668054; margin-right: 15px; }
            .print-univ-info h2 { margin: 0; font-size: 22px; font-weight: 700; color: #111; text-align: left; }
            .print-univ-info p { margin: 2px 0 0; font-size: 12px; color: #555; text-align: left; }
            .print-title-section h1 { font-size: 24px; font-weight: 800; color: #668054; margin: 0 0 5px; text-transform: uppercase; }
            .print-title-section p { margin: 3px 0; font-size: 14px; font-weight: 600; color: #333; }
        }
        @media screen {
            .print-only { display: none !important; }
        }
'''

import re
content = re.sub(r'@media print\s*{[^}]+}', css_replacement, content)

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
                    </div>
                </div>
            </div>
            
            <div class="timetable-wrapper">
'''

content = content.replace('<div class="timetable-wrapper">', html_replacement)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'w', encoding='utf-8') as f:
    f.write(content)
