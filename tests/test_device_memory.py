"""Check inline editing, per-device persistence and reconnects in an isolated store."""
from pathlib import Path
import tempfile
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from device_names import DeviceNames, valid_id
from floating_control import AudioPanel, Bridge
from paths import TEST_OUTPUT_DIR

app = QApplication([])
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'names.json'
    store = DeviceNames(path)
    first, second = 'a' * 32, 'b' * 32
    assert not valid_id('../not-a-device')
    assert not store.remember('invalid', 'iPad')
    assert not path.exists()
    panel = AudioPanel(bridge=Bridge(names=store), testing=True)
    first_client = {'id': first, 'kind': 'iPad', 'name': ''}
    panel.state = {'running': True, 'healthy': True, 'url': 'https://test.invalid', 'clients': [first_client]}
    panel.render_state()
    panel.show()
    app.processEvents()
    assert not hasattr(panel.title_label, 'clicked')
    assert panel.title_label.cursor().shape() != Qt.CursorShape.IBeamCursor
    panel.edit_button.click()
    assert panel.name_stack.currentWidget() is panel.name_editor
    panel.name_editor.setText('我的 iPad Pro')
    panel.name_editor.returnPressed.emit()
    app.processEvents()
    assert panel.name_stack.currentWidget() is panel.title_label
    assert panel.windowTitle() == '我的 iPad Pro'
    assert DeviceNames(path).remember(first, 'iPad') == '我的 iPad Pro'
    assert DeviceNames(path).remember(second, 'iPad') == ''
    panel.edit_custom_name()
    panel.name_editor.setText('不应保存')
    panel.name_editor.cancelled.emit()
    app.processEvents()
    assert DeviceNames(path).remember(first, 'iPad') == '我的 iPad Pro'
    panel.state['clients'] = []
    panel.render_state()
    assert panel.windowTitle() == 'Audio Link', (panel.windowTitle(), panel.name_mode, panel.custom_name)
    panel.state['clients'] = [{'id': first, 'kind': 'iPad', 'name': DeviceNames(path).remember(first, 'iPad')}]
    panel.render_state()
    assert panel.windowTitle() == '我的 iPad Pro', 'Reconnect must restore the stored alias'
    panel.edit_custom_name()
    panel.name_editor.setText('旧设备的新名字')
    panel.state['clients'] = [{'id': second, 'kind': 'iPad', 'name': ''}]
    panel.commit_inline_name()
    assert store.remember(first, 'iPad') == '旧设备的新名字'
    assert store.remember(second, 'iPad') == '', 'Editing must not rename a newly connected device'
    panel.state['clients'] = []
    panel.render_state()
    panel.edit_custom_name()
    panel.name_editor.setText('桌面音响')
    panel.commit_inline_name()
    assert panel.windowTitle() == '桌面音响'
    assert store.remember(second, 'iPad') == ''
    panel.use_automatic_name()
    panel.state['clients'] = [{'id': first, 'kind': 'iPad', 'name': store.remember(first, 'iPad')}]
    panel.render_state()
    panel.apply_scale(85)
    app.processEvents()
    panel.grab().save(str(TEST_OUTPUT_DIR / 'floating-device-name-preview.png'))
    panel.edit_custom_name()
    app.processEvents()
    panel.grab().save(str(TEST_OUTPUT_DIR / 'floating-name-edit-preview.png'))
print('PASS: inline save, Esc cancel, persistent storage reload, reconnect, separate devices, edit target, offline title')
