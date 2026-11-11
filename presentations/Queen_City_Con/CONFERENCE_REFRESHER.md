# Project Refresher: Queen City Con 0x4 (Nov 13–15, 2026)

**Compiled:** 2026-10-28, from `CLAUDE.md`, `QUICK_STARTUP_PROCEDURE.md`, `SYSTEM_STARTUP_GUIDE.md`, `QUEEN_CITY_CON_HARDWARE_LIST.md`, the service unit files and `attack_spoof.py`.
**Last verified on real hardware:** 2026-03-24, so everything below is about 7 months old. Run a full cold-boot test before the conference.

> **For the venue, use `CON_FIELD_GUIDE.md` (runbook) and `CON_CREDENTIALS.md` (logins).** This file is the deep reference and change log behind them.

> ⚠️ This file contains every credential in plain text. Don't commit it, print it where it can be seen, or project it.

---

## 1. What the project is (30-second version)

A simulated **hospital IoT network** on real hardware, plus a **live attack demo**.

1. **Hospital homelab:** 5 Raspberry Pis with Sense HATs act as heart-rate monitors and publish over MQTT. From there the data goes to Node-RED (live dashboard + ECG waveforms), PostgreSQL (storage), Mirth Connect (HL7/FHIR interface engine), HAPI FHIR (Observation resources) and Grafana (historical dashboards). Security stack: Keycloak SSO, Vault secrets, Wazuh SIEM, Suricata IDS → Elasticsearch → Grafana.
2. **"Balloon" demo** (really a **1 L plastic bottle**): two identical pump/solenoid pressure systems held at **25 PSI**.
   - **Vulnerable Pi** trusts pressure readings POSTed to an unauthenticated HTTP `/sensor` endpoint.
   - **Secure Pi** cross-checks network readings against its own I2C sensor and rejects mismatches.
   - The attacker (Suricata laptop) floods both with fake `0.0 PSI`. The vulnerable pump keeps running until the bottle bursts (burst range 39–71 PSI, mean 59.6). The secure system rejects the fake data and stays at 25 PSI.
   - Suricata sees the attack, Grafana's IDS dashboard shows it, and Wazuh logs the secure Pi's rejections.

---

## ⚠️ Changes made 2026-10-28/29 (supersede the older docs)

- **Switch management IP is now `192.168.0.130`** (Default network `192.168.0.0/24`, DHCP). It is **no longer `10.30.0.10`**, so the older docs listing `.10` are out of date.
- **Uplink config (both ends must match):** UDM-SE Port 11 = Native **Default**, Tagged **Allow All**. Switch Port 26 = Native **Default**, Tagged **Allow All**. If the native networks don't match, the switch adopts fine but VLAN 30/VLAN 2 traffic from the Pis never crosses the uplink.
- **Never give the switch a static IP** unless it matches the network its management actually sits on. A mismatched static IP stranded it twice (the old `192.168.1.20`, and then `10.30.0.10`).
- **Switch was factory-reset and re-adopted,** and the port settings were redone. The new port table was never written down; fill it in at `CON_FIELD_GUIDE.md` §1B.
- **Hospital Pis had a duplicate systemd *user* service** running the same script, which caused the MQTT client-ID clash (connect/disconnect every second). It's disabled on Pis 1–4. Pi #5 checked 2026-11-01: no duplicate.
- **Pi clocks boot at their last saved time** (they have no RTC) and need NTP. With no internet at the venue they'll be wrong. **Local NTP (2026-10-29):** chrony on the MQTT VM (10.30.0.51) serves time (`local stratum 10`, allows 10.30.0.0/24 and 192.168.50.0/24, config in `/etc/chrony/conf.d/lab-server.conf`). Pis 1–4 point to it via `/etc/systemd/timesyncd.conf.d/lab.conf` (`NTP=10.30.0.51`). **Still to do:** the same timesyncd file on Pi #5, Secure Pi, Vulnerable Pi and the Suricata laptop, plus UDP 123 added to the Vulnerable Pi → 10.30.0.51 firewall exception.
- **Keycloak** failed at boot because PostgreSQL wasn't up yet (same as March). A systemd drop-in now sets `Restart=on-failure`, `RestartSec=30` and `StartLimitIntervalSec=0`, so it retries until PostgreSQL is ready.
- **VM disks (2026-10-31):** Ubuntu's installer only allocated half of each VM's volume group. The Wazuh disk hit 100% (see `TROUBLESHOOTING_HISTORY.md`). Wazuh, Node-RED, MQTT and HAPI were grown with `sudo lvextend -r -l +100%FREE /dev/ubuntu-vg/ubuntu-lv`. Grafana, Mirth, Keycloak, Vault and Elasticsearch still have half their disk unallocated (all under 40% used). HAPI only allows SSH from 10.30.0.0/24, so from outside the lab use `ssh -J username@10.30.0.55 username@10.30.0.56`.
- **Temporary access from the main PC (192.168.1.200):** routes to 10.30.0.0/24, 192.168.0.0/24 and 192.168.50.0/24 go via the UDM-SE WAN (192.168.1.24), plus the UniFi rule `TEMP - laptop to lab`. **Disable that rule before the conference.**
- SSH from the main lab computer uses **key auth** (no password prompt). The username format is `r-pi-N` (hyphens).
- Pi #5, Secure Pi, Vulnerable Pi and Suricata laptop all done 2026-11-01 (VLAN2 devices use the ALLOW_VLAN2_TO_NTP rule, UDP 123 to 10.30.0.51).

---

## 2. Network & IP map

| VLAN | Subnet | Purpose |
|---|---|---|
| VLAN 30 | 10.30.0.0/24 | Secure hospital infrastructure |
| VLAN 2 | 192.168.50.0/24 | Vulnerable attack lab |

### Infrastructure
| Device | IP | Notes |
|---|---|---|
| UDM-SE gateway | 10.30.0.1 | Web UI, firewall rules |
| TrueNAS server (Dell PowerEdge) | 10.30.0.44 | Hosts all VMs |
| iDRAC 9 | 10.30.0.45 | Out-of-band server management |
| WiFi AP (U6 Pro) | 10.30.0.246 | |

### VMs (all on TrueNAS, auto-start)
| VM | IP | Port(s) |
|---|---|---|
| PostgreSQL 16 | 10.30.0.50 | 5432 (SSL required) |
| MQTT (Mosquitto) | 10.30.0.51 | 1883 (auth, plaintext) |
| Node-RED | 10.30.0.52 | 1880, dashboard at `/ui` |
| Grafana | 10.30.0.53 | 3000 (**shows UTC**: 5 hours ahead of EST) |
| Mirth Connect | 10.30.0.54 | 8443 admin, channel `HeartRate_FHIR_Final` listens on 8081 |
| Wazuh SIEM | 10.30.0.55 | 443 (14 agents) |
| HAPI FHIR (Docker) | 10.30.0.56 | 8080 (Mirth only), OAuth2 Proxy 4180 |
| Keycloak | 10.30.0.57 | 8080, realm `hospital-homelab` |
| Vault | 10.30.0.58 | 8200 |
| ~~Suricata VM~~ | ~~10.30.0.59~~ | Deprecated, replaced by the laptop |
| Elasticsearch | 10.30.0.60 | 9200 (TLS) |

### Raspberry Pis
| Device | IP | Role |
|---|---|---|
| Pi #1 | 10.30.0.20 | 72 BPM ±2.5 |
| Pi #2 | 10.30.0.21 | 68 BPM ±3.5 (most variable) |
| Pi #3 | 10.30.0.22 | 75 BPM ±2 (most stable) |
| Pi #4 | 10.30.0.23 | AFib, irregular 70–150 BPM (fires the Grafana tachycardia alert) |
| Pi #5 | 10.30.0.24 | 70 BPM, rare anomaly about every 5.5 hours |
| Secure Pi (`balloon-secure`, formerly Pi #6) | 10.30.0.25 | VLAN 30 |
| Vulnerable Pi (`balloon-vulnerable`, formerly Pi #7) | 192.168.50.100 | VLAN 2 |
| Suricata/attacker laptop | 192.168.50.191 | VLAN 2. Switch port 6 = management, port 7 = mirror of port 15 (no IP) |

**Suricata laptop USB-Ethernet dongles (verified 2026-11-01).** Each Linux name comes from that dongle's MAC, so the name follows the dongle, not the USB port:
- `enx00051b5153e0` (MAC …53:e0) → **switch port 6, management**, 192.168.50.191
- `enx00051b514370` (MAC …43:70) → **switch port 7, mirror**, no IP. This is the interface Suricata listens on (`af-packet` in `/etc/suricata/suricata.yaml`).
- If the cables are swapped, Suricata watches the management link instead of the mirror. Check with `ip -br addr | grep enx`: the dongle with the IP must be …53e0.
- Suricata and Filebeat are held with `apt-mark hold` so Filebeat stays matched to Elasticsearch 8.19. Wi-Fi is off (`sudo nmcli radio wifi off`). timesyncd points at 10.30.0.51. Filebeat verifies the Elasticsearch cert (`ssl.verification_mode: full`, CA copied from the ES VM `/etc/elasticsearch/certs/http_ca.crt` to `/etc/filebeat/es-http-ca.crt`; cert valid to 2028-02, CA to 2029-02).

Pis 1–4 are powered by PoE from the switch. Pi #5, the Secure Pi and the Vulnerable Pi need **USB-C power adapters**.

### Required cross-VLAN firewall exceptions (UDM-SE)
Both need a priority number **below 20001** so they're evaluated before `BLOCK_VLAN2_TO_VLAN30`:
- `ALLOW_VULNERABLE_PI_TO_MQTT`, priority 19998: 192.168.50.100 → 10.30.0.51 TCP 1883
- `ALLOW_SURICATA_TO_ELASTICSEARCH`, priority 19999: 192.168.50.191 → 10.30.0.60 TCP 9200

If they don't seem to be loaded, check on the UDM-SE with `iptables -L FORWARD -n -v | grep <source-ip>`. Reload with `iptables-restore < /etc/iptables/rules.v4`.

---

## 3. Credentials

**Default password almost everywhere:** `password`

### SSH
| Host | Command |
|---|---|
| TrueNAS | `ssh username@10.30.0.44` |
| PostgreSQL | `ssh username@10.30.0.50` |
| MQTT | `ssh username@10.30.0.51` |
| Node-RED | `ssh username@10.30.0.52` |
| Grafana | `ssh username@10.30.0.53` |
| Mirth | `ssh username@10.30.0.54` |
| Wazuh | `ssh username@10.30.0.55` |
| HAPI FHIR | `ssh username@10.30.0.56` |
| Keycloak | `ssh username@10.30.0.57` |
| Vault | `ssh username@10.30.0.58` |
| Elasticsearch | `ssh username@10.30.0.60` |
| Hospital Pis | `ssh r-pi-N@10.30.0.(19+N)`, e.g. `username@10.30.0.20` … `username@10.30.0.24` |
| Secure Pi | `ssh username@10.30.0.25` |
| Vulnerable Pi | `ssh username@192.168.50.100` |
| Suricata laptop | `ssh username@192.168.50.191` |

All of the above use `password`.

### Web UIs
| Service | URL | Login |
|---|---|---|
| UDM-SE | https://10.30.0.1 | `username` / `password` (**note the `!`**) |
| TrueNAS | http://10.30.0.44 | `username` / `password` |
| Node-RED | http://10.30.0.52:1880 (`/ui` for dashboard) | Keycloak SSO: `username` or `username` / `password` |
| Grafana | http://10.30.0.53:3000 | `admin` / `password`, or SSO |
| Mirth Connect | https://10.30.0.54:8443 | `admin` / `password` |
| Wazuh | https://10.30.0.55 | `admin` / `password` (**SSO broken, use this**) |
| HAPI FHIR | http://10.30.0.56:4180/fhir/ | SSO (`username`/`username`) |
| Keycloak admin | http://10.30.0.57:8080 | `admin` / `password` |
| Vault | http://10.30.0.58:8200 | Method "Token": `password` (OIDC login works but has limited permissions) |
| Elasticsearch | https://10.30.0.60:9200 | `elastic` / `password` (API only) |

### Service credentials
- **MQTT:** `username` / `password` on 10.30.0.51:1883 (anonymous access disabled)
- **PostgreSQL app user:** `nodered` / `password`, database `hospital_data`, `sslmode=require`

### Vault unseal keys (any 3 of 5)
1. `password`
2. `password`
3. `password`
4. `password`
5. `password`

Root token: `password`

---

## 4. Startup sequence (cold boot, about 30 minutes)

### Step 0: Mock WAN (required at the venue, where there's no internet)
The UDM-SE only routes between VLANs when its **WAN port has a link**. Without one, VLAN 2 ↔ VLAN 30 traffic fails: the Vulnerable Pi can't reach MQTT and Suricata can't reach Elasticsearch.
**Decided method: standalone dumb switch.** Plug a short Ethernet cable from the **UDM-SE WAN port** into the dumb switch. Power the dumb switch and plug nothing else into it. Wait 30 seconds and check that the WAN port shows a link in UniFi. Don't use a port on the main switch: the WAN port can pick up an address from the UDM-SE's own network and cause routing problems.

Also connect the **SFP+ DAC cable** between the UDM-SE and the switch. That's the backbone, and nothing works without it.

### Step 1: Power on, in this order
1. **UDM-SE.** Wait 2–3 minutes.
2. **UniFi switch** (Pro Max 24 PoE). Wait 1 minute. Pis 1–4 power on via PoE.
3. **TrueNAS / Dell server** (power button). The VMs auto-start.
4. Plug in USB-C power for **Pi #5, the Secure Pi and the Vulnerable Pi**.
5. Boot the **Suricata laptop**.

### Step 2: Wait about 15 minutes for the VMs
Boot order: PostgreSQL → MQTT → Keycloak → Elasticsearch → everything else.
```bash
for ip in 50 51 52 53 55 57 58 60; do ping -n 1 10.30.0.$ip; done   # Windows ping syntax
```

### Step 3: Unseal Vault (needed after every reboot)
**Browser:** go to http://10.30.0.58:8200 and paste unseal keys 1, 2 and 3, clicking **Unseal** after each.
**CLI** (on the Vault VM):
```bash
ssh username@10.30.0.58
export VAULT_ADDR='http://localhost:8200'
vault operator unseal password
vault operator unseal password
vault operator unseal password
vault status   # Sealed: false
```

### Step 4: Restart the Pi services (needed: they don't auto-start reliably)
```bash
ssh username@10.30.0.20 "sudo systemctl restart heartrate1.service"
ssh username@10.30.0.21 "sudo systemctl restart heartrate2.service"
ssh username@10.30.0.22 "sudo systemctl restart heartrate3.service"
ssh username@10.30.0.23 "sudo systemctl restart heartrate4.service"
ssh username@10.30.0.24 "sudo systemctl restart heartrate5.service"

# Secure Pi: one service
ssh username@10.30.0.25 "sudo systemctl restart balloon-control-secure.service"

# Vulnerable Pi: TWO services (sensor publisher + control API)
ssh username@192.168.50.100 "sudo systemctl restart balloon-sensor-publisher.service"
ssh username@192.168.50.100 "sudo systemctl restart balloon-control-api.service"

# IDS log shipping
ssh username@192.168.50.191 "sudo systemctl restart filebeat"
```
Note: `SYSTEM_STARTUP_GUIDE.md` says the Secure Pi runs `balloon-control-api.service`. That's out of date. The repo's unit file is `balloon-control-secure.service`, which is also what `QUICK_STARTUP_PROCEDURE.md` uses.

### Step 5: Verify
1. **Node-RED** at http://10.30.0.52:1880/ui should show 5 HR gauges, 5 scrolling ECG traces (Pi #4's is irregular and turns red while above 110 BPM; threshold is `TACHY_BPM` in the template), 4 pressure gauges, and the Security Status panel in green ("SYSTEM SECURE").
   - The ECG tiles were replaced on 2026-11-01 with a canvas sweep monitor (dashboard `template` node, code in `hospital scripts/ecg_sweep_template.html`, the same code for all 5). It's wired from the **switch** outputs, because it needs the full payload (`bpm`, `pi_id`, `anomaly_type`). The waveform is synthetic but driven by live BPM. It flatlines with "--" if a Pi sends nothing for 3 s.
   - The old "Generate ECG" functions sat after `set msg payload` (which reduces the payload to just the number), so they never saw the BPM and drew every Pi at a fixed 70.
   - P1 History's chart had been set to UTC and a 2-day window. It was fixed on 2026-11-01 to match the other charts.
2. **Grafana** at http://10.30.0.53:3000 should show all 5 Pis, the Pi #4 BPM tile turning red above 110 and reading "TACHYCARDIA" above 120 (matches the Node-RED ECG tiles), and an IDS dashboard ready to go.
   - The "BPM > 120" tile (changed 2026-11-01) is a Stat panel that reads Pi #4's newest reading on every 5 s dashboard refresh. It replaced an Alert List panel, which only changed when the 60 s alert rule did. Its query uses `localtimestamp - interval '30 seconds'` because timestamps are stored as naive local time, which doesn't match Grafana's UTC time picker. "No data" means Pi #4 hasn't sent anything for 30 s.
   - Editing dashboards needs the **local** `admin` login. `username` via Keycloak SSO is only a Viewer.
   - The alert rule "Tachycardia Alert - BPM > 100" (threshold is actually 120) still evaluates every 60 s on a single reading, and its contact point goes to a nonexistent Alertmanager at localhost:9093, so it only appears on the Alerting page.
3. **Wazuh** at https://10.30.0.55 should show 14 agents as Active.
4. **MQTT firehose** (on the MQTT VM or anywhere `mosquitto-clients` is installed):
   ```bash
   mosquitto_sub -h 10.30.0.51 -u username -P password -t '#' -v
   ```
   Expect `hospital/heartrate/pi-1..5`, `balloon/vulnerable/pressure|relays|sensor_source` and `balloon/secure/status`.
5. **PostgreSQL ingestion:**
   ```bash
   ssh username@10.30.0.50
   sudo -u postgres psql -d hospital_data -c "SELECT pi_id, MAX(timestamp) FROM heartrate_data GROUP BY pi_id ORDER BY pi_id;"
   ```
6. **Mirth:** channel `HeartRate_FHIR_Final` should be Started, with Received and Sent counters climbing.
7. **Elasticsearch from the laptop:**
   ```bash
   curl -k -u elastic:password https://10.30.0.60:9200/_cluster/health?pretty   # yellow is normal
   ```

---

## 5. Data pipelines

```
HOSPITAL
Pi SenseHAT → MQTT 10.30.0.51 → Node-RED 10.30.0.52
     ├→ PostgreSQL hospital_data.heartrate_data (7-day active, pg_cron archives daily at 2 AM UTC)
     ├→ Mirth :8081 (rate-limited to 1/sec) → HAPI FHIR Observation (LOINC 8867-4)
     ├→ Node-RED dashboard (real time) + ECG waveform generator
     └→ Grafana (historical, 30 s refresh)

BALLOON / BOTTLE
Vulnerable Pi: sensor_publisher.py ──HTTP POST /sensor──▶ balloon_control_api_vulnerable.py (Flask :5000) → relays
Secure Pi:     balloon_control_secure.py (reads I2C directly; /sensor validated against I2C)
Both → MQTT → Node-RED gauges + Security Status panel

IDS
Switch port 15 mirrored → laptop port 7 → Suricata eve.json → Filebeat → Elasticsearch 10.30.0.60 → Grafana IDS dashboard
Secure Pi rejections → Wazuh
```

---

## 6. Scripts & services

### Balloon demo (`balloon-demo/scripts/`, deployed to `/home/username/balloon-demo/scripts/` on the Pis)
| Script | Runs on | Service | What it does |
|---|---|---|---|
| `balloon_control_api_vulnerable.py` | Vulnerable Pi | `balloon-control-api.service` | Flask :5000, no auth, no validation, no rate limit (**intentional, don't "fix"**). 25 PSI target, median-of-5 sampling, hysteresis, relief valve at 70 PSI upstream, vents above 35 PSI after an attack. MQTT at 10 Hz. |
| `sensor_publisher.py` | Vulnerable Pi | `balloon-sensor-publisher.service` | Reads the DATAQ sensors via the ADS1115 and POSTs to `/sensor` at 2 Hz |
| `balloon_control_secure.py` | Secure Pi | `balloon-control-secure.service` | Reads I2C directly. Rejects network data more than **10.0** PSI off from I2C (verified live 2026-11-01: a 0 PSI spoof against a real 27 PSI returns HTTP 400 `{"status":"rejected","reason":"sensor_mismatch","threshold":10.0}`; docs previously said 1.0), rate-limited to 2 Hz, flags changes faster than 5 PSI/s, logs to Wazuh. MQTT `balloon/secure/status` at about 2 Hz. |
| `attack_spoof.py` | Suricata laptop | (manual) | Spoofing flood, see below |
| `test_pressure_sensor.py`, `test_relays.py`, `test_burst_pressure.py` | either | (manual) | Hardware sanity tests |

Copies of exactly what was deployed are in `deployed_to_pi6/` (secure) and `deployed_to_pi7/` (vulnerable).

### The attack (run from the Suricata laptop, on VLAN 2 so the IDS captures it)
```bash
python3 attack_spoof.py --dual --check                      # check both targets are reachable
python3 attack_spoof.py --dual --pressure 0.0 --rate 0.01   # attack both at 100 Hz each (--rate = seconds between requests)
python3 attack_spoof.py --continuous --pressure 0.0         # vulnerable target only
```
Ctrl+C stops it. Note that `--pressure` defaults to 20.0, so pass `0.0` explicitly. Expected result: the vulnerable system climbs past 25 PSI and the bottle bursts, while the secure system rejects the data (|0.0 − 25| > 10.0 threshold). The Security Status panel turns red and pulses, and it clears about 1 second after the attack stops.

### Hospital (`hospital scripts/heartrate/`)
`HeartRate{1..5}Monitor.py` runs as `heartrate{1..5}.service` on each Pi, from `/home/r-pi-N/`, using paho-mqtt.

### Deploying an updated unit file
```bash
sudo cp balloon-demo/services/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart <service>
sudo journalctl -u <service> -f      # live logs
```

---

## 7. Balloon hardware cheat sheet

- **Sensors:** DATAQ 100 PSI, 0.5–4.5 V. Red = 12 V+, black = GND, **yellow = signal**. A0 = upstream (redundant), A1 = downstream (primary control).
- **Signal chain:** sensor → ADS1115 (5 V, I2C 0x48) ↔ BSS138 level shifter ↔ Pi 5 (3.3 V).
  BSS138 wiring: LV = Pi pin 1 (3.3 V), HV = Pi pin 2 (5 V), A1 = Pi SCL, A2 = Pi SDA, B1 = ADS SDA, B2 = ADS SCL.
- **8-relay HAT** (I2C 0x27, all ID switches ON), controlled with `lib8relind.set(0, n, 0/1)`: relay 2 = inflate, relay 3 = vent, relay 4 = relief. The solenoids are normally closed (NC): 1 = open.
- **40 A 3-relay HAT** (I2C 0x60, side-mounted on a ribbon cable): `lib3relind.set(0, 3, 1)` turns the pump on (23 A load).
- **Power:** 12 V 29 A PSU, with a **kill switch**.
- **If I2C is flaky:** add `dtparam=i2c_arm_baudrate=10000` to `/boot/config.txt`.
- **If a solenoid sticks** (known issue): tap the valve body. Then check 12 V under load and clean the plunger with IPA.

---

## 8. Common problems → fixes

| Symptom | Fix |
|---|---|
| Can't reach 192.168.50.x from 10.30.0.x | Mock WAN cable missing (Step 0), or firewall rules not loaded |
| Vulnerable gauges at 0, Secure fine | Check `ALLOW_VULNERABLE_PI_TO_MQTT`. Test on the Pi: `timeout 5 bash -c 'cat < /dev/null > /dev/tcp/10.30.0.51/1883' && echo open` |
| IDS dashboard frozen | Check `ALLOW_SURICATA_TO_ELASTICSEARCH`, then `sudo systemctl restart filebeat` on the laptop |
| Vault "Sealed" | Normal after a reboot: unseal (Step 3) |
| HR gauges at 0 | Restart the Pi services (Step 4). If MQTT has data but the dashboard doesn't, run `sudo systemctl restart nodered.service` on 10.30.0.52 |
| Can ping VMs but not Pis | Unplug and replug the switch uplink |
| HAPI FHIR down | On 10.30.0.56: `sudo docker start hapi-fhir` |
| Mirth channel stopped | In the web UI, right-click `HeartRate_FHIR_Final` → Start |
| Grafana panels show SSL errors | `sudo sqlite3 /var/lib/grafana/grafana.db "UPDATE data_source SET json_data = json_set(json_data, '$.sslmode', 'require') WHERE type = 'grafana-postgresql-datasource';"`, then restart grafana-server |
| Wazuh agents disconnected | On 10.30.0.55: `sudo systemctl restart wazuh-manager`. Check with `sudo /var/ossec/bin/agent_control -l` |
| OAuth2 Proxy shows a huge restart count | Harmless: it starts before Keycloak is up |
| Grafana times look 5 hours off | It displays UTC |

`TROUBLESHOOTING_HISTORY.md` has the full write-ups.

---

## 9. Things to think about for a 3-day, all-weekend demo

- **Bottles are consumable.** Every full demo bursts one. Bring plenty, and plan whether you'll run the full burst each time or stop the attack early and let the post-attack venting (above 35 PSI) bring it down.
- **Stopping the attack:** Ctrl+C on the laptop. The secure panel clears in about 1 second. The vulnerable system vents on its own.
- **If the venue loses power overnight:** redo Step 3 (Vault) and Step 4 (Pi services). Everything else auto-recovers.
- **Storage:** PostgreSQL grows about 1.2 GB/day while running. If it ran over the summer, check disk space on 10.30.0.50 and the TrueNAS pool.
- **Wazuh SSO is broken.** Always use basic auth.
- **Bring this file printed and kept off the table,** or on a phone, as a credentials cheat sheet.

### Pre-conference testing (aim for about Nov 6, one week before)
- [ ] Full cold boot with Mock WAN (air-gap mode)
- [ ] End-to-end attack: vulnerable system compromised, secure system protected
- [ ] All 5 ECG waveforms on Node-RED
- [ ] Grafana IDS shows the attack traffic
- [ ] Wazuh logs the secure Pi's rejections
- [ ] Every credential above still works (7 months since last verified)
- [ ] HDMI to an external monitor
- [ ] Packing: **SFP+ DAC cable**, **mock-WAN dumb switch + short cable**, **3 USB-C Pi adapters**, 12 V PSU + wiring, Suricata laptop, spare bottles, power strips (full list in `QUEEN_CITY_CON_HARDWARE_LIST.md`)
