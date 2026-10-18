"""Generate documentation artwork with fictional device/address data only."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'app'))
from PySide6.QtWidgets import QApplication
from floating_control import AudioPanel, ROOT

app = QApplication([])
panel = AudioPanel(testing=True)
panel.state = {'running': True, 'healthy': True, 'url': 'https://your-pc.local:8787', 'clients': [{'kind': 'iPad', 'name': 'Audio Link'}]}
panel.render_state()
panel.show()
app.processEvents()
panel.grab().save(str(ROOT / 'assets' / 'screenshots' / 'desktop.png'))
