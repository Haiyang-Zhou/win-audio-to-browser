"""Reliable, uncompressed s16le capture transport, separate from Opus signaling."""
import asyncio
import sys
import json
from aiohttp import web
from device_names import valid_id
from paths import WEB_DIR
from connection_settings import apply_diagnostics


async def pcm_socket(request):
    origin = request.headers.get('Origin')
    if origin and origin != f'{request.scheme}://{request.host}':
        raise web.HTTPForbidden(text='Cross-origin PCM connections are not allowed')
    capture = request.app['capture']
    if sys.byteorder != 'little':
        raise web.HTTPServiceUnavailable(text='PCM capture requires little-endian samples')
    ws = web.WebSocketResponse(heartbeat=10, max_msg_size=1024, compress=False)
    await ws.prepare(request)
    clients = request.app['pcm_clients']
    clients[ws] = {
        'kind': request.app['pcm_device_kind'](request.query, request.headers.get('User-Agent', '')),
        'mode': 'listen', 'id': valid_id(request.query.get('deviceId')), 'transport': 'pcm',
        'bits': 16, 'sampleRate': capture.rate, 'channels': capture.channels, 'ready': False,
    }
    queue = capture.subscribe(maxsize=25)
    reader = asyncio.create_task(_read_until_closed(ws, clients[ws]))
    pending = None
    try:
        await ws.send_json({'type': 'format', 'version': 1, 'codec': 'pcm_s16le',
                            'sampleRate': capture.rate, 'channels': capture.channels,
                            'bits': 16, 'framesPerChunk': capture.samples_per_chunk})
        while not ws.closed:
            pending = asyncio.create_task(queue.get())
            done, _ = await asyncio.wait((pending, reader), return_when=asyncio.FIRST_COMPLETED)
            if reader in done:
                break
            chunk = pending.result()
            pending = None
            # Never hide capture queue loss behind a "lossless" connection.
            if getattr(queue, 'dropped_chunks', 0):
                await ws.close(code=1013, message=b'PCM capture queue overflow')
                break
            await asyncio.wait_for(ws.send_bytes(chunk), timeout=1)
    except (TimeoutError, ConnectionError, RuntimeError):
        await ws.close(code=1013, message=b'PCM network stalled')
    finally:
        capture.unsubscribe(queue)
        clients.pop(ws, None)
        tasks = [reader] + ([pending] if pending is not None else [])
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    return ws


async def _read_until_closed(ws, info):
    async for message in ws:
        if message.type != web.WSMsgType.TEXT:
            continue
        try:
            data = json.loads(message.data)
            rate = data.get('outputSampleRate') if isinstance(data, dict) else None
            if data.get('type') == 'ready' and isinstance(rate, int) and 8000 <= rate <= 192000:
                info.update(ready=True, outputSampleRate=rate)
            if data.get('type') == 'stats':
                apply_diagnostics(info, data)
        except (ValueError, AttributeError):
            continue


async def worklet_asset(request):
    return web.FileResponse(WEB_DIR / 'pcm-worklet.js', headers={'Cache-Control': 'no-cache'})


async def close_pcm(app):
    await asyncio.gather(*(ws.close(code=1001, message=b'Server stopped')
                           for ws in list(app['pcm_clients'])), return_exceptions=True)


def install_pcm_routes(app, device_kind):
    app['pcm_clients'] = {}
    app['pcm_device_kind'] = device_kind
    app.router.add_get('/pcm', pcm_socket)
    app.router.add_get('/pcm-worklet.js', worklet_asset)
    app.on_shutdown.insert(0, close_pcm)
