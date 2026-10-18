"""Desktop publishes the selected language locally; browsers can only read it."""
import json
from pathlib import Path
from ui_languages import LANGUAGES
from paths import DATA_DIR

DEFAULT_PATH = DATA_DIR / 'ui-preferences.json'


def read_language(path=None):
    try:
        data = json.loads(Path(path or DEFAULT_PATH).read_text(encoding='utf-8'))
        value = data.get('language')
        return value if value in LANGUAGES else 'zh-CN'
    except (OSError, ValueError, AttributeError):
        return 'zh-CN'


def save_language(language, path=None):
    if language not in LANGUAGES:
        raise ValueError('Unsupported language')
    destination = Path(path or DEFAULT_PATH)
    temporary = destination.with_suffix('.json.tmp')
    temporary.write_text(json.dumps({'language': language}), encoding='utf-8')
    temporary.replace(destination)
