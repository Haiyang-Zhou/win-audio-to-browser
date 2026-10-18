"""Receiver UI strings shared by all browser types."""
from ui_languages import LANGUAGES, MESSAGES
from audio_modes import MODE_MESSAGES

KEYS = ('hero', 'intro', 'listen', 'mic', 'listen_hint', 'mic_hint', 'secure_hint',
        'ready', 'connecting', 'live_listen', 'live_mic', 'disconnected', 'blocked',
        'error', 'sync', 'local', 'buffer', 'loss', 'note', 'device', 'private',
        'play', 'enable_mic', 'stop', 'sending', 'offline', 'unsupported', 'details')
ROWS = {
 'zh-CN': ['声音，自由流转。', '把电脑的声音，带到你手边的设备。', '聆听', '麦克风', '接收电脑声音，使用当前设备播放。', '将当前设备的麦克风传回电脑。', '麦克风需要 HTTPS 和浏览器授权。', '准备好连接', '正在建立连接…', '正在接收电脑声音', '麦克风正在传输', '连接已断开，可重新连接', '请点按按钮以允许播放声音', '连接失败：{error}', '跟随桌面', '仅局域网', '播放缓冲', '丢包 / 秒', '缓冲仅为浏览器端数据，不是总延迟。保持页面前台，锁屏可能中断。', '当前设备', '声音仅在你的局域网内传输。', '开始聆听', '启用麦克风', '断开连接', '发送包 / 秒', '暂无法同步桌面设置', '此浏览器不支持 WebRTC，请使用新版 Safari、Chrome、Edge 或 Firefox。', '连接详情'],
 'zh-TW': ['聲音，自由流轉。', '讓電腦的聲音，來到你手邊的裝置。', '聆聽', '麥克風', '接收電腦聲音，使用目前裝置播放。', '將目前裝置的麥克風傳回電腦。', '麥克風需要 HTTPS 與瀏覽器授權。', '準備好連線', '正在建立連線…', '正在接收電腦聲音', '麥克風正在傳送', '連線已中斷，可重新連線', '請點按按鈕以允許播放聲音', '連線失敗：{error}', '跟隨桌面', '僅區域網路', '播放緩衝', '遺失封包 / 秒', '緩衝只計算瀏覽器端，並非總延遲。請保持網頁前景，鎖定螢幕可能中斷。', '目前裝置', '聲音只在你的區域網路內傳送。', '開始聆聽', '啟用麥克風', '中斷連線', '傳送封包 / 秒', '暫時無法同步桌面設定', '此瀏覽器不支援 WebRTC，請使用新版 Safari、Chrome、Edge 或 Firefox。', '連線詳細資訊'],
 'en': ['Sound, a little closer.', 'Bring your computer’s sound to the device beside you.', 'Listen', 'Microphone', 'Play your computer’s audio on this device.', 'Send this device’s microphone to your computer.', 'Microphone access requires HTTPS and your permission.', 'Ready to connect', 'Connecting…', 'Receiving computer audio', 'Microphone is live', 'Disconnected. You can reconnect.', 'Tap the button to allow audio playback', 'Connection failed: {error}', 'Follows desktop', 'Local network only', 'Playback buffer', 'Packets lost / sec', 'Buffer is browser-side only, not total latency. Keep this page in front; locking the screen may interrupt audio.', 'This device', 'Your sound stays on your local network.', 'Start listening', 'Enable microphone', 'Disconnect', 'Packets sent / sec', 'Desktop settings are temporarily unavailable', 'WebRTC is unavailable. Try a current Safari, Chrome, Edge or Firefox.', 'Connection details'],
 'fr': ['Le son, tout près.', 'Retrouvez le son de votre ordinateur sur votre appareil.', 'Écouter', 'Microphone', 'Écoutez le son de l’ordinateur sur cet appareil.', 'Envoyez le microphone de cet appareil à l’ordinateur.', 'Le microphone nécessite HTTPS et votre autorisation.', 'Prêt à se connecter', 'Connexion…', 'Réception du son de l’ordinateur', 'Microphone actif', 'Déconnecté. Vous pouvez réessayer.', 'Touchez le bouton pour autoriser le son', 'Échec de connexion : {error}', 'Suit le bureau', 'Réseau local', 'Tampon de lecture', 'Paquets perdus / s', 'Le tampon concerne le navigateur, pas la latence totale. Gardez la page au premier plan ; le verrouillage peut couper le son.', 'Cet appareil', 'Votre son reste sur votre réseau local.', 'Commencer l’écoute', 'Activer le micro', 'Déconnecter', 'Paquets envoyés / s', 'Réglages du bureau indisponibles', 'WebRTC indisponible. Essayez Safari, Chrome, Edge ou Firefox à jour.', 'Détails de connexion'],
 'de': ['Klang, ganz nah.', 'Hören Sie Ihren Computer auf dem Gerät neben Ihnen.', 'Hören', 'Mikrofon', 'Computer-Audio auf diesem Gerät wiedergeben.', 'Das Mikrofon dieses Geräts an den Computer senden.', 'Das Mikrofon benötigt HTTPS und Ihre Erlaubnis.', 'Bereit zur Verbindung', 'Verbindung wird hergestellt…', 'Computer-Audio wird empfangen', 'Mikrofon ist aktiv', 'Getrennt. Erneut verbinden möglich.', 'Zum Erlauben der Wiedergabe die Taste antippen', 'Verbindung fehlgeschlagen: {error}', 'Wie am Desktop', 'Nur lokales Netz', 'Wiedergabepuffer', 'Paketverlust / Sek.', 'Der Puffer betrifft nur den Browser, nicht die Gesamtverzögerung. Seite im Vordergrund lassen; Sperren kann Audio unterbrechen.', 'Dieses Gerät', 'Ihr Audio bleibt im lokalen Netzwerk.', 'Wiedergabe starten', 'Mikrofon aktivieren', 'Trennen', 'Pakete gesendet / Sek.', 'Desktop-Einstellungen derzeit nicht verfügbar', 'WebRTC fehlt. Aktuelles Safari, Chrome, Edge oder Firefox verwenden.', 'Verbindungsdetails'],
 'es': ['El sonido, más cerca.', 'Lleva el sonido de tu ordenador al dispositivo que tienes a mano.', 'Escuchar', 'Micrófono', 'Reproduce el audio del ordenador en este dispositivo.', 'Envía el micrófono de este dispositivo al ordenador.', 'El micrófono requiere HTTPS y tu permiso.', 'Listo para conectar', 'Conectando…', 'Recibiendo audio del ordenador', 'Micrófono activo', 'Desconectado. Puedes volver a conectar.', 'Pulsa el botón para permitir el audio', 'Error de conexión: {error}', 'Sigue al escritorio', 'Solo red local', 'Búfer de reproducción', 'Paquetes perdidos / s', 'El búfer es solo del navegador, no la latencia total. Mantén la página abierta; bloquear la pantalla puede interrumpir el audio.', 'Este dispositivo', 'Tu audio permanece en tu red local.', 'Empezar a escuchar', 'Activar micrófono', 'Desconectar', 'Paquetes enviados / s', 'Ajustes del escritorio no disponibles', 'WebRTC no disponible. Usa Safari, Chrome, Edge o Firefox actualizado.', 'Detalles de conexión'],
 'ja': ['音を、もっと身近に。', 'パソコンの音を、手元のデバイスへ。', '聴く', 'マイク', 'パソコンの音声をこの端末で再生します。', 'この端末のマイクをパソコンへ送ります。', 'マイクには HTTPS と利用許可が必要です。', '接続の準備完了', '接続中…', 'パソコンの音声を受信中', 'マイク送信中', '切断されました。再接続できます。', 'ボタンを押して音声再生を許可してください', '接続エラー：{error}', 'デスクトップと同期', 'ローカル通信のみ', '再生バッファ', '損失パケット / 秒', 'バッファはブラウザー側のみで、総遅延ではありません。ページを前面に保ってください。画面ロックで音声が止まる場合があります。', 'この端末', '音声はローカルネットワーク内だけで転送されます。', '聴き始める', 'マイクを有効にする', '切断する', '送信パケット / 秒', 'デスクトップ設定を同期できません', 'WebRTC 非対応です。最新版の Safari、Chrome、Edge、Firefox をお試しください。', '接続の詳細'],
 'ko': ['소리, 더 가까이.', '컴퓨터의 소리를 손안의 기기로 가져오세요.', '듣기', '마이크', '컴퓨터의 소리를 이 기기에서 재생합니다.', '이 기기의 마이크를 컴퓨터로 전송합니다.', '마이크에는 HTTPS와 사용 권한이 필요합니다.', '연결 준비 완료', '연결 중…', '컴퓨터 오디오 수신 중', '마이크 전송 중', '연결이 끊겼습니다. 다시 연결하세요.', '버튼을 눌러 오디오 재생을 허용하세요', '연결 실패: {error}', '데스크톱과 동기화', '로컬 네트워크', '재생 버퍼', '손실 패킷 / 초', '버퍼는 브라우저 측 수치이며 전체 지연이 아닙니다. 페이지를 전면에 두세요. 화면을 잠그면 끊길 수 있습니다.', '현재 기기', '오디오는 로컬 네트워크 안에서만 전송됩니다.', '듣기 시작', '마이크 켜기', '연결 해제', '전송 패킷 / 초', '데스크톱 설정을 동기화할 수 없습니다', 'WebRTC가 없습니다. 최신 Safari, Chrome, Edge, Firefox를 사용하세요.', '연결 세부 정보'],
 'ru': ['Звук становится ближе.', 'Слушайте звук компьютера на устройстве рядом с вами.', 'Слушать', 'Микрофон', 'Воспроизводите звук компьютера на этом устройстве.', 'Передавайте микрофон этого устройства на компьютер.', 'Для микрофона нужны HTTPS и ваше разрешение.', 'Готово к подключению', 'Подключение…', 'Приём звука компьютера', 'Микрофон включён', 'Соединение прервано. Можно подключиться снова.', 'Нажмите кнопку, чтобы разрешить воспроизведение', 'Ошибка подключения: {error}', 'Как на компьютере', 'Только локальная сеть', 'Буфер воспроизведения', 'Потери пакетов / с', 'Это буфер браузера, а не полная задержка. Держите страницу открытой; блокировка экрана может прервать звук.', 'Это устройство', 'Звук остаётся в вашей локальной сети.', 'Начать слушать', 'Включить микрофон', 'Отключиться', 'Отправлено пакетов / с', 'Настройки компьютера пока недоступны', 'WebRTC недоступен. Используйте новый Safari, Chrome, Edge или Firefox.', 'Сведения о соединении'],
}
for code, row in ROWS.items():
    if len(row) != len(KEYS):
        raise ValueError(f'Web translation mismatch: {code}')
WEB_MESSAGES = {code: dict(zip(KEYS, row)) for code, row in ROWS.items()}
QUALITY_KEYS = ('quality', 'quality_auto', 'quality_pcm', 'quality_opus',
                'underruns', 'fallback_notice', 'pcm_requires', 'resampled')
QUALITY_ROWS = {
 'zh-CN': ['音频线路', '自动（优先无损）', '无损 PCM', '兼容 Opus', '播放缺帧次数', '已回退到有损 Opus', '无损播放需要 HTTPS 和支持 AudioWorklet 的浏览器', '播放重采样至'],
 'zh-TW': ['音訊線路', '自動（優先無損）', '無損 PCM', '相容 Opus', '播放缺幀次數', '已回退至有損 Opus', '無損播放需要 HTTPS 與支援 AudioWorklet 的瀏覽器', '播放重新取樣至'],
 'en': ['Audio transport', 'Auto (lossless first)', 'Lossless PCM', 'Compatible Opus', 'Playback underruns', 'Fell back to lossy Opus', 'Lossless requires HTTPS and an AudioWorklet-capable browser', 'Playback resampled to'],
 'fr': ['Transport audio', 'Auto (sans perte)', 'PCM sans perte', 'Opus compatible', 'Interruptions audio', 'Repli vers Opus avec perte', 'Le mode sans perte nécessite HTTPS et AudioWorklet', 'Lecture rééchantillonnée à'],
 'de': ['Audioübertragung', 'Auto (verlustfrei zuerst)', 'Verlustfreies PCM', 'Kompatibles Opus', 'Pufferunterläufe', 'Rückfall auf verlustbehaftetes Opus', 'Verlustfrei benötigt HTTPS und AudioWorklet', 'Wiedergabe neu abgetastet auf'],
 'es': ['Transporte de audio', 'Auto (sin pérdidas)', 'PCM sin pérdidas', 'Opus compatible', 'Interrupciones de audio', 'Cambio a Opus con pérdidas', 'Sin pérdidas requiere HTTPS y AudioWorklet', 'Reproducción remuestreada a'],
 'ja': ['音声転送', '自動（ロスレス優先）', 'ロスレス PCM', '互換 Opus', 'バッファ不足回数', '非可逆 Opus に切り替えました', 'ロスレスには HTTPS と AudioWorklet が必要です', '再生時の変換先'],
 'ko': ['오디오 전송', '자동 (무손실 우선)', '무손실 PCM', '호환 Opus', '버퍼 부족 횟수', '손실 Opus로 전환됨', '무손실에는 HTTPS와 AudioWorklet이 필요합니다', '재생 리샘플링'],
 'ru': ['Передача аудио', 'Авто (без потерь)', 'PCM без потерь', 'Совместимый Opus', 'Опустошения буфера', 'Переход на Opus с потерями', 'Для PCM нужны HTTPS и AudioWorklet', 'Частота воспроизведения'],
}
for code, row in QUALITY_ROWS.items():
    if len(row) != len(QUALITY_KEYS):
        raise ValueError(f'Quality translation mismatch: {code}')
    WEB_MESSAGES[code].update(zip(QUALITY_KEYS, row))
    WEB_MESSAGES[code].update(MODE_MESSAGES[code])

SHORT_QUALITY = {
    'zh-CN': ('自动', '无损', '兼容'), 'zh-TW': ('自動', '無損', '相容'),
    'en': ('Auto', 'PCM', 'Opus'), 'fr': ('Auto', 'PCM', 'Opus'),
    'de': ('Auto', 'PCM', 'Opus'), 'es': ('Auto', 'PCM', 'Opus'),
    'ja': ('自動', '無損失', '互換'), 'ko': ('자동', '무손실', '호환'),
    'ru': ('Авто', 'PCM', 'Opus'),
}
for code, short in SHORT_QUALITY.items():
    WEB_MESSAGES[code].update(zip(('quality_short_auto', 'quality_short_pcm', 'quality_short_opus'), short))


def ui_payload(path=None):
    from ui_preferences import read_language
    language = read_language(path)
    return {'language': language, 'languageLabel': LANGUAGES[language], 'messages': WEB_MESSAGES[language]}
