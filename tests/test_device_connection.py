"""Real local WebRTC connection and persisted alias, on an isolated test port."""
import asyncio
from pathlib import Path
import socket
import ssl
import tempfile
import aiohttp
from aiortc import RTCConfiguration, RTCPeerConnection, RTCSessionDescription
from device_names import DeviceNames
from floating_control import Bridge, ROOT


async def connect(bridge, identifier):
    state = bridge.status()
    peer = RTCPeerConnection(RTCConfiguration(iceServers=[]))
    peer.addTransceiver('audio', direction='recvonly')
    await peer.setLocalDescription(await peer.createOffer())
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(state['url'] + '/offer', json={
                'sdp': peer.localDescription.sdp, 'type': peer.localDescription.type,
                'deviceKind': 'iPad', 'deviceId': identifier,
            }, ssl=ssl._create_unverified_context()) as response:
                response.raise_for_status()
                answer = await response.json()
        await peer.setRemoteDescription(RTCSessionDescription(**answer))
        for _ in range(40):
            await asyncio.sleep(.1)
            result = await asyncio.to_thread(bridge.status)
            if result.get('clients'):
                return result['clients'][0]
        raise AssertionError('No connected client reported')
    finally:
        await peer.close()


with tempfile.TemporaryDirectory() as directory:
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    names = DeviceNames(Path(directory) / 'aliases.json')
    bridge = Bridge(port=port, pid_file=Path(directory) / 'bridge.pid', names=names)
    try:
        bridge.start()
        identifier = 'c' * 32
        first = asyncio.run(connect(bridge, identifier))
        assert first['id'] == identifier and first['kind'] == 'iPad'
        names.remember(identifier, 'iPad', '记住的平板')
        remembered = asyncio.run(connect(bridge, identifier))
        assert remembered['name'] == '记住的平板'
        other = asyncio.run(connect(bridge, 'd' * 32))
        assert other['name'] == '', 'Different browser must not inherit the alias'
        print('PASS: real WebRTC device ID, reconnect restores alias, other browser stays separate')
    finally:
        bridge.stop()
