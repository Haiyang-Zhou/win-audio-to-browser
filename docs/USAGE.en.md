# Usage guide

[中文教程](USAGE.zh-CN.md) · [Bilingual project overview](../README.md)

## Recommended: Codex-assisted deployment

On the Windows sender, open this repository with Codex and use the English
deployment prompt in the [README](../README.en.md#recommended-deploy-with-codex).
Ask it to inspect prerequisites, install the project dependencies, run tests,
verify the service and report the URL for your receiving devices.
Codex is optional; it is not required for audio streaming after setup.

Review admin/firewall requests yourself and complete browser certificate or
microphone-permission steps where required. Do not disable protection, expose
public ports or overwrite device records merely to simplify deployment.

## Manual installation

The sender requires Windows 10/11 and Python 3.12 with the Windows `py` launcher.
Extract or clone the repository, run `setup.cmd`, then `start.cmd`.
Setup creates a project-local `.venv`. It does not configure startup tasks,
modify firewall rules or expose public ports automatically.

To create a desktop shortcut after installation:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/create_shortcut.ps1
```

## Everyday controls

Use the blue button to start or stop streaming. Yellow minus minimizes the
controller to the taskbar; red close hides it to the tray. Neither stops audio.
The tray menu can quit the controller while keeping the service, or stop both.
Exclusive-fullscreen games may cover the floating window.

The three-dot menu controls language, scaling, corner docking and automatic
naming. Language changes are saved and reach receiver pages in about two seconds,
without recreating the audio connection.

Click the pencil beside the name to edit it. Enter or focus loss saves; Esc
cancels. Clicking the name itself does not edit it. With one identifiable device
connected, an alias is saved for that browser. With no device or several devices,
the edit changes only the window name.

Aliases are stored in `data/device-names.json`; browser language is published in
`data/ui-preferences.json`. Desktop preferences use Qt's Windows user settings.
A browser keeps its random device ID in localStorage. Changing browsers, clearing
site data or using another address/port can create a different identity.

## Receiver setup

Connect your phone, tablet or another computer to the same router as the sender.
Avoid guest networks with client isolation. Open the controller's HTTPS URL in
a modern WebRTC-capable browser. Only after verifying it is your own PC should
you manually handle its self-signed certificate prompt.

Select Listen and start playback. The same primary button disconnects the session.
Regular listening does not require microphone permission. Background and locked-
screen playback depend on the OS/browser; keep the page in the foreground.

The playback-buffer metric measures only the browser buffer, not end-to-end
latency. Bluetooth headphones may add more delay. Start testing with the device's
built-in speakers before tuning anything else.

## No sound or connection

Check the default Windows playback device, player volume and receiver volume.
After changing the PC's default output, stop and restart the service.
Muting Windows can mute the captured stream too. To avoid duplicate sound,
reduce the physical speaker's own volume rather than muting Windows.

Keep the firewall enabled. On a trusted private network, an administrator may
optionally run the following, replacing the adapter name with the actual one:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/configure_firewall.ps1 -InterfaceAlias "Wi-Fi"
```

This limits inbound access to this installation's Python, the selected adapter,
the local subnet and private profiles: TCP 8787 for HTTPS and UDP for WebRTC.
It does not reclassify public networks, change the router or create a tunnel.

## Microphone mode

Disconnect listening first, then select Microphone. HTTPS and explicit browser
microphone permission are required. Audio plays to the PC's output device by
default. Using it as an input for another application requires separately setting
up a virtual audio cable. Avoid speaker/microphone feedback loops.

## Developer commands

```powershell
.venv\Scripts\python.exe app/server.py --host 127.0.0.1 --port 8787
.venv\Scripts\python.exe app/server.py --list-devices
.venv\Scripts\python.exe scripts/verify_audio.py --host 127.0.0.1 --port 8787
.venv\Scripts\python.exe scripts/run_tests.py
```

The first command binds only to the sender itself. Use its actual LAN address
for access from another device. The audio verification script briefly plays a
test tone. `AUDIO_LINK_DATA_DIR` can redirect runtime state to another writable
directory. Never add runtime data or private keys to a public repository.

## Lossless listening

Select Auto (lossless first), Lossless PCM, or Compatible Opus in Listen mode.
Both desktop and browser controls are editable and synchronized. Selection persists on
the PC and applies globally to updated Listen receivers; active listeners briefly reconnect.
Expand Connection details on either end for format and receiver-reported metrics.
Refresh receiver pages after upgrades; tap play again if browser autoplay rules require it.
Auto visibly falls
back to lossy Opus if PCM is unavailable or its bounded buffer overflows. Forced
PCM reports the error instead. PCM carries captured 16-bit mono/stereo at the
capture rate (1.536 Mb/s at 48 kHz stereo), not the untouched original source.
Use HTTPS and an AudioWorklet-capable browser. Actual format and any playback
resampling are shown. Underruns count cumulative playback-buffer starvation events,
not lost network packets. Keep the page foreground; lossless transport does not
guarantee uninterrupted playback or zero latency. Reverse microphone remains Opus.

