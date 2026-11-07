# Hospital Homelab Network Setup Progress - PART 3 (Lines 1000-1363 - FINAL)
## Last Updated: 2026-02-14 (Security Hardening Complete ✓, Data Archival Complete ✅, 100% SSL Coverage Achieved 🔒)

## Continued from PART 2...

- [✓] Timezone synchronized to EST across all Pis (2025-11-25)

### VM Infrastructure (COMPLETE ✓)
- [✓] Node-RED VM operational (10.30.0.52)
- [✓] MQTT Broker VM operational (10.30.0.51)
- [✓] MQTT ↔ Node-RED connection tested (2025-11-17)
- [✓] PostgreSQL VM operational (10.30.0.50) - 1TB disk, data ingestion active (2025-11-25)
- [✓] Node-RED Dashboard deployed with real-time monitoring at http://10.30.0.52:1880/ui (2025-11-25)
  - 5 BPM gauges with live data (0-200 range, color zones)
  - 5 trend charts with bezier interpolation for smooth curves (5-min history, 40-160 BPM range)
  - Tachycardia alert system with notifications (BPM > 100 threshold)
  - Performance optimized: 20 Hz data rate (100 messages/sec total) for stable rendering
- [✓] PostgreSQL data storage integration - COMPLETE (2025-11-25)
  - All 5 Pis streaming to database at 100 inserts/second
  - heartrate_data table with full schema and indexes
  - 1TB storage capacity (~13+ years at current rate)
- [✓] Grafana VM (10.30.0.53) - FULLY OPERATIONAL (2025-12-09)
  - Ubuntu Server 24.04 LTS with Grafana installed
  - PostgreSQL data source configured and tested
  - Web interface at http://10.30.0.53:3000
  - Auto-start enabled (grafana-server.service)
  - ✓ Dashboard deployed: "Heart Rate Monitoring - All Patients"
    - 5 individual Pi heart rate panels + Pi #4 AFib panel + Pi #5 anomaly panel
    - Alert list panel showing active alerts
    - Auto-refresh: 30 seconds
    - Tachycardia alert: Pi #4 BPM > 120 for 1 minute
  - Note: Displays in UTC (5 hours ahead of EST)
- [✓] Mirth Connect VM (10.30.0.54) - FULLY OPERATIONAL (2025-12-15)
  - Ubuntu Server 24.04 LTS with Mirth Connect 4.5.2
  - Web interface accessible at https://10.30.0.54:8443
  - FHIR transformation channel operational: `HeartRate_FHIR_Final`
  - Real-time data flow: MQTT → Node-RED → HTTP → Mirth → HAPI FHIR
  - FHIR Observation resources saved to `/tmp/fhir-observations/` AND posted to HAPI FHIR
  - See Phase 3 roadmap for full implementation details
- [✓] HAPI FHIR Server VM (10.30.0.56) - FULLY OPERATIONAL (2026-01-16)
  - Docker deployment with hapiproject/hapi:latest (FHIR R4)
  - 3GB Java heap configured (fixed OutOfMemoryError)
  - PostgreSQL backend for persistent storage (survives reboots)
  - 5 Patient resources created (pi-1 through pi-5)
  - Receiving and storing Observations from Mirth (1/second)
  - REST API tested and validated
  - Complete end-to-end healthcare data pipeline operational
- [✓] Wazuh SIEM VM (10.30.0.55) - FULLY OPERATIONAL (2026-01-16)
  - Ubuntu Server 24.04 LTS with Wazuh 4.9.2 All-in-One
  - 12 agents deployed: 5 Raspberry Pis + 7 VMs
  - Web interface: https://10.30.0.55
  - Real-time security monitoring across entire infrastructure
  - HIPAA compliance dashboards (164.312.b audit controls)
  - File integrity monitoring, vulnerability detection, anomaly detection
- [✓] Keycloak IDM VM (10.30.0.57) - FULLY OPERATIONAL (2026-01-16)
  - Ubuntu Server 24.04 LTS with Keycloak 26.0.7
  - PostgreSQL backend (10.30.0.50:5432/keycloak)
  - Web interface: http://10.30.0.57:8080
  - Hospital-homelab realm configured with 2 users
  - Grafana SSO integration working (OAuth2/OpenID Connect)
  - Centralized identity and access management operational

---

## MAINTENANCE TASKS

### Documentation Needed
- [ ] Cloud Key G2 Plus IP address
- [ ] TrueNAS physical server hardware specs
- [ ] TrueNAS br0 physical NIC identification
- [ ] Dream Router 7 WAN IP from ISP
- [ ] UDM-SE WAN IP from Dream Router

### Network Cleanup
- [ ] Delete unused VLANs (10, 20, 40, 50) from UDM-SE
- [ ] Test air-gapped mode (disconnect WAN, verify operation)
- [ ] Delete opnsense dataset from TrueNAS

---

## TROUBLESHOOTING NOTES

### Common Issues
- **Devices on switch can't reach network**: Verify Switch Port 26 (SFP+ uplink) is set to correct VLAN
- **Pi not responding**: Check PoE power delivery and NetworkManager connection status
- **TrueNAS not accessible**: Verify br0 interface has correct IP and gateway

### Power Outage Recovery (2026-01-04)
After a power outage, the following issues occurred and were resolved:
1. **UniFi Switch unreachable**: Switch temporarily had wrong IP (192.168.1.20 from old config). Reset to 10.30.0.10 via UniFi controller.
2. **Raspberry Pi services not running**: All 5 heartrate services needed manual restart after power restored:
   - SSH into each Pi: `ssh r-pi-{1-5}@10.30.0.{20-24}`
   - Restart service: `sudo systemctl restart heartrate{1-5}.service`
   - Verify: `systemctl status heartrate{1-5}.service`
3. **Node-RED not inserting to PostgreSQL**: Node-RED service needed restart to restore database connection:
   - SSH: `ssh username@10.30.0.52`
   - Restart: `sudo systemctl restart nodered.service`
4. **Grafana showing wrong timezone**: PostgreSQL was in UTC, Grafana queries needed timezone conversion:
   - Set PostgreSQL VM timezone: `sudo timedatectl set-timezone America/New_York`
   - Configure PostgreSQL: `ALTER SYSTEM SET timezone = 'America/New_York';`
   - Restart PostgreSQL: `sudo systemctl restart postgresql`
   - Update Grafana queries to use: `timestamp AT TIME ZONE 'America/New_York'`

### HAPI FHIR Server Issues (2026-01-15/16)
**OutOfMemoryError** - Server crashed with Java heap space errors:
- **Cause**: Default Java heap too small for HAPI FHIR workload
- **Solution**: Recreated Docker container with increased heap (3GB) and PostgreSQL backend
- **Status**: Fixed - server stable with 3GB heap and persistent PostgreSQL storage

### Security Hardening Issues (2026-02-13)

**1. MQTT Anonymous Access Still Working After Disabling**
- **Problem**: `mosquitto_sub` without credentials still worked after setting `allow_anonymous false`
- **Cause**: Configuration conflicts between `/etc/mosquitto/mosquitto.conf` and `/etc/mosquitto/conf.d/default.conf`
- **Solution**: Consolidated all auth settings in `default.conf`, removed conflicting lines from main config
- **Verification**: Anonymous subscribe blocked, authenticated access working

**2. Node-RED PostgreSQL SSL Certificate Error**
- **Problem**: `Error: self-signed certificate, code: DEPTH_ZERO_SELF_SIGNED_CERT` after enabling PostgreSQL SSL
- **Cause**: Node.js client rejecting self-signed certificates
- **Solution**: Configure Node-RED with `"ssl": "{\"rejectUnauthorized\":false}"` in flows.json
- **Status**: Fixed - all connections using SSL with self-signed cert acceptance

**3. Grafana PostgreSQL SSL Configuration**
- **Problem**: Grafana installed via APT doesn't use YAML provisioning files
- **Solution**: Update via SQLite database directly:
  ```bash
  sudo sqlite3 /var/lib/grafana/grafana.db \
    "UPDATE data_source SET json_data = json_set(json_data, '$.sslmode', 'require') \
     WHERE type = 'grafana-postgresql-datasource';"
  ```
- **Status**: Fixed - Grafana using SSL connections

**4. HAPI FHIR SSH Access Blocked After Firewall Rules**
- **Problem**: SSH connection timeout after adding UFW rules for port 8080
- **Cause**: Firewall rule ordering - deny rule processed before SSH allow rule
- **Solution**: Re-ordered rules with `sudo ufw insert 1 allow from 10.30.0.0/24 to any port 22`
- **Verification**: SSH allow rule now Rule #1, processed before deny rules

**5. PostgreSQL Data Archival Performance**
- **Problem**: Archiving 582M rows taking 3-4+ hours with standard INSERT...SELECT
- **Cause**: Massive dataset with limited RAM (4GB on PostgreSQL VM)
- **Solution**: Used UNLOGGED table for archive to skip WAL writes during bulk insert
- **Monitoring**: Track progress with `SELECT pg_size_pretty(pg_table_size('heartrate_data_archive'));`
- **Status**: In progress - archive table growing from 0 GB → 88 GB estimated

**Data Loss After Reboot** (2026-01-16):
- **Cause**: H2 embedded database losing data on container restarts
- **Solution**: Migrated to PostgreSQL backend on 10.30.0.50:5432
- **Database**: Created `hapi_fhir` database owned by `nodered` user
- **Result**: Patient resources and Observations now survive reboots and power loss
- **Docker Configuration**: Added PostgreSQL connection parameters to container
- **Status**: System now HIPAA-compliant with persistent audit trail

**Mirth FileNotFoundException** (2026-01-16):
- **Cause**: `/tmp/fhir-observations/` directory deleted on reboot
- **Solution**: Created systemd service `/etc/systemd/system/mirth-fhir-dir.service`
- **Service Actions**: Creates directory, sets ownership to username, sets 755 permissions
- **Status**: Directory auto-created before Mirth starts on every boot

### Mirth Connect Disk Space Crisis (2026-01-22)
**Derby Database Filling Disk** - Mirth VM disk reached 100% capacity:
- **Symptoms**: Web UI hanging, service wouldn't stop gracefully, database corruption
- **Cause**: Derby database at `/opt/mirthconnect/appdata/mirthdb` grew to 36GB, filling 100% of 48GB disk
- **Root Issue**: No auto-pruning configured, message logs accumulated indefinitely
- **Recovery Steps**:
  1. Force-killed Java process: `sudo pkill -9 java`
  2. Completely removed Derby database: `sudo rm -rf /opt/mirthconnect/appdata/mirthdb`
  3. Restarted Mirth to recreate fresh database: `sudo systemctl start mirthconnect`
  4. Reset admin credentials (database reset to defaults: `admin` / `admin`)
  5. Recreated `HeartRate_FHIR_Final` channel with proper configuration
  6. Configured Data Pruner: 30-day retention, daily schedule, no archiving
- **Channel Recreation Details**:
  - Source: HTTP Listener on port 8081 (changed from 9999)
  - Data Types: JSON inbound and outbound (not Raw or XML)
  - Source Transformer: JavaScript converts heart rate JSON to FHIR R4 Observation
  - Destination: HTTP Sender to `http://10.30.0.56:8080/fhir/Observation`
  - Content field: `${message.encodedData}` (critical for sending HTTP body in JSON mode)
  - Queue messages: Never (send immediately, no queuing)
- **Preventive Measures**:
  - Data Pruner runs daily at 2 AM
  - Prunes events older than 30 days
  - Keeps only errors and queued messages for troubleshooting
  - Disk usage reduced from 100% to 21% (48GB total, 10GB used)
- **Status**: ✓ Fixed - Pipeline fully operational, auto-pruning prevents future issues
- **HIPAA Compliance**: Message routing logs can be pruned; clinical data safely stored in HAPI FHIR PostgreSQL

### Air-Gap Goal
System designed to operate fully isolated from internet once setup complete:
- Unplug WAN cable from UDM-SE Port 10
- All services continue on 10.30.0.0/24 network
- Portable for demos/presentations
- Simulates real isolated healthcare network
- Reconnect for updates when needed

---

## QUICK REFERENCE

### SSH One-Liners
```bash
# Ping all Raspberry Pis
for /L %i in (20,1,24) do @ping -n 1 10.30.0.%i | findstr "Reply TTL"

# Test all key devices
ping 10.30.0.1 && ping 10.30.0.44 && ping 10.30.0.45 && ping 10.30.0.50 && ping 10.30.0.51 && ping 10.30.0.52
```

### Network Summary
- **Gateway**: 10.30.0.1 (UDM-SE)
- **Raspberry Pis (VLAN30)**: 10.30.0.20-25 (5× HeartRate monitors ✓, 1× Secure Balloon Demo [PLANNED])
- **Raspberry Pis (VLAN50)**: 192.168.50.100 (1× Vulnerable Balloon Demo [PLANNED])
- **TrueNAS**: 10.30.0.44 (Storage + VM host)
- **iDRAC 9**: 10.30.0.45 (Server management)
- **VMs**: 10.30.0.50-58 (PostgreSQL ✓, MQTT ✓, Node-RED ✓, Grafana ✓, Mirth ✓, Wazuh ✓, HAPI FHIR ✓, Keycloak ✓, **Vault ✓**)
- **WiFi AP**: 10.30.0.246 (U6 Pro)

---

## WHEN RESUMING WORK

**Current State (2026-02-03):**
- ✓ Flat network complete - all devices on 10.30.0.0/24 (VLAN30)
- ✓ 5 Raspberry Pis operational with realistic HeartRate monitors
- ✓ All 5 Pis standardized on Debian 12 (Raspberry Pi OS Bookworm)
- ✓ All 5 Pis running systemd services (auto-start on boot)
- ✓ 4 Pis on PoE++ ports (9-12), Pi #5 on external power (port 13)
- ✓ ECG displays verified on all Sense HATs
- ✓ TrueNAS + iDRAC 9 + all VMs accessible
- ✓ MQTT Broker VM installed and tested
- ✓ Node-RED ↔ MQTT connection working
- ✓ mosquitto-clients installed on WSL laptop for testing
- ✓ **Complete MQTT → PostgreSQL data pipeline operational (2025-11-25)**:
  - All 5 Pis publishing at 20 Hz (50ms intervals, optimized for dashboard)
  - Internal ECG simulation at 60 columns/second for smooth visual display
  - Realistic heart rate patterns with unique HRV per Pi (critically damped physics)
  - Pi #5 anomaly system: ~1 event every 5.5 hours with 2-minute cooldown
  - Node-RED dashboard with real-time gauges and charts at http://10.30.0.52:1880/ui
  - Tachycardia alert system with duration/max BPM tracking
  - Dashboard performance stable: no connection drops or lag
  - PostgreSQL database storing 100 records/second (all 5 Pis)
  - 1TB storage capacity (~13+ years at 200 MB/day growth rate)
  - heartrate_data table: timestamp, pi_id, bpm, status, anomaly_type with indexes
- ✓ **Grafana VM fully operational with dashboards (2025-12-09)**:
  - VM created: 10.30.0.53 (2 vCPUs, 4GB RAM, 50GB disk)
  - Ubuntu Server 24.04 LTS with Grafana installed
  - PostgreSQL data source configured and connection tested successfully
  - Web interface accessible at http://10.30.0.53:3000
  - Auto-start enabled (grafana-server.service)
  - Credentials: admin / password
  - Dashboard: "Heart Rate Monitoring - All Patients"
    - 5 individual Pi time-series panels showing heart rate trends
    - Pi #4 AFib focused panel for irregular rhythm monitoring
    - Pi #5 anomaly detection panel for rare events
    - Alert list panel displaying active alerts
    - Auto-refresh: 30 seconds
  - Alert configured: Tachycardia (Pi #4 BPM > 120 for 1 minute)
  - Note: Dashboard displays in UTC (5 hours ahead of EST)
- ✓ **Mirth Connect VM (10.30.0.54) - FULLY OPERATIONAL (2025-12-15)**:
  - VM created and operational with Mirth Connect 4.5.2
  - Web interface at https://10.30.0.54:8443
  - Channel `HeartRate_FHIR_Final` successfully deployed and running
  - HTTP Listener on port 9999 receiving data from Node-RED
  - Real-time FHIR R4 transformation: Heart rate data → Observation resources
  - FHIR files saved to `/tmp/fhir-observations/`
  - HTTP Sender posting to HAPI FHIR server
  - Complete data pipeline: IoT → MQTT → Node-RED → HTTP → Mirth → HAPI FHIR
  - Implementation mirrors real healthcare IoT→EHR integration patterns
- ✓ **HAPI FHIR Server VM (10.30.0.56) - FULLY OPERATIONAL (2026-01-16)**:
  - Docker deployment: hapiproject/hapi:latest (FHIR R4, v8.6.0)
  - Fixed OutOfMemoryError with 3GB Java heap (-Xmx3072m)
  - **Migrated to PostgreSQL backend (10.30.0.50:5432/hapi_fhir)**
  - 5 Patient resources created (pi-1 through pi-5) - persist across reboots
  - Receiving FHIR Observations from Mirth at 1/second
  - REST API fully functional at http://10.30.0.56:8080/fhir/
  - Query capabilities tested and validated:
    - Filter by patient: `?subject=Patient/pi-4`
    - Filter by LOINC: `?code=8867-4`
    - Filter by value: `?value-quantity=gt100`
    - Sort by date: `&_sort=-date`
  - **Reboot resilient**: Data persists across power loss/reboots
  - Docker container auto-restart enabled
- ✓ **Wazuh SIEM VM (10.30.0.55) - FULLY OPERATIONAL (2026-01-22)**:
  - Ubuntu Server 24.04 LTS with Wazuh 4.9.2 All-in-One
  - 12 agents deployed: 5 Raspberry Pis + 7 VMs (including Keycloak)
  - Web interface: https://10.30.0.55
  - **SSO Login:** "Log in with OpenID Connect" button (username or username)
  - Local admin: admin / password
  - **OpenID Connect SSO integration working** - Keycloak authentication
  - Real-time security monitoring across entire infrastructure
  - HIPAA compliance dashboards (164.312.b audit controls)
  - File integrity monitoring, vulnerability detection, anomaly detection
- ✓ **Keycloak IDM VM (10.30.0.57) - FULLY OPERATIONAL (2026-01-28)**:
  - Ubuntu Server 24.04 LTS with Keycloak 26.0.7
  - PostgreSQL backend (10.30.0.50:5432/keycloak)
  - Web interface: http://10.30.0.57:8080 (admin / password)
  - Hospital-homelab realm with 2 users (username, username)
  - **5 SSO integrations working:**
    - ✓ Grafana (OAuth2/OpenID Connect)
    - ✓ Node-RED (OAuth2/OpenID Connect)
    - ✓ Wazuh (OpenID Connect)
    - ✓ HAPI FHIR (OAuth2/OpenID Connect via OAuth2 Proxy)
    - ✓ HashiCorp Vault (OIDC) - **NEW 2026-02-02**
  - Centralized identity management operational
  - Wazuh agent deployed and monitoring
- ✓ **PostgreSQL Performance (2026-01-16)**:
  - 397,645,663 rows (46+ days of continuous heart rate data)
  - Created indexes for pi_id, timestamp, and composite pi_id+timestamp
  - Query performance: 35 seconds → 79ms (445× faster)
  - HIPAA data retention: All 397M rows preserved per audit requirements
  - Hosts 3 databases: hospital_data, hapi_fhir, keycloak
- **Phase 1 COMPLETE** ✓ - Core data pipeline operational
- **Phase 2 COMPLETE** ✓ - Real-time + historical visualization operational
- **Phase 3 COMPLETE** ✓ - Healthcare FHIR layer fully operational with persistent storage
- **Phase 4 COMPLETE** ✓ - Wazuh SIEM + Keycloak IDM + HashiCorp Vault deployed, 13 agents active (2026-02-02)
- **SYSTEM RESILIENCE ACHIEVED** ✓:
  - HAPI FHIR: PostgreSQL backend for data persistence
  - Mirth: Systemd service auto-creates `/tmp/fhir-observations/`
  - Docker: Auto-restart enabled on HAPI FHIR container
  - Keycloak: Systemd service auto-starts, PostgreSQL-backed
  - **Ready for expo demonstration** - survives power loss
- **SECURITY & IDENTITY MANAGEMENT** ✓:
  - Centralized authentication via Keycloak SSO
  - **5 SSO integrations working:** Grafana, Node-RED, Wazuh, HAPI FHIR, **Vault** (2026-02-02)
  - **Centralized secrets management via HashiCorp Vault** (2026-02-02):
    - Dynamic PostgreSQL credentials (1hr TTL with automatic rotation)
    - Static secrets (OAuth2 client secrets, passwords, API keys)
    - AES-256-GCM encryption at rest and in transit
    - Complete audit trail of all secret access
    - Integrated with Keycloak for OIDC authentication
    - Automated daily backups with 30-day retention
  - 14 systems monitored by Wazuh SIEM (added Vault 2026-02-02, Pi #6 balloon-secure 2026-02-03)
  - HIPAA-compliant audit logging across all systems
  - HIPAA-compliant session timeouts (30min absolute, 10min refresh)
  - HIPAA-compliant credential encryption (164.312.a.2.iv)
- ✓ **HashiCorp Vault VM (10.30.0.58) - FULLY OPERATIONAL (2026-02-02)**:
  - Ubuntu Server 24.04 LTS with HashiCorp Vault (latest stable)
  - Integrated Raft storage backend (HA-capable)
  - Web interface: http://10.30.0.58:8200
  - **Authentication:** OIDC via Keycloak (username, username) or Token
  - **Root Token:** `password`
  - **Unseal Keys:** 5 keys generated, 3 required to unseal (stored in CREDENTIALS section)
  - **Secrets Engines:**
    - KV v2 (`kv/`) - Versioned static secrets
    - Database (`database/`) - Dynamic PostgreSQL credentials with 1hr TTL
  - **Stored Secrets:**
    - PostgreSQL credentials, MQTT broker credentials
    - All Keycloak OAuth2 client secrets (Grafana, Node-RED, Wazuh, HAPI FHIR)
    - Wazuh admin password
  - **Security Features:**
    - File audit logging monitored by Wazuh
    - Daily automated backups (30-day retention)
    - Policy-based access control (RBAC)
    - Complete audit trail for HIPAA compliance
  - **Integration:** Keycloak OIDC SSO + Wazuh monitoring operational
  - **Achievement:** Eliminated plaintext passwords, centralized secrets management
- **Current Work (2026-02-03)**:
  - **Phase 5:** Expo Balloon Security Demo - Design COMPLETE ✓, Hardware ORDERED ✓, First Delivery ✅
    - ✓ Demo concept finalized (secure vs vulnerable balloon control systems)
    - ✓ Bill of Materials created with verified pricing and links ($1,444.90 total)
    - ✓ Hardware store shopping list created (HARDWARE_STORE_SHOPPING_LIST.md)
    - ✓ **Wiring diagrams complete** (WIRING_DIAGRAM_MERMAID.md, WIRING_DIAGRAM_VULNERABLE.md)
      - 9 comprehensive diagrams per system (electrical, pneumatic, I²C, relay control, power, layout, states, network)
      - Includes all wire colors, terminal positions, pin numbers, I²C addresses
      - Safety features documented (6 layers of protection)
    - ✓ **Network configuration documented** (BALLOON_DEMO_NETWORK_CONFIG.md)
      - VLAN50 (192.168.50.0/24) creation steps for vulnerable demo network
      - UDM-SE firewall rules (block VLAN50 ↔ VLAN30 traffic)
      - Switch port assignments (Ports 14, 15, 16) and trunk update (Port 26)
      - Pi #6 (10.30.0.25) on VLAN30 secure, Pi #7 (192.168.50.100) on VLAN50 vulnerable
      - MQTT broker strategy, Wazuh integration, testing procedures
      - Complete attack demonstration script for expo
    - ✓ **All hardware purchased** - delivery expected within 2 weeks from 2026-02-02
    - ✅ **Items arrived (42 total as of 2026-02-05):**
      - Early shipment (34): WiFi adapter, terminal blocks, microSD, cables, monitors, electrical, plumbing, mounting
      - Latest (8): 🎉 Solenoid valves, BMP388 sensors, air pumps, pressure gauges, piezo buzzers, brass tees, brass elbows (partial), standoffs
    - ✅ **Pi #6 (Secure System) - FULLY CONFIGURED (2026-02-03)**
      - Raspberry Pi OS (Debian 12) installed and updated
      - Static IP configured: 10.30.0.25 on VLAN30
      - I2C enabled (ready for relay HAT and sensors)
      - Python libraries installed (MQTT, GPIO, sensors)
      - Wazuh agent deployed (Agent ID: 014, active)
      - Project directory structure created: ~/balloon-demo/
      - Configuration file ready: ~/balloon-demo/config/settings.json
      - MQTT connectivity tested (broker 10.30.0.51)
      - Username: username | Hostname: balloon-secure
    - ⏳ NEXT: Receive remaining hardware (ETA ~10 days)
    - ⏳ NEXT: Set up Pi #7 (vulnerable system) on VLAN50
    - ⏳ NEXT: Implement network configuration (VLAN50, firewall rules, switch ports)
    - ⏳ NEXT: Assemble physical systems (pneumatic + electrical wiring)
    - ⏳ NEXT: Write Python control scripts (secure, vulnerable, attack)
    - ⏳ NEXT: Deploy and test complete system
    - Timeline: 3-4 weeks to expo (hardware arrival + 2-3 weeks assembly/testing)
  - **Session 2026-02-10: IDS Infrastructure Complete** ✓
    - ✅ **Elasticsearch VM deployed (10.30.0.60)**
      - Ubuntu Server 24.04 LTS, Elasticsearch 8.19.11
      - 4 vCPUs, 4GB RAM, 100GB disk
      - Single-node cluster, external connections enabled
      - Credentials: elastic / password
      - Status: Fully operational, accepting connections on 0.0.0.0:9200
    - ✅ **Suricata IDS deployed on bare metal laptop**
      - Ubuntu 24.04 Desktop (dual boot with Windows 11)
      - Disabled BitLocker, 50GB partition allocated
      - USB-C Ethernet adapter (enx00051b514370) for monitoring
      - Connected to Switch Port 6 (mirror destination)
      - Monitoring interface: 10.30.0.191 (temporary management IP)
    - ✅ **Port mirroring configured and verified**
      - Source: Switch Port 15 (Vulnerable Pi #7 at 192.168.50.100)
      - Destination: Switch Port 6 → Suricata laptop
      - Verified: All traffic to/from vulnerable Pi captured successfully
      - tcpdump confirmed unicast traffic visible (ping, curl, HTTP)
    - ✅ **Suricata detection rules operational**
      - 324 rules loaded (321 default + 3 custom)
      - Custom rules: Traffic to vulnerable Pi, VLAN30 traffic, ICMP detection
      - Fast log: /var/log/suricata/fast.log (plain text alerts)
      - EVE JSON: /var/log/suricata/eve.json (structured logs)
      - Alerts verified with live traffic testing
    - **Why Bare Metal:**
      - Initial VM attempt failed due to TrueNAS macvtap filtering
      - macvtap "bridge" mode filters by MAC address
      - Mirrored traffic has arbitrary MACs, blocked by virtualization layer
      - Bare metal bypasses all filtering, guarantees packet capture
    - ⏳ **NEXT SESSION:**
      - Install Filebeat on Suricata laptop
      - Configure Filebeat to ship eve.json to Elasticsearch (10.30.0.60)
      - Add Elasticsearch data source to Grafana (10.30.0.53)
      - Build IDS dashboard in Grafana for live attack visualization
      - Test end-to-end pipeline: Suricata → Filebeat → Elasticsearch → Grafana
  - **Session 2026-02-10 (Continued): LED Indicator System Design** ✓
    - ✅ **8-LED system design finalized**
      - 4 LEDs per Pi: Red (critical), Yellow (warning), Green (healthy), Blue (inflating)
      - Physical layout: Traffic light sequence (red/yellow/green) vertical on side/back
      - Blue LED isolated on front for high visibility during inflation
      - Junction boxes use 8 of 12 available 22mm gasket positions
    - ✅ **Attack demonstration logic documented**
      - CRITICAL: Both Pis run IDENTICAL control code
      - Secure Pi #6: Receives real pressure → LEDs show actual state (green→yellow→red)
      - Vulnerable Pi #7: Receives spoofed pressure → LEDs stuck on green (never yellow/red)
      - Attack visual: Left box progresses normally, right box stays green until balloon pops
    - ✅ **Relay channel assignments planned**
      - Relay HAT #1 (Pi #6): Ch1=Green, Ch2=Yellow, Ch3=Red, Ch4=Blue, Ch5-8=Reserved
      - Relay HAT #2 (Pi #7): Same mapping (Yellow/Red wired but never activated by attack)
      - 8 channels used, 8 channels reserved for future expansion
    - ✅ **Documentation created: LED_INDICATOR_DESIGN.md**
      - Complete physical layout diagrams
      - Wiring details and power distribution
      - Python control code examples (LEDController class)
      - Testing procedures and safety considerations
      - Integration with balloon control scripts
      - Bill of materials for LED system ($163.98)
    - **Status:** Ready for physical assembly when relay HATs installed

- **Future steps**:
  1. **Phase 5 (Current):** Complete Expo Balloon Security Demo (see Phase 5 roadmap above)
  2. **Phase 3 (Optional):** Install Orthanc PACS VM for medical imaging (DICOM)
  3. **Phase 4 (Optional):** Zeek/Suricata IDS/IPS VM for network security
  4. **Phase 6 (Future):** Advanced Attack Lab (Kali Linux, Metasploitable, T-Pot honeypot)
  5. (Optional) Migrate services to use Vault dynamic credentials (Node-RED, Grafana, etc.)
  6. (Optional) Enable TLS/HTTPS on Vault with self-signed certificate
  7. (Optional) Implement data retention policies in PostgreSQL
  8. (Optional) Add email/Slack notifications for Grafana alerts
  9. (Optional) Configure HTTPS with Let's Encrypt for OAuth2 Proxy

Tell Claude: "Let's continue with the project. Read NETWORK_SETUP_PROGRESS.md for current status."
