"""Naming and live-client reporting checks; no user stream is interrupted."""
import asyncio
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from PySide6.QtWidgets import QApplication
from floating_control import AudioPanel, automatic_name
from server import device_kind, status


async def check_status():
    class Peer:
        def __init__(self, state):
            self.connectionState = state
    connected, waiting = Peer('connected'), Peer('connecting')
    app = web.Application()
    app['clients'] = {connected: {'kind': 'iPad', 'mode': 'listen'}, waiting: {'kind': 'Android', 'mode': 'listen'}}
    app.router.add_get('/status', status)
    async with TestClient(TestServer(app)) as client:
        response = await client.get('/status')
        assert (await response.json())['clients'] == [{'kind': 'iPad', 'mode': 'listen', 'id': ''}]
        assert response.headers['Cache-Control'] == 'no-store'
        connected.connectionState = 'disconnected'
        assert (await (await client.get('/status')).json())['clients'] == []


assert device_kind({'deviceKind': 'iPad'}, 'Macintosh') == 'iPad'
assert device_kind({}, 'Mozilla iPhone') == 'iPhone'
assert device_kind({'deviceKind': '<bad>'}, 'Android') == 'Android'
assert device_kind({}, '') == 'Browser'
assert automatic_name([]) == 'Audio Link'
assert automatic_name([{'kind': 'iPad'}]) == 'iPad Audio'
assert automatic_name([{'kind': 'iPhone'}]) == 'iPhone Audio'
assert automatic_name([{'kind': 'Android'}]) == 'Android Audio'
assert automatic_name([{'kind': 'iPad'}, {'kind': 'iPhone'}]) == '2 台设备'
asyncio.run(check_status())
app = QApplication([])
panel = AudioPanel(testing=True)
panel.state = {'running': True, 'healthy': True, 'url': 'https://your-pc.local:8787', 'clients': [{'kind': 'iPad'}]}
panel.render_state()
assert panel.windowTitle() == 'iPad Audio'
panel.save_name('custom', '我的桌面音响')
assert panel.windowTitle() == '我的桌面音响'
panel.state['clients'] = [{'kind': 'Android'}]
panel.render_state()
assert panel.windowTitle() == '我的桌面音响', 'Custom name must not change with device'
panel.use_automatic_name()
assert panel.windowTitle() == 'Android Audio'
panel.state['clients'] = []
panel.render_state()
assert panel.windowTitle() == 'Audio Link'
print('PASS: device detection, active clients only, disconnect, auto naming, custom override, restore automatic')
