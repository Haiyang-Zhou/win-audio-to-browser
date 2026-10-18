"""Same-origin controls and bounded, receiver-reported diagnostics on the LAN."""
import math
from aiohttp import web
from ui_preferences import save_quality


async def control_json(request):
    if request.headers.get('Origin') not in (None, f'{request.scheme}://{request.host}'):
        raise web.HTTPForbidden()
    if request.headers.get('X-Audio-Link') != '1' or request.content_type != 'application/json':
        raise web.HTTPForbidden()
    body = await request.read()
    if len(body) > 2048:
        raise web.HTTPRequestEntityTooLarge(max_size=2048, actual_size=len(body))
    try:
        import json
        data = json.loads(body)
        if not isinstance(data, dict):
            raise ValueError()
        return data
    except (ValueError, UnicodeError):
        raise web.HTTPBadRequest(text='Invalid JSON')


async def quality_settings(request):
    data = await control_json(request)
    try:
        result = save_quality(data.get('quality'), request.app.get('ui_preferences_path'))
    except ValueError:
        raise web.HTTPBadRequest(text='Unsupported transport')
    return web.json_response(result, headers={'Cache-Control': 'no-store'})


def apply_diagnostics(info, data):
    for key, maximum in (('bufferMs', 10000), ('underruns', 1000000000), ('packets', 1000000)):
        value = data.get(key)
        if isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= maximum:
            info[key] = round(value, 2)
    import time
    info['statsAt'] = time.time()


async def diagnostics(request):
    data = await control_json(request)
    for info in request.app.get('clients', {}).values():
        if info.get('sessionId') and info['sessionId'] == data.get('sessionId'):
            apply_diagnostics(info, data)
            return web.Response(status=204)
    raise web.HTTPNotFound()


def install_control_routes(app):
    app.router.add_post('/ui/quality', quality_settings)
    app.router.add_post('/diagnostics', diagnostics)
