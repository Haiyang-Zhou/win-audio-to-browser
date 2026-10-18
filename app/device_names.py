"""Local device aliases keyed by a browser-generated random ID, never by IP."""
import json
from pathlib import Path
import re
import threading
from paths import DATA_DIR

_LOCK = threading.RLock()


def valid_id(value):
    return value if isinstance(value, str) and re.fullmatch(r'[a-f0-9]{32}', value) else ''


class DeviceNames:
    def __init__(self, path=None):
        self.path = Path(path) if path else DATA_DIR / 'device-names.json'

    def read(self):
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('设备名称记录格式不正确，请检查 device-names.json')
        if any(not valid_id(key) or not isinstance(item, dict) or not isinstance(item.get('name', ''), str) for key, item in data.items()):
            raise ValueError('设备名称记录存在无效条目，请检查 device-names.json')
        return data

    def remember(self, identifier, kind, name=None):
        identifier = valid_id(identifier)
        if not identifier:
            return ''
        with _LOCK:
            data = self.read()
            previous = data.get(identifier, {})
            item = {'kind': kind, 'name': previous.get('name', '')}
            if name is not None:
                item['name'] = ' '.join(name.split())[:24]
            if previous != item:
                data[identifier] = item
                temporary = self.path.with_suffix('.json.tmp')
                temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                temporary.replace(self.path)
            return item['name']
