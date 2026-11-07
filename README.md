# Hospital IoT Security Homelab & "When the Sensor Lies" Demo

University of Cincinnati Computer Engineering senior capstone by **David G. Moad**, presented at **Queen City Con 0x4 (November 2026)**.

A simulated hospital IoT network running on real hardware, plus a live OT attack demo.

- **Hospital pipeline:** five Raspberry Pi "patient monitors" publish heart-rate data over MQTT → Node-RED → PostgreSQL, Mirth Connect → HAPI FHIR (Observation resources), and Grafana. They're secured with Keycloak SSO, HashiCorp Vault, a Wazuh SIEM, and Suricata IDS → Elasticsearch.
- **Bottle-pressure demo:** two identical pump/valve controllers hold a 1 L bottle at 25 PSI. One trusts pressure readings sent over the network; the other cross-checks them against its own sensor. A spoofed "0 PSI" reading makes the first one over-pressurize and burst its bottle, while the second rejects the reading and logs the attack.

## ⚠️ Intentionally vulnerable code

`balloon-demo/scripts/balloon_control_api*.py` and the "vulnerable" Node-RED flows are **deliberately insecure**: no authentication, no input validation, no rate limiting. They exist to demonstrate the attack. Run them only on an isolated lab network you own. The physical demo involves a high-current pump and pressurized bottles that burst; use eye protection and a kill switch.

## Credentials in this repo

Every password, key, token and account name has been replaced with the placeholder `password` / `username`. Substitute your own when you rebuild the lab.

## Where to start

| Path | What it is |
|---|---|
| `Queen_City_Con/CON_FIELD_GUIDE.md` | Current setup, testing and troubleshooting runbook (Nov 2026) |
| `Queen_City_Con/When the Sensor Lies.pptx` | Conference talk deck |
| `Final_Technical_Report_Rev_9_CLEAN.md` | Full capstone technical report |
| `balloon-demo/` | Demo controller scripts, systemd units, Node-RED flows |
| `hospital scripts/` | Raspberry Pi heart-rate monitor scripts and the ECG dashboard widget |
| `Queen_City_Con/backups/` | Grafana, Mirth and Keycloak configuration exports |
| `NETWORK_*.md`, `SYSTEM_STARTUP_GUIDE.md`, `TROUBLESHOOTING_HISTORY.md` | Build history and network notes (older; the field guide wins where they disagree) |

## License

MIT. See `LICENSE`.
