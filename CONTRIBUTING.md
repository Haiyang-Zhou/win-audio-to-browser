# Contributing

Use Windows and Python 3.12. Install `requirements.txt` in an isolated environment.
Run `python scripts/run_tests.py` before submitting changes. Hardware tests are
optional and require an enabled WASAPI playback device. Check browser code with
`node --check web/receiver.js` and test responsive layouts in a real browser.

Keep public assets under `web/`, reusable icons under `assets/icons/` and curated
documentation images under `assets/screenshots/`. Put generated output in `data/`
or `dist/`, never the source directories. Do not commit certificates, device IDs,
private aliases, logs, local paths or screenshots containing personal information.

Add desktop and web strings to the relevant language tables; preserve formatting
placeholders across all languages. Do not translate user-provided device names.
Changes must preserve user-gesture playback unlocking, explicit microphone
permission, connection cleanup and language switching without reconnecting audio.

Keep original third-party notices. Do not add public-network exposure or access
control bypasses. Describe tests and compatibility limitations in pull requests.
