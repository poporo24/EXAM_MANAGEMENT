with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

old_cards = """            <!-- Stats strip -->
            <div class="no-print grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
                <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
                    <p class="text-xs text-gray-500 uppercase tracking-wide font-medium">Scheduled</p>
                    <p class="text-2xl font-bold text-[#668054] mt-1">{{ sched_count }} <span class="text-lg text-gray-400 font-normal">/ {{ total }}</span></p>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
                    <p class="text-xs text-gray-500 uppercase tracking-wide font-medium">Unscheduled</p>
                    <p class="text-2xl font-bold {% if unscheduled|length > 0 %}text-red-500{% else %}text-gray-400{% endif %} mt-1">{{ unscheduled|length }}</p>
                </div>
                <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4 {% if conflict_ids|length > 0 %}cursor-pointer hover:border-orange-300 hover:shadow-md transition-all{% endif %}"
                     {% if conflict_ids|length > 0 %}onclick="document.getElementById('conflictSummary').scrollIntoView({behavior:'smooth'})" title="Click to view all conflicts"{% endif %}>
                    <p class="text-xs text-gray-500 uppercase tracking-wide font-medium">Conflicts</p>
                    <p class="text-2xl font-bold {% if conflict_ids|length > 0 %}text-orange-500{% else %}text-gray-400{% endif %} mt-1">
                        {{ conflict_ids|length }}
                        {% if conflict_ids|length > 0 %}<span class="text-xs font-normal text-orange-400 ml-1">? view</span>{% endif %}
                    </p>
                </div>
            </div>"""

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
            </div>"""

if old_cards in html:
    html = html.replace(old_cards, new_cards)
else:
    print("WARNING: Could not find old cards!")

# 2. Add id="tab_scheduled" to the Timetable block wrapper
# We will wrap it right above `{% if dates and times %}`
old_timetable = """            <!-- ?? TIMETABLE GRID ?? -->
            {% if dates and times %}"""
new_timetable = """            <!-- ?? TIMETABLE GRID ?? -->
            <div id="tab_scheduled" class="block">
            {% if dates and times %}"""
html = html.replace(old_timetable, new_timetable)

# And close `tab_scheduled` right before the UNSCHEDULED EXAMS block
old_close_timetable = """            <!-- ?? UNSCHEDULED EXAMS ?? -->"""
new_close_timetable = """            </div> <!-- End tab_scheduled -->
            <!-- ?? UNSCHEDULED EXAMS ?? -->"""
html = html.replace(old_close_timetable, new_close_timetable)


# 3. Add id="tab_unscheduled" wrapper
old_unsched = """            <!-- ?? UNSCHEDULED EXAMS ?? -->
            {% if unscheduled %}"""
new_unsched = """            <!-- ?? UNSCHEDULED EXAMS ?? -->
            <div id="tab_unscheduled" class="hidden mb-8 no-print">
            {% if unscheduled %}"""
html = html.replace(old_unsched, new_unsched)

old_close_unsched = """            {% endif %}

            <!-- ?? CONFLICT SUMMARY ?? -->"""
new_close_unsched = """            {% else %}
                <div class="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-500"><i class="fa-solid fa-check-circle text-4xl text-green-500 mb-3 block"></i>There are no unscheduled exams!</div>
            {% endif %}
            </div> <!-- End tab_unscheduled -->

            <!-- ?? CONFLICT SUMMARY ?? -->"""
html = html.replace(old_close_unsched, new_close_unsched)


# 4. Add id="tab_conflicts" wrapper
old_conflicts = """            <!-- ?? CONFLICT SUMMARY ?? -->
            {% if conflict_ids|length > 0 %}"""
new_conflicts = """            <!-- ?? CONFLICT SUMMARY ?? -->
            <div id="tab_conflicts" class="hidden mb-8 no-print">
            {% if conflict_ids|length > 0 %}"""
html = html.replace(old_conflicts, new_conflicts)

old_close_conflicts = """            {% endif %}

        </div>
    </div>

    <!-- EDIT SCHEDULE MODAL -->"""
new_close_conflicts = """            {% else %}
                <div class="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-500"><i class="fa-solid fa-check-circle text-4xl text-green-500 mb-3 block"></i>There are no conflicts in the schedule!</div>
            {% endif %}
            </div> <!-- End tab_conflicts -->

        </div>
    </div>

    <!-- EDIT SCHEDULE MODAL -->"""
html = html.replace(old_close_conflicts, new_close_conflicts)

js_code = """
        /* ? Tab Switching Logic */
        function switchTab(tabId) {
            // Hide all tabs
            document.getElementById('tab_scheduled').classList.replace('block', 'hidden');
            document.getElementById('tab_unscheduled').classList.replace('block', 'hidden');
            document.getElementById('tab_conflicts').classList.replace('block', 'hidden');
            
            // Show selected tab
            document.getElementById('tab_' + tabId).classList.replace('hidden', 'block');
            
            // Reset all cards styling
            const cards = ['card_scheduled', 'card_unscheduled', 'card_conflicts'];
            cards.forEach(id => {
                const el = document.getElementById(id);
                el.classList.remove('border-[#668054]');
                el.classList.add('border-transparent');
                const strip = el.querySelector('.bg-\\[\\#668054\\]');
                if (strip) strip.remove();
                const title = el.querySelector('p.text-xs');
                title.classList.remove('text-[#668054]', 'font-bold');
                title.classList.add('text-gray-500', 'font-medium');
            });
            
            // Highlight selected card
            const activeEl = document.getElementById('card_' + tabId);
            activeEl.classList.remove('border-transparent');
            activeEl.classList.add('border-[#668054]');
            
            const indicator = document.createElement('div');
            indicator.className = 'absolute top-0 right-0 w-2 h-full bg-[#668054]';
            activeEl.appendChild(indicator);
            
            const activeTitle = activeEl.querySelector('p.text-xs');
            activeTitle.classList.remove('text-gray-500', 'font-medium');
            activeTitle.classList.add('text-[#668054]', 'font-bold');
        }
"""
if "function switchTab" not in html:
    html = html.replace("</script>\n</body>", js_code + "\n</script>\n</body>")

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Redid tabs UI")
