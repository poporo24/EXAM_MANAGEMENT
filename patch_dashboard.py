with open("template/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace(
    '<tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">subject_name</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">Required. e.g. <em>Programming 1</em></td></tr>',
    '<tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">subject_code</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">Required. e.g. <em>IT111</em></td></tr>'
)

with open("template/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Dashboard patched")
