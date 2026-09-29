import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Insert @page landscape into @media print
css_addition = '''
        @media print {
            @page { size: landscape; margin: 10mm; }
            .timetable { table-layout: fixed; width: 100%; word-wrap: break-word; }
            .timetable th, .timetable td { overflow-wrap: break-word; font-size: 11px; padding: 4px !important; }
            .exam-card { font-size: 10px !important; padding: 4px !important; margin-bottom: 2px !important; }
            .exam-card .subject { font-size: 11px !important; white-space: normal !important; line-height: 1.1; }
            .exam-card .meta { font-size: 9px !important; white-space: normal !important; line-height: 1.1; }
            .badge { padding: 1px 4px !important; font-size: 8px !important; }
            
            .no-print { display: none !important; }
'''

content = re.sub(r'@media print\s*{\s*\.no-print\s*{\s*display:\s*none\s*!important;\s*}', css_addition, content)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\schedule.html', 'w', encoding='utf-8') as f:
    f.write(content)
