import glob
import re

for filepath in glob.glob('template/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the toggle logic back to single classes
    content = content.replace("classList.toggle('md:w-64 w-16')", "classList.toggle('md:w-64')\n          sidebar.classList.toggle('w-0')")
    content = content.replace("classList.toggle('md:ml-64 ml-0')", "classList.toggle('md:ml-64')")
    content = content.replace("classList.toggle('md:ml-16 ml-0')", "classList.toggle('md:ml-16')")
    
    # Also fix the init logic
    content = content.replace("sidebar.classList.add('md:w-64 w-16')", "sidebar.classList.add('w-16'); sidebar.classList.remove('md:w-64')")
    content = content.replace("mainContent.classList.remove('md:ml-64 ml-0')", "mainContent.classList.remove('md:ml-64')")
    content = content.replace("mainContent.classList.add('md:ml-16 ml-0')", "mainContent.classList.add('md:ml-16')")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed JS toggle logic")
