with open("template/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Inject Select2 CSS and JS in the head
head_injection = """
    <!-- Select2 for searchable dropdowns -->
    <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
    <style>
        /* Make Select2 match Tailwind inputs */
        .select2-container .select2-selection--single {
            height: 38px !important;
            border: 1px solid #d1d5db !important;
            border-radius: 0.5rem !important;
            display: flex;
            align-items: center;
        }
        .select2-container--default .select2-selection--single .select2-selection__arrow {
            height: 36px !important;
        }
        .select2-container--default.select2-container--focus .select2-selection--single {
            border-color: #668054 !important;
            box-shadow: 0 0 0 2px rgba(102, 128, 84, 0.2) !important;
        }
        .select2-dropdown {
            border: 1px solid #d1d5db !important;
            border-radius: 0.5rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        }
        .select2-container--default .select2-results__option--highlighted[aria-selected] {
            background-color: #668054 !important;
        }
    </style>
"""
if "select2.min.css" not in html:
    html = html.replace('</title>', '</title>' + head_injection)

# 2. Add class 'searchable-select' to both section dropdowns
html = html.replace('name="section" required class="border border-gray-300', 'name="section" required class="searchable-select border border-gray-300')
html = html.replace('class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none shadow-sm" title="Filter by Section"', 'class="searchable-select border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#668054] focus:border-[#668054] outline-none shadow-sm" title="Filter by Section" style="width: 150px;"')

# 3. Initialize Select2
js_init = """
    <script>
        $(document).ready(function() {
            $('.searchable-select').select2({
                placeholder: "Search section...",
                allowClear: false
            });
            
            // Fix onchange for the filter dropdown
            $('select[title="Filter by Section"]').on('change', function() {
                window.location.href = '/schedule?section=' + encodeURIComponent($(this).val());
            });
        });
    </script>
</body>"""

if "$('.searchable-select').select2" not in html:
    html = html.replace('</body>', js_init)
    
# Wait, the native onchange won't work on Select2 if it relies on 'this.value' inline sometimes?
# Let's remove the inline onchange from the filter select to let jQuery handle it
import re
html = re.sub(r'onchange="window\.location\.href=\'/schedule\?section=\' \+ encodeURIComponent\(this\.value\)"', '', html)

with open("template/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Injected Select2!")
