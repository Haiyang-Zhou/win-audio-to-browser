"""Atomic, process-safe shared language and transport preferences."""
import json
import os
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path
from ui_languages import LANGUAGES
from paths import DATA_DIR

DEFAULT_PATH = DATA_DIR / 'ui-preferences.json'
QUALITIES = ('auto', 'pcm', 'opus')
_lock = threading.Lock()


def read_preferences(path=None):
    try:
        data = json.loads(Path(path or DEFAULT_PATH).read_text(encoding='utf-8'))
        return {'language': data.get('language') if data.get('language') in LANGUAGES else 'zh-CN',
                'quality': data.get('quality') if data.get('quality') in QUALITIES else 'auto',
                'revision': max(0, int(data.get('revision', 0)))}
    except (OSError, ValueError, TypeError, AttributeError):
        return {'language': 'zh-CN', 'quality': 'auto', 'revision': 0}


@contextmanager
def _exclusive(destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with _lock, destination.with_suffix('.lock').open('a+b') as handle:
        if os.name == 'nt':
            import msvcrt
            if handle.seek(0, os.SEEK_END) == 0:
                handle.write(b'0')
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == 'nt':
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def _save(key, value, path):
    destination = Path(path or DEFAULT_PATH)
    with _exclusive(destination):
        data = read_preferences(destination)
        data.update({key: value, 'revision': data['revision'] + 1})
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent,
                                             prefix='prefs-', suffix='.tmp', delete=False) as handle:
                temporary = Path(handle.name)
                json.dump(data, handle)
            temporary.replace(destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return data


def read_language(path=None):
    return read_preferences(path)['language']


def save_language(language, path=None):
    if language not in LANGUAGES:
        raise ValueError('Unsupported language')
    return _save('language', language, path)


def save_quality(quality, path=None):
    if quality not in QUALITIES:
        raise ValueError('Unsupported transport')
    return _save('quality', quality, path)
