"""Translation coverage, live switching, editor button and scaled layout checks."""
from pathlib import Path
from string import Formatter
import tempfile
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from floating_control import AudioPanel, ROOT
from paths import TEST_OUTPUT_DIR
from ui_languages import LANGUAGES, MESSAGES, translate

fields = lambda text: {field for _, field, _, _ in Formatter().parse(text) if field}
for code in LANGUAGES:
    assert MESSAGES[code].keys() == MESSAGES['zh-CN'].keys()
    for key, text in MESSAGES[code].items():
        assert text.strip() and fields(text) == fields(MESSAGES['zh-CN'][key]), (code, key)

app = QApplication([])
panel = AudioPanel(testing=True)
panel.state = {'running': True, 'healthy': True, 'url': 'https://your-pc.local:8787', 'clients': [{'kind': 'iPad', 'name': '我的 iPad Pro'}]}
panel.show()
for code in LANGUAGES:
    panel.set_language(code)
    assert panel.power.text() == translate(code, 'stop')
    assert panel.copy.text() == translate(code, 'copy')
    assert panel.language_menu.title() == translate(code, 'language')
    assert panel.windowTitle() == '我的 iPad Pro', 'Language change must preserve user names'
    assert sum(action.isChecked() for action in panel.language_group.actions()) == 1
    for scale in (75, 85, 100, 130):
        panel.apply_scale(scale)
        app.processEvents()
        assert panel.name_stack.geometry().right() < panel.edit_button.geometry().left()
        assert panel.edit_button.geometry().right() < panel.edit_button.parentWidget().width()
        assert panel.width() == round(344 * scale / 100)
        assert panel.power.geometry().right() < panel.power.parentWidget().width()
        if scale == 85:
            panel.grab().save(str(TEST_OUTPUT_DIR / f'floating-lang-{code}.png'))
    panel.edit_button.click()
    assert panel.name_stack.currentWidget() is panel.name_editor
    assert panel.name_editor.text() == '我的 iPad Pro'
    panel.cancel_inline_name()
    panel.state['running'] = panel.state['healthy'] = False
    panel.render_state()
    assert panel.power.text() == translate(code, 'start')
    panel.state['running'] = panel.state['healthy'] = True

with tempfile.TemporaryDirectory() as folder:
    panel.settings = QSettings(str(Path(folder) / 'preferences.ini'), QSettings.Format.IniFormat)
    panel.preferences_path = Path(folder) / 'ui-preferences.json'
    panel.testing = False
    panel.set_language('fr')
    panel.settings.sync()
    restored = QSettings(str(Path(folder) / 'preferences.ini'), QSettings.Format.IniFormat)
    assert restored.value('language') == 'fr'
    panel.testing = True
print(f'PASS: {len(LANGUAGES)} complete translations, matching placeholders, live switching, saved preference, pencil editing, 4 scales, aliases unchanged')
