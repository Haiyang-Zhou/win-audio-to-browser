"""Window behavior checks without touching the running audio service."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from floating_control import AudioPanel

app = QApplication([])
panel = AudioPanel(testing=True)
panel.show()
for scale in (75, 85, 100, 115, 130):
    panel.apply_scale(scale)
    app.processEvents()
    assert panel.width() == round(344 * scale / 100)
    assert panel.screen().availableGeometry().contains(panel.geometry())
panel.set_docked(False)
assert not panel.dock_action.isChecked()
panel.set_docked(True)
assert panel.windowFlags() & Qt.WindowType.WindowMinimizeButtonHint
assert (panel.windowFlags() & Qt.WindowType.WindowType_Mask) == Qt.WindowType.Window
panel.minimize_button.click()
app.processEvents()
assert panel.isMinimized()
panel.reveal()
app.processEvents()
assert not panel.isMinimized() and panel.isVisible()
print('PASS: five scales, docking, taskbar minimization and restoration')
