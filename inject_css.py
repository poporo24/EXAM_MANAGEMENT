import glob

# Restore the original state using simple replacements based on known bad patterns
for filepath in glob.glob('template/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Revert my bad replacements
    content = content.replace('md:ml-64 ml-0', 'ml-64')
    content = content.replace('md:w-64 w-16', 'w-64')
    content = content.replace('md:ml-16 ml-0', 'ml-16')
    content = content.replace("classList.toggle('md:w-64')\n          sidebar.classList.toggle('w-0')", "classList.toggle('w-64')")
    content = content.replace("classList.toggle('md:ml-64')", "classList.toggle('ml-64')")
    content = content.replace("classList.toggle('md:ml-16')", "classList.toggle('ml-16')")
    content = content.replace("sidebar.classList.add('w-16'); sidebar.classList.remove('md:w-64')", "sidebar.classList.add('w-16'); sidebar.classList.remove('w-64')")
    content = content.replace("mainContent.classList.remove('md:ml-64')", "mainContent.classList.remove('ml-64')")
    content = content.replace("mainContent.classList.add('md:ml-16')", "mainContent.classList.add('ml-16')")

    # Now add the robust CSS media query for tables and mobile layout!
    # We will inject it right before </head>
    css = '''
    <style>
        /* Mobile Responsive Overrides */
        @media (max-width: 768px) {
            #sidebar { width: 4rem !important; z-index: 50; }
            #main-content { margin-left: 4rem !important; width: calc(100% - 4rem) !important; }
            .nav-text { display: none !important; }
            
            /* Make ALL tables horizontally scrollable */
            table { display: block !important; width: 100% !important; overflow-x: auto !important; -webkit-overflow-scrolling: touch; }
            th, td { white-space: nowrap !important; }
            
            /* Make modals scrollable if they overflow */
            .fixed.inset-0 > div { padding: 1rem; overflow-y: auto; max-height: 100vh; }
        }
    </style>
</head>'''
    
    # Prevent double injection
    if '/* Mobile Responsive Overrides */' not in content:
        content = content.replace('</head>', css)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Restored layout classes and injected safe global mobile CSS!")
