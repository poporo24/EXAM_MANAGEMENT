import os
import zipfile

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        # Exclude unnecessary folders
        if '__pycache__' in root or '.git' in root or '.vscode' in root:
            continue
        for file in files:
            if file.endswith('.zip') or file.endswith('.pyc'):
                continue
            filepath = os.path.join(root, file)
            arcname = os.path.relpath(filepath, path)
            ziph.write(filepath, arcname)

with zipfile.ZipFile('deploy.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir('.', zipf)

print("Created deploy.zip")
