import os

filepath = 'template/proctor_dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

insert_idx = -1
for i, line in enumerate(lines):
    if line.strip() == 'You have no proctoring assignments yet.':
        # the div ends 3 lines down
        insert_idx = i + 4
        break

if insert_idx != -1:
    content_to_insert = """
                <!-- Availability -->
                <div class="lg:col-span-1">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">My Assigned Availability</h3>
                    <div class="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                        <p class="text-sm text-gray-500 mb-4">Your available dates and time slots as set by the administration.</p>
                        {% if saved_dates %}
                            <ul class="space-y-3">
                                {% for slot in saved_dates %}
                                <li class="flex flex-col border-b border-gray-100 last:border-0 pb-3 last:pb-0">
                                    <span class="text-sm font-bold text-gray-800"><i class="fa-regular fa-calendar text-[#668054] w-4 mr-1"></i> {{ slot.date }}</span>
                                    <span class="text-xs text-gray-500 ml-6"><i class="fa-regular fa-clock w-3 mr-1"></i> {{ slot.start_time }} - {{ slot.end_time }}</span>
                                </li>
                                {% endfor %}
                            </ul>
                        {% else %}
                            <div class="text-center py-6 text-gray-400 text-sm bg-gray-50 rounded-lg">
                                <i class="fa-solid fa-calendar-xmark text-3xl mb-2 opacity-50 block"></i>
                                <p>No availability set.</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
"""
    lines.insert(insert_idx, content_to_insert)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully inserted.")
else:
    print("Could not find insertion point.")
