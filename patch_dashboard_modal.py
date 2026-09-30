with open("template/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

old_table = """                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">subject_code</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">Required. e.g. <em>IT111</em></td></tr>
                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">section</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">e.g. <em>IT1A</em></td></tr>
                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">subject_type</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400"><em>Major</em> or <em>Minor</em> (default: Major)</td></tr>
                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">institute_code</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">e.g. <em>ICSLIS</em>, leave blank for GED</td></tr>"""

new_table = """                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">subject_name</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">e.g. <em>Filipino 1</em></td></tr>
                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">subject_code</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">Required. e.g. <em>6ADPROG</em></td></tr>
                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">section</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">e.g. <em>GED1A</em></td></tr>
                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">subject_type</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400"><em>Major</em> or <em>Minor</em></td></tr>
                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">institute_code</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">e.g. <em>ICSLIS</em>, leave blank for GED</td></tr>"""

html = html.replace(old_table, new_table)
html = html.replace('<code class="bg-gray-100 px-1 rounded">Programming 1,IT1A,Major,ICSLIS</code>', '<code class="bg-gray-100 px-1 rounded">Filipino 1,6ADPROG,GED1A,Minor,</code>')

with open("template/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Dashboard modal patched")
