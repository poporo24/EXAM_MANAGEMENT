import re
with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

new_cards = """            <!-- Stats strip / Tabs -->
            <div class="no-print grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
                <!-- Scheduled Tab -->
                <div id="card_scheduled" onclick="switchTab('scheduled')" class="bg-white rounded-xl border-2 border-[#668054] shadow-sm p-4 cursor-pointer hover:shadow-md transition-all relative overflow-hidden">
                    <div class="absolute top-0 right-0 w-2 h-full bg-[#668054]"></div>
                    <p class="text-xs text-[#668054] uppercase tracking-wide font-bold">Scheduled</p>
                    <p class="text-2xl font-bold text-[#668054] mt-1">{{ sched_count }} <span class="text-lg text-gray-400 font-normal">/ {{ total }}</span></p>
                </div>
                <!-- Unscheduled Tab -->
                <div id="card_unscheduled" onclick="switchTab('unscheduled')" class="bg-white rounded-xl border-2 border-transparent shadow-sm p-4 cursor-pointer hover:border-gray-300 hover:shadow-md transition-all">
                    <p class="text-xs text-gray-500 uppercase tracking-wide font-medium">Unscheduled</p>
                    <p class="text-2xl font-bold {% if unscheduled|length > 0 %}text-red-500{% else %}text-gray-400{% endif %} mt-1">{{ unscheduled|length }}</p>
                </div>
                <!-- Conflicts Tab -->
                <div id="card_conflicts" onclick="switchTab('conflicts')" class="bg-white rounded-xl border-2 border-transparent shadow-sm p-4 cursor-pointer hover:border-gray-300 hover:shadow-md transition-all">
                    <p class="text-xs text-gray-500 uppercase tracking-wide font-medium">Conflicts</p>
                    <p class="text-2xl font-bold {% if conflict_ids|length > 0 %}text-orange-500{% else %}text-gray-400{% endif %} mt-1">{{ conflict_ids|length }}</p>
                </div>
            </div>

            <!-- ?? TIMETABLE GRID ?? -->"""

html = re.sub(r'<!-- Stats strip -->.*?<!-- ?? TIMETABLE GRID ?? -->', new_cards, html, flags=re.DOTALL)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Replaced Stats Strip successfully!")
