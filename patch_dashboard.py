with open("template/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

import re

old_row = """<tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">subjects_taught</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">Pipe-separated: <em>Math|Physics</em></td></tr>"""

new_row = """<tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">subjects_taught</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">Pipe-separated: <em>Math|Physics</em></td></tr>
                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded text-[#668054]">availability</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-[#668054] font-medium">e.g. <em>Mon 07:00-12:00, Wed</em></td></tr>"""

html = html.replace(old_row, new_row)

old_sample = """<code class="bg-gray-100 px-1 rounded">Juan Dela Cruz,ICSLIS,Main Building,0,IT 2|Database</code>"""
new_sample = """<code class="bg-gray-100 px-1 rounded">Juan Dela Cruz,ICSLIS,Main Building,0,IT 2|Database,"Mon 07:00-12:00"</code>"""

html = html.replace(old_sample, new_sample)

with open("template/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Updated UI in dashboard.html!")
