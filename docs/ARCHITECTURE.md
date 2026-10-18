# Architecture

## Audio and signaling

Windows WASAPI loopback is captured by PyAudioWPatch. A depth-one queue feeds
aiortc, which encodes Opus and sends audio over WebRTC. Surround endpoints are
opened natively and reduced to stereo. The browser handles playback and jitter
buffering. Reverse microphone audio is explicitly activated by the user.

`app/server.py` serves only the receiver HTML, two allowlisted assets, UI
translations, connection summaries and WebRTC offer endpoints. The project root,
runtime files and certificates are never mounted as a static directory.
The desktop starts the server on its selected LAN interface, not all interfaces.
The standalone CLI defaults to loopback binding.

## Desktop and language synchronization

`app/floating_control.py` uses Qt (PySide6 Essentials). Potentially blocking work
runs off the GUI thread. A local socket avoids duplicate controller windows.
The service has an independent lifetime so minimizing or closing the window
does not interrupt audio. PID operations verify the target server command.

The desktop publishes language changes atomically to `data/ui-preferences.json`.
The read-only `/ui` endpoint reads that file, allowing updates without restarting
the server. Receivers poll every two seconds without replacing their peer.
Translations live in `app/ui_languages.py` and `app/web_languages.py`.

## Device names

Receivers generate a random 128-bit identifier and keep it in localStorage.
The desktop associates an alias with that ID in `data/device-names.json`.
Names are not based on IP addresses or private OS device names. LocalStorage is
origin-specific: changing hostname, address, port or browser can create a new ID.
These IDs are convenience labels, not authentication.

## Repository layout

`app/` contains Python source, `web/` contains public browser resources,
`assets/` contains distributable icons/screenshots, and `data/` is ignored runtime
state. Tests use a temporary `AUDIO_LINK_DATA_DIR`. Packaging uses an allowlist;
only curated source/resource directories and root documentation are included.
