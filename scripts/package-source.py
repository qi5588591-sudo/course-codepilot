"""Creates a credential-free source archive with a manifest, excluding local state."""
import hashlib
import json
import os
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[1]
include=['backend','extension','sandbox','evaluation','tests','scripts','docs','examples','.github']
skip={'node_modules','__pycache__','.pytest_cache','.vscode-test','out'}
files=[]
for name in include:
    for directory, folders, names in os.walk(root/name):
        folders[:] = [folder for folder in folders if folder not in skip]
        files.extend(Path(directory)/name for name in names)
for name in ['README.md','AGENTS.md','pyproject.toml','requirements.lock.txt','.env.example','.gitignore','.gitattributes','LICENSE','THIRD_PARTY_NOTICES.md']:
    if (root/name).exists():files.append(root/name)
for file in (root/'artifacts').glob('*'):
    if file.suffix in ['.vsix','.xml','.json','.jsonl','.md','.csv'] and 'evaluation-real' not in file.name: files.append(file)
for file in (root/'deliverables').glob('*'):
    if file.suffix in ['.docx','.pptx','.mp4']: files.append(file)
target=root/'artifacts/codepilot-source.zip'
manifest=[]
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(set(files)):
        relative=file.relative_to(root).as_posix()
        if file.name=='.env' or file.suffix in ['.sqlite3','.key','.pem']:raise RuntimeError('Unexpected private file')
        archive.write(file,'codepilot/'+relative)
        manifest.append({'path':relative,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    archive.writestr('codepilot/MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
print(target)
