"""Reject accidental local files and machine-specific paths in release inputs."""
from pathlib import Path
import importlib.util
import re

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('source_packaging', ROOT / 'scripts' / 'package_source.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
files = list(module.source_files())
assert len(files) > 20
for path in files:
    relative = path.relative_to(ROOT)
    assert not {'.git', '.venv', 'data', '__pycache__', 'dist'}.intersection(relative.parts)
    assert path.suffix not in {'.pem', '.key', '.log', '.pid', '.json'}
    if path.suffix in {'.py', '.md', '.ps1', '.cmd', '.html', '.js', '.css'}:
        text = path.read_text(encoding='utf-8')
        assert not re.search(r'[C-F]:[\\/](?:Users|software|Codex)[\\/]', text), str(relative)
        assert '.'.join(('192', '168', '1', '192')) not in text, str(relative)
from ui_languages import MESSAGES
assert MESSAGES['zh-CN']['connected'] == '已连接 · {device}'
for path in files:
    if path.suffix == '.md':
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if target.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            destination = target.split('#', 1)[0]
            assert (path.parent / destination).exists(), (path.name, target)
print(f'PASS: {len(files)} allowlisted source files; no runtime secrets or machine paths')
