"""API tests and an optional loopback-only browser preview server."""
import argparse
import asyncio
from pathlib import Path
from string import Formatter
import tempfile
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from server import index, ui_settings, receiver_asset, offer, mic_offer, make_on_startup, on_shutdown
from ui_preferences import save_language, read_language
from ui_languages import LANGUAGES
from web_languages import WEB_MESSAGES, ui_payload
from paths import TEST_OUTPUT_DIR
from pcm_transport import install_pcm_routes
from server import device_kind, status
from connection_settings import install_control_routes

ROOT = Path(__file__).parent
PREVIEW_PREFERENCES = TEST_OUTPUT_DIR / 'test-web-preferences.json'


def make_app(path):
    app = web.Application()
    app['clients'] = {}
    install_pcm_routes(app, device_kind)
    install_control_routes(app)
    app['ui_preferences_path'] = path
    app.router.add_get('/', index)
    app.router.add_get('/ui', ui_settings)
    app.router.add_get('/{asset:receiver\\.(?:css|js)}', receiver_asset)
    return app


async def test_api():
    fields = lambda text: {field for _, field, _, _ in Formatter().parse(text) if field}
    with tempfile.TemporaryDirectory() as directory:
        preferences = Path(directory) / 'settings.json'
        assert read_language(preferences) == 'zh-CN'
        async with TestClient(TestServer(make_app(preferences))) as client:
            for code in LANGUAGES:
                save_language(code, preferences)
                response = await client.get('/ui')
                result = await response.json()
                assert result['language'] == code
                assert result['messages'].keys() == WEB_MESSAGES['en'].keys()
                for key, text in result['messages'].items():
                    assert fields(text) == fields(WEB_MESSAGES['en'][key])
                assert response.headers['Cache-Control'] == 'no-store'
            assert 'Audio Link' in await (await client.get('/')).text()
            headers = {'X-Audio-Link': '1'}
            assert (await client.post('/ui/quality', json={'quality': 'pcm'})).status == 403
            assert (await client.post('/ui/quality', json={'quality': 'pcm'}, headers={**headers, 'Origin': 'https://foreign.invalid'})).status == 403
            assert (await client.post('/ui/quality', json={'quality': 'invalid'}, headers=headers)).status == 400
            for quality in ('pcm', 'opus', 'auto'):
                response = await client.post('/ui/quality', json={'quality': quality}, headers=headers)
                saved = await response.json()
                current = await (await client.get('/ui')).json()
                assert current['quality'] == quality and current['revision'] == saved['revision']
                assert current['language'] == code
            assert 'best-mode' not in await (await client.get('/')).text()
            page = await (await client.get('/')).text()
            assert 'role="radiogroup"' in page and page.count('role="radio"') == 3
            assert '<select' not in page
            app = client.server.app
            app['clients']['peer'] = {'sessionId': 'known', 'transport': 'opus'}
            response = await client.post('/diagnostics', json={'sessionId': 'known', 'bufferMs': 35, 'packets': 0}, headers=headers)
            assert response.status == 204 and app['clients']['peer']['bufferMs'] == 35
            assert (await client.post('/diagnostics', json={'sessionId': 'other', 'bufferMs': 35}, headers=headers)).status == 404
            for file in ('receiver.css', 'receiver.js', 'pcm-worklet.js'):
                response = await client.get('/' + file)
                assert response.status == 200, (file, response.status)
                assert 'no-cache' == response.headers['Cache-Control']
            for private in ('/server.py', '/ui-preferences.json', '/.mic-key.pem'):
                assert (await client.get(private)).status == 404
        print('PASS: 9 browser translations, language updates without restart, assets, cache rules, private-file isolation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--set-language')
    args = parser.parse_args()
    if args.set_language:
        save_language(args.set_language, PREVIEW_PREFERENCES)
    elif args.preview:
        save_language('zh-CN', PREVIEW_PREFERENCES)
        app = make_app(PREVIEW_PREFERENCES)
        app['pcs'] = set()
        app.router.add_get('/status', status)
        app.router.add_post('/offer', offer)
        app.router.add_post('/mic-offer', mic_offer)
        app.on_startup.append(make_on_startup(None, None))
        app.on_shutdown.append(on_shutdown)
        web.run_app(app, host='127.0.0.1', port=8878)
    else:
        asyncio.run(test_api())
