with open("template/faculty.html", "r", encoding="utf-8") as f:
    html = f.read()

old_add_name_field = """                    <form action="/add_instructor" method="POST" id="addInstructorForm" class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Full Name</label>
                            <input type="text" name="name" required class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                        </div>"""

new_add_name_fields = """                    <form action="/add_instructor" method="POST" id="addInstructorForm" class="space-y-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Last Name</label>
                                <input type="text" name="last_name" required class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">First Name</label>
                                <input type="text" name="first_name" required class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Middle Name</label>
                                <input type="text" name="middle_name" class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2" placeholder="e.g. M.">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Suffix (Optional)</label>
                                <input type="text" name="suffix" class="mt-1 focus:ring-[#668054] block w-full sm:text-sm border-gray-300 rounded-md border p-2" placeholder="e.g. Jr.">
                            </div>
                        </div>"""

if old_add_name_field in html:
    html = html.replace(old_add_name_field, new_add_name_fields)
    with open("template/faculty.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Patched faculty.html add instructor HTML")
else:
    print("Could not find old_add_name_field in faculty.html")
