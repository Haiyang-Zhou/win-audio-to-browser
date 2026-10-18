"""Run each Qt/async test in its own process; audio hardware tests are opt-in."""
import argparse
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--audio-hardware', action='store_true', help='Also open WASAPI devices and real local WebRTC sessions')
args = parser.parse_args()
tests = ['test_naming.py', 'test_device_memory.py', 'test_languages.py', 'test_web_ui.py', 'test_pcm.py', 'test_preferences.py', 'test_audio_modes.py', 'test_quality_control.py', 'test_window.py', 'test_repository.py']
if args.audio_hardware:
    tests += ['test_floating.py', 'test_device_connection.py']
with tempfile.TemporaryDirectory(prefix='audio-link-tests-') as folder:
    env = dict(os.environ, PYTHONPATH=str(ROOT / 'app'), PYTHONIOENCODING='utf-8', AUDIO_LINK_DATA_DIR=folder)
    for test in tests:
        result = subprocess.run([sys.executable, str(ROOT / 'tests' / test)], env=env, cwd=ROOT)
        if result.returncode:
            raise SystemExit(result.returncode)
node = shutil.which('node')
if node:
    for script in ('test_worklet.js', 'test_receiver.js'):
        subprocess.run([node, str(ROOT / 'tests' / script)], check=True)
else:
    print('SKIP: JavaScript unit tests require Node.js (not an audio runtime dependency)')
print(f'PASS: {len(tests)} Python test programs')
