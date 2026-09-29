import os
import glob
import re

html_files = glob.glob('template/*.html')
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Wrap tables in overflow-x-auto if not already wrapped
    # We look for <table ...> and check if it's inside a div.
    # A simple regex replacement:
    # First, undo any previous wrapping if we ran this before (idempotency)
    # Actually, simpler: replace <table with <div class="overflow-x-auto max-w-full block"><table
    # and </table> with </table></div>
    # But only if not already there.
    
    if '<table' in content and 'overflow-x-auto' not in content:
        content = re.sub(r'(<table[^>]*>)', r'<div class="overflow-x-auto w-full">\1', content)
        content = content.replace('</table>', '</table></div>')
        
    # 2. Ensure main content doesn't force a strict ml-64 on mobile that breaks the screen
    # Change ml-64 to max-md:ml-16 md:ml-64 (Tailwind v3 arbitrary variants, or just use standard classes)
    # Actually, if we just let the body be overflow-x-hidden and main be overflow-x-auto, it works.
    content = content.replace('ml-64', 'md:ml-64 ml-0')
    content = content.replace('w-64', 'md:w-64 w-16')
    content = content.replace('ml-16', 'md:ml-16 ml-0')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Applied responsive scroll fixes to all pages")
