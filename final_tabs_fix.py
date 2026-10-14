import re

with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Replace the Stats Strip
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

            <!-- ------ TIMETABLE GRID ------ -->"""

html = re.sub(r'<!-- Stats strip -->.*?<!-- ------ TIMETABLE GRID ------ -->', new_cards, html, flags=re.DOTALL)

# 2. Add tab wrappers around the sections
html = html.replace('<!-- ------ TIMETABLE GRID ------ -->\n            {% if dates and times %}', '<!-- ------ TIMETABLE GRID ------ -->\n            <div id="tab_scheduled">\n            {% if dates and times %}')

html = html.replace('<!-- ------ CONFLICTS SUMMARY ------ -->', '            </div>\n\n            <!-- ------ CONFLICTS SUMMARY ------ -->\n            <div id="tab_conflicts" class="hidden">')

html = html.replace('<!-- ------ UNSCHEDULED LIST ------ -->', '            </div>\n\n            <!-- ------ UNSCHEDULED LIST ------ -->\n            <div id="tab_unscheduled" class="hidden">')

html = html.replace('<!-- --------------------------------- MODALS --------------------------------- -->', '            </div>\n\n            <!-- --------------------------------- MODALS --------------------------------- -->')

# 3. Inject JS
js_code = """
        /* ? Tabs Logic */
        function switchTab(tabName) {
            // Hide all tabs
            document.getElementById('tab_scheduled').classList.add('hidden');
            document.getElementById('tab_unscheduled').classList.add('hidden');
            document.getElementById('tab_conflicts').classList.add('hidden');
            
            // Reset card styling
            ['scheduled', 'unscheduled', 'conflicts'].forEach(name => {
                const card = document.getElementById('card_' + name);
                card.classList.remove('border-[#668054]');
                card.classList.add('border-transparent');
                
                // Remove the green bar indicator if it exists
                const indicator = card.querySelector('.bg-\\[\\#668054\\]');
                if (indicator) indicator.remove();
                
                // Reset text colors
                const title = card.querySelector('p.uppercase');
                title.classList.remove('text-[#668054]');
                title.classList.add('text-gray-500');
            });
            
            // Show target tab
            document.getElementById('tab_' + tabName).classList.remove('hidden');
            
            // Highlight target card
            const activeCard = document.getElementById('card_' + tabName);
            activeCard.classList.remove('border-transparent');
            activeCard.classList.add('border-[#668054]');
            
            // Add green bar indicator
            const indicator = document.createElement('div');
            indicator.className = 'absolute top-0 right-0 w-2 h-full bg-[#668054]';
            activeCard.appendChild(indicator);
            
            // Highlight text
            const title = activeCard.querySelector('p.uppercase');
            title.classList.remove('text-gray-500');
            title.classList.add('text-[#668054]');
        }
"""

if 'function switchTab' not in html:
    html = html.replace('</script>\n</body>', js_code + '\n</script>\n</body>')

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Tabs UI fully rebuilt!")
