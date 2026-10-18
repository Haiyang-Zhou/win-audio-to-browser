"""Create a source-only archive using an allowlist, never local runtime files."""
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
ROOT_FILES = {'README.md', 'README.en.md', 'LICENSE', 'requirements.txt', '.gitignore', '.gitattributes', 'setup.cmd', 'start.cmd', 'CHANGELOG.md', 'CONTRIBUTING.md', 'SECURITY.md', 'THIRD_PARTY_NOTICES.md'}
DIRECTORIES = {'app', 'web', 'assets', 'docs', 'scripts', 'tests', '.github'}
SUFFIXES = {'.py', '.html', '.css', '.js', '.png', '.ico', '.md', '.ps1', '.yml', '.txt'}


def source_files():
    for path in sorted(ROOT.rglob('*')):
        relative = path.relative_to(ROOT)
        if not path.is_file() or '__pycache__' in relative.parts:
            continue
        if len(relative.parts) == 1 and relative.name in ROOT_FILES:
            yield path
        elif relative.parts[0] in DIRECTORIES and path.suffix in SUFFIXES:
            yield path


if __name__ == '__main__':
    destination = ROOT / 'dist'
    destination.mkdir(exist_ok=True)
    archive = destination / 'audio-link-source.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as output:
        for path in source_files():
            info = zipfile.ZipInfo('audio-link/' + path.relative_to(ROOT).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            output.writestr(info, path.read_bytes())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (destination / 'SHA256SUMS.txt').write_text(f'{digest}  {archive.name}\n', encoding='ascii')
    print(f'{archive}\nSHA256 {digest}')
