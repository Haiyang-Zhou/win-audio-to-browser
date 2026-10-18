# Changelog

## 2.0.0 - 2026-10-18

Versioned open-source source release. See [bilingual V2 notes](docs/RELEASE-v2.md).

- Apple-inspired segmented quality controls on desktop and browser, with animated white selection pills.
- Compact translated labels, full accessible names/tooltips and keyboard navigation, preserving shared mode synchronization.

- Editable desktop/browser transport selectors with shared persistent state (default Auto).
- Bidirectional synchronization and active Listen reconnection on manual mode changes.
- Collapsed desktop connection diagnostics with bounded, freshness-checked receiver metrics.
- Removed maximum-quality banners from both UIs; moved technical format information into details.

- Windows venv launcher child detection so stopping a service releases its listening port.

- Live current-mode browser badges and desktop negotiated-mode summaries.
- Mixed-device detail tooltips, PCM receiver readiness acknowledgement and capture capabilities.
- Unknown/idle/negotiating modes are distinct from active lossless transport.

- Uncompressed s16le WebSocket listening with bounded AudioWorklet playback.
- Remembered Auto / PCM / Opus selection, visible downgrade reasons and format.
- Nine-language quality controls and cumulative PCM underrun diagnostics.
- PCM byte-integrity, lifecycle, overflow and mono/stereo worklet sample tests.

- Curated standalone Audio Link source layout, with upstream MIT attribution.
- Desktop controller with tray/taskbar controls, scaling and docking.
- Pencil-only inline editing and per-browser remembered device names.
- Nine languages shared by desktop controls and responsive receiver UI.
- Read-only language synchronization while WebRTC audio remains connected.
- Local runtime isolation, private-file exclusions, tests and source packaging.
- Removed legacy receiver page, duplicate launch scripts and transient previews
  from the distributable source set.
