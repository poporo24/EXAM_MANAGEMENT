import re
with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Wrap tables in tab divs
if '<div id="tab_scheduled">' not in html:
    html = html.replace('<!-- Scheduled Exams List -->', '<div id="tab_scheduled">\n            <!-- Scheduled Exams List -->')
    html = html.replace('<!-- Unscheduled Exams Table -->', '</div>\n\n            <!-- Unscheduled Exams Table -->\n            <div id="tab_unscheduled" class="hidden">')
    html = html.replace('<!-- Conflict Exams Table -->', '</div>\n\n            <!-- Conflict Exams Table -->\n            <div id="tab_conflicts" class="hidden">')
    # Close the last tab div before the Modals section
    html = html.replace('<!-- ????????????????????????????????? MODALS ????????????????????????????????? -->', '</div>\n\n            <!-- ????????????????????????????????? MODALS ????????????????????????????????? -->')

# 2. Inject Javascript
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
print("Tabs fully restored!")
