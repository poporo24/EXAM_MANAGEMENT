import glob

for filepath in glob.glob('template/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find where I injected the CSS block before, and add a JS block to automatically wrap all tables.
    js_fix = '''
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            // Automatically wrap all tables to make them horizontally scrollable on small screens
            document.querySelectorAll("table").forEach(function(table) {
                if (!table.parentElement.classList.contains("overflow-x-auto")) {
                    const wrapper = document.createElement("div");
                    wrapper.className = "overflow-x-auto w-full";
                    table.parentNode.insertBefore(wrapper, table);
                    wrapper.appendChild(table);
                }
            });
        });
    </script>
</head>'''
    
    if 'document.querySelectorAll("table").forEach' not in content:
        content = content.replace('</head>', js_fix)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Injected global table wrapper script!")
