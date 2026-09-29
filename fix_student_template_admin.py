import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\student_timetable.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''
        <button class="ctrl-btn ctrl-btn-print" onclick="window.print()">
            <i class="fa-solid fa-print"></i> Print
        </button>
        {% if full_name != "Admin Generated" %}
        <button class="ctrl-btn ctrl-btn-outline" onclick="openStudentPwModal()">
            <i class="fa-solid fa-key"></i> Change Password
        </button>
        <a href="/logout" class="ctrl-btn ctrl-btn-logout">
            <i class="fa-solid fa-right-from-bracket"></i> Logout
        </a>
        {% endif %}
'''
content = content.replace('''
        <button class="ctrl-btn ctrl-btn-print" onclick="window.print()">
            <i class="fa-solid fa-print"></i> Print
        </button>
        <button class="ctrl-btn ctrl-btn-outline" onclick="openStudentPwModal()">
            <i class="fa-solid fa-key"></i> Change Password
        </button>
        <a href="/logout" class="ctrl-btn ctrl-btn-logout">
            <i class="fa-solid fa-right-from-bracket"></i> Logout
        </a>''', replacement)

content = content.replace('<!-- Change Password Modal -->', '{% if full_name != "Admin Generated" %}\n<!-- Change Password Modal -->')
content = content.replace('</form>\n    </div>\n</div>\n\n<main class="main-content" id="examContainer">', '</form>\n    </div>\n</div>\n{% endif %}\n\n<main class="main-content" id="examContainer">')

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\student_timetable.html', 'w', encoding='utf-8') as f:
    f.write(content)
