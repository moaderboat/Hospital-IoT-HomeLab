# Action Items - Hospital Homelab & Balloon Demo

**Created:** 2026-02-05
**Last Updated:** 2026-02-05

---

## 🔥 THIS WEEKEND (HIGH PRIORITY)

### 1. 🛒 Order Mason Jars & I²C Extension Wires
**Priority:** HIGH - Needed for balloon demo sensors
**Time Estimate:** 30 minutes
**Cost:** ~$25-30
**Status:** [ ] Not Started

**Why Important:**
- BMP388 sensors already arrived (2026-02-05)
- Sensors unusable without pressure chambers
- Mason jars = pressure chambers for sensor setup
- This unblocks sensor testing while waiting for relay HAT

---

### 2. ⚡ Enable I²C on Both Balloon Pis
**Priority:** HIGH - Quick win, unblocks sensor testing
**Time Estimate:** 5 minutes
**Status:** [ ] Not Started

**Why Important:**
- Required before BMP388 sensors can be detected
- Must be done before connecting sensors
- Simple configuration change - do this today!

**Action Steps:**
1. SSH to PostgreSQL VM:
   ```bash
   ssh username@10.30.0.50
   ```

2. Choose a strategy:

   **Option A: Create Archive Table (Recommended)**
   ```sql
   sudo -u postgres psql -d hospital_data

   -- Create archive table
   CREATE TABLE heartrate_data_archive (LIKE heartrate_data INCLUDING ALL);

   -- Create index on archive table
   CREATE INDEX idx_archive_timestamp ON heartrate_data_archive(timestamp);

   -- Move data older than 90 days to archive
   INSERT INTO heartrate_data_archive
   SELECT * FROM heartrate_data
   WHERE timestamp < NOW() - INTERVAL '90 days';

   DELETE FROM heartrate_data
   WHERE timestamp < NOW() - INTERVAL '90 days';

   -- Vacuum to reclaim space
   VACUUM FULL heartrate_data;
   ```

   **Option B: Set Simple Retention (Quick Fix)**
   ```sql
   -- Delete data older than 90 days (run monthly)
   DELETE FROM heartrate_data
   WHERE timestamp < NOW() - INTERVAL '90 days';

   VACUUM FULL heartrate_data;
   ```

3. Create monthly maintenance cron job:
   ```bash
   crontab -e

   # Add this line (runs 1st of each month at 2 AM):
   0 2 1 * * psql -d hospital_data -c "DELETE FROM heartrate_data WHERE timestamp < NOW() - INTERVAL '90 days'; VACUUM FULL heartrate_data;"
   ```

4. Document the retention policy in NETWORK_SETUP_PROGRESS.md

**Success Criteria:**
- [ ] Archive table created OR retention policy set
- [ ] Data older than 90 days moved/deleted
- [ ] Monthly cron job configured
- [ ] Policy documented

---

## 📅 NEXT 2 WEEKS (MEDIUM PRIORITY)

### 3. 📊 Implement PostgreSQL Data Retention Policy
**Priority:** MEDIUM - Plan ahead, not urgent
**Time Estimate:** 2-3 hours
**Status:** [ ] Not Started

**Why This Can Wait:**
- Database has 397,645,663 rows (46+ days of data)
- Growing at 8.6 million rows/day
- **BUT: 957GB free space remaining (~18-24 months runway)**
- NOT an immediate crisis - you have time to plan this properly

**Why You Should Still Do It:**
- Need HIPAA-compliant retention policy (6 years for audit logs)
- Easier to set up now than clean up later
- Best practice to have data lifecycle management

**What to Buy:**

**LOCAL PICKUP (Today/This Week):**
- [ ] **Ball 4oz Mason Jars (12-pack)** - $10-15
  - Where: Walmart, Target, any grocery store
  - Product: Ball Regular Mouth 4oz Quilted Crystal Jelly Jars
  - Links:
    - Walmart: https://www.walmart.com/ip/Ball-Regular-Mouth-4oz-Quilted-Pint-Mason-Jars-12-Count/17203435
    - Amazon: https://www.amazon.com/Airtight-Canning-Kitchen-Handmade-Desserts/dp/B0CR6H5CJN
  - Need: 2 jars (buy 12-pack for spares)

- [ ] **Clear Silicone Sealant (100% silicone)** - $5-8
  - Where: Home Depot, Lowe's, Ace Hardware
  - Purpose: Seal bulkhead fittings and wire holes airtight
  - Brand: GE Silicone II or DAP 100% Silicone

**AMAZON ORDER:**
- [ ] **Female-to-Female DuPont Jumper Wires (30cm, 120pcs kit)** - $7-8
  - Link: https://www.amazon.com/SIM-NAT-Breadboard-Arduino-Raspberry/dp/B06XRV92ZB
  - Purpose: Extend I²C wires from sensor inside jar to Pi GPIO
  - Need: 8 wires total (4 per sensor × 2 systems)

**Success Criteria:**
- [ ] Mason jars purchased (12-pack)
- [ ] Silicone sealant purchased
- [ ] I²C extension wires ordered on Amazon

---

### 3. ⚡ Enable I²C on Both Balloon Pis
**Priority:** HIGH - Quick win, unblocks sensor testing
**Time Estimate:** 5 minutes
**Status:** [ ] Not Started

**Why Important:**
- Required before BMP388 sensors can be detected
- Must be done before connecting sensors
- Simple configuration change

**Action Steps:**

**Pi #7 (Vulnerable System):**
```bash
ssh username@192.168.50.100

sudo raspi-config
# Navigate to: 3 Interface Options → I5 I2C → Yes → Finish → Yes (Reboot)
```

**Pi #6 (Secure System):**
```bash
ssh username@10.30.0.25

sudo raspi-config
# Navigate to: 3 Interface Options → I5 I2C → Yes → Finish → Yes (Reboot)
```

**Verification (after reboot):**
```bash
# Should show empty I²C grid (no devices yet, but tool works)
i2cdetect -y 1

# Expected output: Grid with "--" showing I²C bus is active
```

**Success Criteria:**
- [ ] I²C enabled on Pi #7 (192.168.50.100)
- [ ] I²C enabled on Pi #6 (10.30.0.25)
- [ ] Both Pis rebooted
- [ ] `i2cdetect -y 1` shows grid on both Pis

---

---

## 🔒 NEXT WEEK (HIGH PRIORITY - SECURITY)

### 4. 🛡️ Deploy Wazuh Agent to TrueNAS Server
**Priority:** HIGH - Critical monitoring gap
**Time Estimate:** 1 hour
**Status:** [ ] Not Started

**Why Important:**
- TrueNAS hosts ALL your VMs and data
- Currently NO security monitoring on host server
- HIPAA compliance requires comprehensive audit logging
- Need to monitor: VM activity, file access, authentication

**Action Steps:**

1. SSH to TrueNAS:
   ```bash
   ssh username@10.30.0.44
   ```

2. Download Wazuh agent for FreeBSD/TrueNAS:
   ```bash
   # Check TrueNAS version first
   uname -a

   # Download appropriate Wazuh agent (adjust URL for your version)
   # For TrueNAS SCALE (Debian-based):
   curl -s https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.9.2-1_amd64.deb -o wazuh-agent.deb

   # Install with manager configuration
   sudo WAZUH_MANAGER='10.30.0.55' \
        WAZUH_AGENT_NAME='truenas-server' \
        dpkg -i wazuh-agent.deb
   ```

3. Start and enable agent:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable wazuh-agent
   sudo systemctl start wazuh-agent
   ```

4. Verify on Wazuh dashboard:
   ```
   https://10.30.0.55 → Agents → Should see "truenas-server" (Active)
   ```

5. Configure monitoring for critical paths:
   ```bash
   sudo nano /var/ossec/etc/ossec.conf

   # Add monitoring for:
   # - /mnt/Hospital_Main (dataset access)
   # - VM configuration files
   # - Authentication logs
   ```

**Success Criteria:**
- [ ] Wazuh agent installed on TrueNAS
- [ ] Agent shows "Active" in Wazuh dashboard
- [ ] File integrity monitoring configured for datasets
- [ ] Agent count increases to 15 total

---

### 5. 🔒 Configure UDM-SE Syslog Forwarding to Wazuh
**Priority:** HIGH - Network monitoring gap
**Time Estimate:** 30 minutes
**Status:** [ ] Not Started

**Why Important:**
- UDM-SE is your network gateway/firewall
- Currently NO logging to SIEM
- Need firewall logs, authentication attempts, VLAN traffic for security analysis
- HIPAA compliance requires network audit logging

**Action Steps:**

1. Login to UDM-SE web interface:
   ```
   https://10.30.0.1
   User: username | Pass: password
   ```

2. Configure syslog forwarding:
   ```
   Navigate to: Settings → System → Advanced → Logging

   Remote Logging:
   - Enable: ✓ Remote Logging
   - Host: 10.30.0.55
   - Port: 514
   - Protocol: UDP

   Log Categories (enable all):
   - ✓ Firewall Logs
   - ✓ Authentication Logs
   - ✓ DHCP Logs
   - ✓ System Logs
   - ✓ VPN Logs

   Save Changes
   ```

3. Configure Wazuh to receive UDM-SE logs:
   ```bash
   ssh username@10.30.0.55

   sudo nano /var/ossec/etc/ossec.conf

   # Add remote syslog configuration:
   <remote>
     <connection>syslog</connection>
     <port>514</port>
     <protocol>udp</protocol>
     <allowed-ips>10.30.0.1</allowed-ips>
   </remote>

   sudo systemctl restart wazuh-manager
   ```

4. Verify logs are being received:
   ```bash
   # On Wazuh server
   sudo tail -f /var/ossec/logs/archives/archives.log | grep 10.30.0.1
   ```

5. Check Wazuh dashboard for UDM-SE events

**Success Criteria:**
- [ ] Syslog forwarding enabled on UDM-SE
- [ ] Wazuh receiving logs from 10.30.0.1
- [ ] Firewall events visible in Wazuh dashboard
- [ ] Authentication attempts logged

---

### 6. 🫙 Build Pressure Chambers (When Jars Arrive)
**Priority:** HIGH - Enables sensor testing
**Time Estimate:** 2 hours
**Status:** [ ] Waiting for mason jars

**Prerequisites:**
- [ ] Mason jars received
- [ ] Silicone sealant received
- [ ] Bulkhead fittings received (check if already ordered)

**Tools Needed:**
- Electric drill
- 20mm drill bit (for bulkhead fitting - 3/4" or 13/16")
- 15.5mm drill bit (for PG9 cable gland OR 3/16" for wires)
- Safety glasses
- Marker/pen
- Ruler/measuring tape

**Action Steps (Per Chamber - Make 2 Total):**

1. **Mark hole positions on mason jar lid:**
   - Hole 1: Center, for bulkhead fitting (air inlet)
   - Hole 2: Off-center, for I²C wire bundle

2. **Drill bulkhead fitting hole:**
   ```
   - Use 20mm (13/16") drill bit
   - Drill slowly through metal lid
   - Deburr edges with file
   ```

3. **Drill wire hole:**
   ```
   - Use 15.5mm (for PG9 cable gland) OR 3/16" (for direct wires)
   - Drill slowly
   - Deburr edges
   ```

4. **Install bulkhead fitting:**
   ```
   - Insert from INSIDE lid (threads poke through outside)
   - Apply silicone sealant around threads
   - Tighten fitting
   - Let cure 24 hours
   ```

5. **Mount BMP388 sensor inside jar:**
   ```
   - Use M2.5 brass standoffs glued to jar bottom
   - Position sensor horizontally, centered
   - Ensure wires reach lid hole
   ```

6. **Thread I²C wires through lid:**
   ```
   - 4 wires: VIN (3.3V), GND, SCL, SDA
   - Connect female DuPont wires to sensor
   - Thread through lid hole
   ```

7. **Seal wire hole:**
   ```
   - Apply silicone sealant around all wires
   - Ensure airtight seal
   - Let cure 24 hours
   ```

8. **Final assembly:**
   ```
   - Screw lid onto jar (rubber gasket seals automatically)
   - Connect air tube to bulkhead fitting
   - Connect I²C wires to Pi GPIO:
     - VIN → Pin 1 (3.3V)
     - GND → Pin 6 (Ground)
     - SCL → Pin 5 (GPIO 3)
     - SDA → Pin 3 (GPIO 2)
   ```

9. **Test sensor detection:**
   ```bash
   i2cdetect -y 1
   # Should show: 0x77 (BMP388 sensor)

   cd ~/balloon-demo/scripts
   python3 test_bmp388.py
   # Should display live pressure readings
   ```

**Success Criteria:**
- [ ] 2 pressure chambers built (one per system)
- [ ] BMP388 sensors mounted inside jars
- [ ] I²C wires sealed and connected
- [ ] Both sensors detected at address 0x77
- [ ] `test_bmp388.py` shows live readings

---

## 📦 WHEN HARDWARE ARRIVES

### 7. 📬 Track & Install Sequent 8-RELAYS HAT
**Priority:** CRITICAL BLOCKER - #1 hardware dependency
**Time Estimate:** 1 hour (when arrives)
**Status:** [ ] On order, tracking

**What's Blocking:**
- Cannot control pumps or valves without relay HAT
- Cannot complete balloon demo without this component
- Software is 100% ready, waiting on hardware

**Current Status:**
- Ordered from Amazon
- ETA: ~5-7 days from order date
- Cost: $90 (×2 = $180)

**When It Arrives:**

1. **Check delivery daily:**
   - Check Amazon order status
   - Track package

2. **Install HAT on both Pis:**
   ```
   - Power off Pi
   - Carefully press HAT onto 40-pin GPIO header
   - Ensure all pins aligned
   - HAT should sit flush on GPIO
   - Power on Pi
   ```

3. **Install lib8relind library:**
   ```bash
   cd ~
   git clone https://github.com/SequentMicrosystems/8relind-rpi.git
   cd 8relind-rpi/python
   sudo python3 setup.py install
   ```

4. **Verify relay HAT detection:**
   ```bash
   i2cdetect -y 1
   # Should show:
   # - 0x20 (Relay HAT)
   # - 0x77 (BMP388 sensor, if connected)
   ```

5. **Test relays:**
   ```bash
   cd ~/balloon-demo/scripts
   python3 test_relays.py

   # Should:
   # - Detect relay HAT
   # - Cycle relay 1 (pump) ON/OFF
   # - Cycle relay 2 (valve) ON/OFF
   # - Test inflation sequence (valve opens, pump starts, etc.)
   ```

6. **Enable systemd services:**
   ```bash
   # Pi #7 (Vulnerable)
   ssh username@192.168.50.100
   sudo systemctl enable balloon-sensor-publisher.service
   sudo systemctl start balloon-sensor-publisher.service
   sudo systemctl status balloon-sensor-publisher.service

   # Pi #6 (Secure)
   ssh username@10.30.0.25
   sudo systemctl enable balloon-control-secure.service
   sudo systemctl start balloon-control-secure.service
   sudo systemctl status balloon-control-secure.service
   ```

7. **Verify auto-start:**
   ```bash
   sudo reboot
   # Wait 1 minute
   sudo systemctl status balloon-*
   # All services should be "active (running)"
   ```

**Success Criteria:**
- [ ] Relay HATs installed on both Pis
- [ ] lib8relind library installed
- [ ] Both HATs detected at I²C address 0x20
- [ ] test_relays.py successfully cycles relays
- [ ] All systemd services enabled and running
- [ ] Services auto-start after reboot

---

## 🧹 NEXT 2 WEEKS (MEDIUM PRIORITY)

### 8. 🗑️ Delete Unused VLANs from UDM-SE
**Priority:** MEDIUM - Network cleanup
**Time Estimate:** 15 minutes
**Status:** [ ] Not Started

**Why Important:**
- Reduces attack surface
- Prevents accidental device assignment to wrong VLAN
- Simplifies network management

**VLANs to Delete:**
- [ ] VLAN 10 (verify not in use first)
- [ ] VLAN 20 (old network, everything moved to VLAN30)
- [ ] VLAN 40 (verify not in use first)
- [ ] **DO NOT DELETE:** VLAN 50 (verify it's the "RED TEAM" network mentioned in docs)

**Action Steps:**

1. Login to UDM-SE:
   ```
   https://10.30.0.1
   User: username | Pass: password
   ```

2. Check each VLAN for active devices:
   ```
   Navigate to: Settings → Networks → [VLAN Name]
   Check: Connected Clients list
   ```

3. Delete unused VLANs:
   ```
   For each unused VLAN:
   Settings → Networks → [VLAN Name] → Delete Network
   Confirm deletion
   ```

4. Verify no devices disconnected:
   ```
   Navigate to: Clients
   Verify all expected devices still connected
   ```

**Success Criteria:**
- [ ] Unused VLANs identified
- [ ] VLANs 10, 20, 40 deleted (if unused)
- [ ] All devices still connected and operational
- [ ] Network list cleaned up

---

### 9. 🔍 Verify/Fix VLAN2 vs VLAN50 Inconsistency
**Priority:** MEDIUM - Documentation accuracy
**Time Estimate:** 30 minutes
**Status:** [ ] Not Started

**Why Important:**
- Documentation shows conflicting information
- Pi #7 IP is 192.168.50.100 but unclear which VLAN
- Some docs say "VLAN2", others say "VLAN50"
- Network config doc says: "VLAN ID: 2 (VLAN50 was taken by RED TEAM)"

**Inconsistencies Found:**
```
NETWORK_SETUP_PROGRESS.md line 44:
- "Pi #7 | 192.168.50.100 | VLAN2 (Vulnerable)"

NETWORK_SETUP_PROGRESS.md line 51:
- "Attack Lab Subnet (VLAN2): 192.168.50.0/24"

BALLOON_DEMO_NETWORK_CONFIG.md:
- "VLAN ID: 2" but also mentions "VLAN50 was taken by RED TEAM"
```

**Action Steps:**

1. **Check actual VLAN configuration on UDM-SE:**
   ```
   https://10.30.0.1 → Settings → Networks

   Look for:
   - What VLAN ID is 192.168.50.0/24 actually configured as?
   - Is there a VLAN2?
   - Is there a VLAN50? What is it used for?
   ```

2. **Check Pi #7 actual VLAN assignment:**
   ```
   https://10.30.0.1 → UniFi Devices → Switch Pro Max → Port 15

   Verify:
   - What VLAN is Port 15 assigned to?
   - Native VLAN setting
   ```

3. **Document findings:**
   ```
   Create note with:
   - Actual VLAN ID for 192.168.50.0/24
   - Actual VLAN for Pi #7
   - Whether VLAN50 exists and what it's for
   ```

4. **Update all documentation to be consistent:**
   ```
   Files to update:
   - NETWORK_SETUP_PROGRESS.md
   - BALLOON_DEMO_NETWORK_CONFIG.md
   - BALLOON_DEMO_DESIGN_NOTES.md
   - Any scripts that reference VLAN numbers
   ```

**Success Criteria:**
- [ ] Actual VLAN configuration documented
- [ ] All documentation updated to match reality
- [ ] No conflicting VLAN references in docs

---

## 📝 DOCUMENTATION GAPS (LOW PRIORITY)

### 10. 📄 Document Missing Network Information
**Priority:** LOW - Nice to have
**Time Estimate:** 1 hour
**Status:** [ ] Not Started

**Missing Information:**
- [ ] Cloud Key G2 Plus IP address
- [ ] TrueNAS physical server hardware specs (CPU, RAM, disk config)
- [ ] TrueNAS br0 physical NIC identification
- [ ] Dream Router 7 WAN IP from ISP
- [ ] UDM-SE WAN IP from Dream Router

**Action Steps:**

1. **Find Cloud Key IP:**
   ```
   Check UDM-SE: Settings → UniFi Devices → Cloud Key G2 Plus
   OR
   Check router DHCP leases
   ```

2. **Document TrueNAS hardware:**
   ```bash
   ssh username@10.30.0.44

   # CPU info
   cat /proc/cpuinfo | grep "model name" | head -1

   # RAM
   free -h

   # Disk config
   zpool status
   zpool list
   ```

3. **Identify br0 NIC:**
   ```bash
   ssh username@10.30.0.44
   ifconfig br0
   # Note physical adapter (igb0, em0, etc.)
   ```

4. **Get WAN IPs:**
   ```
   Dream Router 7 web interface: Check WAN status
   UDM-SE: Settings → Internet → WAN → IP Address
   ```

5. **Update NETWORK_SETUP_PROGRESS.md** with all findings

**Success Criteria:**
- [ ] All missing IPs documented
- [ ] TrueNAS hardware specs recorded
- [ ] Network topology fully documented
- [ ] NETWORK_SETUP_PROGRESS.md updated

---

## 🎯 COMPLETION TRACKING

### This Weekend Goals
- [ ] PostgreSQL retention policy implemented ⚠️ MOST CRITICAL
- [ ] Mason jars & I²C wires ordered
- [ ] I²C enabled on both balloon Pis

### Next Week Goals
- [ ] Wazuh agent on TrueNAS
- [ ] UDM-SE syslog forwarding
- [ ] Pressure chambers built (when jars arrive)

### When Hardware Arrives
- [ ] Relay HATs installed and tested
- [ ] All systemd services running
- [ ] Balloon demo hardware complete

### Cleanup Tasks
- [ ] Unused VLANs deleted
- [ ] VLAN2/VLAN50 inconsistency resolved
- [ ] Documentation gaps filled

---

## 📊 PROGRESS SUMMARY

**Total Tasks:** 10
**Completed:** 0
**In Progress:** 0
**Blocked:** 1 (Relay HAT delivery)

**Critical Path Items:**
1. PostgreSQL retention (URGENT - do first!)
2. Order mason jars + wires (enables sensor testing)
3. Enable I²C (5 min quick win)
4. Track relay HAT delivery (critical blocker)

---

## ✅ SYSTEM COMPLETENESS CHECK

### VMs - All Operational ✅
- ✅ PostgreSQL VM (10.30.0.50) - Database
- ✅ MQTT Broker VM (10.30.0.51) - Messaging
- ✅ Node-RED VM (10.30.0.52) - Workflow automation
- ✅ Grafana VM (10.30.0.53) - Dashboards
- ✅ Mirth Connect VM (10.30.0.54) - HL7/FHIR integration
- ✅ Wazuh SIEM VM (10.30.0.55) - Security monitoring
- ✅ HAPI FHIR VM (10.30.0.56) - FHIR server
- ✅ Keycloak IDM VM (10.30.0.57) - Identity management
- ✅ HashiCorp Vault VM (10.30.0.58) - Secrets management

**No missing VMs - all systems deployed and operational!**

### Security Monitoring Coverage
**Current:** 14/16 systems monitored

**Monitored (14):**
- ✅ 5 Heart Rate Monitor Pis (10.30.0.20-24)
- ✅ PostgreSQL VM
- ✅ Node-RED VM
- ✅ Grafana VM
- ✅ Mirth Connect VM
- ✅ HAPI FHIR VM
- ✅ MQTT Broker VM
- ✅ Keycloak IDM VM
- ✅ HashiCorp Vault VM
- ✅ Pi #6 (balloon-secure)

**NOT Monitored (2):**
- ❌ **TrueNAS Server (10.30.0.44)** - HOST FOR ALL VMs ← Add this
- ❌ **UDM-SE Gateway (10.30.0.1)** - Network firewall ← Add syslog forwarding
- ⚠️ Pi #7 (balloon-vulnerable) - Intentionally unmonitored for demo

**Action:** Items #4 and #5 in this document will close these gaps.

### Data Flow - Complete ✅
**Pipeline:** Raspberry Pi → MQTT → Node-RED → PostgreSQL
- ✅ All 5 Pis publishing at 20 Hz
- ✅ MQTT broker receiving and forwarding
- ✅ Node-RED processing and storing
- ✅ PostgreSQL storing (100 inserts/sec)

**Pipeline:** Node-RED → Mirth → HAPI FHIR
- ✅ Node-RED rate-limiting to 1/sec
- ✅ Mirth transforming to FHIR R4
- ✅ HAPI FHIR storing Observations
- ✅ All 5 patients with active data

**Pipeline:** All systems → Wazuh SIEM
- ✅ 14 agents reporting
- ⚠️ TrueNAS missing (add agent)
- ⚠️ UDM-SE missing (add syslog)

**No missing data flows - architecture is complete!**

### SSO Integration - Complete ✅
- ✅ Grafana → Keycloak OAuth2
- ✅ Node-RED → Keycloak OAuth2
- ✅ Wazuh → Keycloak OpenID Connect
- ✅ HAPI FHIR → Keycloak OAuth2 (via OAuth2 Proxy)
- ✅ HashiCorp Vault → Keycloak OIDC

**All web interfaces support SSO - centralized authentication complete!**

### Missing Items Summary
**Security Monitoring Gaps (Fix Next Week):**
1. TrueNAS Wazuh agent (Task #4)
2. UDM-SE syslog forwarding (Task #5)

**Network Cleanup (Fix Next 2 Weeks):**
1. Delete unused VLANs (Task #8)
2. Fix VLAN2/VLAN50 documentation inconsistency (Task #9)

**Everything else is complete and operational!**

---

## 🔔 REMINDERS

**THIS WEEKEND:**
- 🛒 Order mason jars from local store
- 🛒 Order I²C wires on Amazon
- ⚡ Enable I²C on both Pis (5 minutes!)

**NEXT WEEK:**
- 🛡️ Deploy Wazuh to TrueNAS (close monitoring gap)
- 🔒 Configure UDM-SE syslog (close monitoring gap)

**DAILY:**
- 📦 Check Amazon for relay HAT delivery status

**WHEN JARS ARRIVE:**
- 🫙 Build pressure chambers (2 hours)

**NEXT 2 WEEKS (Lower Priority):**
- 📊 PostgreSQL retention policy (you have 18+ months runway)
- 🧹 Network cleanup (VLANs, documentation)

---

**Last Updated:** 2026-02-05
**Next Review:** Check this file daily to mark completed tasks
