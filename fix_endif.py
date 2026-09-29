import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\student_timetable.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
content = re.sub(r'        </form>\n    </div>\n</div>', r'        </form>\n    </div>\n</div>\n{% endif %}', content)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\student_timetable.html', 'w', encoding='utf-8') as f:
    f.write(content)
