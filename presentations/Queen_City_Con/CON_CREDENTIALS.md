# Queen City Con — Credentials (SENSITIVE)

> Keep this off the projector and off the table. Print one copy for your pocket, and keep a PDF on your phone.
> Copied from `CONFERENCE_REFRESHER.md` §3 on 2026-11-06. Re-verify every line during the at-home rehearsal (field guide 1D).

**Default password almost everywhere:** `password`

## SSH (all use the default password unless keys are installed)
| Host | Login |
|---|---|
| Pis #1–#5 | `username@10.30.0.20` … `username@10.30.0.24` (hyphens) |
| Secure Pi | `username@10.30.0.25` |
| Vulnerable Pi | `username@192.168.50.100` |
| Suricata laptop | `username@192.168.50.191` |
| TrueNAS | `username@10.30.0.44` |
| PostgreSQL | `username@10.30.0.50` |
| MQTT | `username@10.30.0.51` |
| Node-RED | `username@10.30.0.52` |
| Grafana | `username@10.30.0.53` |
| Mirth | `username@10.30.0.54` |
| Wazuh | `username@10.30.0.55` |
| HAPI FHIR | `username@10.30.0.56` (from VLAN 30 only; else `ssh -J username@10.30.0.55 username@10.30.0.56`) |
| Keycloak | `username@10.30.0.57` |
| Vault | `username@10.30.0.58` |
| Elasticsearch | `username@10.30.0.60` |

## Web UIs
| Service | URL | Login |
|---|---|---|
| UDM-SE | https://10.30.0.1 | `username` / `password` (**with `!`**) |
| TrueNAS | http://10.30.0.44 | `username` / `password` |
| Node-RED | http://10.30.0.52:1880 (`/ui`) | Keycloak SSO: `username` or `username` / `password` |
| Grafana | http://10.30.0.53:3000 | Local `admin` / `password` (needed to edit; SSO is Viewer only) |
| Mirth | https://10.30.0.54:8443 | `admin` / `password` |
| Wazuh | https://10.30.0.55 | `admin` / `password` (SSO broken) |
| HAPI FHIR | http://10.30.0.56:4180/fhir/ | SSO (`username` / `username`) |
| Keycloak admin | http://10.30.0.57:8080 | `admin` / `password` |
| Vault | http://10.30.0.58:8200 | Method "Token": `password` |
| Elasticsearch | https://10.30.0.60:9200 | `elastic` / `password` (API only) |

## Service accounts
- MQTT: `username` / `password` (10.30.0.51:1883)
- PostgreSQL app: `nodered` / `password`, database `hospital_data`, `sslmode=require`

## Vault unseal (any 3 of 5, after every reboot)
1. `password`
2. `password`
3. `password`
4. `password`
5. `password`

Root token: `password`
