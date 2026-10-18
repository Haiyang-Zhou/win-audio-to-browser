"""Exercise lifecycle on a separate port, leaving the user's stream alone."""
import socket
from urllib.parse import urlsplit
from floating_control import Bridge, ROOT
from paths import DATA_DIR

original = Bridge().status()
with socket.socket() as probe:
    probe.bind(('127.0.0.1', 0))
    port = probe.getsockname()[1]
pid_file = DATA_DIR / 'test-floating.pid'
bridge = Bridge(port=port, pid_file=pid_file)
try:
    assert not bridge.status()['running']
    state = bridge.start()
    assert state['running'] and state['healthy'], state
    assert state['clients'] == [], 'Live device status endpoint missing'
    pid = bridge.process().pid
    assert bridge.start()['healthy']
    assert bridge.process().pid == pid, 'Duplicate server started'
    assert not bridge.stop()['running']
    with socket.socket() as closed_probe:
        closed_probe.settimeout(1)
        assert closed_probe.connect_ex((urlsplit(state['url']).hostname, port)) != 0, 'Server child still owns the port after stop'
    assert not bridge.stop()['running']
    if original['healthy']:
        assert Bridge().status()['healthy'], 'Original service interrupted'
    print('PASS: start, health check, duplicate prevention, stop, repeated stop; original service untouched')
finally:
    bridge.stop()
