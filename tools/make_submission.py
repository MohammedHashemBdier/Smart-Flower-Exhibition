"""Create a ZIP submission package including source, tests, README and deliverables.
Usage: python tools/make_submission.py
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'submission.zip'

include_patterns = [
    '*.py',
    'README.md',
    'deliverables.md',
    'deliverables.pdf',
    'smart_flower_exhibition-output.md',
    'smart_flower_exhibition-output.txt',
]

# collect files
files = []
for pattern in include_patterns:
    files.extend(ROOT.glob(pattern))

# include tests and tools
files.extend(ROOT.glob('tests/**'))
files.extend((ROOT / 'tools').glob('**/*'))

# Remove duplicates and directories
files = [p for p in dict.fromkeys(files) if p.is_file()]

if not files:
    print('No files found to include in submission.zip')
else:
    tmp_dir = ROOT / '__submission_tmp__'
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir()
    for p in files:
        rel = p.relative_to(ROOT)
        dest = tmp_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)

    shutil.make_archive(str(OUT.with_suffix('')), 'zip', root_dir=tmp_dir)
    shutil.rmtree(tmp_dir)
    print('Created', OUT)
