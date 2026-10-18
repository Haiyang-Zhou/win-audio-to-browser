"""Separate versioned resources from local runtime state."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = PROJECT_ROOT / 'web'
ASSETS_DIR = PROJECT_ROOT / 'assets'
DATA_DIR = Path(os.environ.get('AUDIO_LINK_DATA_DIR', str(PROJECT_ROOT / 'data'))).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)
TEST_OUTPUT_DIR = DATA_DIR / 'test-output'
TEST_OUTPUT_DIR.mkdir(exist_ok=True)
