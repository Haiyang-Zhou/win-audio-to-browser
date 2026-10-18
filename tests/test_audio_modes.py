"""Mode summaries never confuse sender capabilities with an active receiver."""
from PySide6.QtWidgets import QApplication
from floating_control import AudioPanel
from audio_modes import MODE_MESSAGES, desktop_mode
from ui_preferences import read_preferences, save_quality

app = QApplication([])
panel = AudioPanel(testing=True)
state = {'running': True, 'healthy': True, 'url': 'https://your-pc.local:8787',
         'audio': {'pcm': {'bits': 16, 'sampleRate': 48000, 'channels': 2}}, 'clients': []}
for language, messages in MODE_MESSAGES.items():
    assert desktop_mode(state, language)[0] == messages['audio_idle']
    pcm = {'name': 'Tablet', 'kind': 'iPad', 'transport': 'pcm', 'ready': False,
           'bits': 16, 'sampleRate': 48000, 'channels': 2}
    state['clients'] = [pcm]
    assert desktop_mode(state, language)[0] == messages['audio_pending']
    pcm['ready'] = True
    assert desktop_mode(state, language)[0] == messages['audio_pcm']
    state['clients'].append({'name': 'Phone', 'transport': 'opus'})
    label, detail = desktop_mode(state, language)
    assert label == messages['audio_mixed'] and 'Tablet' in detail and 'Phone' in detail
    panel.state = state
    panel.set_language(language)
    for scale in (75, 85, 100, 130):
        panel.apply_scale(scale)
        app.processEvents()
        assert panel.mode_label.toolTip() == detail
        assert panel.mode_label.width() <= panel.width() / 2
        assert '48 kHz' in panel.details_text.text()
        assert '最高支持' not in panel.details_text.text() and 'Best supported' not in panel.details_text.text()
        panel.details_button.setChecked(True)
        assert panel.details_open and not panel.details_scroll.isHidden()
        assert panel.height() == round(500 * scale / 100)
        panel.details_button.setChecked(False)
        assert not panel.details_open and panel.details_scroll.isHidden()
    state['clients'] = [{'kind': 'Browser'}]
    assert desktop_mode(state, language)[0] == messages['audio_unknown']
    state['clients'] = []
panel.quality_selector.setCurrentIndex(2)
assert read_preferences(panel.preferences_path)['quality'] == 'opus'
save_quality('pcm', panel.preferences_path)
panel.render_state()
assert panel.quality_selector.currentData() == 'pcm'
save_quality('auto', panel.preferences_path)
panel.close()
print('PASS: 9-language idle, pending, PCM, Opus, mixed and legacy states; 4 UI scales')
