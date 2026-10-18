"""Generate documentation artwork with fictional device/address data only."""
from pathlib import Path
import argparse
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'app'))
from PySide6.QtWidgets import QApplication
from floating_control import AudioPanel, ROOT

app = QApplication([])
parser = argparse.ArgumentParser()
parser.add_argument('--details', action='store_true')
args = parser.parse_args()
panel = AudioPanel(testing=True)
panel.state = {'running': True, 'healthy': True, 'url': 'https://your-pc.local:8787',
               'audio': {'pcm': {'bits': 16, 'sampleRate': 48000, 'channels': 2}},
               'clients': [{'kind': 'iPad', 'name': 'Audio Link', 'transport': 'pcm',
                            'ready': True, 'bits': 16, 'sampleRate': 48000, 'channels': 2,
                            'bufferMs': 64, 'underruns': 0, 'statsAt': time.time()}]}
panel.render_state()
panel.show()
if args.details:
    panel.details_button.setChecked(True)
app.processEvents()
panel.grab().save(str(ROOT / 'assets' / 'screenshots' / ('desktop-details.png' if args.details else 'desktop.png')))
