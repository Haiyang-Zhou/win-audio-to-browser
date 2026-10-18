"""Verify PCM bytes, device visibility, queue overflow and disconnect cleanup."""
import asyncio
from aiohttp import web, WSMsgType
from aiohttp.test_utils import TestClient, TestServer
from pcm_transport import install_pcm_routes
from server import LoopbackCapture, device_kind, status


class Capture:
    rate = 48000
    channels = 2
    samples_per_chunk = 960

    def __init__(self):
        self.queues = set()

    def subscribe(self, maxsize=1):
        queue = asyncio.Queue(maxsize=maxsize)
        self.queues.add(queue)
        return queue

    def unsubscribe(self, queue):
        self.queues.discard(queue)


async def main():
    app = web.Application()
    app['capture'] = capture = Capture()
    install_pcm_routes(app, device_kind)
    app.router.add_get('/status', status)
    async with TestClient(TestServer(app)) as client:
        response = await client.get('/pcm', headers={'Origin': 'https://unrelated.invalid'})
        assert response.status == 403
        ws = await client.ws_connect('/pcm?deviceKind=iPad&deviceId=' + 'a' * 32)
        metadata = await ws.receive_json()
        assert metadata['codec'] == 'pcm_s16le' and metadata['sampleRate'] == 48000
        clients = (await (await client.get('/status')).json())['clients']
        assert clients[0]['id'] == 'a' * 32 and clients[0]['transport'] == 'pcm'
        assert clients[0]['ready'] is False
        await ws.send_json({'type': 'ready', 'outputSampleRate': 44100})
        for _ in range(50):
            data = await (await client.get('/status')).json()
            if data['clients'][0]['ready']:
                break
            await asyncio.sleep(0.01)
        assert data['clients'][0]['outputSampleRate'] == 44100
        assert data['audio']['pcm'] == {'bits': 16, 'sampleRate': 48000, 'channels': 2}
        await ws.send_json({'type': 'stats', 'bufferMs': 64, 'underruns': 2})
        for _ in range(50):
            info = (await (await client.get('/status')).json())['clients'][0]
            if 'bufferMs' in info:
                break
            await asyncio.sleep(0.01)
        assert info['bufferMs'] == 64 and info['underruns'] == 2
        # All possible 16-bit sample patterns, including negative extrema.
        payload = bytes(range(256)) * 256
        for queue in capture.queues:
            queue.put_nowait(payload)
        result = await ws.receive(timeout=2)
        assert result.type == WSMsgType.BINARY and result.data == payload
        await ws.close()
        assert not app['pcm_clients']
        for _ in range(50):
            if not capture.queues:
                break
            await asyncio.sleep(0.01)
        assert not capture.queues and not app['pcm_clients']
        ws = await client.ws_connect('/pcm')
        await ws.receive_json()
        queue = next(iter(capture.queues))
        for _ in range(26):
            LoopbackCapture._offer_chunk(queue, b'\0' * 3840)
        assert queue.dropped_chunks == 1
        result = await ws.receive(timeout=2)
        assert result.type == WSMsgType.CLOSE and result.data == 1013
        await ws.close()
    print('PASS: PCM byte equality, metadata, device identity, overflow rejection, cleanup')


asyncio.run(main())
