# Security Policy

## Scope
LAN Device Monitor reads the operating system's existing ARP/neighbor cache. It does not perform port scans, packet capture, credential collection, exploitation, or active probing.

## Safe use
Run it only on systems and networks you are authorized to inspect. Snapshot files contain local IP and MAC addresses; treat them as potentially sensitive inventory data and store them appropriately.

## Reporting
Please open a GitHub issue for non-sensitive defects. For security-sensitive reports, use GitHub's private vulnerability reporting feature when enabled rather than publishing exploit details.

## Supported version
Security fixes target the latest release on the default branch.
