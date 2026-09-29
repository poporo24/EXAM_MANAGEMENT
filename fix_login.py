import os

filepath = 'app.py'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We need to find the stray decorators and move them above def login():
# The stray decorators are around line 180-184
new_lines = []
stray_decorators = []
inside_stray = False

for i, line in enumerate(lines):
    if line.startswith("@app.route(\"/login\"") or line.startswith("@app.route(\"/\", methods=[\"GET\", \"POST\"]"):
        stray_decorators.append(line)
        continue
    
    if line.startswith("def login():"):
        for d in stray_decorators:
            new_lines.append(d)
        new_lines.append(line)
        continue
        
    new_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
