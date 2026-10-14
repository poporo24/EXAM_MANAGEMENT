with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

badges = {
    """<span class="badge badge-conflict-room"><i class="fa-solid fa-door-open mr-0.5"></i>Room</span>""": """<span class="badge badge-conflict-room" title="Another exam is already scheduled in this room at this time."><i class="fa-solid fa-door-open mr-0.5"></i>Room</span>""",
    """<span class="badge badge-conflict-proctor"><i class="fa-solid fa-user-xmark mr-0.5"></i>Proctor</span>""": """<span class="badge badge-conflict-proctor" title="This proctor is already assigned to another room or is unavailable at this time."><i class="fa-solid fa-user-xmark mr-0.5"></i>Proctor</span>""",
    """<span class="badge badge-conflict-section"><i class="fa-solid fa-users mr-0.5"></i>Section</span>""": """<span class="badge badge-conflict-section" title="This section has another exam overlapping or less than 1 hour away."><i class="fa-solid fa-users mr-0.5"></i>Section</span>""",
    """<span class="badge badge-conflict-subject"><i class="fa-solid fa-book mr-0.5"></i>Subject</span>""": """<span class="badge badge-conflict-subject" title="Integrity Risk: Different sections of this subject are taking the exam at different times."><i class="fa-solid fa-book mr-0.5"></i>Subject</span>""",
    """<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;2 Major/day</span>""": """<span class="badge badge-conflict-daily" title="This section is exceeding the limit of 2 Major exams per day."><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;2 Major/day</span>""",
    """<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;3 Minor/day</span>""": """<span class="badge badge-conflict-daily" title="This section is exceeding the limit of 3 Minor exams per day."><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;3 Minor/day</span>""",
    """<span class="badge badge-conflict-daily"><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;3 Exams/day</span>""": """<span class="badge badge-conflict-daily" title="This section is exceeding the limit of 3 total exams per day."><i class="fa-solid fa-calendar-xmark mr-0.5"></i>&gt;3 Exams/day</span>"""
}

for old, new in badges.items():
    html = html.replace(old, new)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched tooltips")
