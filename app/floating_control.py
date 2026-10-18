"""Small LAN audio controller. The bridge remains independent of the window."""
import json
import os
import re
from pathlib import Path
import socket
import ssl
import subprocess
import sys
import time
import urllib.request

import psutil
from PySide6.QtCore import QObject, QPoint, QRunnable, QSettings, QSize, Qt, QThreadPool, QTimer, Signal
from PySide6.QtGui import QAction, QActionGroup, QColor, QFont, QFontDatabase, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QMenu, QPushButton, QStackedWidget, QSystemTrayIcon, QVBoxLayout, QWidget
from device_names import DeviceNames, valid_id
from ui_languages import LANGUAGES, MESSAGES, translate
from ui_preferences import save_language
from paths import PROJECT_ROOT, DATA_DIR

ROOT = PROJECT_ROOT
PYTHON = ROOT / '.venv' / 'Scripts' / 'python.exe'
if not PYTHON.exists():
    PYTHON = Path(sys.executable).with_name('python.exe')
SERVER = Path(__file__).with_name('server.py')
PORT = 8787
CREATE_HIDDEN = subprocess.CREATE_NO_WINDOW


class Bridge:
    def __init__(self, port=PORT, pid_file=None, names=None):
        self.port = port
        self.pid_file = pid_file or DATA_DIR / 'server.pid'
        self.names = names or DeviceNames()

    def process(self):
        try:
            process = psutil.Process(int(self.pid_file.read_text().strip()))
            args = process.cmdline()
            if not any(os.path.normcase(os.path.abspath(arg)) == os.path.normcase(str(SERVER)) for arg in args[1:] if not arg.startswith('-')):
                return None
            if '--port' not in args or args[args.index('--port') + 1] != str(self.port):
                return None
            return process if process.is_running() else None
        except (OSError, ValueError, psutil.Error, IndexError):
            return None

    def status(self):
        process = self.process()
        if not process:
            return {'running': False, 'url': '', 'healthy': False}
        args = process.cmdline()
        host = args[args.index('--host') + 1] if '--host' in args else '127.0.0.1'
        url = f'https://{host}:{self.port}'
        healthy = False
        clients = None
        try:
            # Only our explicitly identified local process uses this certificate.
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ssl._create_unverified_context()))
            with opener.open(url, timeout=1.5) as response:
                healthy = response.status == 200
            try:
                with opener.open(url + '/status', timeout=1.5) as response:
                    payload = json.load(response)
                    if isinstance(payload.get('clients'), list):
                        clients = payload['clients']
                        for client in clients:
                            if isinstance(client, dict):
                                try:
                                    client['name'] = self.names.remember(client.get('id'), client.get('kind', 'Browser'))
                                except (OSError, ValueError):
                                    client['name_error'] = '设备名称记录无法读取或写入'
            except (OSError, ValueError, AttributeError):
                pass  # Older bridges remain usable until the user restarts them.
        except OSError:
            pass
        return {'running': True, 'healthy': healthy, 'url': url, 'clients': clients}

    def start(self):
        if self.process():
            return self.status()
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe.connect(('8.8.8.8', 80))  # Select route only; send no packet.
            host = probe.getsockname()[0]
        finally:
            probe.close()
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        log_name = 'server' if self.port == PORT else f'server-test-{self.port}'
        with (DATA_DIR / f'{log_name}.log').open('w', encoding='utf-8') as out, (DATA_DIR / f'{log_name}-error.log').open('w', encoding='utf-8') as err:
            process = subprocess.Popen([str(PYTHON), '-u', str(SERVER), '--host', host, '--port', str(self.port)], cwd=ROOT, env=env, stdout=out, stderr=err, creationflags=CREATE_HIDDEN)
        self.pid_file.write_text(str(process.pid), encoding='ascii')
        for _ in range(40):
            if process.poll() is not None:
                raise RuntimeError('start_failed')
            state = self.status()
            if state['healthy']:
                return state
            time.sleep(.2)
        raise RuntimeError('start_timeout')

    def stop(self):
        process = self.process()
        if process:
            process.terminate()
            try:
                process.wait(5)
            except psutil.TimeoutExpired:
                raise RuntimeError('stop_timeout')
        self.pid_file.unlink(missing_ok=True)
        return self.status()


class TaskSignals(QObject):
    done = Signal(object, str)


class Task(QRunnable):
    def __init__(self, function):
        super().__init__()
        self.function = function
        self.signals = TaskSignals()

    def run(self):
        try:
            self.signals.done.emit(self.function(), '')
        except Exception as exc:
            self.signals.done.emit(None, str(exc))


def audio_icon(size=64):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor('#087fff'))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(0, 0, size, size, size * .25, size * .25)
    painter.setPen(QPen(QColor('white'), size * .065, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    for i, height in enumerate([.20, .42, .65, .34, .18]):
        x = size * (.23 + i * .135)
        painter.drawLine(QPoint(round(x), round(size * (.5 - height / 2))), QPoint(round(x), round(size * (.5 + height / 2))))
    painter.end()
    return QIcon(pixmap)


def pencil_icon(size=40):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(size / 24, size / 24)
    painter.setPen(QPen(QColor('#647f9f'), 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    path = QPainterPath()
    path.moveTo(5, 19)
    path.lineTo(6.2, 14.8)
    path.lineTo(16, 5)
    path.quadTo(17.2, 3.8, 18.4, 5)
    path.lineTo(20, 6.6)
    path.quadTo(21.2, 7.8, 20, 9)
    path.lineTo(10.2, 18.8)
    path.closeSubpath()
    painter.drawPath(path)
    painter.drawLine(14, 7, 18, 11)
    painter.end()
    return QIcon(pixmap)


def automatic_name(clients, language='zh-CN'):
    if not clients:
        return 'Audio Link'
    kinds = [client.get('kind', 'Browser') for client in clients if isinstance(client, dict)]
    if not kinds:
        return 'Audio Link'
    if len(kinds) > 1:
        return translate(language, 'devices', count=len(kinds))
    if clients[0].get('name'):
        return clients[0]['name']
    kind = kinds[0] if kinds[0] in ('iPad', 'iPhone', 'Android', 'Windows', 'Mac') else 'Browser'
    return f'{kind} Audio'


class NameEditor(QLineEdit):
    cancelled = Signal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            event.accept()
        else:
            super().keyPressEvent(event)


class AudioPanel(QWidget):
    def __init__(self, bridge=None, testing=False):
        super().__init__()
        self.bridge = bridge or Bridge()
        self.testing = testing
        self.settings = QSettings('AudioLink', 'Desktop')
        self.preferences_path = DATA_DIR / 'ui-preferences.json'
        self.language = 'zh-CN' if testing else self.settings.value('language', 'zh-CN')
        if self.language not in LANGUAGES:
            self.language = 'zh-CN'
        self.scale_percent = 100 if testing else int(self.settings.value('scale', 85))
        if self.scale_percent not in (75, 85, 100, 115, 130):
            self.scale_percent = 100
        self.docked = True if testing else self.settings.value('docked', True, type=bool)
        self.name_mode = 'auto' if testing else self.settings.value('name_mode', 'auto')
        self.custom_name = '' if testing else str(self.settings.value('custom_name', ''))[:24]
        self.rename_target = None
        self.editing_name = False
        self.busy = False
        self.state = {'running': False, 'url': '', 'healthy': False}
        self.drag_origin = None
        self.setWindowTitle('iPad Audio')
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowIcon(audio_icon())
        self.setFixedSize(344, 274)
        outer = QVBoxLayout(self)
        self.outer_layout = outer
        outer.setContentsMargins(7, 7, 7, 7)
        card = QFrame()
        card.setObjectName('card')
        outer.addWidget(card)
        layout = QVBoxLayout(card)
        self.card_layout = layout
        layout.setContentsMargins(22, 17, 22, 18)
        layout.setSpacing(12)
        header = QHBoxLayout()
        self.hide_button = QPushButton('×')
        self.hide_button.setObjectName('close')
        self.hide_button.setFixedSize(23, 23)
        self.hide_button.setToolTip('收起到托盘，保持声音传输')
        self.hide_button.clicked.connect(self.close)
        header.addWidget(self.hide_button)
        self.minimize_button = QPushButton('−')
        self.minimize_button.setObjectName('minimize')
        self.minimize_button.setFixedSize(23, 23)
        self.minimize_button.setToolTip('最小化到任务栏，保持声音传输')
        self.minimize_button.clicked.connect(self.showMinimized)
        header.addWidget(self.minimize_button)
        tag = QLabel('AUDIO  /  LINK')
        tag.setObjectName('eyebrow')
        header.addStretch()
        header.addWidget(tag)
        self.pin = QPushButton('置顶')
        self.pin.setObjectName('pin')
        self.pin.setCheckable(True)
        self.pin.setChecked(True)
        self.pin.clicked.connect(self.toggle_pin)
        header.addWidget(self.pin)
        self.options = QPushButton('⋯')
        self.options.setObjectName('options')
        self.options.setToolTip('窗口大小与停靠位置')
        self.options.setFixedSize(24, 23)
        header.addWidget(self.options)
        self.view_menu = QMenu(self)
        self.view_menu.setStyleSheet('QMenu { background: #f8fafc; color: #303846; padding: 6px; border: 1px solid #d5dde8; border-radius: 10px; } QMenu::item { padding: 7px 17px; border-radius: 6px; } QMenu::item:selected { background: #e1edff; color: #0878f3; }')
        self.scale_group = QActionGroup(self)
        for percent in (75, 85, 100, 115, 130):
            action = self.view_menu.addAction(f'{percent}% 缩放')
            action.setCheckable(True)
            action.setData(percent)
            self.scale_group.addAction(action)
            action.triggered.connect(lambda checked=False, value=percent: self.apply_scale(value))
        self.view_menu.addSeparator()
        self.dock_action = self.view_menu.addAction('停靠右下角（避开任务栏）')
        self.dock_action.setCheckable(True)
        self.dock_action.setChecked(self.docked)
        self.dock_action.triggered.connect(self.set_docked)
        self.view_menu.addSeparator()
        self.auto_name_action = self.view_menu.addAction('自动命名（按已连接设备）')
        self.auto_name_action.setCheckable(True)
        self.auto_name_action.setChecked(self.name_mode != 'custom')
        self.auto_name_action.triggered.connect(self.use_automatic_name)
        self.edit_name_action = self.view_menu.addAction('直接编辑名称…')
        self.edit_name_action.triggered.connect(self.edit_custom_name)
        self.view_menu.addSeparator()
        self.language_menu = self.view_menu.addMenu('语言')
        self.language_group = QActionGroup(self)
        for code, label in LANGUAGES.items():
            action = self.language_menu.addAction(label)
            action.setCheckable(True)
            action.setData(code)
            self.language_group.addAction(action)
            action.triggered.connect(lambda checked=False, value=code: self.set_language(value))
        self.options.clicked.connect(lambda: self.view_menu.popup(self.options.mapToGlobal(QPoint(0, self.options.height()))))
        layout.addLayout(header)
        title_row = QHBoxLayout()
        icon = QLabel()
        self.audio_badge = icon
        icon.setPixmap(audio_icon().pixmap(44, 44))
        title_row.addWidget(icon)
        titles = QVBoxLayout()
        self.title_layout = titles
        titles.setSpacing(2)
        title = QLabel('iPad Audio')
        self.title_label = title
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setMinimumWidth(0)
        title.setObjectName('title')
        self.name_stack = QStackedWidget()
        self.name_stack.setMinimumWidth(0)
        self.name_stack.addWidget(title)
        self.name_editor = NameEditor()
        self.name_editor.setObjectName('nameEditor')
        self.name_editor.setMaxLength(24)
        self.name_editor.setPlaceholderText('输入名称，回车保存')
        self.name_editor.returnPressed.connect(self.commit_inline_name)
        self.name_editor.cancelled.connect(self.cancel_inline_name)
        self.name_editor.editingFinished.connect(self.commit_inline_name)
        self.name_stack.addWidget(self.name_editor)
        name_row = QHBoxLayout()
        name_row.setSpacing(4)
        name_row.addWidget(self.name_stack)
        self.edit_button = QPushButton()
        self.edit_button.setObjectName('edit')
        self.edit_button.setIcon(pencil_icon())
        self.edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_button.clicked.connect(self.edit_custom_name)
        name_row.addWidget(self.edit_button)
        name_row.addStretch()
        titles.addLayout(name_row)
        self.subtitle = QLabel('让声音，轻松流动')
        self.subtitle.setObjectName('muted')
        titles.addWidget(self.subtitle)
        title_row.addLayout(titles)
        title_row.addStretch()
        layout.addLayout(title_row)
        status_row = QHBoxLayout()
        self.status_label = QLabel('●  正在检查服务')
        self.status_label.setObjectName('status')
        self.mode_label = QLabel('局域网 · 双声道')
        self.mode_label.setObjectName('muted')
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        status_row.addWidget(self.mode_label)
        layout.addLayout(status_row)
        self.power = QPushButton('启动音频传输')
        self.power.setObjectName('power')
        self.power.setFixedHeight(43)
        self.power.clicked.connect(self.toggle)
        layout.addWidget(self.power)
        link_row = QHBoxLayout()
        self.address = QLabel('启动后显示 iPad 访问地址')
        self.address.setObjectName('address')
        self.copy = QPushButton('复制')
        self.copy.setObjectName('copy')
        self.copy.clicked.connect(self.copy_address)
        link_row.addWidget(self.address, 1)
        link_row.addWidget(self.copy)
        layout.addLayout(link_row)
        self.setStyleSheet('''
            QWidget { font-family: "Noto Sans SC", "Microsoft YaHei UI"; font-size: 11px; color: #22252a; }
            QFrame#card { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ffffff,stop:1 #eaf0f7); border: 1px solid #cfd8e3; border-radius: 23px; }
            QLabel { background: transparent; border: none; }
            QLabel#eyebrow { font-size: 9px; font-weight: 600; color: #929ba7; letter-spacing: 1px; }
            QLabel#title { font-family: "Segoe UI Variable Display", "Segoe UI"; font-size: 25px; font-weight: 600; letter-spacing: -0.5px; }
            QLineEdit#nameEditor { font-size: 18px; font-weight: 500; color: #243246; background: #ffffff; border: 1px solid #6baaff; border-radius: 7px; padding: 2px 4px; selection-background-color: #c9e2ff; }
            QLabel#muted { color: #7b8591; font-size: 10px; }
            QLabel#address { color: #647286; font-size: 10px; }
            QLabel#status { color: #718092; font-size: 11px; }
            QPushButton { border: none; border-radius: 9px; padding: 4px 8px; background: transparent; }
            QPushButton:hover { background: #dfe7f0; }
            QPushButton#close { padding: 0; color: #8b5352; background: #ffcfca; border-radius: 11px; font-size: 17px; }
            QPushButton#close:hover { background: #ffaaa1; }
            QPushButton#minimize { padding: 0; color: #89631b; background: #ffe5a6; border-radius: 11px; font-size: 17px; }
            QPushButton#minimize:hover { background: #ffd574; }
            QPushButton#pin { color: #75808e; font-size: 10px; }
            QPushButton#pin:checked { color: #0878f3; background: #e4eeff; }
            QPushButton#power { color: white; background: #087fff; font-size: 13px; font-weight: 600; border-radius: 13px; }
            QPushButton#power:hover { background: #0070eb; }
            QPushButton#power:disabled { background: #9cbbe0; }
            QPushButton#copy { color: #0878f3; font-size: 10px; }
            QPushButton#options { color: #75808e; padding: 0; font-size: 17px; font-weight: 600; }
            QPushButton#options::menu-indicator { image: none; }
            QPushButton#edit { padding: 0; border-radius: 8px; background: transparent; }
            QPushButton#edit:hover { background: #dceaff; }
        ''')
        self.base_style = self.styleSheet()
        self.base_metrics = [(item, item.spacing()) for item in (outer, layout, header, title_row, titles, name_row, status_row, link_row)]
        self.apply_scale(self.scale_percent, save=False)
        self.tray = QSystemTrayIcon(audio_icon(), self)
        self.tray.setToolTip('iPad Audio · 点击显示悬浮窗')
        menu = QMenu()
        show = menu.addAction('显示悬浮窗')
        self.show_action = show
        show.triggered.connect(self.reveal)
        self.tray_power = menu.addAction('启动音频传输')
        self.tray_power.triggered.connect(self.toggle)
        self.folder_action = menu.addAction('打开软件目录')
        self.folder_action.triggered.connect(lambda: os.startfile(ROOT))
        self.settings_action = menu.addMenu(self.view_menu)
        menu.addSeparator()
        self.quit_keep_action = menu.addAction('退出悬浮窗（保留服务）')
        self.quit_keep_action.triggered.connect(QApplication.instance().quit)
        self.stop_quit_action = menu.addAction('停止传输并退出')
        self.stop_quit_action.triggered.connect(self.stop_and_exit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.reveal() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.exit_when_done = False
        self.set_language(self.language, save=False)
        if not testing:
            self.tray.show()
            point = self.settings.value('position')
            available = QApplication.primaryScreen().availableGeometry()
            if self.docked:
                self.dock_bottom_right()
            elif isinstance(point, QPoint) and any(screen.availableGeometry().contains(point) for screen in QApplication.screens()):
                self.move(point)
            else:
                self.move(available.right() - self.width() - 24, available.top() + 100)
            for screen in QApplication.screens():
                screen.availableGeometryChanged.connect(lambda _: self.dock_bottom_right() if self.docked else None)
            self.poll = QTimer(self)
            self.poll.timeout.connect(lambda: self.run(self.bridge.status))
            self.poll.start(3000)
            self.run(self.bridge.status)

    def apply_scale(self, percent, save=True):
        self.scale_percent = percent
        factor = percent / 100
        px = lambda value: max(1, round(value * factor))
        self.setFixedSize(px(344), px(274))
        self.outer_layout.setContentsMargins(*([px(7)] * 4))
        self.card_layout.setContentsMargins(px(22), px(17), px(22), px(18))
        for layout, spacing in self.base_metrics:
            if spacing >= 0:
                layout.setSpacing(px(spacing))
        self.hide_button.setFixedSize(px(23), px(23))
        self.minimize_button.setFixedSize(px(23), px(23))
        self.options.setFixedSize(px(24), px(23))
        self.edit_button.setFixedSize(px(24), px(26))
        self.edit_button.setIconSize(QSize(px(17), px(17)))
        self.power.setFixedHeight(px(43))
        self.audio_badge.setPixmap(audio_icon().pixmap(px(44), px(44)))
        self.setStyleSheet(re.sub(r'(-?\d+(?:\.\d+)?)px', lambda match: f'{float(match[1]) * factor:g}px', self.base_style))
        for action in self.scale_group.actions():
            action.setChecked(action.data() == percent)
        if hasattr(self, 'tray'):
            self.update_name()
        if self.docked:
            self.dock_bottom_right()
        else:
            area = (self.screen() or QApplication.primaryScreen()).availableGeometry()
            self.move(max(area.left(), min(self.x(), area.right() - self.width() + 1)), max(area.top(), min(self.y(), area.bottom() - self.height() + 1)))
        if save and not self.testing:
            self.settings.setValue('scale', percent)
            self.settings.setValue('position', self.pos())

    def t(self, key, **values):
        return translate(self.language, key, **values)

    def set_language(self, code, save=True):
        if code not in LANGUAGES:
            return
        self.language = code
        if save and not self.testing:
            self.settings.setValue('language', code)
        sync_error = None
        if not self.testing:
            try:
                save_language(code, self.preferences_path)
            except OSError as exc:
                sync_error = str(exc)
        for action in self.language_group.actions():
            action.setChecked(action.data() == code)
        for action in self.scale_group.actions():
            action.setText(self.t('scale', percent=action.data()))
        self.language_menu.setTitle(self.t('language'))
        self.pin.setText(self.t('pin'))
        self.hide_button.setToolTip(self.t('hide_tip'))
        self.minimize_button.setToolTip(self.t('minimize_tip'))
        self.options.setToolTip(self.t('settings_tip'))
        self.dock_action.setText(self.t('dock'))
        self.auto_name_action.setText(self.t('auto_name'))
        self.edit_name_action.setText(self.t('edit_name'))
        self.edit_button.setToolTip(self.t('edit_tip'))
        self.edit_button.setAccessibleName(self.t('edit_name'))
        self.name_editor.setPlaceholderText(self.t('edit_placeholder'))
        self.show_action.setText(self.t('show'))
        self.folder_action.setText(self.t('folder'))
        self.settings_action.setText(self.t('settings'))
        self.quit_keep_action.setText(self.t('quit_keep'))
        self.stop_quit_action.setText(self.t('stop_quit'))
        self.mode_label.setText(self.t('mode'))
        self.copy.setText(self.t('copy'))
        self.render_state()
        if self.busy:
            self.power.setText(self.t('working'))
        if sync_error:
            self.tray.showMessage('Audio Link', self.t('operation_failed') + ': ' + sync_error, QSystemTrayIcon.MessageIcon.Warning)

    def dock_bottom_right(self):
        name = self.settings.value('dock_screen', '') if not self.testing else ''
        screen = next((s for s in QApplication.screens() if s.name() == name), self.screen() or QApplication.primaryScreen())
        area = screen.availableGeometry()
        self.move(area.right() - self.width() - 15, area.bottom() - self.height() - 15)

    def set_docked(self, checked):
        self.docked = checked
        self.dock_action.setChecked(checked)
        if not self.testing:
            self.settings.setValue('docked', checked)
            if checked:
                self.settings.setValue('dock_screen', self.screen().name())
        if checked:
            self.dock_bottom_right()

    def run(self, function):
        if self.busy:
            return
        self.busy = True
        self.power.setEnabled(False)
        self.tray_power.setEnabled(False)
        task = Task(function)
        task.signals.done.connect(self.completed)
        QThreadPool.globalInstance().start(task)

    def completed(self, state, error):
        self.busy = False
        self.power.setEnabled(True)
        self.tray_power.setEnabled(True)
        if error:
            self.exit_when_done = False
            self.status_label.setText('●  ' + self.t('operation_failed'))
            self.status_label.setToolTip(error)
            message = self.t(error) if error in MESSAGES[self.language] else error
            self.tray.showMessage('Audio Link', message, QSystemTrayIcon.MessageIcon.Warning)
            return
        self.state = state
        self.render_state()
        if self.exit_when_done:
            QApplication.instance().quit()

    def render_state(self):
        running = self.state['running']
        healthy = self.state['healthy']
        self.status_label.setText('●  ' + self.t('running' if healthy else ('not_ready' if running else 'stopped')))
        self.status_label.setStyleSheet(f"color: {'#259a69' if healthy else '#7b8591'}")
        self.status_label.setToolTip(self.t('health_tip') if healthy else '')
        text = self.t('stop' if running else 'start')
        self.power.setText(text)
        self.tray_power.setText(text)
        self.address.setText(self.state['url'] or self.t('address_hint'))
        self.copy.setEnabled(bool(self.state['url']))
        self.update_name()

    def update_name(self):
        clients = self.state.get('clients')
        name = self.custom_name if self.name_mode == 'custom' and self.custom_name else automatic_name(clients, self.language)
        self.setWindowTitle(name)
        self.tray.setToolTip(self.t('tray_tip', name=name))
        width = round(182 * self.scale_percent / 100)
        self.title_label.setText(self.title_label.fontMetrics().elidedText(name, Qt.TextElideMode.ElideRight, width))
        self.title_label.setToolTip(name)
        if not self.editing_name:
            self.name_stack.setFixedWidth(min(width, self.title_label.fontMetrics().horizontalAdvance(self.title_label.text()) + 4))
        if self.state.get('healthy') and clients is None:
            self.subtitle.setText(self.t('restart_hint'))
        elif self.state.get('healthy') and not clients:
            self.subtitle.setText(self.t('waiting'))
        elif clients:
            detail = self.t('devices', count=len(clients)) if len(clients) > 1 else str(clients[0].get('kind', 'Browser'))
            self.subtitle.setText(self.t('connected', device=detail))
        else:
            self.subtitle.setText(self.t('tagline'))
        self.subtitle.setToolTip(self.subtitle.text())
        self.subtitle.setFixedWidth(round(212 * self.scale_percent / 100))
        self.subtitle.setText(self.subtitle.fontMetrics().elidedText(self.subtitle.text(), Qt.TextElideMode.ElideRight, self.subtitle.width()))

    def save_name(self, mode, name=''):
        self.name_mode = mode
        if mode == 'custom':
            self.custom_name = ' '.join(name.split())[:24]
        self.auto_name_action.setChecked(mode == 'auto')
        if not self.testing:
            self.settings.setValue('name_mode', mode)
            self.settings.setValue('custom_name', self.custom_name)
        self.update_name()

    def use_automatic_name(self):
        self.save_name('auto')

    def edit_custom_name(self):
        self.editing_name = True
        self.name_stack.setFixedWidth(round(182 * self.scale_percent / 100))
        clients = self.state.get('clients') or []
        self.rename_target = dict(clients[0]) if len(clients) == 1 and valid_id(clients[0].get('id')) else None
        self.name_editor.setText(self.windowTitle())
        self.name_stack.setCurrentWidget(self.name_editor)
        self.name_editor.setFocus()
        self.name_editor.selectAll()
        self.name_editor.setToolTip(self.t('remember_tip' if self.rename_target else 'window_only_tip'))

    def cancel_inline_name(self):
        self.editing_name = False
        self.rename_target = None
        self.name_stack.setCurrentWidget(self.title_label)
        self.update_name()

    def commit_inline_name(self):
        if not self.editing_name or self.name_stack.currentWidget() is not self.name_editor:
            return
        name = ' '.join(self.name_editor.text().split())[:24]
        target = self.rename_target
        self.cancel_inline_name()
        if not name:
            return
        if target:
            try:
                self.bridge.names.remember(target['id'], target['kind'], name)
            except (OSError, ValueError) as exc:
                self.subtitle.setText(self.t('save_failed'))
                self.subtitle.setToolTip(str(exc))
                return
            for client in self.state.get('clients') or []:
                if client.get('id') == target['id']:
                    client['name'] = name
            self.save_name('auto')
        else:
            self.save_name('custom', name)
            self.subtitle.setText(self.t('window_saved'))

    def toggle(self):
        self.power.setText(self.t('working'))
        self.run(self.bridge.stop if self.state['running'] else self.bridge.start)

    def stop_and_exit(self):
        if self.busy:
            return
        self.exit_when_done = True
        self.run(self.bridge.stop)

    def copy_address(self):
        QApplication.clipboard().setText(self.state['url'])
        self.copy.setText(self.t('copied'))
        QTimer.singleShot(1300, lambda: self.copy.setText(self.t('copy')))

    def toggle_pin(self):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.pin.isChecked())
        self.show()

    def reveal(self):
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()
        self.raise_()
        self.activateWindow()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_origin = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.drag_origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            if self.docked:
                self.set_docked(False)
            self.move(event.globalPosition().toPoint() - self.drag_origin)

    def mouseReleaseEvent(self, event):
        self.drag_origin = None
        if not self.testing:
            self.settings.setValue('position', self.pos())

    def closeEvent(self, event):
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.hide()
            event.ignore()
        else:
            event.accept()
            QApplication.instance().quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    family = 'Noto Sans SC' if 'Noto Sans SC' in QFontDatabase.families() else 'Microsoft YaHei UI'
    app.setFont(QFont(family, 10))
    socket_name = 'audio-link-desktop-8787'
    client = QLocalSocket()
    client.connectToServer(socket_name)
    if client.waitForConnected(500):
        client.write(b'show')
        client.waitForBytesWritten(500)
        return
    QLocalServer.removeServer(socket_name)
    singleton = QLocalServer()
    if not singleton.listen(socket_name):
        return
    panel = AudioPanel()
    def wake_existing():
        connection = singleton.nextPendingConnection()
        if connection:
            connection.close()
            connection.deleteLater()
        panel.reveal()
    singleton.newConnection.connect(wake_existing)
    panel.show()
    app.exec()


if __name__ == '__main__':
    main()
