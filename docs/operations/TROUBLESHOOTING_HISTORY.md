# Troubleshooting History & Historical Fixes

This document archives detailed troubleshooting steps and fixes that were implemented throughout the project. These are historical records kept for reference.

---

## Wazuh VM Disk 100% Full (FIXED 2026-10-31)

**PROBLEM:** The UDM-SE internet graph showed a ~9-10 Mbps download spike every hour. `ossec.log` showed `content-updater: ERROR: Action for 'vulnerability_feed_manager' failed: ... Failed writing received data to disk` at :47 past every hour.

**ROOT CAUSE:** The Wazuh VM root filesystem (48 GB) was 100% full:
- `/var/ossec/queue/vd_updater` held 15 GB of failed feed downloads and `/var/ossec/queue/vd` held 7.5 GB. Every failed hourly update re-downloaded the full feed.
- `/var/log/syslog` was 12 GB. The dashboard had `logging.verbose: true` and wrote an "ops" line every 5 seconds (98% of syslog lines). Logrotate had stopped rotating since Oct 25 because the disk was full.
- Ubuntu's installer had only allocated half of the 97 GB volume group (48.47 GB free in `vgs`).

**FIX:**
```bash
sudo journalctl --vacuum-size=200M                          # free room so LVM can write its metadata
sudo lvextend -r -l +100%FREE /dev/ubuntu-vg/ubuntu-lv      # 48 GB -> 96 GB, online
sudo systemctl stop wazuh-manager
sudo rm -rf /var/ossec/queue/vd /var/ossec/queue/vd_updater # Wazuh re-downloads the feed (~15 min)
sudo systemctl start wazuh-manager
sudo truncate -s 0 /var/log/syslog
# /etc/wazuh-dashboard/opensearch_dashboards.yml: logging.verbose: false, added logging.quiet: true
sudo systemctl restart wazuh-dashboard
# /etc/logrotate.d/rsyslog: added "maxsize 500M" after "rotate 4"
```

**RESULT:** The disk is at ~25% of 96 GB, `Feed update process completed` was logged at 20:39 UTC, and the syslog flood stopped.

**Also noticed (not fixed):** `opensearch_security.openid.logout_url` uses `https://10.30.0.57:8080` but Keycloak serves plain HTTP on 8080. This may be related to the broken Wazuh SSO.

**Check:** `df -h /` and `sudo grep -i "content-updater" /var/ossec/logs/ossec.log | tail -3`

---

## UDM-SE Firewall Rules Not Loaded After Reboot (FIXED 2026-03-23)

**PROBLEM:** Vulnerable Pi (192.168.50.100) could not connect to MQTT broker (10.30.0.51:1883). MQTT connection timed out with "No route to host" error.

**ROOT CAUSE:** Firewall rules existed in `/etc/iptables/rules.v4` and boot script `/data/on_boot.d/99-firewall-rules.sh` existed, but rules were never loaded into memory after UDM-SE reboot. The boot script calls `iptables-restore < /etc/iptables/rules.v4`, but the rules weren't active.

**SYMPTOMS:**
- `ping 10.30.0.51` from Vulnerable Pi: 100% packet loss
- `nc -zv 10.30.0.51 1883` from Vulnerable Pi: Connection timed out
- `iptables -L FORWARD -n -v | grep 192.168.50.100` on UDM-SE: No output (rules not in memory)
- Balloon control API logs: `✗ MQTT connection failed: timed out`

**DIAGNOSIS STEPS:**
1. Verified firewall rules file exists: `cat /etc/iptables/rules.v4` showed correct rules
2. Verified boot script exists: `cat /data/on_boot.d/99-firewall-rules.sh`
3. Checked if rules active: `iptables -L FORWARD -n -v | grep 192.168.50.100` returned nothing
4. Tested connectivity from Vulnerable Pi: ping and port 1883 both failed

**FIX:**
```bash
# On UDM-SE (root@192.168.0.1):
iptables-restore < /etc/iptables/rules.v4
```

**VERIFICATION:**
```bash
# On UDM-SE:
iptables -L FORWARD -n -v | grep 192.168.50.100
# Output: Shows rule with counters (0 0 initially, then increments with traffic)

# On Vulnerable Pi:
nc -zv 10.30.0.51 1883
# Output: Connection to 10.30.0.51 1883 port [tcp/*] succeeded!

# Restart service:
sudo systemctl restart balloon-control-api.service

# Check logs:
sudo journalctl -u balloon-control-api.service --since "now" | grep MQTT
# Output: ✓ Connected to MQTT broker at 10.30.0.51:1883
```

**NOTE:** Ping still fails because firewall rule only allows TCP port 1883, not ICMP. This is expected and correct.

**PERMANENT FIX:** The boot script should handle this automatically on reboot, but may need investigation why it didn't run on last boot.

---

## Keycloak Service Down - PostgreSQL Connection Timeout (FIXED 2026-03-23)

**PROBLEM:** Node-RED Keycloak SSO login returned "connection refused" error.

**ROOT CAUSE:** Keycloak service failed to start on 2026-03-14 22:30:17 due to PostgreSQL connection timeout ("No route to host"). Service remained down for 9 days until manually restarted.

**SYMPTOMS:**
- `systemctl status keycloak`: Active: failed (Result: exit-code)
- Node-RED login redirect to Keycloak: Connection refused
- Keycloak logs: `org.postgresql.util.PSQLException: The connection attempt failed` → `java.net.NoRouteToHostException: No route to host`

**DIAGNOSIS STEPS:**
1. SSH to Keycloak VM: `ssh username@10.30.0.57` (pass: password)
2. Check service status: `systemctl status keycloak` showed failed since Mar 14
3. Check logs: `sudo journalctl -u keycloak -n 100` showed PostgreSQL connection failure
4. Test connectivity: `ping 10.30.0.50` and `nc -zv 10.30.0.50 5432` both succeeded (network OK now)

**FIX:**
```bash
# On Keycloak VM:
sudo systemctl restart keycloak

# Verify:
systemctl status keycloak  # Should show "active (running)"
curl -I http://localhost:8080  # Should return HTTP 302
```

**RESULT:** Keycloak started successfully, Node-RED SSO login working.

**LIKELY CAUSE:** PostgreSQL VM (10.30.0.50) was down or rebooting on Mar 14, preventing Keycloak from connecting. When PostgreSQL came back up, Keycloak didn't auto-retry and remained failed.

**PREVENTION:** Consider adding `Restart=on-failure` and `RestartSec=30` to Keycloak systemd service to handle transient DB failures.

---

## Node-RED MQTT Not Receiving Balloon Data (FIXED 2026-03-23)

**PROBLEM:** Node-RED MQTT In node showed "connected" status but received no balloon messages. Debug panel only showed heartrate messages.

**ROOT CAUSE:** Topic subscription had typo: `balloom/vulnerable/#` instead of `balloon/vulnerable/#`

**SYMPTOMS:**
- MQTT In node status: "connected" (green dot)
- `mosquitto_sub -h 10.30.0.51 -u username -P password -t 'balloon/vulnerable/#'` showed data flowing at 10 Hz
- Node-RED debug panel: No balloon messages, only heartrate messages

**FIX:**
1. Double-click MQTT In node in Node-RED
2. Change topic from `balloom/vulnerable/#` to `balloon/vulnerable/#`
3. Click Done → Deploy

**RESULT:** Balloon messages immediately appeared in debug panel at 10 Hz.

**LESSON:** Always verify topic spelling exactly matches publisher.

---

## Pi Heartrate Services Not Publishing to MQTT After Reboot (FIXED 2026-02-18)

**Root cause:** `After=network.target` only waits for the network interface, not a routable connection. paho-mqtt v2.1.0 fails silently on initial connect if network isn't ready.

**Fix applied to all 5 Pis:**
```ini
[Unit]
Description=Heart Rate Monitor N - ECG Display
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=r-pi-N
ExecStartPre=/bin/sleep 15
ExecStart=/usr/bin/python3 /home/r-pi-N/Desktop/hospital-scripts/heartrate/HeartRateNMonitor.py
Restart=always
RestartSec=10
```

Also enabled on all 5 Pis: `sudo systemctl enable systemd-networkd-wait-online.service`

Without this, `network-online.target` completes immediately regardless of actual network state.

Also added `Environment=PYTHONUNBUFFERED=1` to all 5 service files so stdout flushes to journal immediately — without this, `[MQTT] Connected` never appears in `journalctl` output.

**Diagnosing Node-RED no data:** Check in order:
1. `mosquitto_sub -h localhost -u username -P password -t '#' -v` on MQTT VM — silent = Pis not publishing
2. `sudo journalctl -u heartrate1.service -n 50` on Pi — no "[MQTT] Connected" = network timing issue
3. `timeout 10 python3 HeartRate1Monitor.py` manually on Pi — if it connects manually but not as service = systemd network ordering issue

---

## Mirth Disk Crisis (RESOLVED)

Derby DB filled 100% disk. Fixed by deleting `/opt/mirthconnect/appdata/mirthdb` and reconfiguring with auto-pruning. Data Pruner runs daily at 2 AM, 30-day retention.

---

## Grafana SSL Config

Set via SQLite directly (APT install ignores YAML provisioning):
```bash
sudo sqlite3 /var/lib/grafana/grafana.db \
  "UPDATE data_source SET json_data = json_set(json_data, '$.sslmode', 'require') \
   WHERE type = 'grafana-postgresql-datasource';"
```

---

## HAPI FHIR Firewall Rule Ordering

SSH allow must be Rule #1 before port 8080 deny rules:
```bash
sudo ufw insert 1 allow from 10.30.0.0/24 to any port 22
```

---

## Suricata YAML Syntax Error (FIXED 2026-03-06)

**Root cause:** Indentation error at line 169 of `/etc/suricata/suricata.yaml` — some properties under `alert:` had 13 spaces instead of 12.

**Fix:** Corrected indentation to 12 spaces for all properties under `- alert:` block. Suricata config now validates with `sudo suricata -T -c /etc/suricata/suricata.yaml`.

---

## Balloon Vulnerable System Control Loop Safety (FIXED 2026-03-06)

`balloon_control_api_vulnerable.py` automatically starts a background control loop (`threading.Thread(target=control_loop)`) that actively controls relays when the Flask server starts.

For safe testing without hardware control, comment out lines 451-452 in the script:
```python
# TESTING MODE - Control loop disabled for safety
# control_thread = threading.Thread(target=control_loop, daemon=True)
# control_thread.start()
```

This allows the Flask API to run for IDS testing without triggering relay/pump activation.

---

## I2C Communication Errors with ADS1115 (FIXED 2026-03-04)

**Root cause:** Default I2C bus speed (100 kHz) too fast for long wiring runs, causing `[Errno 121] Remote I/O error`.

**Fix:** Add `dtparam=i2c_arm_baudrate=10000` to `/boot/config.txt` to slow I2C to 10 kHz.

After reboot, sensors read reliably with no errors.

---

## Vulnerable Pi Pump Backflow During Overpressure Venting (FIXED 2026-03-17)

**Root cause:** When overpressure venting triggered, control loop turned pump OFF then opened vents. High-pressure air (72+ PSI) rushed backwards through inflate valve → pump impeller, spinning it in reverse and making audible pump sound even though relay was OFF.

**Solution - Overpressure detection sequence:**
1. Open ALL vents (inflate + downstream + upstream) FIRST while pump still running forward (prevents backflow)
2. Wait 0.1s for vents to open
3. Pump OFF (vents already open, no reverse flow path)
4. Wait 0.2s
5. Close all vents (return to clean state)
6. Enter venting_mode loop for pressure-based continuous venting

**Venting mode behavior:**
- Pump OFF (forced 3x to ensure)
- Upstream CLOSED (prevents any backflow through pump)
- Inflate + Downstream OPEN (bottle vents directly)
- Exits when real sensor shows <30 PSI AND source != "attacker"
- 3-second cooldown before pump can restart

---

## Shutdown Depressurization (FIXED 2026-03-17)

- Pump OFF
- Inflate OPEN (send 3x to ensure)
- Downstream OPEN (send 3x to ensure)
- Upstream OPEN (send 3x to ensure)
- Wait 5 seconds for full depressurization
- Close all valves

Commands sent 3x and longer wait time ensure proper venting during Ctrl+C shutdown.

---

## Service File Logging (FIXED 2026-03-17)

Add `Environment=PYTHONUNBUFFERED=1` to `/etc/systemd/system/balloon-control-api.service` so control loop messages (pump start/stop, venting, overpressure) appear in `journalctl` output immediately instead of being buffered.

---

## Vulnerable Pi Pump Control Improvements (FIXED 2026-03-17 Evening Session)

**Root cause:** Pump control logic was not matching secure system behavior, causing overshoot and instability.

**Changes made:**
1. **Single target pressure threshold**: Changed from dual thresholds (`TARGET_PRESSURE_MIN=25`, `TARGET_PRESSURE_MAX=30`) to single `TARGET_PRESSURE=25` matching secure system
2. **Pump command optimization**: Pump ON command now sent only ONCE when starting inflation (not every 20ms loop), with hardware settling delays (0.1s-0.2s) between valve operations
3. **Inflate valve closes at target**: System now closes inflate valve when pressure ≥25 PSI to isolate bottle from upstream pressure buildup (prevents 32 PSI → 40 PSI upstream spikes that were pushing downstream into overpressure)
4. **Control flow restructured**:
   - pressure ≥25 PSI: Pump OFF, inflate valve CLOSED, all vents closed (maintain target)
   - pressure <25 PSI: Start inflation sequence (close vents → open inflate → start pump)

**Attack behavior (VERIFIED 2026-03-17):**
- Attack at 100 Hz (`--rate 0.01`) successfully dominates median-of-5 sampling
- Real sensor: 2 Hz, Attack: 100 Hz → attack wins 98% of samples
- System successfully pushed to 66.3-69.25 PSI during attack (above average burst pressure of 59.6 PSI)
- Overpressure venting triggers when real sensor reading gets through median occasionally
- **Known issue**: After attack ends, system sits at 35-40 PSI waiting for natural leak instead of actively venting down
- **Attempted fix REVERTED**: Adding active venting for pressures >30 PSI created dangerous upstream pressure buildup (89.9 PSI), immediately reverted for safety

---

## IDS Not Detecting Cross-VLAN Attack Traffic (INVESTIGATED 2026-03-06)

**Root cause:** Cross-VLAN traffic (VLAN 30 → VLAN 2) is Layer 3 routed through UDM-SE gateway, not Layer 2 switched through mirrored port.

**Investigation steps:**
1. SSH'd to UDM-SE (`root@192.168.0.1`, password: password)
2. Connected to MongoDB: `mongo --port 27117`
3. Attempted to configure "mirror all ports": `db.device.update({"_id": ObjectId("68d5e7f4cc1cbf750851510a")}, {"$set": {"port_overrides.6.mirror_port_idx": "all"}})`
4. Result: UniFi switches don't support "all" parameter, config ignored
5. Verification: Attack from laptop (10.30.0.123) → Pi #7 (192.168.50.100) successful (200 OK), but Suricata only saw SSH traffic to itself (10.30.0.191)

**Resolution:** Accepted architectural limitation. For expo demo, run attacks from Suricata laptop (10.30.0.191) where traffic is on same VLAN2 network and passes through mirrored Port 15.

**Why this happens:** Inter-VLAN routing happens at gateway (UDM-SE), not at switch. Port mirroring can only capture traffic physically passing through switch ports, not routed traffic.

**Alternative solution (not implemented):** Would require running Suricata directly on UDM-SE gateway where all routed traffic flows.

---

## Attack Functionality Restoration (FIXED 2026-03-15)

**PROBLEM:** Attack script flooding at 100 Hz, real sensor at 2 Hz, but control loop was reading real sensor data (23-24 PSI) instead of attack data (19 PSI). Pump would not run.

**ROOT CAUSE #1:** `pump_running` flag stuck at True from pulse mode → code skipped pump start command even when pressure dropped to 19 PSI

**ROOT CAUSE #2:** Control loop sampling (every 50ms) was synchronized with real sensor updates (every 500ms), catching real data instead of attack data

**FIX #1:** Always send `set_relay(RELAY_PUMP, True)` when pressure ≤20 PSI, regardless of `pump_running` flag state

**FIX #2:** Median sampling (best 3 of 5 over 50ms) - filters out occasional real sensor spikes, attack wins statistically

**VERIFIED:** Attack successfully pushes real pressure from 30 PSI → 47.63 PSI before overpressure venting triggers

**Follow-up improvements:**
- **Fixed attack**: Median sampling (best 3 of 5) + always send pump ON command when pressure ≤20 PSI
- **Removed pulse mode**: Replaced with simple continuous pump + hysteresis (25-30 PSI dead band)
- **New pump control**:
  - pressure < 25 PSI: pump ON continuously
  - 25-30 PSI: maintain current state (hysteresis - prevents rapid cycling)
  - pressure ≥ 30 PSI: pump OFF
  - pressure > 35 PSI: overpressure venting mode
- **Ctrl+C on API script**: Works perfectly - controlled depressurization sequence ✓
- **Attack working**: Successfully pushes real pressure to 37-47 PSI before overpressure venting ✓

---

## Pump Cycling During Overpressure Venting (2026-03-15 - KNOWN ISSUE)

**PROBLEM:** When attack stops (Ctrl+C attack script), real pressure is 45+ PSI → overpressure venting triggers → pump goes into weird on/pulse mode instead of staying OFF

**ATTEMPTED FIXES:**
- Tried triple relay commands to force pump OFF (caused relay chatter/pulsing)
- Tried overpressure check before median sampling (would break attack during normal operation)
- Made venting mode only exit on real sensor data (helps but doesn't fix pump cycling)

**STATUS:** Much better than before - attack works reliably, just overpressure venting has minor pump cycling issue

**NEED TO INVESTIGATE:** Root cause of pump not staying OFF during venting mode - possible threading/timing issue

---

## Pi #6 Secure System - ADS1115 Channel Swapping and I2C Errors (FIXED 2026-03-17)

**PROBLEM:** Pi #6 secure system shows persistent ADS1115 channel swapping every 3-5 seconds + `[Errno 121] Remote I/O error` on I2C bus

**INITIAL HYPOTHESIS:** Defective ADS1115 module (same symptoms as previous session)

**SOFTWARE ROOT CAUSE (DISCOVERED 2026-03-16):** Secure script reads ADS1115 at **50 Hz** (5 samples × 10 Hz loop), vulnerable reads at **2 Hz** via sensor_publisher.py
- Secure: `for _ in range(5): downstream_samples.append(voltage_to_psi(chan_a1.voltage, ...))` - reads I2C hardware 5 times per loop
- Vulnerable: `for _ in range(5): pressure_samples.append(current_pressure)` - samples global variable (updated by publisher at 2 Hz)
- **ADS1115 being hammered at 50+ Hz with channel switching exceeds datasheet specs → causes channel swapping glitch**

**ACTUAL HARDWARE ROOT CAUSE (DISCOVERED 2026-03-17):** Custom PCB had **master ground wire in wrong GPIO pin**
- PCB is EPLZON-manufactured blank with hand-soldered ADS1115, BSS138, and wire connections
- Ground pin was connected to incorrect GPIO pin, causing all I2C communication to fail
- Fixing ground connection immediately resolved all issues

**TROUBLESHOOTING STEPS (2026-03-17):**
1. ✅ Tested Pi #7 vulnerable system - confirmed working perfectly at 10 kHz I2C, no errors, no channel swapping
2. ✅ Verified Pi #7 I2C config: `dtparam=i2c_arm_baudrate=10000`
3. ✅ Desoldered and rebuilt Pi #6 custom PCB to EXACTLY match Pi #7 wiring
4. ✅ Created complete color-coded wiring schematic for rebuild (see session notes)
5. ✅ Discovered ground pin in wrong location during testing
6. ✅ Fixed ground connection → all three I2C devices stable (0x27, 0x48, 0x60)
7. ✅ Verified with pump test: A0 spiked to 85 PSI, A1 stayed at 0 PSI, no channel swapping

**FILES UPDATED (2026-03-16):**
- `balloon_control_secure.py` line 361-373: Removed median sampling loop, now reads I2C once per control loop (10 Hz)

**FINAL HARDWARE CONFIGURATION (BOTH SYSTEMS IDENTICAL):**
- Custom PCB with ADS1115 + BSS138 level shifter soldered
- Pi → BSS138 → ADS1115 → dual DATAQ 100 PSI sensors
- BSS138 wiring: A1→B1 (SCL), A2→B2 (SDA)
- Separate +12V feeds for each DATAQ sensor (don't tie together)
- I2C speed: 10 kHz (`dtparam=i2c_arm_baudrate=10000`)
- HAT stack: Pi GPIO → 8-relay HAT (0x27) → 40A HAT (0x60)

---

## Safety Features Implementation (2026-03-19)

### Upstream Safety Relief ✅ IMPLEMENTED
- If `current_pressure_upstream > 70.0 PSI` → open upstream vent (close when <65 PSI hysteresis)
- Location: Line 250-261 in balloon_control_api_vulnerable.py
- Tested: Works correctly - vents 89.9 PSI → 2.8 PSI instantly
- **ISSUE FOUND**: Triggers during normal operation (every pump cycle)
- **ROOT CAUSE**: Inflate valve closes while pump still running → upstream buildup
- **STATUS**: Working but needs pump sequence fix (see below)

### Post-Attack Downstream Venting ✅ IMPLEMENTED
- If `pressure_reading > 35 PSI` → actively vent down to 30 PSI
- Location: Line 403-432 in balloon_control_api_vulnerable.py
- Sequence: Pump OFF → inflate closed → upstream closed → downstream open
- **ISSUE FOUND**: Threshold too low (was 30 PSI), triggered during normal overshoot
- **FIX APPLIED**: Changed threshold from >30 PSI to >35 PSI (2026-03-19)
- **STATUS**: Needs testing with actual attack

### Pump Shutdown Sequence Fix (2026-03-19)

**CURRENT ISSUE:**
During normal operation when pressure reaches 25 PSI target:
1. Control loop closes inflate valve (line 421-423)
2. Pump is still running → air trapped between pump and closed valve
3. Upstream pressure spikes to 89.9 PSI
4. Upstream safety relief triggers (not needed during normal operation)
5. This stresses the pump unnecessarily

**FIX:**
Changed pump shutdown sequence in normal operation (pressure >= TARGET_PRESSURE):
- **OLD**: Close inflate valve → stop pump
- **NEW**: Stop pump FIRST → wait 0.2s for pump to settle → THEN close inflate valve
- Location: Line 447-449 in balloon_control_api_vulnerable.py
- **RESULT**: Upstream buildup eliminated during normal operation ✅

### Attack Test Results (2026-03-19 18:31)
- Attack rate: 100 Hz (`--rate 0.01`)
- Real sensor: 2 Hz
- **Attack reached 67.97 PSI** (above 59.6 PSI average burst pressure) ✅
- Overpressure venting triggered correctly at 67.97 PSI
- Vented 67.97 → 15.41 PSI in ~1 second ✅
- System recovered to normal operation (25 PSI target) ✅
- **NO upstream overpressure warnings during normal operation** ✅
- Upstream safety relief present but not needed (would trigger at 70+ PSI if needed)

---

## Deployment State Evolution (2026-03-20)

### Before Cleanup (2026-03-20 SESSION START)

**Vulnerable Pi (192.168.50.100):**
- **Systemd Services Installed:**
  - `/etc/systemd/system/balloon-control-api.service` ✓ (inactive)
  - `/etc/systemd/system/balloon-sensor-publisher.service` ✓ (inactive)
- **Python Scripts (~/balloon-demo/scripts/):**
  - `balloon_control_api_vulnerable.py` (29K, Mar 19 - has safety features)
  - `sensor_publisher.py` (5.0K, Mar 15)
  - `test_pressure_sensor.py`
- **Currently Running:**
  - `sensor_publisher.py` → PID 3480827 (manual process, started Mar 19)
  - Control API → STOPPED
- **Files to Clean Up:**
  - `~/balloon_control_api_vulnerable.py` (duplicate in home dir)
  - `sensor_publisher.py` needs rename to `sensor_publisher_vulnerable.py`

**Secure Pi (10.30.0.25):**
- **Systemd Services Installed:**
  - `/etc/systemd/system/balloon-control-secure.service` ✓ (inactive)
  - `/etc/systemd/system/balloon-sensor-publisher-secure.service` ✓ (inactive)
  - `/etc/systemd/system/balloon-sensor-publisher.service` ⚠️ (inactive - should be removed)
- **Python Scripts (~/balloon-demo/scripts/):**
  - `balloon_control_secure.py` (last service run: Mar 17)
  - `sensor_publisher_secure.py`
  - `sensor_publisher.py` ⚠️ (should be removed)
  - `test_relays.py`
  - `test_pressure_sensor.py`
- **Currently Running:**
  - `sensor_publisher_secure.py` → PID 78263 (manual process, started Mar 17)
  - Control API → STOPPED
- **Files to Clean Up:**
  - `~/balloon-demo/scripts/sensor_publisher.py` (old/duplicate)
  - `/etc/systemd/system/balloon-sensor-publisher.service` (wrong service file)

**ISSUES FOUND:**
1. Neither system running as systemd services (both using manual processes)
2. Vulnerable Pi sensor publisher needs rename: `sensor_publisher.py` → `sensor_publisher_vulnerable.py`
3. Secure Pi has duplicate/old files to remove
4. Service files need updates to match renamed scripts

### Deployment Tasks Completed (2026-03-20)
- [x] Fix pump shutdown sequence (pump OFF first, then close inflate valve) ✅ COMPLETE
- [x] Deploy updated script to Vulnerable Pi ✅ COMPLETE
- [x] Test normal operation - verify no upstream overpressure ✅ VERIFIED
- [x] Test with attack to verify both safety features work during attack ✅ VERIFIED
- [x] Document current deployment state ✅ COMPLETE
- [x] Clean up Vulnerable Pi: Remove ~/balloon_control_api_vulnerable.py duplicate ✅ COMPLETE
- [x] Rename Vulnerable Pi: sensor_publisher.py → sensor_publisher_vulnerable.py ✅ COMPLETE
- [x] Update Vulnerable Pi service file to use sensor_publisher_vulnerable.py ✅ COMPLETE
- [x] Clean up Secure Pi: Remove sensor_publisher.py and its service file ✅ COMPLETE
- [x] Stop manual processes on both Pis ✅ COMPLETE
- [x] Enable and start services on Vulnerable Pi (balloon-control-api + sensor-publisher) ✅ COMPLETE
- [x] Enable and start services on Secure Pi (balloon-control-secure + sensor-publisher-secure) ✅ COMPLETE
- [x] Verify both systems running correctly as systemd services ✅ COMPLETE
- [x] Fix MQTT broker configuration on Vulnerable Pi (localhost → 10.30.0.51) ✅ COMPLETE (2026-03-20)
  - Changed MQTT_BROKER from "localhost" to "10.30.0.51"
  - Added authentication: `username.username_pw_set("username", "password")`
  - Verified publishing: `balloon/vulnerable/pressure`, `balloon/vulnerable/relays`, `balloon/vulnerable/sensor_source`
  - Backup created: `balloon_control_api_vulnerable.py.backup-20260320-*`

---

## EXPO Posterboard Evolution (2026-03-11)

### Initial 6-Poster Approach (COMPLETE BUT REPLACED)
- Original approach: 6 detailed posters (24×36 each) with extensive technical content
- Professor feedback: "Too much info, judges will be overwhelmed, letters too small"
- Completed all 6 posters but decided to simplify for EXPO presentation
- Files saved in Final Posters/ directory for reference

### Trifold Board Creation Process
- [x] Multiple AI-generated attempts (v1-v10) failed ✅ ABANDONED
  - Issues: dark backgrounds, overlaying text, sparse layouts, not matching UC template
  - Root cause: Claude AI Sonnet 4.6 couldn't interpret complex layout specs
- [x] Created TRIFOLD_TEXT_ONLY.txt ✅ COMPLETE (2026-03-10)
  - Plain text content organized by section for manual copy/paste
  - No layout instructions, just content
- [x] Manual PowerPoint editing ✅ SUCCESS (2026-03-11)
  - Used UC CEAS Trifold Board Template.pdf as base
  - Manual copy/paste from TRIFOLD_TEXT_ONLY.txt
  - Generated first_real_attempt.pdf - looks professional and clean
- [x] Abstract condensed by 1/3 ✅ COMPLETE
  - Original 4 paragraphs → condensed to 3 paragraphs
  - Shortened infrastructure details, tighter vulnerable/secure comparison
- [x] Results section structure finalized ✅ COMPLETE
  - Main "Results:" header (46pt red)
  - 3 paragraphs: methodology, vulnerable outcomes, secure outcomes
  - "Attack Outcomes:" subheading + IDS detection results
  - "Performance Outcomes:" subheading + infrastructure stability results
- [x] Final content organization verified ✅ COMPLETE
  - **LEFT panel (12"):** The Problem + Process
  - **CENTER panel (24"):** Abstract + Analysis
  - **RIGHT panel (12"):** Results (with subheadings) + References + Student/Advisor info
  - Advisor: Rob Kuschel, CTH / GE Aerospace

---

## Secure Pi Attack Detection False Positive (2026-03-23)

**Issue:** `attack_detected` flag remained stuck at `true` indefinitely after legitimate pressure events, even when no attacks were occurring.

**Symptoms:**
```json
"pressure_i2c": 26.34, "attack_detected": true, "rejected_network_count": 0
```
- Flag stuck `true` with 0 rejections
- All network sensors being accepted
- No actual attacks in progress

**Root Cause:**
Attack detection logic set `attack_detected = True` but never cleared it. Two trigger points:
1. **sensor_loop()**: `detect_attack()` function checked I2C pressure > 30 PSI (legitimate overshoot during inflation)
2. **/sensor endpoint**: Range validation, sensor mismatch, or rate-of-change violations

Once set to `true`, flag persisted forever because there was no clearing logic.

**Investigation Steps:**
1. Checked MQTT output: `attack_detected: true` persisting during normal 26 PSI operation
2. Examined `balloon_control_secure.py` code paths for attack flag setting
3. Found flag was set in multiple locations but never cleared:
   - Line 447: `attack_detected = True` in sensor_loop (I2C attack detection)
   - Line 692: `attack_detected = True` in /sensor (range check)
   - Line 710: `attack_detected = True` in /sensor (sensor mismatch)
   - Line 742: `attack_detected = True` in /sensor (rate-of-change)
4. No corresponding logic to set `attack_detected = False`

**Fix Applied:**
Added attack clearing mechanism with timeout:

1. **Global variables** (after line 108):
```python
last_attack_time = None  # Track when last attack was detected
ATTACK_CLEAR_TIMEOUT = 1.0  # Seconds of clean operation before clearing flag
```

2. **Modified sensor_loop() attack detection** (lines 444-456):
```python
is_attack, attack_desc = detect_attack(pressure_psi)

if is_attack:
    if not attack_detected:
        attack_detected = True
        log_to_wazuh("alert", f"ATTACK DETECTED: {attack_desc}", "security_attack")
    last_attack_time = datetime.now()
elif attack_detected and last_attack_time:
    # Check if enough time has passed since last attack
    time_since_attack = (datetime.now() - last_attack_time).total_seconds()
    if time_since_attack > ATTACK_CLEAR_TIMEOUT:
        attack_detected = False
        last_attack_time = None
        log_to_wazuh("info", "Attack cleared - system returned to normal", "attack_cleared")
```

3. **Updated /sensor endpoint** - Added `last_attack_time = datetime.now()` after each `attack_detected = True` statement (lines 693, 711, 743)

4. **Fixed false positive trigger** - Changed `detect_attack()` threshold from `> 30 PSI` to `> MAX_VALID_PRESSURE (100 PSI)` to avoid triggering on legitimate 32-34 PSI overshoot

5. **Added global declarations** - Added `last_attack_time` to both `sensor_loop()` and `update_sensor()` function globals

**File Modified:**
- `/balloon-demo/scripts/deployed_to_pi6/balloon_control_secure.py`

**Deployment:**
```bash
scp "/balloon-demo/scripts/deployed_to_pi6/balloon_control_secure.py" username@10.30.0.25:/home/username/balloon-demo/scripts/
ssh username@10.30.0.25 sudo systemctl restart balloon-control-secure.service
```

**Verification:**
```bash
mosquitto_sub -h 10.30.0.51 -u username -P password -t 'balloon/secure/status' -v
```

**Results:**
- ✅ During attack: `attack_detected: true`, `rejected_network_count` climbing
- ✅ 1 second after attack stops: `attack_detected: false`
- ✅ Normal operation: `attack_detected: false` consistently
- ✅ No false positives during 32-34 PSI overshoot
- ✅ Dual-target attack test: 143 attacks rejected, flag cleared properly

---

## Secure Pi Control Loop Oscillation (2026-03-23)

**Issue:** Secure Pi exhibited severe pressure oscillation: inflate to 36+ PSI → vent to 0.5 PSI → repeat cycle indefinitely.

**Symptoms:**
```
Cycle timeline:
- t=0s: Inflate from 2 PSI → 36 PSI (pump running)
- t=8s: Overpressure venting triggered (>35 PSI)
- t=10s: Deflated to 0.5 PSI (pump off, vents open)
- t=11s: Restart inflation from 0.5 PSI
- Repeat cycle every ~11 seconds
```

**Observable MQTT Data:**
```json
{"pressure_i2c": 26.63, "pressure_network": 36.33, "pressure_control": 36.33}
{"pressure_i2c": 20.72, "pressure_network": 36.33, "pressure_control": 36.33}  // Stale!
{"pressure_i2c": 5.46, "pressure_network": 36.33, "pressure_control": 36.33}   // Still stale!
{"pressure_i2c": 0.47, "pressure_network": 36.33, "pressure_control": 36.33}   // Dangerously stale!
```

**Root Cause:**
Network sensor lag + stale data retention during rapid pressure changes:

1. **Pump phase**: Pressure rising 10+ PSI/sec, network sensor lags 0.5-1 second behind I2C
2. **Network overshoot**: By the time network reports "30 PSI reached," I2C already at 34+ PSI
3. **Venting triggered**: Control sees network report 36 PSI → triggers overpressure venting (>35 PSI threshold)
4. **Rapid deflation**: Venting causes 15+ PSI/sec pressure drop
5. **Network rejections**: Rate-of-change validator rejects rapid deflation readings (exceeds 20 PSI/sec limit)
6. **Stale control data**: `current_pressure_network` retains last accepted value (36.33 PSI) indefinitely
7. **Control loop stuck**: System uses stale 36.33 PSI for control decisions while real pressure is 0.5 PSI
8. **Over-deflation**: Vents stay open until network sensor finally catches up and provides fresh data
9. **Cycle repeats**: Fresh data shows 0.5 PSI → pump restarts → cycle repeats

**Key Problem:** `current_pressure_network` variable persisted the last validated reading with no expiration. During rapid pressure changes when all new network readings were rejected, control loop used increasingly stale data.

**Investigation Steps:**
1. Observed oscillation pattern via MQTT monitoring
2. Noticed `pressure_network` lagging behind `pressure_i2c` during inflation
3. Identified `pressure_network` getting "stuck" at high values during deflation
4. Checked `/sensor` endpoint rejections: rate-of-change violations during venting
5. Confirmed `current_pressure_network` had no timeout mechanism
6. Traced control decision logic: always preferred network data when available, regardless of age

**Initial Fix Attempt (FAILED):**
Added 2-second timeout to clear stale network data:
```python
NETWORK_DATA_TIMEOUT = 2.0
if time_since_network > NETWORK_DATA_TIMEOUT:
    current_pressure_network = None  # Force I2C fallback
```
**Result:** Still oscillated - 2 seconds was too slow for 15 PSI/sec deflation rate.

**Working Solution (COMPLETE):**
Deployed version from `deployed_to_pi6/` directory which had simpler, more stable control logic:
- Uses validated network data when available
- Falls back to I2C during sensor rejection periods
- No explicit stale-data timeout (relies on continuous sensor updates at 2 Hz)
- Critical difference: TARGET_PRESSURE_MIN/MAX (25-30 PSI) instead of single TARGET_PRESSURE constant

**File Path Confusion:**
- Initially edited: `/balloon-demo/scripts/balloon_control_secure.py` (wrong file, had old 15/30 PSI sensor configs)
- Correct file: `/balloon-demo/scripts/deployed_to_pi6/balloon_control_secure.py` (100 PSI DATAQ sensors, 25 PSI target)

**Deployment:**
```bash
scp "/balloon-demo/scripts/deployed_to_pi6/balloon_control_secure.py" username@10.30.0.25:/home/username/balloon-demo/scripts/
ssh username@10.30.0.25 sudo systemctl restart balloon-control-secure.service
```

**Verification Test - Dual Attack:**
```bash
# From attacker laptop (192.168.50.191):
python3 attack_spoof.py --dual --pressure 0.0 --rate 0.1
```

**Results:**
```
Timeline during attack (15:46:05-15:46:29):
- 15:46:05-15:46:20: Normal operation, 28 PSI, rejected_count: 0
- 15:46:20: Attack begins, rejections: 0 → 34 (attack_detected: true)
- 15:46:21: Rejections climb: 34 → 78 → 123 → 143
- 15:46:22: Pressure stable 25-26 PSI, pump OFF (protected!)
- 15:46:23: Attack cleared (attack_detected: false), final rejections: 143
- 15:46:28: Pressure drops to 24.98 PSI (natural leak)
- 15:46:29: Pump restarts, inflates to 31.5 PSI, stops cleanly
- ✅ NO overshoot venting cycle
- ✅ NO oscillation
- ✅ System resumes normal operation smoothly
```

**Vulnerable Pi (comparison):**
- ✅ Accepted all spoofed 0.0 PSI data (100% compromise)
- ✅ Pump kept running continuously
- ✅ Real pressure exceeded safe limits

**Final State:**
- ✅ Secure Pi: Stable control, no oscillation, attack protection working
- ✅ Vulnerable Pi: Successfully compromised during attack
- ✅ System parity maintained: Both use network-based control, but secure has validation
- ✅ Demo ready: Clear contrast between vulnerable and secure systems

---

## Wazuh SIEM Keycloak SSO Broken After securityadmin.sh (2026-03-24)

**Issue:** Wazuh Dashboard Keycloak SSO authentication stopped working. OpenID login redirects to Keycloak successfully, user authenticates, but callback to Wazuh fails with `{"statusCode":401,"error":"Unauthorized","message":"Unauthorized"}`.

**Background:** SSO was documented as working previously but broke at some point. No configuration backups available from when it was functional.

**Symptoms:**
- Dashboard loads at `https://10.30.0.55` ✓
- "Log in with single sign-on" button redirects to Keycloak ✓
- User authentication in Keycloak succeeds ✓
- Redirect back to Wazuh fails with 401 Unauthorized ✗
- Dashboard logs: `OpenId authentication failed: Error: Authentication Exception`
- OpenSearch logs: `No 'Authorization' header, send 401` or completely silent (no OpenID attempts logged)

**Root Cause:** Running `/usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh` to apply OpenID configuration to OpenSearch changed SSL client certificate requirements, breaking the dashboard-to-OpenSearch connection.

**Investigation Timeline (2026-03-24 00:00-05:30 UTC):**

### Phase 1: Initial Diagnosis (00:00-01:30)
1. **Verified Keycloak configuration:**
   - Client: `wazuh` in `hospital-homelab` realm
   - Client authentication: ON (confidential client)
   - Valid redirect URIs: `https://10.30.0.55/*` ✓
   - Standard flow: ENABLED ✓
   - Client secret: `client-secret` ✓
   - Realm roles mapper configured to include roles in tokens ✓

2. **Checked OpenSearch security configuration:**
   - `/etc/wazuh-indexer/opensearch-security/config.yml` had basic_internal_auth_domain but missing OpenID config
   - Added `openid_auth_domain` with client credentials:
     ```yaml
     openid_auth_domain:
       description: "Authenticate via Keycloak OpenID Connect"
       http_enabled: true
       transport_enabled: false
       order: 1
       http_authenticator:
         type: openid
         challenge: false
         config:
           openid_connect_url: "http://10.30.0.57:8080/realms/hospital-homelab/.well-known/openid-configuration"
           subject_key: preferred_username
           roles_key: roles
           client_id: wazuh
           client_secret: password
       authentication_backend:
         type: noop
     ```

3. **Updated role mappings:**
   - Added `username` and `username` to `all_access` role in `/etc/wazuh-indexer/opensearch-security/roles_mapping.yml`

4. **Enabled debug logging:**
   - Added `logger.org.opensearch.security: DEBUG` to `/etc/wazuh-indexer/opensearch.yml`

**Result:** Config changes made but NOT applied to running OpenSearch instance yet. Error persisted.

### Phase 2: Dashboard Configuration (01:30-02:30)
5. **Discovered missing cookie encryption password:**
   - Dashboard config at `/etc/wazuh-dashboard/opensearch_dashboards.yml` had all OpenID settings EXCEPT cookie encryption key
   - Dashboard was failing to store session cookies in OpenSearch, causing "cookie-session-storage Error: Unauthorized" in logs
   - Added:
     ```yaml
     opensearch_security.cookie.secure: true
     opensearch_security.cookie.password: "atleast32charactersLongSecurePasswordForCookieEncryption2026"
     ```

6. **Applied OpenSearch security config with securityadmin.sh:**
   ```bash
   export OPENSEARCH_JAVA_HOME=/usr/share/wazuh-indexer/jdk
   sudo -E /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh \
     -cd /etc/wazuh-indexer/opensearch-security/ \
     -icl -nhnv \
     -cacert /etc/wazuh-indexer/certs/root-ca.pem \
     -cert /etc/wazuh-indexer/certs/admin.pem \
     -key /etc/wazuh-indexer/certs/admin-key.pem
   ```
   **Output:** "Done with success" ✓

**Result:** Config applied successfully, but **NEW ERROR APPEARED** - dashboard could no longer connect to OpenSearch at all!

### Phase 3: SSL Certificate Rejection Crisis (02:30-04:30)
7. **Dashboard completely broken after securityadmin.sh:**
   - Error: `sslv3 alert certificate unknown` (SSL certificate rejected)
   - Dashboard showing "Wazuh did not load properly. Check the server output for more information."
   - OpenSearch rejecting ALL connections from dashboard, not just OpenID

8. **Attempted Fix #1 - Add client certificates to dashboard:**
   - Added to `/etc/wazuh-dashboard/opensearch_dashboards.yml`:
     ```yaml
     opensearch.ssl.certificate: "/etc/wazuh-dashboard/certs/dashboard.pem"
     opensearch.ssl.key: "/etc/wazuh-dashboard/certs/dashboard-key.pem"
     ```
   - **Result:** FAILED - Still getting `sslv3 alert certificate unknown`

9. **Attempted Fix #2 - Remove client certificates:**
   - Removed the cert lines added above
   - **Result:** FAILED - Still getting SSL errors

10. **Attempted Fix #3 - Set clientauth_mode: OPTIONAL:**
    - Added to `/etc/wazuh-indexer/opensearch.yml`:
      ```yaml
      plugins.security.ssl.http.clientauth_mode: OPTIONAL
      ```
    - Restarted OpenSearch and dashboard
    - **Result:** FAILED - 10+ SSL errors still appearing

11. **Attempted Fix #4 - Set clientauth_mode: NONE:**
    - Changed to `clientauth_mode: NONE`
    - **Result:** FAILED - SSL errors persisted, AND this prevented admin cert from working

12. **HTTP vs HTTPS Investigation (03:00-03:30):**
    - Compared with working Grafana SSO setup
    - Grafana: HTTP on port 3000, Keycloak: HTTP → works perfectly ✓
    - Wazuh: HTTPS on port 443, Keycloak: HTTP → broken ✗
    - **Hypothesis:** Mixed content (HTTPS ↔ HTTP) causing browser to block cookies

13. **Attempted Fix #5 - Switch Wazuh to HTTP:**
    - Changed `/etc/wazuh-dashboard/opensearch_dashboards.yml`:
      ```yaml
      server.port: 80
      server.ssl.enabled: false
      opensearch_security.openid.base_redirect_url: "http://10.30.0.55"
      ```
    - Updated Keycloak client redirect URIs to `http://10.30.0.55/*`
    - **Result:** FAILED - Port 80 blocked by firewall (UDM-SE only allows port 443)

14. **Reverted to HTTPS (03:30-04:00):**
    - Changed back to port 443 and HTTPS
    - Updated Keycloak back to `https://10.30.0.55/*`
    - **SSL errors still persisting**

### Phase 4: Root Cause Identified (04:00-04:30)
15. **Discovered the real issue:**
    - Running `securityadmin.sh` changed OpenSearch's SSL client certificate requirements
    - Even with `clientauth_mode: NONE`, OpenSearch was rejecting dashboard connections
    - The cookie password we added was correct, but OpenSearch backend SSL was fundamentally broken
    - **NO BACKUP** of the original working OpenSearch security configuration

16. **Key Finding:**
    - OpenSearch DEBUG logs showed ZERO OpenID authentication attempts reaching the backend
    - Dashboard was failing during token exchange with Keycloak OR before sending token to OpenSearch
    - The entire SSL connection was broken, not just OpenID authentication

### Phase 5: Resolution - Revert Security Config (04:30-05:30)
17. **Decision: Remove OpenID config and restore basic functionality:**
    - Edited `/etc/wazuh-indexer/opensearch-security/config.yml`
    - **Removed entire `openid_auth_domain` section**
    - Kept only `basic_internal_auth_domain`

18. **Problem: securityadmin.sh failed:**
    - Error: `Connected as null` - admin certificate not being recognized
    - Cause: `clientauth_mode: NONE` in opensearch.yml was blocking ALL client certs

19. **Fix: Remove clientauth_mode setting:**
    - Deleted `plugins.security.ssl.http.clientauth_mode: NONE` from opensearch.yml
    - Restarted OpenSearch

20. **Successfully reverted security config:**
    ```bash
    export OPENSEARCH_JAVA_HOME=/usr/share/wazuh-indexer/jdk
    sudo -E /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh \
      -cd /etc/wazuh-indexer/opensearch-security/ \
      -icl -nhnv \
      -cacert /etc/wazuh-indexer/certs/root-ca.pem \
      -cert /etc/wazuh-indexer/certs/admin.pem \
      -key /etc/wazuh-indexer/certs/admin-key.pem
    ```
    **Output:** "Done with success" ✓

21. **Restarted dashboard:**
    ```bash
    sudo systemctl restart wazuh-dashboard
    ```

22. **Verification:**
    - Dashboard loads at `https://10.30.0.55` ✓
    - Basic auth login works (admin / password) ✓
    - SSL errors gone ✓
    - OpenSearch connection restored ✓
    - SSO button removed (OpenID config no longer present) ✓

### Phase 6: MQTT Broker Agent Issue (05:00-05:30)
23. **Secondary issue discovered:**
    - Wazuh dashboard showed `MQTT_Broker_VM` agent (ID 006) as "Disconnected"
    - New agent `mqttbroker` (ID 015) showing "Never connected"

24. **Root cause:**
    - Agent re-registered itself with hostname `mqttbroker` (new ID 015)
    - Old registration `MQTT_Broker_VM` (ID 006) still in database

25. **Fix:**
    ```bash
    # On MQTT VM:
    ssh username@10.30.0.51
    sudo systemctl restart wazuh-agent

    # Verify from manager:
    sudo /var/ossec/bin/agent_control -l | grep "015\|mqttbroker"
    # Output: ID: 015, Name: mqttbroker, IP: any, Active ✓
    ```

26. **Cleanup (optional):**
    - Can remove duplicate agent ID 006 with: `sudo /var/ossec/bin/manage_agents -r 006`

**Final Configuration State:**

**Files Modified:**
- `/etc/wazuh-dashboard/opensearch_dashboards.yml`:
  - ✓ Cookie encryption password added (retained)
  - ✓ Port 443, HTTPS enabled (retained)
  - ✓ All OpenID settings present but non-functional (retained for reference)

- `/etc/wazuh-indexer/opensearch-security/config.yml`:
  - ✗ OpenID auth domain **REMOVED**
  - ✓ Basic internal auth domain (only method available)

- `/etc/wazuh-indexer/opensearch.yml`:
  - ✗ `clientauth_mode` setting **REMOVED**
  - ✓ Debug logging enabled (retained)

**What Works:**
- ✅ Wazuh Dashboard basic authentication (admin login)
- ✅ Dashboard-to-OpenSearch SSL connection
- ✅ All Wazuh agents reporting (15 agents active)
- ✅ MQTT broker agent reconnected
- ✅ All core functionality operational

**What Doesn't Work:**
- ❌ Keycloak SSO authentication (OpenID config removed)
- ❌ "Log in with single sign-on" button (no longer functional)

**Why This Happened:**
1. Running `securityadmin.sh` to add OpenID config changed OpenSearch's SSL requirements
2. The dashboard-to-OpenSearch SSL connection broke completely
3. No backup of the original working OpenSearch security configuration existed
4. Unable to determine what changed between "working SSO" state and current state
5. Only resolution was to revert to basic auth to restore dashboard functionality

**Lessons Learned:**
1. **ALWAYS backup security configs before running securityadmin.sh**
2. **Document working SSO configuration in detail** (what made it work before)
3. **Test in non-production first** when changing OpenSearch security settings
4. **The cookie password fix was correct** - would have worked if SSL connection wasn't broken

**Future SSO Restoration:**
To restore Keycloak SSO in the future:
1. Need to identify what the OpenSearch security configuration looked like when SSO was working
2. Check for any VM snapshots or backups from that time period
3. Compare OpenSearch SSL settings between working and broken states
4. Likely need different `clientauth_mode` or certificate configuration
5. The dashboard config (including cookie password) is already correct

**Workaround:**
Use basic authentication: `admin` / `password`

---

## PostgreSQL Archival Verification and Troubleshooting (2026-03-25)

**Issue:** Need to verify pg_cron automated archival is running correctly and maintaining 7-day retention in active table.

**Background:**
- PostgreSQL has `heartrate_data` (active, 7-day retention) and `heartrate_data_archive` (historical, unlimited retention)
- pg_cron job runs daily at 2 AM UTC (10 PM EDT) to move data older than 7 days to archive
- Job was fixed on 2026-03-23 after "connection failed" errors by setting `cron.database_name = 'hospital_data'` in postgresql.conf

**Verification Procedure:**

1. **SSH to PostgreSQL VM:**
   ```bash
   ssh username@10.30.0.50  # Password: password
   sudo -u postgres psql -d hospital_data
   ```

2. **Check pg_cron job status (last 5 runs):**
   ```sql
   SELECT
       jobid,
       runid,
       status,
       return_message,
       start_time,
       end_time
   FROM cron.job_run_details
   WHERE start_time IS NOT NULL
   ORDER BY start_time DESC
   LIMIT 5;
   ```

   **Expected:**
   - ✅ Recent runs with `status: succeeded`
   - ✅ `return_message: 1 row`
   - ✅ `start_time` around 22:00 EDT (previous day) or 02:00 UTC
   - ✅ Run duration: 2-3 minutes typical

   **Problem indicators:**
   - ❌ `status: failed`
   - ❌ `return_message: connection failed` → pg_cron can't connect to database
   - ❌ No recent runs (last run > 24 hours ago)

3. **Check job configuration:**
   ```sql
   SELECT * FROM cron.job;
   ```

   **Expected:**
   - ✅ `schedule: 0 2 * * *` (2 AM UTC daily)
   - ✅ `command: SELECT archive_old_heartrate_data();`
   - ✅ `database: hospital_data`
   - ✅ `active: t` (true)

4. **Check active table status:**
   ```sql
   SELECT
       'heartrate_data' as table_name,
       pg_size_pretty(pg_total_relation_size('heartrate_data')) as total_size,
       COUNT(*) as row_count,
       MIN(timestamp) as oldest_record,
       MAX(timestamp) as newest_record,
       NOW() - MIN(timestamp) as data_age
   FROM heartrate_data;
   ```

   **Expected:**
   - ✅ `oldest_record` within last **7-8 days** (allows for time until next run)
   - ✅ `newest_record` within last few seconds (current time)
   - ✅ Row count: ~60-70M rows typical for 7 days

   **Problem indicators:**
   - ❌ `oldest_record` > 10 days ago → archival not running
   - ❌ Table size growing indefinitely

5. **Check archive table status:**
   ```sql
   SELECT
       'heartrate_data_archive' as table_name,
       pg_size_pretty(pg_total_relation_size('heartrate_data_archive')) as total_size,
       COUNT(*) as row_count,
       MIN(timestamp) as oldest_record,
       MAX(timestamp) as newest_record
   FROM heartrate_data_archive;
   ```

   **Expected:**
   - ✅ Row count growing over time (receives archived data daily)
   - ✅ `newest_record` should be ~7 days old (data that was just archived)

**Common Issues and Fixes:**

### Issue 1: pg_cron Job Showing "connection failed"

**Symptom:**
```sql
SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 5;
-- Shows: status: failed, return_message: connection failed
```

**Cause:** pg_cron doesn't know which database to connect to.

**Fix:**
```bash
# Exit psql
\q

# Edit PostgreSQL config
sudo nano /etc/postgresql/16/main/postgresql.conf

# Add or verify this line exists:
cron.database_name = 'hospital_data'

# Save and exit (Ctrl+X, Y, Enter)

# Restart PostgreSQL
sudo systemctl restart postgresql

# Wait 10 seconds, then verify
sleep 10
sudo -u postgres psql -d hospital_data -c "SHOW cron.database_name;"
```

**Expected output:** `hospital_data`

### Issue 2: Active Table Has More Than 7-8 Days of Data

**Symptom:**
```sql
SELECT MIN(timestamp), NOW() - MIN(timestamp) FROM heartrate_data;
-- Shows data older than 8 days
```

**Cause:** Archival job not running or failing silently.

**Fix:**
```sql
-- Manually trigger archival
SELECT archive_old_heartrate_data();
```

**Expected output:**
```
NOTICE:  Daily archival complete: XXXXXX rows archived, XXXXXX rows deleted from cutoff YYYY-MM-DD HH:MM:SS
```

**Verify:**
```sql
SELECT MIN(timestamp) FROM heartrate_data;
-- Should now show timestamp from exactly 7 days ago
```

### Issue 3: pg_cron Not Loaded

**Symptom:**
```sql
SELECT * FROM cron.job;
-- ERROR: relation "cron.job" does not exist
```

**Cause:** pg_cron extension not installed or not loaded in shared_preload_libraries.

**Fix:**
```bash
# Check if pg_cron is in shared libraries
sudo grep shared_preload_libraries /etc/postgresql/16/main/postgresql.conf

# Expected: shared_preload_libraries = 'pg_cron'
# If missing, add it and restart PostgreSQL
```

**Manual Archival for Cleanup:**

If archival hasn't run in several days, manually run:

```sql
-- This archives data older than 7 days
SELECT archive_old_heartrate_data();

-- Optional: Reclaim disk space (can take 5-10 minutes)
VACUUM FULL heartrate_data;
```

**Note:** `VACUUM FULL` locks the table and should be run during low-traffic periods. Autovacuum will gradually reclaim space without downtime.

**Verification Results (2026-03-25):**
- ✅ Job running successfully: Last run 2026-03-24 22:00 EDT (succeeded)
- ✅ Active table: 59.8M rows, oldest record 2026-03-18 (7 days)
- ✅ Archive table: 873.7M rows, 131 GB preserved
- ✅ Manual test: 764,743 rows successfully archived
- ✅ Schedule: 10 PM EDT daily (2 AM UTC)

**Status:** RESOLVED - Archival working correctly, verification procedure documented.

**Status:** Resolved (dashboard functional with basic auth), SSO remains broken by design (removed to restore functionality)
