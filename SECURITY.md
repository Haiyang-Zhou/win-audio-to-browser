# Security

Audio Link is a **trusted-LAN tool**, not an authenticated public streaming service.
Do not expose its port through a router, tunnel, reverse proxy or public hosting.
Peers that can reach the server can request audio and use microphone mode.
Connection/device IDs are self-reported and must not be treated as trusted identity.

HTTPS uses a locally generated self-signed certificate. Verify the server address
yourself before accepting its browser warning. Do not install arbitrary root
certificates or disable browser/firewall protections to use this application.

Keep `data/`, private keys, logs, device aliases and local settings out of Git.
The included ignore rules and source packager exclude them. An ignore rule does
not remove secrets that were already committed; review history before publishing.
The curated initial repository includes no local runtime files or prior upstream
Git history. Dependencies are installed separately and are not vendored here.

The optional firewall script is administrator-only and restricts inbound rules to
the selected adapter, private profiles and the local subnet. Installation does
not run it automatically or create public exposure.

Stop the service during sensitive meetings or whenever streaming is not needed.
Do not enable microphone mode without understanding the destination output device.

For vulnerability reports, avoid public disclosure of exploitable details or logs.
Use the repository owner's private security advisory channel if enabled. This
source template does not claim a security audit or provide a private contact.
