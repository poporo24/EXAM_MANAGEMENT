with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

# We need to replace the plain badges in the conflict summary with the group-hover wrapper versions
replacements = {
    '<span class="badge badge-conflict-room"><i class="fa-solid fa-door-open mr-0.5"></i>Room</span>': """<div class="group relative inline-flex justify-center">
    <span class="badge badge-conflict-room"><i class="fa-solid fa-door-open mr-0.5"></i> Room</span>
    <div class="absolute bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-gray-800 text-white text-[11px] leading-tight rounded shadow-lg z-[100] text-center pointer-events-none before:content-[''] before:absolute before:top-full before:left-1/2 before:-translate-x-1/2 before:border-4 before:border-transparent before:border-t-gray-800">
        Another exam is already scheduled in this room at this time.
    </div>
</div>""",
    '<span class="badge badge-conflict-proctor"><i class="fa-solid fa-user-xmark mr-0.5"></i>Proctor</span>': """<div class="group relative inline-flex justify-center">
    <span class="badge badge-conflict-proctor"><i class="fa-solid fa-user-xmark mr-0.5"></i> Proctor</span>
    <div class="absolute bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-gray-800 text-white text-[11px] leading-tight rounded shadow-lg z-[100] text-center pointer-events-none before:content-[''] before:absolute before:top-full before:left-1/2 before:-translate-x-1/2 before:border-4 before:border-transparent before:border-t-gray-800">
        This proctor is already assigned to another room or is unavailable at this time.
    </div>
</div>""",
    '<span class="badge badge-conflict-section"><i class="fa-solid fa-users mr-0.5"></i>Section</span>': """<div class="group relative inline-flex justify-center">
    <span class="badge badge-conflict-section"><i class="fa-solid fa-users mr-0.5"></i> Section</span>
    <div class="absolute bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-gray-800 text-white text-[11px] leading-tight rounded shadow-lg z-[100] text-center pointer-events-none before:content-[''] before:absolute before:top-full before:left-1/2 before:-translate-x-1/2 before:border-4 before:border-transparent before:border-t-gray-800">
        This section has another exam overlapping or less than 1 hour away.
    </div>
</div>""",
    '<span class="badge badge-conflict-subject"><i class="fa-solid fa-book mr-0.5"></i>Subject</span>': """<div class="group relative inline-flex justify-center">
    <span class="badge badge-conflict-subject"><i class="fa-solid fa-book mr-0.5"></i> Subject</span>
    <div class="absolute bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-gray-800 text-white text-[11px] leading-tight rounded shadow-lg z-[100] text-center pointer-events-none before:content-[''] before:absolute before:top-full before:left-1/2 before:-translate-x-1/2 before:border-4 before:border-transparent before:border-t-gray-800">
        Integrity Risk: Different sections of this subject are taking the exam at different times.
    </div>
</div>""",
    '<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;2 Major/day</span>': """<div class="group relative inline-flex justify-center">
    <span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i> &gt;2 Major/day</span>
    <div class="absolute bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-gray-800 text-white text-[11px] leading-tight rounded shadow-lg z-[100] text-center pointer-events-none before:content-[''] before:absolute before:top-full before:left-1/2 before:-translate-x-1/2 before:border-4 before:border-transparent before:border-t-gray-800">
        This section is exceeding the limit of 2 Major exams per day.
    </div>
</div>""",
    '<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;3 Minor/day</span>': """<div class="group relative inline-flex justify-center">
    <span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i> &gt;3 Minor/day</span>
    <div class="absolute bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-gray-800 text-white text-[11px] leading-tight rounded shadow-lg z-[100] text-center pointer-events-none before:content-[''] before:absolute before:top-full before:left-1/2 before:-translate-x-1/2 before:border-4 before:border-transparent before:border-t-gray-800">
        This section is exceeding the limit of 3 Minor exams per day.
    </div>
</div>""",
    '<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;3 Exams/day</span>': """<div class="group relative inline-flex justify-center">
    <span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i> &gt;3 Exams/day</span>
    <div class="absolute bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-gray-800 text-white text-[11px] leading-tight rounded shadow-lg z-[100] text-center pointer-events-none before:content-[''] before:absolute before:top-full before:left-1/2 before:-translate-x-1/2 before:border-4 before:border-transparent before:border-t-gray-800">
        This section is exceeding the limit of 3 total exams per day.
    </div>
</div>"""
}

if 'CONFLICTS SUMMARY' in html:
    parts = html.split('CONFLICTS SUMMARY')
    before = parts[0]
    after = parts[1]
    
    for old, new in replacements.items():
        after = after.replace(old, new)
        
    html = before + 'CONFLICTS SUMMARY' + after
    
    with open("template/schedule.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Patched Conflicts Summary tooltips!")
else:
    print("Could not find Conflicts Summary section!")
