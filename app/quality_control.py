"""Compact segmented transport selector with a softly animated selection pill."""
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QButtonGroup, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QPushButton, QWidget


class QualityControl(QWidget):
    currentIndexChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('qualitySelector')
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._index = 0
        self._values = []
        self.buttons = []
        self._layout = QHBoxLayout(self)
        self._layout.setSpacing(0)
        self._pill = QFrame(self)
        self._pill.setObjectName('qualityPill')
        self._pill.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._shadow = QGraphicsDropShadowEffect(self._pill)
        self._shadow.setColor(QColor(39, 57, 80, 24))
        self._pill.setGraphicsEffect(self._shadow)
        self._animation = QPropertyAnimation(self._pill, b'geometry', self)
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._group.idClicked.connect(self.setCurrentIndex)
        self.setScale(1)

    def addItem(self, text, value):
        index = len(self.buttons)
        button = QPushButton(text, self)
        button.setObjectName('qualityOption')
        button.setCheckable(True)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._group.addButton(button, index)
        self._layout.addWidget(button, 1)
        self.buttons.append(button)
        self._values.append(value)
        self.buttons[self._index].setChecked(True)
        self._pill.lower()

    def setItemText(self, index, text, short=None):
        self.buttons[index].setText(short or text)
        self.buttons[index].setToolTip(text)
        self.buttons[index].setAccessibleName(text)

    def currentData(self):
        return self._values[self._index]

    def currentIndex(self):
        return self._index

    def setCurrentIndex(self, index):
        if not 0 <= index < len(self.buttons):
            return
        changed = self._index != index
        self._index = index
        self.buttons[index].setChecked(True)
        if changed:
            self._position_pill(animate=self.isVisible())
            self.currentIndexChanged.emit(index)

    def setScale(self, factor):
        px = lambda value: max(1, round(value * factor))
        self._inset = px(3)
        self._layout.setContentsMargins(*([self._inset] * 4))
        self.setFixedHeight(px(33))
        self._shadow.setBlurRadius(px(9))
        self._shadow.setOffset(0, px(1))
        self.setStyleSheet(f'''
            QWidget#qualitySelector {{ background: #e9eef5; border: 1px solid #dfe6ef; border-radius: {px(11)}px; }}
            QWidget#qualitySelector:focus {{ border-color: #8bbbf3; }}
            QFrame#qualityPill {{ background: #ffffff; border: 1px solid #ffffff; border-radius: {px(8)}px; }}
            QPushButton#qualityOption {{ background: transparent; border: none; padding: 0; border-radius: {px(7)}px; color: #758397; font-size: {10 * factor:g}px; font-weight: 500; }}
            QPushButton#qualityOption:checked {{ color: #264b75; font-weight: 600; }}
            QPushButton#qualityOption:hover:!checked {{ color: #405e80; }}
            QPushButton#qualityOption:disabled {{ color: #a0acbb; }}
        ''')
        self._position_pill()

    def _position_pill(self, animate=False):
        if not self.buttons:
            return
        inset = self._inset
        width = (self.width() - 2 * inset) / len(self.buttons)
        from PySide6.QtCore import QRect
        rectangle = QRect(round(inset + self._index * width), inset,
                          round(width), max(1, self.height() - 2 * inset))
        self._animation.stop()
        if animate:
            self._animation.setStartValue(self._pill.geometry())
            self._animation.setEndValue(rectangle)
            self._animation.start()
        else:
            self._pill.setGeometry(rectangle)

    def resizeEvent(self, event):
        self._position_pill()
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Up, Qt.Key.Key_Right, Qt.Key.Key_Down):
            offset = -1 if key in (Qt.Key.Key_Left, Qt.Key.Key_Up) else 1
            self.setCurrentIndex((self._index + offset) % len(self.buttons))
        elif key in (Qt.Key.Key_Home, Qt.Key.Key_End):
            self.setCurrentIndex(0 if key == Qt.Key.Key_Home else len(self.buttons) - 1)
        else:
            super().keyPressEvent(event)
