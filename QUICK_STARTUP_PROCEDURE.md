# Quick Startup Procedure

**Last Updated:** 2026-03-24
**Purpose:** Simple step-by-step guide to start the hospital homelab from powered-down state

---

## Total Time: ~30 minutes

---

## Step 0: Air-Gap/Expo Mode Setup (OPTIONAL - Required if no internet available)

⚠️ **CRITICAL FOR EXPO:** The UDM-SE requires WAN link-up for cross-VLAN routing to work. Without this, VLAN 2 ↔ VLAN 30 communication fails.

**Mock WAN Setup:**
1. Take a **spare Ethernet cable**
2. Plug one end into **UDM-SE WAN port**
3. Plug other end into:
   - **Any open port on the 24-port switch**, OR
   - **A small travel router/dumb switch** (brings to expo)
4. Wait 30 seconds for link to establish
5. Verify cross-VLAN connectivity works (test after Step 2)

**Why this works:** UDM-SE checks for physical link-up on WAN port. With a cable plugged in (even without real internet), inter-VLAN routing enables properly.

**What to bring to expo:**
- Small 5-port dumb switch ($15-20) OR travel router
- 1 short Ethernet cable (1-3 feet)

---

## Step 1: Power On (5 minutes)

### Order:
1. **UDM-SE Gateway** - Power on FIRST, wait 2-3 minutes
2. **UniFi Switch** - Power on SECOND, wait 1 minute
3. **TrueNAS Server** - Press power button, wait 5 minutes
4. **Raspberry Pis** - Plug in external power adapters (Pi #5, Secure Pi, Vulnerable Pi)
   - PoE Pis (1-4) auto-power when switch is on

---

## Step 2: Wait for VMs to Boot (15 minutes)

All VMs auto-start when TrueNAS boots. Wait **15 minutes** after powering on TrueNAS.

**Critical VMs that must be up:**
- PostgreSQL (10.30.0.50)
- MQTT Broker (10.30.0.51)
- Keycloak (10.30.0.57)
- Node-RED (10.30.0.52)
- Grafana (10.30.0.53)
- Wazuh (10.30.0.55)
- Vault (10.30.0.58)

---

## Step 3: Unseal Vault (2 minutes) ⚠️ REQUIRED

**URL:** http://10.30.0.58:8200

1. Open browser to Vault URL
2. You'll see "Unseal Vault" page
3. Enter these 3 keys one at a time, clicking "Unseal" after each:
   - `password`
   - `password`
   - `password`
4. Page will redirect to login - Vault is ready

**To login:** Select "Token" method, enter: `password`

---

## Step 4: Restart Pi Services (3 minutes) ⚠️ CURRENTLY REQUIRED

**Known Issue:** Pi services don't auto-start reliably after power cycle.

### Restart all Pi heart rate services:

```bash
ssh username@10.30.0.20 "sudo systemctl restart heartrate1.service"
ssh username@10.30.0.21 "sudo systemctl restart heartrate2.service"
ssh username@10.30.0.22 "sudo systemctl restart heartrate3.service"
ssh username@10.30.0.23 "sudo systemctl restart heartrate4.service"
ssh username@10.30.0.24 "sudo systemctl restart heartrate5.service"
```

**Password for all:** `password`

### Restart balloon demo services (if needed):

**Secure Pi (VLAN 30):**
```bash
ssh username@10.30.0.25 "sudo systemctl restart balloon-control-secure.service"
```

**Vulnerable Pi (VLAN 2) - TWO services required:**
```bash
ssh username@192.168.50.100 "sudo systemctl restart balloon-sensor-publisher.service"
ssh username@192.168.50.100 "sudo systemctl restart balloon-control-api.service"
```

### Restart IDS pipeline (if Grafana IDS dashboard shows no new data):

**Suricata laptop (VLAN 2):**
```bash
ssh username@192.168.50.191 "sudo systemctl restart filebeat"
```
**Note:** Filebeat ships Suricata logs to Elasticsearch (10.30.0.60). Requires cross-VLAN firewall exception.

---

## Step 5: Verify Everything Works (10 minutes)

### Quick Visual Check:

**1. Node-RED Dashboard** - http://10.30.0.52:1880/ui
- ✅ All 5 heart rate gauges updating (1-5)
- ✅ All 5 ECG waveforms scrolling (green traces, Pi #4 in red for AFib)
- ✅ 4 balloon pressure gauges updating (Vulnerable Pi upstream/downstream, Secure Pi upstream/downstream)
- ✅ Security Status Panel (bottom right) showing "SYSTEM SECURE" in green

**2. Grafana** - http://10.30.0.53:3000
- ✅ Heart rate dashboards loading
- ✅ All 5 Pis showing data
- ✅ "Tachycardia Alert - BPM > 100" firing for Pi #4 (AFib simulation)
- ✅ IDS Dashboard showing recent events (if starred)

**3. Wazuh** - https://10.30.0.55
- Login: `admin` / `password`
- ✅ All 14 agents showing "Active"
- ✅ Historical SIEM data visible

---

### Complete Pipeline Verification (Optional - For Troubleshooting):

**Pipeline #1: Hospital Heart Rate (Pi → MQTT → Node-RED → PostgreSQL → Mirth → FHIR)**

Check PostgreSQL data ingestion:
```bash
ssh username@10.30.0.50
# Password: password
sudo -u postgres psql -d hospital_data -c "SELECT pi_id, MAX(timestamp) as latest FROM heartrate_data GROUP BY pi_id ORDER BY pi_id;"
exit
```
- ✅ All 5 Pis showing timestamps within last 10-20 seconds

Check PostgreSQL archival job (optional - verify 7-day retention):
```bash
ssh username@10.30.0.50
sudo -u postgres psql -d hospital_data
-- Check last archival run
SELECT status, return_message, start_time, end_time
FROM cron.job_run_details
WHERE start_time IS NOT NULL
ORDER BY start_time DESC LIMIT 1;
-- Check active table data age
SELECT MIN(timestamp) as oldest, NOW() - MIN(timestamp) as age FROM heartrate_data;
\q
exit
```
- ✅ Last run: `status: succeeded`, within last 24 hours
- ✅ Oldest record: 7-8 days old (next run will archive older data)
- ❌ If older than 10 days: See TROUBLESHOOTING_HISTORY.md "PostgreSQL Archival Verification"

Check Mirth Connect channel:
- Open: https://10.30.0.54:8443 (Login: `admin` / `password`)
- ✅ Channel `HeartRate_FHIR_Final` status: Started
- ✅ "Received" and "Sent" counters climbing, "Queued" and "Errored" static

Check HAPI FHIR resource creation:
```bash
ssh username@10.30.0.50
curl -s "http://10.30.0.56:8080/fhir/Observation?_sort=-_lastUpdated&_count=5" | head -20
exit
```
- ✅ Should show recent FHIR Observation resources with recent timestamps

**Pipeline #2: Balloon Demo (Vulnerable Pi + Secure Pi → MQTT → Node-RED)**

Check Vulnerable Pi services:
```bash
ssh username@192.168.50.100
# Password: password
sudo systemctl status balloon-sensor-publisher.service
sudo systemctl status balloon-control-api.service
exit
```
- ✅ Both services "active (running)"
- ✅ Recent log entries showing pressure readings

Check Secure Pi service:
```bash
ssh username@10.30.0.25
sudo systemctl status balloon-control-secure.service
exit
```
- ✅ Service "active (running)"
- ✅ MQTT connection successful

**Pipeline #3: IDS (Suricata → Filebeat → Elasticsearch → Grafana)**

Check Filebeat on Suricata laptop:
```bash
ssh username@192.168.50.191
# Password: password
sudo systemctl status filebeat
exit
```
- ✅ Service "active (running)"
- ✅ Recent log entries showing events published to Elasticsearch

Check Elasticsearch connectivity:
```bash
ssh username@192.168.50.191
curl -k -u elastic:password https://10.30.0.60:9200/_cluster/health?pretty
exit
```
- ✅ Should show cluster health (status: "yellow" is normal for single-node)

Check Grafana IDS Dashboard:
- Open: http://10.30.0.53:3000
- Navigate to IDS Dashboard
- Set time range: "Last 15 minutes"
- ✅ "Events Over Time" showing data
- ✅ "Top Source IPs" and "Top Destination IPs" tables populated

---

## Common Issues

### Cannot Ping or SSH to VLAN 2 Devices (Vulnerable Pi, Suricata Laptop)
**Symptom:** Cannot reach 192.168.50.100 or 192.168.50.191 from VLAN 30 workstation
**Cause:** UDM-SE requires WAN link-up for cross-VLAN routing
**Fix:**
1. Verify **Step 0** completed (mock WAN cable plugged in)
2. If WAN cable is connected, check UDM-SE firewall rules (see below)

### Cross-VLAN Communication Fails (Air-Gap Mode)
**Symptom:** Can ping VLAN 30 devices (10.30.0.x) but not VLAN 2 devices (192.168.50.x)
**Cause:** UDM-SE blocks inter-VLAN routing when WAN is disconnected
**Fix:** **Step 0 - Mock WAN Setup** is REQUIRED
- Plug UDM-SE WAN port into switch or travel router
- This provides physical link-up without requiring real internet
- Wait 30 seconds after connecting, then test cross-VLAN ping

### Vulnerable Pi Not Showing Data in Node-RED
**Symptom:** Balloon demo gauges at 0 for Vulnerable Pi, Secure Pi works fine
**Cause:** Firewall blocking VLAN 2 → VLAN 30 MQTT traffic (192.168.50.100 → 10.30.0.51:1883)
**Diagnosis:**
```bash
ssh username@192.168.50.100
# Test MQTT connectivity
timeout 5 bash -c 'cat < /dev/null > /dev/tcp/10.30.0.51/1883' && echo "Port 1883 open" || echo "Port 1883 blocked"
exit
```
**Fix:**
1. Open UDM-SE Web UI: https://10.30.0.1
2. Settings → Security → Firewall → Create New Rule
3. Configure:
   - Name: `ALLOW_VULNERABLE_PI_TO_MQTT`
   - Action: Accept
   - Priority: **19998** (must be ABOVE rule 20001 which blocks VLAN2→VLAN30)
   - Type: LAN In
   - Protocol: TCP
   - Source: IP Address `192.168.50.100`
   - Destination: IP Address `10.30.0.51`
   - Port: `1883`
4. Save rule
5. Restart Vulnerable Pi services:
   ```bash
   ssh username@192.168.50.100
   sudo systemctl restart balloon-sensor-publisher.service
   sudo systemctl restart balloon-control-api.service
   exit
   ```

### Grafana IDS Dashboard Shows No New Data
**Symptom:** IDS dashboard frozen at old timestamp, no recent events
**Cause:** Filebeat cannot reach Elasticsearch (192.168.50.191 → 10.30.0.60:9200 blocked)
**Diagnosis:**
```bash
ssh username@192.168.50.191
curl -k https://10.30.0.60:9200/_cluster/health?pretty
# If this hangs/timeouts, firewall is blocking
exit
```
**Fix:**
1. Open UDM-SE Web UI: https://10.30.0.1
2. Settings → Security → Firewall → Create New Rule
3. Configure:
   - Name: `ALLOW_SURICATA_TO_ELASTICSEARCH`
   - Action: Accept
   - Priority: **19999** (must be ABOVE rule 20001)
   - Type: LAN In
   - Protocol: TCP
   - Source: IP Address `192.168.50.191`
   - Destination: IP Address `10.30.0.60`
   - Port: `9200`
4. Save rule
5. Restart Filebeat:
   ```bash
   ssh username@192.168.50.191
   sudo systemctl restart filebeat
   exit
   ```
6. Refresh Grafana IDS dashboard (set time range to "Last 15 minutes")

### Switch Uplink Not Connected
**Symptom:** Can ping TrueNAS/VMs but not Pis
**Fix:** Unplug and replug the switch uplink cable

### Vault Shows "Sealed"
**Symptom:** Vault web UI shows red "Sealed" banner
**Fix:** Follow Step 3 to unseal (this is normal after power loss)

### Node-RED Shows No Data (Hospital Pis)
**Symptom:** Heart rate gauges at 0, no ECG waveforms
**Fix:** Restart Pi services (Step 4)

### Grafana Missing Pi Data (Hospital Monitors)
**Symptom:** Only some Pis showing in Grafana heart rate dashboards
**Fix:** Check PostgreSQL query (Pipeline #1 verification) - if Pis missing, restart their services

---

## Login Credentials Quick Reference

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| **Node-RED** | http://10.30.0.52:1880 | SSO | `username` / `password` |
| **Grafana** | http://10.30.0.53:3000 | `admin` | `password` |
| **Wazuh** | https://10.30.0.55 | `admin` | `password` |
| **Vault** | http://10.30.0.58:8200 | Token | `password` |
| **Mirth Connect** | https://10.30.0.54:8443 | `admin` | `password` |
| **TrueNAS** | http://10.30.0.44 | `username` | `password` |
| **UDM-SE** | https://10.30.0.1 | `username` | `password` |

**SSH Credentials:**
- **Hospital Pis (1-5):** `r-pi-{1..5}@10.30.0.{20..24}` / `password`
- **Balloon Pis:** `username@10.30.0.25` and `username@192.168.50.100` / `password`
- **Suricata Laptop:** `username@192.168.50.191` / `password`
- **PostgreSQL VM:** `username@10.30.0.50` / `password`

---

## Notes

- **Verified:** 2026-03-24 full power cycle test + air-gap mode testing
- **Expected downtime:** System fully operational 30 minutes after power-on (includes pipeline verification)
- **Manual steps:** Vault unseal, Pi service restarts, and optional pipeline verification
- **Historical data:** All SIEM logs and database records preserved across reboots
- **Air-Gap Operation:** Mock WAN setup (Step 0) is REQUIRED for expo/air-gap mode
  - UDM-SE requires WAN link-up for cross-VLAN routing between VLAN 30 ↔ VLAN 2
  - Bring: Small dumb switch ($15) + short Ethernet cable to expo
- **Firewall Rules:** Two cross-VLAN exceptions required for full system operation:
  - `ALLOW_VULNERABLE_PI_TO_MQTT` (192.168.50.100 → 10.30.0.51:1883)
  - `ALLOW_SURICATA_TO_ELASTICSEARCH` (192.168.50.191 → 10.30.0.60:9200)
  - Both must have priority < 20001 to process before BLOCK_VLAN2_TO_VLAN30 rule
- **Pipelines Verified:** Hospital Heart Rate, Balloon Demo, PostgreSQL Ingestion, Grafana Dashboards, Mirth→FHIR, IDS (Suricata→Elasticsearch→Grafana)

---

## Related Documentation

- `SYSTEM_STARTUP_GUIDE.md` - Detailed troubleshooting and technical information
- `CLAUDE.md` - Complete project architecture and configuration reference
- `TROUBLESHOOTING_HISTORY.md` - Historical issue resolution documentation
