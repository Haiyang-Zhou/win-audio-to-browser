"""Extract the source archive elsewhere and run hardware-independent tests."""
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
archive = ROOT / 'dist' / 'audio-link-source.zip'
with tempfile.TemporaryDirectory(prefix='audio-link-release-') as folder:
    temporary = Path(folder).resolve()
    assert temporary.is_relative_to(Path(tempfile.gettempdir()).resolve())
    with zipfile.ZipFile(archive) as source:
        for member in source.infolist():
            assert member.filename.startswith('audio-link/')
            assert '..' not in Path(member.filename).parts
            assert (temporary / member.filename).resolve().is_relative_to(temporary)
            assert not {'.git', '.venv', 'data', '__pycache__'}.intersection(Path(member.filename).parts)
        source.extractall(temporary)
    project = temporary / 'audio-link'
    assert (project / 'assets' / 'screenshots' / 'desktop.png').exists()
    assert (project / 'assets' / 'screenshots' / 'receiver.png').exists()
    subprocess.run([sys.executable, str(project / 'scripts' / 'run_tests.py')], cwd=project, check=True)
print('PASS: source archive is relocatable and its clean-copy tests pass')
