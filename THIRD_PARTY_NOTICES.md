# Third-party notices

## Upstream source

This project is a derivative of:

- Repository: https://github.com/Azec-Zuckerberg/pc-audio-to-iphone
- Copyright: 2026 Azec-Zuckerberg
- License: MIT; original notice preserved in `LICENSE`.

The Windows capture, WebRTC audio bridge and audio timing verification originate
from that project. This derivative adds and restructures the desktop controller,
device naming, browser UI, localization, runtime isolation and source packaging.

## Dependencies

Dependencies in `requirements.txt` are fetched from PyPI, not included in the
source archive. They retain their respective licenses. Consult each installed
distribution and upstream project before redistributing binary builds.
In particular, review Qt/PySide licensing obligations when packaging a desktop
executable. This repository does not supply a prebuilt bundled executable.

## Artwork and trademarks

The audio and pencil icons are drawn by this application's own Qt code; receiver
illustrations are inline SVG/CSS. Documentation images show example device data.
Apple-inspired styling does not imply endorsement by Apple. Platform and browser
names identify compatibility targets and remain their owners' trademarks.
