# Queen City Con 0x4 — Field Guide

**Talk + all-weekend booth demo:** "When the Sensor Lies", Nov 13–15, 2026
**Written:** 2026-11-06. This guide supersedes the startup sections of `CONFERENCE_REFRESHER.md`, `QUICK_STARTUP_PROCEDURE.md` and `SYSTEM_STARTUP_GUIDE.md` wherever they disagree.
**Safe to show on screen:** this file has **no passwords**. Credentials are in `CON_CREDENTIALS.md` (keep that one off the projector).

**How to use it**
- Section 1 is homework for **this week** at home. Don't skip it, because the venue is the wrong place to find out a backup doesn't exist.
- Sections 3–6 are the venue runbook, in order. Each step says what you should see. If you don't see it, jump to the troubleshooting row it names.
- Section 8 is troubleshooting by symptom. Section 9 is what to do when something is dead and can't be fixed in time.

Files in this folder:

| File | Use |
|---|---|
| `CON_FIELD_GUIDE.md` | This runbook (print it) |
| `CON_CREDENTIALS.md` | Every login, Vault keys (print, keep in a pocket) |
| `con_health_check.ps1` | Run on the admin laptop: pings every device and checks every service port |
| `restart_pi_services.ps1` | Run on the admin laptop: restarts all 7 Pi services plus Filebeat |
| `When the Sensor Lies.pptx` | **The talk deck (current, 14 slides)** |
| `QUEEN_CITY_CON_HARDWARE_LIST.md` | Packing list / hardware reference |
| `CONFERENCE_REFRESHER.md` | Deep reference: how everything works, Oct–Nov change log |
| `QueenCityCon_Presentation.md` | **Old draft talk, superseded by the .pptx.** Several numbers in it are wrong |

---

## 0. The two computers

| | **Admin laptop** (new: replaces the desktop) | **Suricata / attacker laptop** |
|---|---|---|
| Network | VLAN 30 (hospital side), wired | VLAN 2, 192.168.50.191, two USB-Ethernet dongles |
| Job | Slides on the projector, dashboards, SSH to everything, Vault unseal, health checks | Suricata IDS on the mirror port, Filebeat → Elasticsearch, runs the attack script |
| Shown to audience | Yes (HDMI) | The attack terminal, briefly |

Why the admin laptop must be on **VLAN 30**: the hospital VMs and Pis live there, the HAPI VM only accepts SSH from 10.30.0.0/24, and VLAN 2 is deliberately blocked from VLAN 30. From VLAN 30 you can still reach VLAN 2 (Vulnerable Pi, Suricata laptop) through the UDM-SE.

**What does not carry over from the desktop:** the desktop reaches the lab through home-network routes via the UDM-SE WAN (192.168.1.24) plus the UniFi rule `TEMP - laptop to lab`. None of that exists at the venue, and the desktop's SSH keys aren't on the laptop. Section 2 sets the laptop up properly.

---

## 1. This week, at home (Nov 6–12)

Work down the list. Tick each item when it's done.

### 1A. Back up what the repo doesn't have — **highest priority**
If one of these VMs dies, these exports are what you restore from. Everything goes into `Queen_City_Con\backups\<date_time>\` (OneDrive syncs it to the laptop).

**Scripted (rerun right before packing):**
- `powershell -ExecutionPolicy Bypass -File .\con_backup.ps1`: Grafana (all dashboards, data sources, alerting), Mirth (full restorable server config + channels), Keycloak (both realms: clients, roles, groups, users). Read-only. **First run 2026-11-06 14:24: all three OK** (`backups\2026-11-06_1424\`).
- **Node-RED (manual, about 2 min; done 2026-11-06 →** `backups\2026-11-06_1424\nodered\nodered_userdir.tgz`**: 3 flow tabs / 66 nodes, credential key included).** To redo it:
  1. `ssh username@10.30.0.52`, then:
     `D=$(getent passwd $(systemctl show -p User --value nodered) | cut -d: -f6)/.node-red; ls $D`
     `sudo tar czf /tmp/nodered_backup.tgz --exclude=node_modules -C "$(dirname "$D")" .node-red && sudo chmod 644 /tmp/nodered_backup.tgz`
  2. On the desktop: `scp username@10.30.0.52:/tmp/nodered_backup.tgz .\Queen_City_Con\backups\<folder>\nodered\nodered_userdir.tgz`
  3. Back on the VM: `rm -f /tmp/nodered_backup.tgz`
  - **Restore:** unpack into the service user's home, `npm install` inside `.node-red`, restart `nodered`. Keep `.config.runtime.json`: it holds the key that decrypts `flows_cred.json`.
- These files are **sensitive**: the Node-RED credentials and the Keycloak exports. Keep them in OneDrive and off USB sticks you might lose.

- [ ] **Node-RED main flow** (hospital heart rate → PostgreSQL/Mirth, ECG sweep monitor, Security Status panel, balloon gauges). In the editor at http://10.30.0.52:1880 open the ☰ menu → Export → **All flows** → Download. Save as `backups\nodered_all_flows_2026-11.json`.
  Also copy the Node-RED settings and credentials files from the VM. The flow export does **not** include passwords for the MQTT/PostgreSQL nodes:
  `scp username@10.30.0.52:~/.node-red/{settings.js,flows_cred.json,package.json} backups\nodered\`
  (If the Node-RED user directory isn't `~/.node-red`, find it with `sudo systemctl cat nodered`.)
- [x] **Grafana, Mirth, Keycloak:** done by `con_backup.ps1` (2026-11-06). The manual steps below are only for reference.
- [x] **Node-RED:** done 2026-11-06 (manual steps above).
- [ ] **Grafana dashboards (manual alternative).** Partly done 2026-11-06: `backups\grafana_heart_rate_dashboard_before_2026-11-06.json` (v36, before the query fix). Export the **current** v37 too. Use the hospital heart-rate dashboard (the IDS one is already in the repo as `grafana_ids_dashboard.json`). Log in as **local `admin`** → open the dashboard → Share → Export → **Save to file**. Repeat for every dashboard you show.
- [ ] **Mirth channel** `HeartRate_FHIR_Final`. In the Mirth Administrator, select the channel → **Export Channel** → save the XML.
- [ ] **Keycloak realm** `hospital-homelab`. In the admin console select realm → Realm settings → Action (top right) → **Partial export**, with groups/roles and clients included. Save the JSON. (Client secrets come out masked. That's fine for a reference copy.)
- [ ] **HAPI FHIR container's exact run command.** The two docs disagree on it. On 10.30.0.56 run `sudo docker inspect hapi-fhir > hapi_inspect.json` and copy it into `backups\`.
- [ ] **UniFi backups.** UDM-SE → Settings → System → Backups → **Download**. Save the `.unifi` file.
- [ ] **TrueNAS config.** System → General → **Save Config** (include the secret seed). The repo copy is from Nov 2025 and predates every VM change since.
- [ ] Optional: copy the deployed unit files from each Pi (`/etc/systemd/system/heartrate*.service`, `balloon-*.service`). The repo's heartrate units are known to be **stale** (the deployed ones have `network-online` + `sleep 15` and a different path).

### 1B. Write down the switch port map (it doesn't exist anymore)
The switch was factory-reset in October and every older port table is out of date. In UniFi → Devices → the switch → Ports, fill this in and keep the printed copy:

| Port | Device | Native network | Notes |
|---|---|---|---|
| ___ | Pi #1 (PoE) | VLAN 30 | |
| ___ | Pi #2 (PoE) | VLAN 30 | |
| ___ | Pi #3 (PoE) | VLAN 30 | |
| ___ | Pi #4 (PoE) | VLAN 30 | |
| ___ | Pi #5 | VLAN 30 | USB-C power |
| ___ | Secure Pi | VLAN 30 | USB-C power |
| **15** | Vulnerable Pi | VLAN 2 | **mirror source** |
| **6** | Suricata laptop mgmt dongle (…53e0) | VLAN 2 | 192.168.50.191 |
| **7** | Suricata laptop mirror dongle (…4370) | — | **mirror destination of 15** |
| ___ | U6 Pro AP | | |
| ___ | **Admin laptop** | **VLAN 30** | new: set this up (1C) |
| 26 (SFP+) | Uplink to UDM-SE port 11 | **Default**, tagged Allow All | must match UDM side |

**UDM-SE ports (confirmed 2026-11-06):**

| UDM-SE port | Device |
|---|---|
| 1 | **Admin_Laptop**: VLAN 30, **no DHCP**, so set the laptop to static 10.30.0.30 (see 1C) |
| 3 | TrueNAS **eno1** → `br0` (10.30.0.44 and **all VMs**). **Critical:** no VMs without this cable. |
| 5 | iDRAC9 |
| 7 | R720 **eno3** ("third nic test"), passed straight through to the **deprecated `suricata_ids` VM** (old capture link from the VM-based IDS design). Not used by the current demo: the IDS is now the bare-metal laptop on lab switch port 7. Verified 2026-11-06: unplugging it changed nothing. Optional. |
| **9** | **WAN1 ("Internet 1"): the Mock WAN / home cable goes here** |
| 10 | WAN2 ("Internet 2"): nothing connected; must stay on DHCP (see section 8) |
| 11 (SFP+) | Lab switch uplink (DAC) |

Lab switch ports confirmed so far: 6 = Suricata mgmt, 7 = Suricata mirror, 9/10/11 = Pi #1/#2/#3. Fill in the rest of the switch table above.

**Take phone photos of the back of the rack with every cable plugged in.** At the venue you just match the photo.

### 1C. Give the admin laptop a home on VLAN 30
- [x] **Done 2026-11-06:** the laptop uses **UDM-SE port 1 ("Admin_Laptop", VLAN 30)**. That port gives **no DHCP address** (you get 169.254.x), so set the laptop's wired adapter (Intel I219-LM, "Ethernet") by hand: Settings → Network & internet → Ethernet → IP assignment → Manual → IPv4 **10.30.0.30**, mask **255.255.255.0**, gateway **10.30.0.1**, DNS **10.30.0.1**. Verified: the UDM-SE UI, TrueNAS, Node-RED and MQTT all answer from there.
  - At home with Wi-Fi on, leave the gateway blank so Wi-Fi keeps the internet. At the venue, set the gateway to 10.30.0.1 (Wi-Fi off) so you can reach VLAN 2.
- [ ] Label the cable "ADMIN LAPTOP → UDM-SE port 1".

### 1D. Rehearse the whole thing **on the laptop, with the Mock WAN**
The point is to prove the venue setup works, so do it exactly as you will there:
- [ ] Unplug the UDM-SE WAN from the home switch and plug it into the **standalone dumb switch** (Mock WAN). This also proves the lab works with no internet: NTP, Keycloak SSO and Grafana all have to work offline.
- [ ] Laptop: Wi-Fi **off**, Ethernet into its VLAN 30 port.
- [ ] Full power-off of everything, then follow sections 4–6 start to finish using only this guide. Time it. Fix the guide where reality differs.
- [ ] Run `con_health_check.ps1` and get all green.
- [ ] Run a full attack demo (section 6), including Wazuh and Grafana IDS.
- [ ] Present the deck from the laptop over HDMI to a TV/monitor while the dashboards run.
- [ ] Afterwards, put the UDM-SE WAN back on the home switch if you still need home access.

### 1E. Loose ends
- [ ] **Disable the UniFi rule `TEMP - laptop to lab`** (it opens the lab to the home network). Optionally remove the desktop's routes: `route delete 10.30.0.0`, `route delete 192.168.0.0`, `route delete 192.168.50.0` (admin prompt).
- [x] **Decided 2026-11-06: bottles burst** (section 6.3). Pack enough bottles, safety glasses and a shield.
- [x] **Decided 2026-11-06: attack at 100 Hz per target.** `--rate` is the *interval in seconds*: `0.01` = 100 Hz, while the old `0.1` = only 10 Hz. Slide 10 (100 Hz) is correct. The repo's `attack_spoof.py` still defaults to 0.1, so always pass `--rate 0.01`.
- [ ] **During rehearsal, confirm the 100 Hz run:** the script's live stats should show ~100 req/s per target. If they don't, the laptop or Pis can't keep up, so note the real rate and say that in the talk.
- [ ] **Wazuh disk at 100 Hz:** every rejected packet is logged, and the Wazuh disk filled up once already (2026-10-31). After the rehearsal attack, check `df -h` on 10.30.0.55, and check it each morning at the con.
- [ ] Verify the Wazuh search you'll show actually returns the Secure Pi rejections. The old draft said `rule.id:100001`; confirm it during the rehearsal and write the working query here: ____________________.
- [ ] Where does `attack_spoof.py` live on the Suricata laptop? Path: ____________________.
- [ ] Buy the **5-port dumb switch** (Mock WAN) and retrieve the **SFP+ DAC** from your dad's house.
- [ ] Print this guide + `CON_CREDENTIALS.md`. Put a PDF of both on your phone.
- [ ] Export the deck to PDF too (File → Export → PDF), as a fallback if PowerPoint misbehaves on the venue's display.

---

## 2. Admin laptop setup (do once, during 1D)

1. **OneDrive:** right-click the `Senior Design I` folder → **Always keep on this device**. Then the guide, deck, scripts and backups are available with no internet. Confirm by opening a file with Wi-Fi off.
2. **SSH client:** Windows 10/11 has `ssh` built in. Check with `ssh -V` in PowerShell.
3. **SSH keys** (avoids typing the password 20 times at the booth). With the laptop on its VLAN 30 port:
   ```powershell
   ssh-keygen -t ed25519            # accept defaults
   $pub = Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
   $hosts = 'username@10.30.0.20','username@10.30.0.21','username@10.30.0.22','username@10.30.0.23','username@10.30.0.24',
            'username@10.30.0.25','username@192.168.50.100','username@192.168.50.191',
            'username@10.30.0.58','username@10.30.0.51','username@10.30.0.52','username@10.30.0.50',
            'username@10.30.0.55','username@10.30.0.56','username@10.30.0.44'
   foreach ($h in $hosts) { $pub | ssh $h "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys" }
   ```
   You'll type the password once per host. Afterwards `ssh username@10.30.0.20` should log straight in.
   The service-restart script uses `sudo`. If the Pis prompt for a sudo password, `ssh -t` lets you type it. Check during rehearsal.
4. **Browser bookmarks** (one folder, "QCC"), in the order you'll show them:
   Node-RED dashboard `http://10.30.0.52:1880/ui` · Grafana hospital `http://10.30.0.53:3000` · Grafana IDS dashboard · Wazuh `https://10.30.0.55` · Vault `http://10.30.0.58:8200` · Mirth `https://10.30.0.54:8443` · UDM-SE `https://10.30.0.1` · TrueNAS `http://10.30.0.44` · iDRAC `https://10.30.0.45`
   Open each once and accept the self-signed certificate warnings now, not in front of an audience.
5. **Deck:** open `When the Sensor Lies.pptx` once with Wi-Fi off to make sure fonts render. Set Presenter View to show notes on the laptop and slides on the projector.
6. **Power & display:** disable sleep/lid-close-sleep while plugged in (Settings → System → Power). Turn off notifications (Focus / Do Not Disturb). Have the HDMI adapter the laptop needs.
7. **Wi-Fi at the venue:** keep it **off** while presenting. If you need venue Wi-Fi for something, check its subnet (`ipconfig`). If it uses 10.30.0.x, 192.168.0.x or 192.168.50.x it will fight with the lab, so turn it back off.

---

## 3. Physical setup at the venue

Allow **2 hours** from unloading to demo-ready. Match the rack photos from 1B.

1. **Power plan.** The R720, UDM-SE, switch, 3 Pi adapters, 2 laptops, monitor and the 12 V pneumatic PSU all fit on one standard 15 A circuit, but use **2 power strips**. Put the 12 V PSU on its own strip so you can kill it independently. Keep the **kill switch** within arm's reach of where you stand.
2. **Rack / table:** UDM-SE, switch, R720. Leave airflow room behind the server. It's loud, so face its exhaust away from the audience.
3. **Backbone:** SFP+ **DAC** between UDM-SE port 11 and switch port 26. Nothing crosses between devices without it.
4. **Mock WAN:** short cable from the UDM-SE **WAN** port into the standalone **dumb switch**, and plug **nothing else** into that dumb switch. Power the dumb switch. (Not into the main switch. That can confuse the UDM's routing.)
5. **Server:** TrueNAS NIC and iDRAC cables to the UDM-SE ports from your 1B notes.
6. **Pis:** PoE cables to Pis 1–4. Data cables + **USB-C power** to Pi #5, Secure Pi, Vulnerable Pi (don't plug in power yet). Vulnerable Pi **must be on port 15** (the mirror source).
7. **Suricata laptop:** dongle **…53e0 → port 6** (management) and dongle **…4370 → port 7** (mirror). Swapping them makes Suricata watch the wrong link (section 8).
8. **Admin laptop:** its labeled cable to its VLAN 30 port. HDMI to projector/monitor.
9. **Pneumatics:** sensors, solenoids, pump, 12 V wiring to terminal blocks. **12 V kill switch OFF** until section 5. Fit a **fresh bottle**. Teflon tape on fittings if a joint leaks.
10. **Safety:** clear zone/shield around the bottles if you're bursting them, and safety glasses for you.

---

## 4. Power-on and bring-up (about 30 min)

| # | Do | Expect | If not |
|---|---|---|---|
| 4.1 | Power **UDM-SE**. Wait 3 min. | Front display shows it's up. | — |
| 4.2 | Power the **switch**. Wait 1–2 min. | Pis 1–4 light up (PoE). | Check the DAC. |
| 4.3 | Check the **Mock WAN**: UDM-SE display/UI shows WAN **link up** (no internet is fine). | WAN link up | Reseat the cable and power the dumb switch. Without WAN link, VLAN 2 ↔ VLAN 30 traffic fails. |
| 4.4 | Power the **R720** (front button). | TrueNAS boots in ~5 min, then the VMs auto-start. | Watch the console via iDRAC `https://10.30.0.45`. |
| 4.5 | Plug in USB-C power: **Pi #5, Secure Pi, Vulnerable Pi**. | — | — |
| 4.6 | Boot **Suricata laptop**. Check `ip -br addr \| grep enx` shows the IP on **…53e0**. | 192.168.50.191 on …53e0, no IP on …4370 | Swap the dongle cables. |
| 4.7 | **Admin laptop:** Wi-Fi off, Ethernet in. `ipconfig` shows its VLAN 30 address. | 10.30.0.x | Port profile isn't VLAN 30 (UniFi). |
| 4.8 | **Wait ~15 min** for the VMs (PostgreSQL → MQTT → Keycloak → Elasticsearch → the rest). Run `.\con_health_check.ps1` every few minutes. | VMs turn green one by one | Section 8, "VM not answering". |
| 4.9 | **Unseal Vault:** `http://10.30.0.58:8200`, paste unseal keys 1, 2, 3 (`CON_CREDENTIALS.md`), Unseal after each. | Status: Unsealed | Vault VM not up yet: wait. |
| 4.10 | **Resync Pi clocks + restart the hospital Pi services:** `.\restart_pi_services.ps1` (needed after every cold boot; the Pis start before MQTT/NTP is ready, so paho-mqtt fails silently and the clocks stay wrong). This does **not** touch the demo boards. | Each Pi prints `synced=yes`, a clock matching the PC, and `active` | Section 8, "HR gauges at 0" / "Grafana says No data". |
| 4.10b | **Demo boards (this starts the pumps and valves):** only with bottles fitted, the area clear and the kill switch in reach: `.\restart_pi_services.ps1 -IncludeDemoBoards`, then type `YES`. | Both systems pressurize to ~25 PSI | Kill switch OFF if anything looks wrong. |
| 4.11 | **Restart Filebeat** on the Suricata laptop (the script does this too). | — | — |
| 4.12 | Run `.\con_health_check.ps1` again. | **All green** | Fix reds via section 8 before going on. |

Notes:
- The Pis have no real-time clock. They get time from chrony on the MQTT VM (10.30.0.51). If a Pi booted before that VM was up, its clock is old until timesyncd retries. Check with `ssh username@10.30.0.20 timedatectl` ("System clock synchronized: yes").
- Keycloak may fail once at boot because PostgreSQL isn't ready. It has a 30 s auto-retry drop-in, so just wait.
- Grafana shows **UTC** (5 h ahead of EST). Not a fault.

---

## 5. Verification tests (before the doors open, and after any restart)

Do them in order. Each has a pass condition.

| Test | How | Pass |
|---|---|---|
| T1 Network | `.\con_health_check.ps1` | All hosts and ports green |
| T2 MQTT traffic | `ssh username@10.30.0.51` then `mosquitto_sub -h localhost -u username -P <MQTT pw> -t '#' -v` (Ctrl+C to stop) | `hospital/heartrate/pi-1…5`, `balloon/vulnerable/pressure\|relays\|sensor_source`, `balloon/secure/status` all scrolling |
| T3 Node-RED dashboard | `http://10.30.0.52:1880/ui` (Keycloak login `username`) | 5 HR gauges moving, 5 ECG sweeps (Pi #4 irregular, red above 110 BPM), 4 pressure gauges, Security Status **green "SYSTEM SECURE"** |
| T4 PostgreSQL | `ssh username@10.30.0.50` then `sudo -u postgres psql -d hospital_data -c "SELECT pi_id, MAX(timestamp) FROM heartrate_data GROUP BY pi_id ORDER BY pi_id;"` | All 5 Pis with a timestamp within the last minute (local time) |
| T5 Mirth → FHIR | Mirth Administrator: channel `HeartRate_FHIR_Final` | **Started**, Received/Sent counters climbing, Errors not climbing |
| T6 Grafana hospital | `http://10.30.0.53:3000` | All 5 Pis plotting. Pi #4 tile red > 110, "TACHYCARDIA" > 120 |
| T7 Wazuh | `https://10.30.0.55` (local `admin`, **not** SSO) | 14 agents Active |
| T8 Elasticsearch / IDS | On the Suricata laptop: `sudo systemctl is-active suricata filebeat` → both `active`; Grafana IDS dashboard has recent events | Events within the last few minutes |
| T9 12 V system | Kill switch ON. Watch the pressure gauges. | Both systems pump up to ~25 PSI and hold. No hissing leaks. Solenoids click. |
| T10 **Dress rehearsal attack** | Section 6, short version: 5 s attack, then Ctrl+C | Vulnerable gauge drops to 0 and the pump runs; Secure panel goes red then back to green ~1 s after stopping; IDS spike in Grafana; Wazuh shows rejections |
| T11 Display | Deck on projector, dashboards on the laptop | Readable from the back row |

---

## 6. Running the demo

### 6.1 Screen layout
Admin laptop on the projector. Tabs in order: deck → Node-RED dashboard → Grafana IDS → Wazuh. The Suricata laptop shows the attack terminal (or SSH to it from the admin laptop: `ssh username@192.168.50.191`, and run the attack from that window, so the audience sees one screen).

### 6.2 Run it
1. Baseline: both bottles at ~25 PSI, Security Status green.
2. On the Suricata laptop, in the folder holding `attack_spoof.py`:
   ```bash
   python3 attack_spoof.py --dual --check                      # both targets reachable?
   python3 attack_spoof.py --dual --pressure 0.0 --rate 0.01   # attack both systems at 100 Hz each
   ```
   `--pressure` defaults to 20.0, so always pass `0.0`. `--rate` is seconds between requests: `0.01` = 100 Hz (the default `0.1` is only 10 Hz).
3. Narrate: vulnerable gauge shows 0, its pump keeps running, the real upstream sensor climbs. Secure panel turns red, the blocked counter climbs, its bottle stays at setpoint.
4. **Ctrl+C** to stop. Secure panel returns to green in ~1 s. Vulnerable vents if above 35 PSI.
5. Show Grafana IDS (spike, attacker 192.168.50.191 → both targets) and Wazuh (the rejections).

### 6.3 Bursting the bottle (decided: bottles burst)
- Let the attack run. The bottle goes between 39 and 71 PSI (average ~60). The 70 PSI relief **will not** prevent it.
- **Before every run:** shield in place, glasses on, audience behind the line, and a heads-up ("this will be loud").
- **After the burst:**
  1. Ctrl+C the attack.
  2. Kill switch OFF.
  3. Fit a fresh bottle (check the fittings and sensor lines weren't knocked loose).
  4. Kill switch ON, and wait for both systems to settle at 25 PSI.
  5. Glance at the Security Status panel (green) before the next run.
- **Reset time:** expect ~___ min between runs (time it in rehearsal).
- **Budget bottles:** _____ demos/day × 3 days + 3 spares = _____ bottles.
- **Fallback if bottles run low:** press Ctrl+C at ~40 PSI on the vulnerable upstream gauge. Post-attack venting brings it down without a burst.

### 6.4 Emergency
- Anything odd with pressure → **kill switch OFF** (pump and solenoids lose power).
- **Kill-switch caveat:** the solenoids are normally-closed, so with 12 V off they close and **the bottle stays pressurized**. To release it safely, turn 12 V back on with the attack stopped and let the control loop vent, or vent manually (section 8, "Pump stuck on / bottle won't vent").
- The relay HATs **hold their last state** if the control service crashes. A crash with the pump on means the pump stays on. Kill switch first, then investigate.

---

## 7. Running all weekend

- **Every ~2 hours:** `.\con_health_check.ps1`, glance at the dashboards, look for leaks, top up bottles.
- **Overnight, pick one:**
  - **Leave it running** (only if the room is locked and power stays on): kill switch OFF, vent both bottles first, laptops locked/closed.
  - **Shut down** (if power may be cut overnight; this is the safer default): use the shutdown order below, then section 4 again in the morning (~30 min; arrive early).
- **Shutdown order:**
  1. Stop the attack.
  2. Vent the bottles, then kill switch OFF.
  3. `ssh` each Pi: `sudo shutdown -h now`.
  4. Suricata laptop: shut down.
  5. TrueNAS UI → Power → **Shut Down** (VMs shut down cleanly; wait until the server is off).
  6. Switch, then UDM-SE, unplugged last.
- **After any power loss:** Vault re-seals (4.9) and Pi services need a restart (4.10). Everything else comes back on its own.
- **Disk:** PostgreSQL grows ~1.2 GB/day. Fine for a weekend; check with `df -h` on 10.30.0.50 if anything slows down.

---

## 8. Troubleshooting by symptom

Start with `.\con_health_check.ps1`. Most problems show up as a red line.

| Symptom | Likely cause | Fix |
|---|---|---|
| Admin laptop can't reach anything | No static IP (port 1 has no DHCP, so you get 169.254.x), Wi-Fi stealing the route, or wrong port | `ipconfig`: must be 10.30.0.30. Set it manually (1C). Turn Wi-Fi off. Must be in UDM-SE port 1. |
| UDM-SE WAN shows only "IPv6", no IPv4; at home the lab is unreachable and the home console shows ever-increasing IPs (.15, .16, …) | **WAN2 ("Internet 2", port 10, unplugged) had a 192.168.1.x config** overlapping the home network, so WAN1 rejected every offered address (found and fixed 2026-11-06) | UDM-SE → Settings → Internet → Internet 2 → IPv4 = **DHCP**. Keep WAN1 on DHCP. Home console: fixed IP 192.168.1.24 for MAC 6c:63:f8:67:c9:2d. Never type 192.168.1.1 into a UDM-SE WAN field (that's the home router). |
| Everything on VLAN 30 works, nothing on 192.168.50.x | **Mock WAN** has no link, or the firewall rules aren't loaded | Check the WAN link (4.3). Then on the UDM-SE: `iptables -L FORWARD -n -v \| grep 192.168.50` and, if empty, `iptables-restore < /etc/iptables/rules.v4` |
| Vulnerable gauges at 0, secure fine | Rule `ALLOW_VULNERABLE_PI_TO_MQTT` (priority 19998, below 20001) not active, or Mock WAN | On the Vulnerable Pi: `timeout 5 bash -c 'cat < /dev/null > /dev/tcp/10.30.0.51/1883' && echo open`. If not open, fix the rule/WAN, then restart both Vulnerable Pi services. |
| VMs ping, Pis don't (or the reverse) | Uplink native mismatch | UDM-SE port 11 and switch port 26 must **both** be Native **Default**, Tagged **Allow All**. Last resort: unplug and replug the DAC. **Never** give the switch a static IP (it's DHCP on 192.168.0.130). |
| Switch shows offline / can't adopt | Static IP or native mismatch | See above. The switch management lives on Default 192.168.0.0/24. |
| A VM doesn't answer after 20 min | VM didn't auto-start, or it's out of disk | TrueNAS UI → Virtualization → start it. On the VM, `df -h`. If `/` is full: `sudo lvextend -r -l +100%FREE /dev/ubuntu-vg/ubuntu-lv` (Grafana, Mirth, Keycloak, Vault and Elasticsearch still have room to grow). |
| HR gauges at 0 / one Pi missing | Service started before MQTT | `.\restart_pi_services.ps1`. One Pi: `ssh r-pi-N@10.30.0.(19+N) "sudo journalctl -u heartrateN -n 30"` |
| A Pi connects/disconnects every second | Duplicate user service (MQTT client-ID clash) | On that Pi: `systemctl --user list-units \| grep -i heart`. Disable any user copy: `systemctl --user disable --now <name>` |
| MQTT has data but the dashboard doesn't | Node-RED stuck | `ssh username@10.30.0.52 "sudo systemctl restart nodered"` |
| **Grafana says "No data" for every Pi, but data is flowing** (Node-RED live, MQTT busy) | **Pi clocks wrong** (no RTC; they booted before the NTP server on 10.30.0.51 was up and gave up retrying). Readings are stamped hours in the past (seen 2026-11-06: Pis 1.5–2.5 h slow after the Nov 4 power cut). | Run `.\restart_pi_services.ps1`: it resyncs each Pi's clock and prints it before restarting the service. Every clock should match the PC within seconds. |
| ECG flat with "--" for one Pi | That Pi sent nothing for 3 s | Same as "HR gauges at 0" |
| Node-RED/Grafana login loop or SSO error | Keycloak not up yet | Wait a minute (auto-retry). Then `ssh username@10.30.0.57 "sudo systemctl status keycloak"`. Grafana: use the local `admin` login meanwhile. |
| Wazuh SSO fails | Known: SSO is broken | Use local `admin` basic auth (always). |
| Wazuh agents disconnected | Manager started before agents | `ssh username@10.30.0.55 "sudo systemctl restart wazuh-manager"`, then check with `sudo /var/ossec/bin/agent_control -l` |
| Wazuh dashboard won't load | Disk full again | `df -h` on 10.30.0.55. See the 2026-10-31 entry in `TROUBLESHOOTING_HISTORY.md`. |
| Vault says "Sealed" | Normal after reboot | Unseal (4.9) |
| Mirth channel stopped / errors climbing | Channel stopped, or HAPI down | Mirth UI: right-click channel → Start. HAPI: `ssh -J username@10.30.0.55 username@10.30.0.56` then `sudo docker start hapi-fhir` |
| Grafana panels show SSL errors | Datasource sslmode lost | On 10.30.0.53: `sudo sqlite3 /var/lib/grafana/grafana.db "UPDATE data_source SET json_data = json_set(json_data, '$.sslmode', 'require') WHERE type = 'grafana-postgresql-datasource';"` then `sudo systemctl restart grafana-server` |
| Grafana heart-rate graphs say "No data" and the **Cancel** button keeps spinning, but the BPM tile works | Graph queries too slow (fixed 2026-11-06, dashboard v37): `$__timeFilter(timestamp AT TIME ZONE …)` stopped PostgreSQL using its index, so each panel took 11.5 s and the 5 s refresh cancelled them | Queries now use `timestamp BETWEEN ($__timeFrom()::timestamptz AT TIME ZONE 'America/New_York') AND (...)`, about 0.1 s. If it comes back, roll back in Dashboard → Settings → Versions, or compare with `backups\grafana_heart_rate_dashboard_before_2026-11-06.json`. Don't set refresh below 10 s. |
| Grafana "BPM > 120" tile says "No data" | Pi #4 silent for 30 s | Restart `heartrate4` |
| IDS dashboard frozen | Filebeat or rule `ALLOW_SURICATA_TO_ELASTICSEARCH` (priority 19999) | On the Suricata laptop: `sudo systemctl restart filebeat`, then `sudo journalctl -u filebeat -n 30`. Check the rule/Mock WAN. |
| IDS shows nothing during the attack | Dongles swapped, or mirror config lost | `ip -br addr \| grep enx`: the IP must be on **…53e0**. UniFi: port 7 mirroring port 15. The Vulnerable Pi must actually be on port 15. |
| Secure panel never turns red | Attack isn't reaching 10.30.0.25 | `attack_spoof.py --dual --check`. This path worked in the March dual-target tests. Check the Mock WAN, and check that no new UDM-SE rule blocks VLAN 2 → 10.30.0.25:5000. |
| Secure panel stuck red after the attack | Status not updating | Watch `balloon/secure/status` in T2. Restart `balloon-control-secure` on the Secure Pi. |
| Pi clock wrong / TLS or log timestamps odd | No NTP sync | `timedatectl` on the Pi. `ssh username@10.30.0.51 "chronyc clients"`. Then on the Pi: `sudo systemctl restart systemd-timesyncd`. |
| Pressure reads 0 or junk, I2C errors in the log | Loose wiring / bus speed | Reseat the BSS138/ADS1115 wires. `sudo i2cdetect -y 1` should show **48** (and **27**, **60** on the Vulnerable Pi). Persistent errors: `dtparam=i2c_arm_baudrate=10000` in `/boot/firmware/config.txt`, then reboot. |
| Pressure won't rise | Pump relay, inflate solenoid stuck, or a leak | Listen for the pump and a solenoid click. Tap the valve body (known sticking). Check 12 V at the terminals with the multimeter **under load**. Check fittings. |
| Pump stuck on / bottle won't vent | Service crashed with the relay latched, or the vent valve stuck | **Kill switch OFF.** Then on the Vulnerable Pi: `sudo systemctl stop balloon-control-api`. Kill switch ON. Pump off: `python3 -c "import lib3relind; lib3relind.set(0,3,0)"`. Open vent: `python3 -c "import lib8relind; lib8relind.set(0,3,1)"`. When empty, close it: `...set(0,3,0)`. Then `sudo systemctl start balloon-control-api`. |
| Projector shows nothing | Display mode | Win+P → Duplicate/Extend. Try the other HDMI cable/adapter. |

Service log commands (any Pi): `sudo systemctl status <service>` and `sudo journalctl -u <service> -n 50` (add `-f` to follow).

---

## 9. When something can't be fixed in time

Know what the demo **really** needs, and drop the rest.

| Must work for the bottle demo | Nice to have |
|---|---|
| UDM-SE + Mock WAN, switch + DAC | Pis 1–5, PostgreSQL, Mirth, HAPI FHIR |
| MQTT VM (10.30.0.51), Node-RED VM (10.30.0.52), Keycloak (dashboard login) | Grafana hospital dashboard, Vault |
| Secure Pi, Vulnerable Pi, 12 V system | Wazuh (show screenshots instead) |
| Suricata laptop (attack; IDS is a bonus) | Elasticsearch / Grafana IDS (show screenshots instead) |

**Fallbacks to prepare in 1D:** screenshots (or a short screen recording) of a good run of the Node-RED dashboard, Grafana IDS spike and Wazuh rejections, saved in `Queen_City_Con\screens\`. If a monitoring piece dies, show the screenshot and keep the live bottles going.

**If Keycloak is down and Node-RED needs a login:** fix Keycloak first. Restoring from the realm export (1A) takes longer than a booth allows.

**Rebuilding a component from scratch is not a venue task.** If it comes to that, the starting points are:

| Component | Starting point |
|---|---|
| Node-RED | `backups\nodered_all_flows_2026-11.json` (from 1A) → Import; `balloon-demo/nodered/*.json`; ECG code in `hospital scripts/ecg_sweep_template.html` |
| Grafana | Dashboard JSON from 1A + `grafana_ids_dashboard.json` → Import |
| Mirth | Channel XML from 1A → Import Channel (listener port **8081**) |
| HAPI FHIR | `hapi_inspect.json` from 1A |
| Keycloak | Realm export from 1A; client list in `NETWORK_SETUP_PROGRESS_PART1.md` |
| Pi services | `balloon-demo/services/*.service`, `balloon-demo/services/README.md` |
| UDM-SE / switch | `.unifi` backup from 1A |

---

## 10. Teardown

1. Stop the attack. Vent both bottles. Kill switch OFF. Unplug the 12 V PSU.
2. Shut down in the order from section 7.
3. Photograph anything you re-cabled differently.
4. Pack against `QUEEN_CITY_CON_HARDWARE_LIST.md`. Don't leave without: DAC, dumb switch, 3 USB-C adapters, both laptops + dongles, kill switch.
5. Back home: put the UDM-SE WAN back on the home switch. Leave the `TEMP` rule disabled unless you need it again.

---

## Appendix A — IP map

| Device | IP | Notes |
|---|---|---|
| UDM-SE | 10.30.0.1 (also 192.168.0.1 on Default) | Gateway, firewall |
| Switch (USW Pro Max 24 PoE) | 192.168.0.130 (DHCP, Default network) | **Not** 10.30.0.10 (old docs) |
| TrueNAS / iDRAC | 10.30.0.44 / 10.30.0.45 | |
| PostgreSQL | 10.30.0.50 | 5432 |
| MQTT + NTP (chrony) | 10.30.0.51 | 1883, NTP 123/udp |
| Node-RED | 10.30.0.52 | 1880 (`/ui`) |
| Grafana | 10.30.0.53 | 3000 |
| Mirth | 10.30.0.54 | 8443 admin, 8081 channel |
| Wazuh | 10.30.0.55 | 443 |
| HAPI FHIR | 10.30.0.56 | 8080 (Mirth only), 4180 OAuth2 proxy; SSH only from 10.30.0.0/24 |
| Keycloak | 10.30.0.57 | 8080 |
| Vault | 10.30.0.58 | 8200 |
| Elasticsearch | 10.30.0.60 | 9200 |
| Pis #1–#5 | 10.30.0.20–24 | `heartrate1..5.service` |
| Secure Pi | 10.30.0.25 | `balloon-control-secure.service`, /sensor on 5000 |
| Vulnerable Pi | 192.168.50.100 | `balloon-sensor-publisher.service` + `balloon-control-api.service`, Flask 5000 |
| Suricata laptop | 192.168.50.191 | `suricata`, `filebeat` |
| U6 Pro AP | 10.30.0.246 | |
| Admin laptop | ____________ | from 1C |

UDM-SE firewall exceptions (all must be priority **< 20001**, before `BLOCK_VLAN2_TO_VLAN30`): `ALLOW_VULNERABLE_PI_TO_MQTT` (192.168.50.100 → 10.30.0.51 TCP 1883), `ALLOW_SURICATA_TO_ELASTICSEARCH` (192.168.50.191 → 10.30.0.60 TCP 9200), `ALLOW_VLAN2_TO_NTP` (VLAN 2 → 10.30.0.51 UDP 123).

## Appendix B — Facts the older docs get wrong

| Topic | Correct (as of Nov 2026) | Wrong in |
|---|---|---|
| Secure Pi service | `balloon-control-secure.service` | `SYSTEM_STARTUP_GUIDE.md` says `balloon-control-api` |
| Vulnerable Pi | **two** services (publisher + API) | `SYSTEM_STARTUP_GUIDE.md` checks only one |
| Secure rejection threshold | **10.0 PSI** (verified live 2026-11-01) | `QueenCityCon_Presentation.md`, CLAUDE.md say 1.0 |
| Switch IP | 192.168.0.130, DHCP | `NETWORK_INFRASTRUCTURE.md` and others say 10.30.0.10 |
| Mock WAN | standalone dumb switch | `QUICK_STARTUP_PROCEDURE.md` allows the main switch |
| Power-on order | UDM-SE → switch → server → Pis | `SYSTEM_STARTUP_GUIDE.md` starts with TrueNAS |
| Mirth listener | 8081 | `NETWORK_SETUP_PROGRESS_PART2.md` says 9999 |
| Uplink native network | Default on both ends | `BALLOON_DEMO_NETWORK_CONFIG.md` says VLAN 30 |
| Attack rate | `--rate 0.01` = 100 Hz per target | Refresher, hardware list, CLAUDE.md use `--rate 0.1` (10 Hz) |
| Relief valve "saves" the bottle | It doesn't (70 PSI > ~60 PSI average burst) | `QueenCityCon_Presentation.md` demo script |
| Heartrate unit files | Deployed units use network-online + 15 s sleep and a Desktop path | Repo copies in `hospital scripts/heartrate/` are stale |
