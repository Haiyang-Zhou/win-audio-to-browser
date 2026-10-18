"""Segmented appearance, localization, exclusivity, keyboard and compact scales."""
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication
from quality_control import QualityControl
from web_languages import WEB_MESSAGES

app = QApplication([])
control = QualityControl()
for quality in ('auto', 'pcm', 'opus'):
    control.addItem(quality, quality)
control.show()
changes = []
control.currentIndexChanged.connect(changes.append)
for language, labels in WEB_MESSAGES.items():
    for index, quality in enumerate(('auto', 'pcm', 'opus')):
        control.setItemText(index, labels['quality_' + quality], labels['quality_short_' + quality])
        assert control.buttons[index].toolTip() == labels['quality_' + quality]
    for factor in (.75, .85, 1, 1.15, 1.3):
        control.setFixedWidth(round(174 * factor))
        control.setScale(factor)
        app.processEvents()
        for index in range(3):
            control.buttons[index].click()
            assert control.currentIndex() == index
            assert sum(button.isChecked() for button in control.buttons) == 1
            assert control.buttons[index].fontMetrics().horizontalAdvance(control.buttons[index].text()) <= control.buttons[index].width()
        control.setCurrentIndex(0)
        QApplication.sendEvent(control, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Right, Qt.KeyboardModifier.NoModifier))
        assert control.currentData() == 'pcm'
        QApplication.sendEvent(control, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Home, Qt.KeyboardModifier.NoModifier))
        assert control.currentData() == 'auto'
assert changes
control.close()
print('PASS: 9-language segmented control, 5 scales, no text overflow, exclusive selection and keyboard navigation')
