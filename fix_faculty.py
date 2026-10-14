import os

filepath = 'template/faculty.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">subjects_taught</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">Pipe-separated: <em>Math|Physics</em></td></tr>
                        </tbody>
                    </table>
                    <p class="text-xs text-gray-400 mt-2"><span class="font-medium text-gray-500">Sample row:</span> <code class="bg-gray-100 px-1 rounded">Juan Dela Cruz,juan@cca.edu.ph,ICSLIS,Main Building,0,IT 2|Database</code></p>'''

target_r = target.replace('\n', '\r\n')

replacement = '''                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded">subjects_taught</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-gray-400">Pipe-separated: <em>Math|Physics</em></td></tr>
                            <tr><td class="px-3 py-1.5"><code class="bg-gray-100 px-1 rounded text-[#668054]">availability</code></td><td class="px-3 py-1.5 text-gray-500">Text</td><td class="px-3 py-1.5 text-[#668054] font-medium">e.g. <em>Mon 07:00-12:00, Wed</em></td></tr>
                        </tbody>
                    </table>
                    <p class="text-xs text-gray-400 mt-2"><span class="font-medium text-gray-500">Sample row:</span> <code class="bg-gray-100 px-1 rounded">Juan Dela Cruz,juan@cca.edu.ph,ICSLIS,Main Building,0,IT 2|Database,"Mon 07:00-12:00"</code></p>'''

if target in content:
    content = content.replace(target, replacement)
elif target_r in content:
    content = content.replace(target_r, replacement)
else:
    print('Not found')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
