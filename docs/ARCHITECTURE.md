# Architecture

## Audio and signaling

Windows WASAPI loopback is captured by PyAudioWPatch. A depth-one queue feeds
aiortc, which encodes Opus and sends audio over WebRTC. Surround endpoints are
opened natively and reduced to stereo. The browser handles playback and jitter
buffering. Reverse microphone audio is explicitly activated by the user.

`app/server.py` serves only the receiver HTML, allowlisted assets, UI
translations, connection summaries and WebRTC offer endpoints. The project root,
runtime files and certificates are never mounted as a static directory.
The desktop starts the server on its selected LAN interface, not all interfaces.
The standalone CLI defaults to loopback binding.

`app/pcm_transport.py` adds `/pcm` (WebSocket, no compression) and the explicit
`/pcm-worklet.js` asset. A versioned JSON format message precedes binary s16le
blocks. TCP/WebSocket preserves byte order and contents. The endpoint rejects a
foreign browser Origin (device identifiers are still not authentication). Each subscriber
has a 25-block capture queue; a dropped block terminates PCM instead of hiding
the loss. Sends time out after one second. Disconnect and server shutdown close
the socket and unsubscribe capture, including idle/silent streams.

The AudioWorklet converts s16le to exact float sample values, buffers initially
80 ms and caps its ring at 500 ms. Equal-rate playback preserves sample values;
different rates use linear interpolation and display the output rate explicitly.
There is no drift compensation or guarantee of uninterrupted long sessions:
underruns are counted, overflow fails rather than silently discarding samples.
Auto can then use Opus with a visible downgrade notice; forced PCM cannot.
WASAPI capture is 16-bit, at most stereo after downmix, not original bit-perfect
audio. Reverse microphone transport remains WebRTC/Opus.

`audio_modes.py` shares translated mode labels and capture format metadata.
`/status` reports negotiated formats and receiver-ready acknowledgements. Both UIs have
editable quality selectors and collapsed connection diagnostics, without maximum-quality
banners. PCM reports stats over its WebSocket; Opus receivers post bounded telemetry to
`/diagnostics`, using the per-connection ID returned in `X-Audio-Session`. These IDs are
not authentication. Desktop hides metrics older than ten seconds rather than implying
they are live. It summarizes mixed transports without treating every receiver as lossless.

## Desktop and language synchronization

`app/floating_control.py` uses Qt (PySide6 Essentials).
`app/quality_control.py` provides an exclusive, keyboard-operable segmented selector
with localized compact labels, full accessible names and a subtle animated selection
pill. The receiver uses the same labels and an ARIA radio group; reduced-motion CSS
disables its slide animation. Both retain the shared preference and reconnect logic.
Potentially blocking work runs off the GUI thread. A local socket avoids duplicate controller windows.
The service has an independent lifetime so minimizing or closing the window
does not interrupt audio. PID operations verify the target server command.

The desktop publishes language and transport preferences atomically to
`data/ui-preferences.json`. A process lock protects read-modify-write updates and
monotonic revisions prevent stale browser responses from reverting newer selections.
`GET /ui` reads settings; `POST /ui/quality` updates only the transport. Writes require
a same-origin custom-header JSON request, with foreign Origins rejected. Receivers
poll every two seconds; language changes keep their peer, transport changes reconnect
Listen sessions automatically. Microphone sessions remain Opus and are not restarted.
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
