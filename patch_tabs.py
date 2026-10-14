with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update the stat cards to act as tabs
old_cards = """            <!-- Stat Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6 no-print">
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

new_cards = """            <!-- Stat Cards / Tabs -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6 no-print">
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

html = html.replace(old_cards, new_cards)

# Wrap Unscheduled
old_unscheduled = """            <!-- ?? UNSCHEDULED EXAMS -->
            {% if unscheduled %}
            <div class="mb-8 no-print">"""
new_unscheduled = """            <!-- ?? UNSCHEDULED EXAMS -->
            <div id="tab_unscheduled" class="hidden mb-8 no-print">
            {% if unscheduled %}"""
html = html.replace(old_unscheduled, new_unscheduled)

old_unscheduled_end = """            </div>
            {% endif %}

            <!-- ?? CONFLICT SUMMARY -->"""
new_unscheduled_end = """            {% else %}
                <div class="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-500"><i class="fa-solid fa-check-circle text-4xl text-green-500 mb-3 block"></i>There are no unscheduled exams!</div>
            {% endif %}
            </div>

            <!-- ?? CONFLICT SUMMARY -->"""
html = html.replace(old_unscheduled_end, new_unscheduled_end)

# Wrap Conflicts
old_conflicts = """            <!-- ?? CONFLICT SUMMARY -->
            {% if conflict_ids|length > 0 %}
            <div id="conflictSummary" class="mb-8 no-print">"""
new_conflicts = """            <!-- ?? CONFLICT SUMMARY -->
            <div id="tab_conflicts" class="hidden mb-8 no-print">
            {% if conflict_ids|length > 0 %}
            <div id="conflictSummary" class="">"""
html = html.replace(old_conflicts, new_conflicts)

old_conflicts_end = """            </div>
            {% endif %}

            <!-- ?? TIMETABLE DATA -->"""
new_conflicts_end = """            </div>
            {% else %}
                <div class="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-500"><i class="fa-solid fa-check-circle text-4xl text-green-500 mb-3 block"></i>There are no conflicts in the schedule!</div>
            {% endif %}
            </div>

            <!-- ?? TIMETABLE DATA -->"""
html = html.replace(old_conflicts_end, new_conflicts_end)

# Wrap Scheduled
old_scheduled = """            <!-- ?? TIMETABLE DATA -->
            {% if sched_count > 0 %}"""
new_scheduled = """            <!-- ?? TIMETABLE DATA -->
            <div id="tab_scheduled" class="block">
            {% if sched_count > 0 %}"""
html = html.replace(old_scheduled, new_scheduled)

old_scheduled_end = """            </div>
            {% else %}
            <div class="bg-white rounded-xl border border-gray-200 p-12 text-center">"""
new_scheduled_end = """            </div>
            {% else %}
            <div class="bg-white rounded-xl border border-gray-200 p-12 text-center">"""
# Wait, let's just close the div safely before <!-- EDIT SCHEDULE MODAL -->
old_modal = """    <!-- EDIT SCHEDULE MODAL -->"""
new_modal = """            </div>\n    <!-- EDIT SCHEDULE MODAL -->"""
html = html.replace(old_modal, new_modal)

# Add Tab JS logic
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
                // Remove the green indicator strip if it exists
                const strip = el.querySelector('.bg-\\[\\#668054\\]');
                if (strip) strip.remove();
                
                // Reset text colors
                const title = el.querySelector('p.text-xs');
                title.classList.remove('text-[#668054]', 'font-bold');
                title.classList.add('text-gray-500', 'font-medium');
            });
            
            // Highlight selected card
            const activeEl = document.getElementById('card_' + tabId);
            activeEl.classList.remove('border-transparent');
            activeEl.classList.add('border-[#668054]');
            
            // Add green indicator strip
            const indicator = document.createElement('div');
            indicator.className = 'absolute top-0 right-0 w-2 h-full bg-[#668054]';
            activeEl.appendChild(indicator);
            
            // Highlight text
            const activeTitle = activeEl.querySelector('p.text-xs');
            activeTitle.classList.remove('text-gray-500', 'font-medium');
            activeTitle.classList.add('text-[#668054]', 'font-bold');
        }
        
        // Auto-switch to conflicts if there are conflicts on load? No, let user click.
"""

if "function switchTab" not in html:
    html = html.replace("</script>\n</body>", js_code + "\n</script>\n</body>")

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched Tabs UI")
