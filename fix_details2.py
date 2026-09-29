import re
html_path = 'template/super_admin.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

new_details = '''                                  <td class="px-6 py-4 text-sm text-gray-500">
                                      {% if user.role == 'student' %}
                                          {% if user.section %}<span class="block"><span class="font-medium text-gray-600">Section:</span> {{ user.section }}</span>{% endif %}
                                          {% if user.institute_name %}<span class="block"><span class="font-medium text-gray-600">Institute:</span> {{ user.institute_name }}</span>{% endif %}
                                          {% if not user.section and not user.institute_name %}<span class="text-gray-400 italic">No details</span>{% endif %}
                                      {% elif user.role == 'proctor' or user.role == 'secretary' %}
                                          {% if user.institute_name %}<span class="block"><span class="font-medium text-gray-600">Institute:</span> {{ user.institute_name }}</span>{% else %}<span class="text-gray-400 italic">No institute assigned</span>{% endif %}
                                      {% else %}
                                          <span class="text-gray-400">-</span>
                                      {% endif %}
                                  </td>'''

pattern = re.compile(
    r'<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">\s*'
    r'{%\s*if user\.role == .student.\s*%}.*?'
    r'{%\s*endif\s*%}\s*</td>',
    re.DOTALL
)
match = pattern.search(html)
if match:
    html = html.replace(match.group(0), new_details)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed!")
else:
    print("Still not found!")
