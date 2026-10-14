import re

with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

# We want to replace the span tags with a wrapped group div.
# But since there are multiple variations, we can just replace the raw HTML for each reason block.

replacements = {
    "room": "Another exam is already scheduled in this room at this time.",
    "proctor": "This proctor is already assigned to another room or is unavailable at this time.",
    "section": "This section has another exam overlapping or less than 1 hour away.",
    "subject": "Integrity Risk: Different sections of this subject are taking the exam at different times.",
    "daily_major": "This section is exceeding the limit of 2 Major exams per day.",
    "daily_minor": "This section is exceeding the limit of 3 Minor exams per day.",
    "daily_total": "This section is exceeding the limit of 3 total exams per day."
}

def make_tooltip(span_html, text):
    # Remove existing title attribute if any
    span_html = re.sub(r' title="[^"]+"', '', span_html)
    return f"""<div class="group relative inline-flex justify-center">
    {span_html}
    <div class="absolute bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-gray-800 text-white text-[11px] leading-tight rounded shadow-lg z-[100] text-center pointer-events-none before:content-[''] before:absolute before:top-full before:left-1/2 before:-translate-x-1/2 before:border-4 before:border-transparent before:border-t-gray-800">
        {text}
    </div>
</div>"""

# Manually replace the known blocks in Timetable grid
html = re.sub(r'<span class="badge badge-conflict-room"><i class="fa-solid fa-door-open mr-0.5"></i> Room Conflict</span>', make_tooltip('<span class="badge badge-conflict-room"><i class="fa-solid fa-door-open mr-0.5"></i> Room Conflict</span>', replacements['room']), html)

html = re.sub(r'<span class="badge badge-conflict-proctor"><i class="fa-solid fa-user-xmark mr-0.5"></i> Proctor Conflict</span>', make_tooltip('<span class="badge badge-conflict-proctor"><i class="fa-solid fa-user-xmark mr-0.5"></i> Proctor Conflict</span>', replacements['proctor']), html)

html = re.sub(r'<span class="badge badge-conflict-section"><i class="fa-solid fa-users mr-0.5"></i> Section Conflict</span>', make_tooltip('<span class="badge badge-conflict-section"><i class="fa-solid fa-users mr-0.5"></i> Section Conflict</span>', replacements['section']), html)

html = re.sub(r'<span class="badge badge-conflict-subject"><i class="fa-solid fa-book mr-0.5"></i> Subject Conflict</span>', make_tooltip('<span class="badge badge-conflict-subject"><i class="fa-solid fa-book mr-0.5"></i> Subject Conflict</span>', replacements['subject']), html)

html = re.sub(r'<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i> &gt;2 Major/day</span>', make_tooltip('<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i> &gt;2 Major/day</span>', replacements['daily_major']), html)

html = re.sub(r'<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i> &gt;3 Minor/day</span>', make_tooltip('<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i> &gt;3 Minor/day</span>', replacements['daily_minor']), html)

html = re.sub(r'<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i> &gt;3 Exams/day</span>', make_tooltip('<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i> &gt;3 Exams/day</span>', replacements['daily_total']), html)

# Now for the Conflict Summary table which has title tags
html = re.sub(r'<span class="badge badge-conflict-room" title="[^"]+"><i class="fa-solid fa-door-open mr-0.5"></i>Room</span>', make_tooltip('<span class="badge badge-conflict-room"><i class="fa-solid fa-door-open mr-0.5"></i>Room</span>', replacements['room']), html)

html = re.sub(r'<span class="badge badge-conflict-proctor" title="[^"]+"><i class="fa-solid fa-user-xmark mr-0.5"></i>Proctor</span>', make_tooltip('<span class="badge badge-conflict-proctor"><i class="fa-solid fa-user-xmark mr-0.5"></i>Proctor</span>', replacements['proctor']), html)

html = re.sub(r'<span class="badge badge-conflict-section" title="[^"]+"><i class="fa-solid fa-users mr-0.5"></i>Section</span>', make_tooltip('<span class="badge badge-conflict-section"><i class="fa-solid fa-users mr-0.5"></i>Section</span>', replacements['section']), html)

html = re.sub(r'<span class="badge badge-conflict-subject" title="[^"]+"><i class="fa-solid fa-book mr-0.5"></i>Subject</span>', make_tooltip('<span class="badge badge-conflict-subject"><i class="fa-solid fa-book mr-0.5"></i>Subject</span>', replacements['subject']), html)

html = re.sub(r'<span class="badge badge-conflict-daily" title="[^"]+"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;2 Major/day</span>', make_tooltip('<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;2 Major/day</span>', replacements['daily_major']), html)

html = re.sub(r'<span class="badge badge-conflict-daily" title="[^"]+"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;3 Minor/day</span>', make_tooltip('<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;3 Minor/day</span>', replacements['daily_minor']), html)

html = re.sub(r'<span class="badge badge-conflict-daily" title="[^"]+"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;3 Exams/day</span>', make_tooltip('<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;3 Exams/day</span>', replacements['daily_total']), html)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Applied custom tooltips")
