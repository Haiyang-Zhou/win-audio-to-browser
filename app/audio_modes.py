"""Shared mode labels and truthful desktop summaries of negotiated connections."""
MODE_KEYS = ('audio_current', 'audio_pcm', 'audio_opus',
             'audio_idle', 'audio_pending', 'audio_unknown', 'audio_mixed')
MODE_ROWS = {
 'zh-CN': ['当前模式', '无损 PCM', '有损 Opus', '未连接', '协商中', '模式未知', '混合模式'],
 'zh-TW': ['目前模式', '無損 PCM', '有損 Opus', '未連線', '協商中', '模式未知', '混合模式'],
 'en': ['Current mode', 'Lossless PCM', 'Lossy Opus', 'Not connected', 'Negotiating', 'Unknown mode', 'Mixed modes'],
 'fr': ['Mode actuel', 'PCM sans perte', 'Opus avec perte', 'Non connecté', 'Négociation', 'Mode inconnu', 'Modes mixtes'],
 'de': ['Aktueller Modus', 'Verlustfreies PCM', 'Verlustbehaftetes Opus', 'Nicht verbunden', 'Aushandlung', 'Unbekannter Modus', 'Gemischte Modi'],
 'es': ['Modo actual', 'PCM sin pérdidas', 'Opus con pérdidas', 'Sin conexión', 'Negociando', 'Modo desconocido', 'Modos mixtos'],
 'ja': ['現在のモード', 'ロスレス PCM', '非可逆 Opus', '未接続', '接続交渉中', '不明なモード', '混在モード'],
 'ko': ['현재 모드', '무손실 PCM', '손실 Opus', '연결 안 됨', '협상 중', '알 수 없는 모드', '혼합 모드'],
 'ru': ['Текущий режим', 'PCM без потерь', 'Opus с потерями', 'Нет подключения', 'Согласование', 'Режим неизвестен', 'Разные режимы'],
}
MODE_MESSAGES = {code: dict(zip(MODE_KEYS, row, strict=True)) for code, row in MODE_ROWS.items()}


def capture_capabilities(capture):
    if capture is None:
        return None
    return {'pcm': {'bits': 16, 'sampleRate': capture.rate, 'channels': capture.channels},
            'preference': ['pcm', 'opus']}


def mode_key(client):
    if client.get('ready') is False:
        return 'audio_pending'
    return {'pcm': 'audio_pcm', 'opus': 'audio_opus'}.get(client.get('transport'), 'audio_unknown')


def format_audio(info):
    rate = info.get('sampleRate')
    channels = info.get('channels')
    bits = info.get('bits')
    parts = []
    if bits:
        parts.append(f'{bits}-bit')
    if rate:
        parts.append(f'{rate / 1000:g} kHz')
    if channels:
        parts.append(f'{channels} ch')
    if info.get('outputSampleRate') and info['outputSampleRate'] != rate:
        parts.append(f"-> {info['outputSampleRate'] / 1000:g} kHz")
    return ' / '.join(parts)


def desktop_mode(state, language):
    messages = MODE_MESSAGES.get(language, MODE_MESSAGES['en'])
    clients = state.get('clients') or []
    if not state.get('healthy'):
        clients = []
    kinds = {mode_key(client) for client in clients}
    key = next(iter(kinds)) if len(kinds) == 1 else 'audio_mixed' if kinds else 'audio_idle'
    label = messages[key]
    details = [f"{messages['audio_current']}: {label}"]
    for client in clients:
        name = client.get('name') or client.get('kind', 'Browser')
        detail = ' / '.join(filter(None, (messages[mode_key(client)], format_audio(client))))
        details.append(f'{name}: {detail}')
    return label, '\n'.join(details)
