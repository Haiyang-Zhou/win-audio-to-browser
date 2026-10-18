"""Desktop translations. Device aliases are user data and are never translated."""
LANGUAGES = {
    'zh-CN': '简体中文', 'zh-TW': '繁體中文', 'en': 'English', 'fr': 'Français',
    'de': 'Deutsch', 'es': 'Español', 'ja': '日本語', 'ko': '한국어', 'ru': 'Русский',
}

KEYS = (
    'language', 'pin', 'hide_tip', 'minimize_tip', 'settings_tip', 'scale', 'dock',
    'auto_name', 'edit_name', 'edit_placeholder', 'tagline', 'checking', 'mode',
    'start', 'stop', 'address_hint', 'copy', 'copied', 'show', 'folder', 'settings',
    'quit_keep', 'stop_quit', 'tray_tip', 'operation_failed', 'running', 'not_ready',
    'stopped', 'health_tip', 'edit_tip', 'restart_hint', 'waiting', 'connected',
    'devices', 'remember_tip', 'window_only_tip', 'save_failed', 'window_saved',
    'working', 'start_failed', 'start_timeout', 'stop_timeout',
)

ROWS = {
    'ru': [
        'Язык', 'Поверх', 'Свернуть в трей; звук продолжится', 'Свернуть на панель задач; звук продолжится', 'Настройки окна и язык',
        'Масштаб {percent}%', 'Закрепить внизу справа', 'Имя по подключённому устройству', 'Изменить имя', 'Введите имя; Enter для сохранения',
        'Звук без границ', 'Проверка службы', 'LAN · Стерео', 'Включить звук', 'Выключить звук',
        'Адрес появится после запуска', 'Копировать', 'Скопировано', 'Показать окно', 'Открыть папку', 'Настройки окна',
        'Закрыть окно (оставить службу)', 'Выключить звук и выйти', '{name} · Нажмите, чтобы показать окно', 'Не удалось выполнить действие',
        'Служба работает', 'Не готово; проверьте журнал', 'Служба остановлена', 'Служба доступна; подключение iPad не подтверждено',
        'Изменить имя; Enter — сохранить, Esc — отменить', 'Перезапустите службу для определения устройств', 'Ожидание устройства', 'Подключено · {device}',
        'Устройств: {count}', 'Имя этого устройства будет сохранено', 'Устройство не определено; сохраняется только имя окна', 'Не удалось сохранить имя; проверьте файл записей',
        'Имя окна сохранено без привязки к устройству', 'Обработка…', 'Ошибка запуска; см. server-error.log',
        'Время запуска истекло; проверьте журнал', 'Служба ещё не завершена; повторите попытку',
    ],
    'zh-CN': [
        '语言', '置顶', '收起到托盘，保持声音传输', '最小化到任务栏，保持声音传输', '窗口设置与语言',
        '{percent}% 缩放', '停靠右下角（避开任务栏）', '自动命名（按已连接设备）', '编辑名称', '输入名称，回车保存',
        '让声音，轻松流动', '正在检查服务', '局域网 · 双声道', '启动音频传输', '停止音频传输',
        '启动后显示 iPad 访问地址', '复制', '已复制', '显示悬浮窗', '打开软件目录', '窗口设置',
        '退出悬浮窗（保留服务）', '停止传输并退出', '{name} · 点击显示悬浮窗', '操作未完成',
        '传输服务已开启', '服务未就绪，请查看日志', '传输服务已停止', '服务可访问；不代表 iPad 已连接',
        '编辑名称；回车保存，Esc 取消', '设备识别需重启一次传输服务', '等待设备连接', '已连接 · {device}',
        '{count} 台设备', '此设备的名称会被记住', '未识别单台设备，仅保存窗口名称', '名称保存失败，请检查记录文件',
        '已保存窗口名称，尚未绑定设备', '正在处理…', '启动失败，请查看 server-error.log',
        '启动超时，请查看日志；服务可能仍在启动', '服务尚未退出，请稍后再试',
    ],
    'zh-TW': [
        '語言', '置頂', '收起到系統匣，繼續傳送聲音', '最小化至工作列，繼續傳送聲音', '視窗設定與語言',
        '{percent}% 縮放', '停靠右下角（避開工作列）', '自動命名（依連線裝置）', '編輯名稱', '輸入名稱，按 Enter 儲存',
        '讓聲音，輕鬆流動', '正在檢查服務', '區域網路 · 雙聲道', '開始傳送音訊', '停止傳送音訊',
        '啟動後顯示 iPad 存取位址', '複製', '已複製', '顯示懸浮視窗', '開啟軟體資料夾', '視窗設定',
        '退出視窗（保留服務）', '停止傳送並退出', '{name} · 點擊顯示視窗', '操作未完成',
        '傳送服務已開啟', '服務未就緒，請查看記錄', '傳送服務已停止', '服務可存取；不代表 iPad 已連線',
        '編輯名稱；Enter 儲存，Esc 取消', '辨識裝置需重新啟動傳送服務', '等待裝置連線', '已連線 · {device}',
        '{count} 台裝置', '將記住此裝置名稱', '未辨識單台裝置，只儲存視窗名稱', '儲存名稱失敗，請檢查記錄檔',
        '已儲存視窗名稱，尚未綁定裝置', '處理中…', '啟動失敗，請查看 server-error.log',
        '啟動逾時，請查看記錄；服務可能仍在啟動', '服務尚未退出，請稍後再試',
    ],
    'en': [
        'Language', 'Pin', 'Hide to tray; keep streaming', 'Minimize to taskbar; keep streaming', 'Window settings and language',
        '{percent}% scale', 'Dock bottom right (above taskbar)', 'Automatic name (connected device)', 'Edit name', 'Enter a name; press Enter to save',
        'Sound, without boundaries', 'Checking service', 'LAN · Stereo', 'Start streaming', 'Stop streaming',
        'Start to show the iPad address', 'Copy', 'Copied', 'Show floating window', 'Open app folder', 'Window settings',
        'Quit window (keep service)', 'Stop streaming and quit', '{name} · Click to show window', 'Action failed',
        'Service is running', 'Not ready; check logs', 'Service is stopped', 'Service reachable; iPad may not be connected',
        'Edit name; Enter saves, Esc cancels', 'Restart the service to detect devices', 'Waiting for a device', 'Connected · {device}',
        '{count} devices', 'This device name will be remembered', 'No single device identified; saves window name only', 'Cannot save name; check the records file',
        'Window name saved; no device linked', 'Working…', 'Startup failed; check server-error.log',
        'Startup timed out; check logs, service may still be starting', 'Service has not exited; try again shortly',
    ],
    'fr': [
        'Langue', 'Fixer', 'Masquer dans la zone de notification sans couper le son', 'Réduire dans la barre des tâches sans couper le son', 'Réglages et langue',
        'Échelle : {percent} %', 'Ancrer en bas à droite', 'Nom automatique (appareil connecté)', 'Modifier le nom', 'Saisir un nom ; Entrée pour enregistrer',
        'Le son, en toute liberté', 'Vérification', 'LAN · Stéréo', 'Démarrer le son', 'Arrêter le son',
        'Démarrer pour afficher l’adresse', 'Copier', 'Copié', 'Afficher la fenêtre', 'Ouvrir le dossier', 'Réglages',
        'Quitter la fenêtre (garder le service)', 'Arrêter le son et quitter', '{name} · Cliquer pour afficher', 'Échec de l’action',
        'Service actif', 'Non prêt ; voir les journaux', 'Service arrêté', 'Service accessible ; connexion de l’iPad non confirmée',
        'Modifier : Entrée pour enregistrer, Échap pour annuler', 'Redémarrer le service pour détecter les appareils', 'En attente d’un appareil', 'Connecté · {device}',
        '{count} appareils', 'Le nom de cet appareil sera mémorisé', 'Aucun appareil unique ; seul le nom de fenêtre est enregistré', 'Échec de l’enregistrement du nom',
        'Nom de fenêtre enregistré, sans appareil lié', 'En cours…', 'Échec du démarrage ; voir server-error.log',
        'Délai de démarrage dépassé ; consulter les journaux', 'Le service ne s’est pas arrêté ; réessayer',
    ],
    'de': [
        'Sprache', 'Oben', 'In den Infobereich ausblenden; Audio läuft weiter', 'In die Taskleiste minimieren; Audio läuft weiter', 'Fenster und Sprache',
        '{percent}% Skalierung', 'Unten rechts andocken', 'Automatischer Name (verbundenes Gerät)', 'Name bearbeiten', 'Name eingeben; mit Enter speichern',
        'Klang, ganz mühelos', 'Dienst wird geprüft', 'LAN · Stereo', 'Audio starten', 'Audio stoppen',
        'Adresse erscheint nach dem Start', 'Kopieren', 'Kopiert', 'Fenster anzeigen', 'App-Ordner öffnen', 'Fenstereinstellungen',
        'Fenster schließen (Dienst behalten)', 'Audio stoppen und beenden', '{name} · Klicken zum Anzeigen', 'Aktion fehlgeschlagen',
        'Dienst läuft', 'Nicht bereit; Protokoll prüfen', 'Dienst gestoppt', 'Dienst erreichbar; iPad-Verbindung nicht bestätigt',
        'Name bearbeiten; Enter speichert, Esc verwirft', 'Für Geräteerkennung den Dienst neu starten', 'Warte auf ein Gerät', 'Verbunden · {device}',
        '{count} Geräte', 'Dieser Gerätename wird gespeichert', 'Kein einzelnes Gerät; nur Fenstername wird gespeichert', 'Name konnte nicht gespeichert werden',
        'Fenstername gespeichert, ohne Gerätebindung', 'Bitte warten…', 'Start fehlgeschlagen; server-error.log prüfen',
        'Start-Zeitlimit erreicht; Protokoll prüfen', 'Dienst noch nicht beendet; erneut versuchen',
    ],
    'es': [
        'Idioma', 'Fijar', 'Ocultar en la bandeja sin detener el audio', 'Minimizar a la barra de tareas sin detener el audio', 'Ventana e idioma',
        'Escala: {percent} %', 'Anclar abajo a la derecha', 'Nombre automático (dispositivo conectado)', 'Editar nombre', 'Escribe un nombre; Intro para guardar',
        'El sonido, sin límites', 'Comprobando servicio', 'LAN · Estéreo', 'Iniciar audio', 'Detener audio',
        'Inicia para mostrar la dirección', 'Copiar', 'Copiado', 'Mostrar ventana', 'Abrir carpeta', 'Ajustes de ventana',
        'Cerrar ventana (mantener servicio)', 'Detener audio y salir', '{name} · Pulsa para mostrar', 'No se completó la acción',
        'Servicio activo', 'No está listo; revisa el registro', 'Servicio detenido', 'Servicio accesible; conexión del iPad sin confirmar',
        'Editar nombre; Intro guarda, Esc cancela', 'Reinicia el servicio para detectar dispositivos', 'Esperando un dispositivo', 'Conectado · {device}',
        '{count} dispositivos', 'Se recordará el nombre de este dispositivo', 'Sin un único dispositivo; solo se guarda el nombre de ventana', 'No se pudo guardar el nombre',
        'Nombre de ventana guardado, sin dispositivo', 'Procesando…', 'Error al iniciar; revisa server-error.log',
        'Se agotó el tiempo de inicio; revisa el registro', 'El servicio no ha terminado; vuelve a intentarlo',
    ],
    'ja': [
        '言語', '固定', 'トレイに隠す（音声は継続）', 'タスクバーに最小化（音声は継続）', 'ウィンドウと言語の設定',
        '{percent}% 表示', '右下に配置（タスクバーを避ける）', '接続端末に合わせて自動命名', '名前を編集', '名前を入力し Enter で保存',
        '音を、もっと自由に', 'サービスを確認中', 'LAN · ステレオ', '音声転送を開始', '音声転送を停止',
        '開始後に iPad のアドレスを表示', 'コピー', 'コピー済み', 'ウィンドウを表示', 'フォルダーを開く', 'ウィンドウ設定',
        'ウィンドウを終了（サービス継続）', '転送を停止して終了', '{name} · クリックで表示', '操作できませんでした',
        'サービス稼働中', '未準備：ログを確認', 'サービス停止中', 'サービス接続可。iPad の接続は未確認',
        '名前を編集：Enter で保存、Esc で取消', '端末検出にはサービスの再起動が必要', '端末の接続を待機中', '接続中 · {device}',
        '{count} 台の端末', 'この端末の名前を記憶します', '端末が特定できないためウィンドウ名のみ保存', '名前を保存できません。記録を確認してください',
        'ウィンドウ名を保存（端末未登録）', '処理中…', '起動失敗：server-error.log を確認',
        '起動がタイムアウトしました。ログを確認', 'まだ終了していません。再試行してください',
    ],
    'ko': [
        '언어', '고정', '트레이로 숨기기; 오디오는 계속 재생', '작업 표시줄로 최소화; 오디오는 계속 재생', '창 설정 및 언어',
        '{percent}% 크기', '오른쪽 아래에 고정', '연결된 기기로 자동 이름 지정', '이름 편집', '이름 입력 후 Enter로 저장',
        '소리, 더 자유롭게', '서비스 확인 중', 'LAN · 스테레오', '오디오 전송 시작', '오디오 전송 중지',
        '시작하면 iPad 주소가 표시됩니다', '복사', '복사됨', '창 표시', '앱 폴더 열기', '창 설정',
        '창 닫기 (서비스 유지)', '전송 중지 후 종료', '{name} · 클릭하여 창 표시', '작업 실패',
        '서비스 실행 중', '준비 안 됨; 로그 확인', '서비스 중지됨', '서비스에 접근 가능; iPad 연결 여부는 별도',
        '이름 편집; Enter 저장, Esc 취소', '기기 감지를 위해 서비스를 다시 시작하세요', '기기 연결 대기 중', '연결됨 · {device}',
        '기기 {count}대', '이 기기의 이름을 기억합니다', '단일 기기를 식별하지 못해 창 이름만 저장', '이름 저장 실패; 기록 파일을 확인하세요',
        '창 이름 저장됨; 연결된 기기 없음', '처리 중…', '시작 실패; server-error.log를 확인하세요',
        '시작 시간 초과; 로그를 확인하세요', '서비스가 종료되지 않았습니다. 다시 시도하세요',
    ],
}

for _code, _row in ROWS.items():
    if len(_row) != len(KEYS):
        raise ValueError(f'Translation length mismatch: {_code}')
MESSAGES = {code: dict(zip(KEYS, row)) for code, row in ROWS.items()}


def translate(language, key, **values):
    return MESSAGES.get(language, MESSAGES['zh-CN'])[key].format(**values)
