"""Extract the source archive elsewhere and run hardware-independent tests."""
from pathlib import Path
import hashlib
import importlib.util
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('release_packaging', ROOT / 'scripts' / 'package_source.py')
packaging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packaging)
archive = ROOT / 'dist' / packaging.ARCHIVE_NAME
checksum = (ROOT / 'dist' / packaging.CHECKSUM_NAME).read_text(encoding='ascii').strip()
assert checksum == f'{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}'
with tempfile.TemporaryDirectory(prefix='audio-link-release-') as folder:
    temporary = Path(folder).resolve()
    assert temporary.is_relative_to(Path(tempfile.gettempdir()).resolve())
    with zipfile.ZipFile(archive) as source:
        expected = {'audio-link/' + path.relative_to(ROOT).as_posix() for path in packaging.source_files()}
        assert set(source.namelist()) == expected, 'Archive does not match the source allowlist'
        assert source.testzip() is None
        for member in source.infolist():
            assert member.filename.startswith('audio-link/')
            assert '..' not in Path(member.filename).parts
            assert (temporary / member.filename).resolve().is_relative_to(temporary)
            assert not {'.git', '.venv', 'data', '__pycache__'}.intersection(Path(member.filename).parts)
        source.extractall(temporary)
    project = temporary / 'audio-link'
    assert (project / 'VERSION').read_text(encoding='ascii').strip() == packaging.VERSION
    assert (project / 'assets' / 'screenshots' / 'desktop.png').exists()
    assert (project / 'assets' / 'screenshots' / 'receiver.png').exists()
    subprocess.run([sys.executable, str(project / 'scripts' / 'run_tests.py')], cwd=project, check=True)
print(f'PASS: v{packaging.VERSION} checksum, exact source allowlist, archive integrity and clean-copy tests')
