"""Language and quality updates from separate processes preserve each other."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from ui_preferences import read_preferences, save_language, save_quality

with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'shared.json'
    assert read_preferences(path)['quality'] == 'auto'
    save_language('fr', path)
    save_quality('pcm', path)
    assert read_preferences(path) == {'language': 'fr', 'quality': 'pcm', 'revision': 2}
    workers = []
    for function, value in (('save_language', 'ru'), ('save_quality', 'opus')):
        code = f"from ui_preferences import {function}; import sys; [{function}('{value}', sys.argv[1]) for _ in range(20)]"
        workers.append(subprocess.Popen([sys.executable, '-c', code, str(path)], env=os.environ.copy()))
    for process in workers:
        assert process.wait(timeout=20) == 0
    assert read_preferences(path) == {'language': 'ru', 'quality': 'opus', 'revision': 42}
print('PASS: automatic default, persistent bidirectional preferences, process-safe concurrent language/quality updates')
