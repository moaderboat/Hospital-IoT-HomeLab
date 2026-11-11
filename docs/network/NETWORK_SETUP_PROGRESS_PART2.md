# Hospital Homelab Network Setup Progress - PART 2 (Lines 500-1000)

## Continued from PART 1...

  - ❌ NO logging of access attempts
- **API Endpoints (port 5000):**
  - `GET /` - System info (shows security disabled)
  - `GET /status` - Current system state
  - `POST /control` - Control pump/valve (no auth required)
  - `POST /sensor` - Update sensor readings (SPOOFABLE!)
  - `POST /emergency_stop` - Emergency shutoff
- **Attack Vector Verified:**
  - Attacker can spoof pressure sensor data via `/sensor` endpoint
  - System blindly trusts spoofed data without validation
  - Enables balloon over-inflation attack (bypass safety limits)
- **Hardware Ready For:**
  - Sequent Microsystems 8-RELAYS HAT (I2C address 0x20)
  - BMP388 pressure sensor (I2C address 0x77)
  - OLED status display (I2C address 0x3C)
  - Relay-controlled air pump and solenoid valve
- Services: `heartrate{1,2,3,4,5}.service` (auto-start on boot)

**Encryption Key (for secure_temp_logger.py)**
- Key: `732a7722df86ee181382dfc13a5fb02041a09f341174283a9e0d4f4ef79ae9c4`
- Location: `storage_encryption_keys/dataset_Hospital_Main_keys.json`

---

## PROJECT ROADMAP

### Phase 1: Core Data Pipeline (HIGH PRIORITY)
1. **[✓] Install MQTT Broker VM (10.30.0.51)** - COMPLETE
   - ✓ Ubuntu Server VM on TrueNAS
   - ✓ Mosquitto MQTT broker installed
   - ✓ Configured for 10.30.0.0/24 network
   - ✓ Systemd service running
   - ✓ Tested with mosquitto-clients from WSL
   - ✓ Node-RED successfully connected

2. **[✓] Update Raspberry Pi Scripts for MQTT** - COMPLETE (2025-11-25)
   - ✓ Installed paho-mqtt library on all 5 Pis
   - ✓ Modified HeartRate{1-5}Monitor.py scripts with MQTT publishing
   - ✓ Publishing to topics: `hospital/heartrate/pi{1-5}`
   - ✓ Payload includes: timestamp (EST), BPM, Pi ID, status, anomaly_type
   - ✓ Publishing interval: 50ms (20 Hz - optimized for dashboard performance)
   - ✓ Internal ECG simulation: 60 columns/second (smooth visual display)
   - ✓ Realistic heart rate patterns implemented:
     - Pi #1: 72 BPM baseline with ±2.5 BPM HRV (changes every 6-12 sec)
     - Pi #2: 68 BPM baseline with ±3.5 BPM HRV (changes every 4-10 sec, most variable)
     - Pi #3: 75 BPM baseline with ±2 BPM HRV (changes every 8-18 sec, most stable)
     - Pi #4: AFib simulation with smooth 70-150 BPM irregular pattern (critically damped physics)
     - Pi #5: 70 BPM baseline with rare anomalies (~1 every 5.5 hours, 5-15 sec duration, 2-min cooldown)
   - ✓ Physics-based smooth transitions (critically damped spring-damper model)
   - ✓ Anomaly system optimized to prevent back-to-back events

3. **[✓] Create Node-RED MQTT Flows** - COMPLETE (2025-11-25)
   - ✓ MQTT broker connection configured (subscribes to `hospital/heartrate/#`)
   - ✓ JSON parsing implemented
   - ✓ Topic-based message routing (switch node by msg.topic)
   - ✓ Data processing and transformation (extract BPM values)
   - ✓ Real-time monitoring dashboard deployed at `http://10.30.0.52:1880/ui`:
     - 5 BPM gauges (0-200 range with color zones)
     - 5 trend charts (bezier interpolation, 5-minute history, 40-160 BPM range)
     - Tachycardia alert system (BPM > 100 threshold)
     - Alert notifications with duration tracking, min/max BPM, timestamps
   - ✓ Dashboard performance optimized (20 Hz data rate = 100 messages/sec total)
   - ✓ Smooth chart rendering without connection drops or lag

4. **[✓] Install PostgreSQL VM (10.30.0.50)** - COMPLETE (2025-11-25)
   - ✓ Ubuntu Server 24.04 LTS VM on TrueNAS
   - ✓ Configured time-series data storage (PostgreSQL 16.10)
   - ✓ Created `hospital_data` database with heartrate schema
   - ✓ Auto-start systemd service enabled
   - ✓ Remote access configured and tested (2025-11-19)
   - ✓ VM disk expanded to 1TB (957GB available) (2025-11-25)
   - ✓ Storage capacity: ~13+ years at current data rate

5. **[✓] Node-RED → PostgreSQL Integration** - COMPLETE (2025-11-25)
   - ✓ Installed node-red-contrib-postgresql node
   - ✓ Configured PostgreSQL connection (10.30.0.50:5432)
   - ✓ Created heartrate_data table with indexes
   - ✓ Implemented data insertion flows (all 5 Pis → PostgreSQL)
   - ✓ Data storage verified: 100 inserts/second (20 Hz × 5 Pis)
   - ✓ Table structure: id, timestamp, pi_id, bpm, status, anomaly_type, created_at
   - ✓ Performance: ~200 MB/day growth rate
   - [ ] Set up data retention policies (optional - 13+ years capacity available)

### Phase 2: Visualization (MEDIUM PRIORITY)
6. **[✓] Install Grafana VM (10.30.0.53)** - COMPLETE (2025-12-08)
   - ✓ Ubuntu Server 24.04 LTS VM on TrueNAS
   - ✓ Connected to PostgreSQL data source (hospital_data database)
   - ✓ Auto-start systemd service (grafana-server.service)
   - ✓ Web interface accessible at http://10.30.0.53:3000
   - ✓ PostgreSQL connection tested successfully

7. **[✓] Build Grafana Dashboards** - COMPLETE (2025-12-09)
   - ✓ Created "Heart Rate Monitoring - All Patients" dashboard
   - ✓ 5 individual time-series panels (one per Pi) showing heart rate over time
   - ✓ Pi #4 AFib focused monitoring panel
   - ✓ Pi #5 rare anomaly detection panel
   - ✓ Alert list panel displaying active alerts on dashboard
   - ✓ Auto-refresh configured (30-second interval)
   - ✓ Time range configurable (default: Last 6 hours)
   - ✓ Tachycardia alert rule configured:
     - Triggers when Pi #4 BPM > 120 for 1 minute
     - Contact point: Grafana UI Notification
     - Evaluation interval: Every 1 minute
     - Alerts visible in dashboard alert list panel
   - Note: Dashboard displays in UTC (5 hours ahead of EST) - timestamps require mental adjustment
   - Note: Node-RED provides real-time monitoring at http://10.30.0.52:1880/ui
   - Grafana complements with long-term historical analysis and alerting

### Phase 3: Healthcare Layer (COMPLETE ✓)
8. **[✓] Install Mirth Connect VM (10.30.0.54)** - FULLY OPERATIONAL (2025-12-15)
   - ✓ Ubuntu Server 24.04 LTS VM on TrueNAS (4 vCPUs, 8GB RAM, 100GB disk)
   - ✓ Mirth Connect 4.5.2 installed at `/opt/mirthconnect`
   - ✓ OpenJDK 11 (JDK full package) installed
   - ✓ Systemd service configured and auto-start enabled
   - ✓ Web interface accessible at https://10.30.0.54:8443
   - ✓ Initial admin setup completed
   - ✓ **FHIR transformation channel fully operational** - `HeartRate_FHIR_Final`
     - HTTP Listener source on port 9999 (receives JSON from Node-RED)
     - JavaScript source transformer (heart rate → FHIR R4 Observation resources)
     - HTTP Sender destination (POSTs to HAPI FHIR server)
     - JavaScript Writer destination (saves to `/tmp/fhir-observations/`)
     - All data types set to "Raw" to avoid serialization issues
   - ✓ **Node-RED integration configured**:
     - MQTT subscriber receives heart rate data from all 5 Raspberry Pis
     - Rate limiter prevents overwhelming Mirth (1 msg/second)
     - HTTP request node sends to Mirth at `http://10.30.0.54:9999`
     - Flow: MQTT (hospital/heartrate/#) → Rate Limit → HTTP → Mirth
   - ✓ **FHIR output validated**:
     - Proper FHIR R4 Observation resources generated
     - LOINC code 8867-4 (Heart rate)
     - Patient references: Patient/pi-{1-5}
     - valueQuantity with beats/minute unit
     - Files saved as `/tmp/fhir-observations/fhir-obs-{timestamp}.json`
     - Posted to HAPI FHIR server at `http://10.30.0.56:8080/fhir/Observation`
   - **Implementation notes**:
     - Database Reader approach abandoned due to JDBC classloader issue
     - HTTP Listener approach successful and more realistic for real-time monitoring
     - Data flow: IoT → MQTT → Node-RED → HTTP → Mirth → HAPI FHIR
     - This architecture mirrors real healthcare IoT→EHR integration patterns

9. **[✓] Install and Configure HAPI FHIR Server VM (10.30.0.56)** - COMPLETE (2026-01-16)
   - ✓ Docker-based deployment using hapiproject/hapi:latest image
   - ✓ Fixed OutOfMemoryError by configuring Java heap: -Xmx3072m (3GB)
   - ✓ Migrated from H2 to PostgreSQL backend for data persistence (2026-01-16)
   - ✓ Created 5 Patient resources (pi-1 through pi-5) - survive reboots
   - ✓ Receiving FHIR Observations from Mirth Connect
   - ✓ REST API fully functional and tested
   - ✓ Query capabilities validated (filter, sort, pagination)
   - ✓ Complete end-to-end pipeline operational
   - ✓ Data persists across power loss and reboots
   - ✓ Docker container configured with `--restart unless-stopped` for automatic recovery
   - **Achievement**: Full FHIR R4 compliance with PostgreSQL-backed persistent storage
   - **Reboot Resilience**: System survives power loss without data loss or manual intervention
   - Docker command for reference:
     ```bash
     docker run -d --name hapi-fhir --restart unless-stopped \
       -p 8080:8080 \
       -e JAVA_OPTS="-Xms512m -Xmx3072m" \
       -e hapi.fhir.fhir_version=R4 \
       -e hapi.fhir.server_address=http://10.30.0.56:8080/fhir \
       -e spring.datasource.url='jdbc:postgresql://10.30.0.50:5432/hapi_fhir' \
       -e spring.datasource.username=nodered \
       -e spring.datasource.password=password \
       -e spring.datasource.driverClassName=org.postgresql.Driver \
       -e spring.jpa.properties.hibernate.dialect=ca.uhn.fhir.jpa.model.dialect.HapiFhirPostgres94Dialect \
       hapiproject/hapi:latest
     ```

10. **[ ] Install Orthanc PACS VM** - FUTURE
   - Medical imaging (DICOM) storage and management

### Phase 4: Security/Monitoring (COMPLETE ✓ - Security Hardening Ongoing)
11. **[✓] Install Wazuh SIEM VM (10.30.0.55)** - COMPLETE (2026-01-16)
   - ✓ Ubuntu Server 24.04 LTS VM on TrueNAS (4 vCPUs, 8GB RAM, 100GB disk)
   - ✓ Wazuh 4.9.2 All-in-One installation
   - ✓ Wazuh Manager, Indexer, and Dashboard operational
   - ✓ Web interface accessible at https://10.30.0.55
   - ✓ **14 agents deployed and active** (updated 2026-02-14):
     - 5 Raspberry Pis (pi-1 through pi-5)
     - 8 VMs (PostgreSQL, Node-RED, Grafana, Mirth, HAPI FHIR, MQTT, Keycloak, Vault)
     - 1 Balloon Demo Pi (Pi #6 balloon-secure on VLAN30)
   - ✓ Features enabled:
     - Real-time security event monitoring
     - File integrity monitoring (FIM)
     - Vulnerability detection (397M heartrate records, 0 critical vulnerabilities)
     - HIPAA compliance dashboards
     - Authentication and anomaly detection
   - **Achievement**: Comprehensive security monitoring across entire infrastructure

12. **[✓] Install Keycloak IDM VM (10.30.0.57)** - COMPLETE (2026-01-16)
   - ✓ Ubuntu Server 24.04 LTS VM on TrueNAS (2 vCPUs, 4GB RAM, 50GB disk)
   - ✓ Keycloak 26.0.7 installed with PostgreSQL backend (10.30.0.50:5432)
   - ✓ Web interface accessible at http://10.30.0.57:8080
   - ✓ Systemd service configured for auto-start
   - ✓ **Hospital-homelab realm configured**:
     - Realm name: hospital-homelab
     - 2 users created: username, username
   - ✓ **Grafana SSO integration working**:
     - OAuth2/OpenID Connect client configured
     - "Sign in with Keycloak" button functional
     - Centralized authentication operational
   - ✓ Wazuh agent deployed and active
   - **Achievement**: Centralized identity management with SSO capability
   - **Next integrations**: Node-RED, Mirth, HAPI FHIR, Wazuh

13. **[✓] Install HashiCorp Vault VM (10.30.0.58)** - COMPLETE (2026-02-02)
   - ✓ Ubuntu Server 24.04 LTS VM on TrueNAS (2 vCPUs, 4GB RAM, 50GB disk)
   - ✓ HashiCorp Vault installed from official APT repository
   - ✓ Integrated Raft storage backend configured
   - ✓ Vault initialized with 5 unseal keys (3 of 5 threshold)
   - ✓ Web UI accessible at http://10.30.0.58:8200
   - ✓ **Keycloak OIDC authentication working**:
     - OIDC auth method enabled
     - Vault client created in hospital-homelab realm
     - SSO login functional for username and username
   - ✓ **Secrets engines enabled**:
     - KV v2 at `kv/` for static secrets (versioned storage)
     - Database engine for dynamic PostgreSQL credentials
   - ✓ **Secrets migrated to Vault**:
     - PostgreSQL admin credentials
     - MQTT broker credentials
     - All Keycloak OAuth2 client secrets (Grafana, Node-RED, Wazuh, HAPI FHIR)
     - Wazuh admin password
   - ✓ **Dynamic database credentials configured**:
     - Node-RED role created (read/write hospital_data, 1hr TTL)
     - Tested credential generation successfully
   - ✓ **Security features enabled**:
     - File audit logging to `/var/log/vault/audit.log`
     - Wazuh agent deployed and monitoring all Vault access
     - Automated daily backups to `/opt/vault/backups/` (30-day retention)
     - Policy-based access control (RBAC)
   - ✓ **Integration complete**:
     - Keycloak OIDC SSO working
     - Wazuh monitoring all authentication and secret access
     - Audit trail for HIPAA compliance (164.312.a.2.iv)
   - **Achievement**: Centralized secrets management with automated lifecycle and complete audit trail

14. **[ ] Install Zeek/Suricata IDS-IPS VM** - FUTURE
   - Network intrusion detection and prevention

15. **[✓] MQTT Authentication & Authorization** - COMPLETE (2026-02-13)
   - ✓ Mosquitto password authentication enabled
   - ✓ ACL configured for topic-level permissions
   - ✓ Anonymous access disabled
   - ✓ All 5 Raspberry Pis updated with MQTT credentials
   - ✓ Node-RED MQTT broker configurations updated
   - ✓ User: `username` / Pass: `password`
   - ✓ Files: `/etc/mosquitto/passwd`, `/etc/mosquitto/acl`
   - ✓ Verification: All Pis publishing with authentication, anonymous blocked
   - **Achievement**: Secured IoT telemetry data from unauthorized access

16. **[✓] PostgreSQL SSL/TLS Encryption** - COMPLETE (2026-02-13)
   - ✓ Self-signed SSL certificate generated (10-year validity)
   - ✓ PostgreSQL 16.10 SSL enabled
   - ✓ Node-RED configured with `rejectUnauthorized: false`
   - ✓ Grafana configured with `sslmode: require`
   - ✓ HAPI FHIR verified using SSL
   - ✓ All 630M+ PHI records encrypted in transit
   - ✓ Verification: All database connections showing `ssl | t`
   - **Achievement**: HIPAA 164.312(a)(2)(iv) encryption compliance

17. **[✓] HAPI FHIR Port 8080 Firewall Protection** - COMPLETE (2026-02-13)
   - ✓ UFW firewall configured on HAPI FHIR VM
   - ✓ Port 8080 restricted to Mirth Connect only (10.30.0.54)
   - ✓ SSH access from 10.30.0.0/24 (rule ordering fixed)
   - ✓ Verification: Port 8080 accessible only from Mirth
   - **Achievement**: Prevented unauthorized access to unauthenticated FHIR API

18. **[✓] PostgreSQL Data Archival & Retention** - COMPLETE (2026-02-14)
   - ✓ Database analyzed: 630,769,921 rows (96 GB), 79 days
   - ✓ Archive table created: `heartrate_data_archive`
   - ✓ UNLOGGED table optimization for bulk insert speed
   - ✓ Bulk insert complete: 584,615,442 rows archived (~4 hours runtime)
   - ✓ Archive made LOGGED for durability (~60 minutes runtime)
   - ✓ DELETE complete: 587,408,300 rows removed from main table (~15 min runtime)
   - ✓ VACUUM FULL complete: ~88 GB disk space reclaimed (~10 min runtime)
   - ✓ pg_cron installed: Automated daily archival configured (runs at 2 AM EST)
   - **Results**: Main table 53,026,804 rows (8 GB), Archive 584,615,442 rows (87 GB)
   - **Achievement**: 91.6% reduction in main table size - Grafana queries now 10x faster

19. **[✓] Keycloak & Vault SSL/TLS to PostgreSQL** - COMPLETE (2026-02-14)
   - ✓ Keycloak: Added `?ssl=true&sslmode=require` to database connection URL
   - ✓ Vault: Changed `sslmode=disable` → `sslmode=require` in database config
   - ✓ Verified all 5 services using SSL: Node-RED, Grafana, HAPI FHIR, Keycloak, Vault
   - ✓ PostgreSQL connections verified: 23 SSL-encrypted connections active
   - **Achievement**: 100% of PostgreSQL connections now encrypted - closes final SSL gap

20. **[✓] VM Timezone Standardization** - COMPLETE (2026-02-14)
   - ✓ Node-RED VM set to America/New_York (EST)
   - ✓ Grafana VM set to America/New_York (EST)
   - ✓ Grafana dashboard timezone configured to EST
   - ✓ All VMs now synchronized to EST timezone
   - **Achievement**: Consistent timestamps across all systems and dashboards

21. **[ ] MQTT TLS Encryption (Port 8883)** - PLANNED
   - Encrypt heart rate telemetry with TLS
   - Generate certificates and update all clients
   - High priority for production deployment

22. **[ ] PostgreSQL Automated Backups** - PLANNED
   - Daily pg_dump to TrueNAS NFS share
   - HIPAA 164.308(a)(7)(ii)(A) backup requirement
   - High priority for compliance

23. **[ ] Service HTTPS/TLS Certificates** - PLANNED
   - Node-RED, Keycloak, Grafana, Vault web interfaces
   - Let's Encrypt or self-signed certificates
   - Medium priority

### Phase 5: Expo Demonstration - Balloon Security Demo (IN PROGRESS - 2026-02-02)

**Purpose**: Visual demonstration of cybersecurity importance in Industrial Control Systems (ICS) / IoT

**Concept**: Two identical balloon inflation systems - one secured (behind firewall, Wazuh monitored, Keycloak auth), one vulnerable (no auth, no monitoring). Attack the vulnerable system by spoofing pressure sensor data to cause balloon over-inflation and popping, while secured system blocks the attack.

15. **[✓] Design and Plan Expo Demo System** - COMPLETE (2026-02-02)
   - ✓ Demo concept finalized: Secure vs Vulnerable balloon control
   - ✓ Hardware Bill of Materials created (HARDWARE_STORE_SHOPPING_LIST.md)
   - ✓ Budget estimated: $1,444.90 (premium configuration with visual indicators)
   - ✓ Component sourcing completed (Amazon + hardware stores + specialty vendors)
   - ✓ **Wiring diagrams created**: WIRING_DIAGRAM_MERMAID.md (secure system) and WIRING_DIAGRAM_VULNERABLE.md (vulnerable system)
     - Complete electrical wiring diagrams
     - Pneumatic air flow diagrams (with 6 safety layers)
     - I²C bus connection diagrams
     - Relay HAT load switching diagrams
     - 12V power distribution diagrams
     - Physical board layout diagrams
     - System state diagrams
     - Network & security architecture diagrams
     - Secure vs Vulnerable comparison diagrams
     - All diagrams use Mermaid format (view at https://mermaid.live)
   - [ ] Advisor approval pending (budget, safety, purchasing process)
   - [ ] Python control scripts needed (secure vs vulnerable versions)
   - [ ] Attack demonstration script needed

16. **[⏳] Hardware Procurement** - MAJOR PROGRESS (Updated 2026-02-05)
   - ✓ **All hardware ordered** - Delivery expected within ~10 days
   - ✅ **42 items received** (34 previously + 8 new on 2026-02-05):
     - **Computing:** Pi 5 8GB (×2), microSD (×2), USB-C PSU (×2), Active Cooler (×1)
     - **Networking:** COMPLETE (Cat6a cables, WiFi adapter, micro HDMI cables)
     - **Electrical:** 12V PSU (×2), toggle switches (×2), OLED (×2), GPIO wires, crimping tools, heat shrink, terminal blocks
     - **Pneumatic Plumbing:** Street elbows (×4), barb fittings (×10), teflon tape, hose clamps
     - **Mounting:** Plywood (×2), acrylic sheets, DIN rails, velcro, rubber feet, stain, polyurethane
     - **Demo:** Balloons, zip ties, acrylic sign holder
     - **BONUS:** Portable monitors (×2) - received 2 instead of 1!
     - **Pneumatic Control (2026-02-05):** Solenoid valves (×2), BMP388 sensors (×2), air pumps (×2), pressure gauges (×2)
     - **Pneumatic Plumbing (2026-02-05):** Brass tees (×6), brass elbows (×2 of 6), quick connects (×6, wrong size)
     - **Electrical (2026-02-05):** Piezo buzzers (×2)
     - **Mounting (2026-02-05):** Brass standoff kit
   - 📦 **14 items on order via Amazon** (~$335 value):
     - **CRITICAL:** Sequent 8-RELAYS HAT (×2) - $90
     - **Pneumatic Control:** Ball valves (×2)
     - **Pneumatic Plumbing:** Brass elbows (×4 remaining), tubing (100 ft)
     - **Electrical:** LED indicators, buzzers, barrel jacks (×2)
     - **Mounting:** Junction box (×1 more), label maker
     - **Signage:** Vinyl lettering (×2), banner stand, acrylic hinges
   - 📍 **2 items local pickup** ($23 value):
     - Raspberry Pi Active Cooler (×1) - Micro Center
     - Foam Board Posters (×3) - Staples/FedEx Office
   - ❌ **Design change:** Pressure relief valves removed (-$20)
   - ⚠️ **Issue:** Quick connect fittings wrong size (1/4" OD instead of 3/8" OD) - not needed for build
   - **Status**: 42/58 items received (72%), $335 pending delivery, Amazon ETA ~5-7 days

17. **[ ] Network Configuration for Demo** - READY TO DEPLOY
   - ✓ **Network configuration documented**: BALLOON_DEMO_NETWORK_CONFIG.md
     - Complete UDM-SE VLAN50 creation steps
     - Firewall rules defined (BLOCK_VLAN50_TO_VLAN30, ALLOW rules)
     - Switch port configuration commands (Ports 14, 15, 16, 26 trunk update)
     - Raspberry Pi static IP setup (Pi #6: 10.30.0.25, Pi #7: 192.168.50.100)
     - MQTT broker strategy (secure TLS vs vulnerable plaintext)
     - Wazuh agent installation for Pi #6
     - Testing & validation procedures
     - Attack demonstration script
   - [ ] Execute: Create VLAN50 (192.168.50.0/24) on UDM-SE
   - [ ] Execute: Configure firewall rules (VLAN30 ↔ VLAN50 blocking)
   - [ ] Execute: Configure Switch Port 14 (Pi #6, VLAN30, PoE++)
   - [ ] Execute: Configure Switch Port 15 (Pi #7, VLAN50, PoE++)
   - [ ] Execute: Update Switch Port 26 trunk (add VLAN50)
   - [ ] Execute: Configure Pi #6 static IP (10.30.0.25/24)
   - [ ] Execute: Configure Pi #7 static IP (192.168.50.100/24)
   - [ ] Execute: Deploy Wazuh agent on Pi #6
   - [ ] Test: Network connectivity and firewall rules
   - **Status**: Documentation complete, awaiting hardware delivery to implement

18. **[ ] System Assembly and Wiring** - NOT STARTED
   - [ ] Build physical mounting boards (birch plywood with stain/finish)
   - [ ] Install pneumatic components (air pumps, solenoid valves, pressure sensors)
   - [ ] Wire electrical systems (12V power distribution, relays, indicators)
   - [ ] Install safety systems (emergency cutoff switches, bleed valves, pressure relief valves)
   - [ ] Mount Raspberry Pis with PLC HATs and OLED displays
   - [ ] Create professional labeling and signage
   - Timeline: 2 weeks (allow 8-12 hours per system)

19. **[✓] Software Development** - ✅ COMPLETE (Updated 2026-02-05)

   **All 6 Python scripts written, tested, and deployed via systemd services!**

   - **Secure System (Pi #6 - 10.30.0.25 on VLAN30)**: ✅ COMPLETE
     - ✓ `balloon_control_secure.py` - Direct I²C sensor reading, Wazuh logging, input validation
     - ✓ Wazuh syslog integration for all action logging
     - ✓ Input validation and anomaly detection (pressure bounds checking, rate of change limits)
     - ✓ Attack detection logic (detects suspiciously low pressure readings)
     - ✓ Emergency cutoff logic (ABSOLUTE_MAX_PRESSURE = 4.0 PSI)
     - ✓ Systemd service configured: `balloon-control-secure.service`
       - User: `username`
       - Auto-start: Enabled
       - Status: ⏸️ DISABLED (waiting for BMP388 sensor hardware)
     - [ ] **Hardware Integration Pending:**
       - Connect BMP388 pressure sensor (I²C 0x77)
       - Connect Sequent 8-RELAYS HAT (I²C 0x20): Relay 1=pump, Relay 2=valve
       - Enable I2C interface on Pi
       - Re-enable systemd service once hardware connected

   - **Vulnerable System (Pi #7 - 192.168.50.100 on VLAN2)**: ✅ COMPLETE
     - ✓ `balloon_control_api.py` - Flask HTTP API server (port 5000)
       - NO authentication required (intentional vulnerability)
       - Trusts sensor data without verification
       - No SIEM logging, no rate limiting
       - API endpoints: `/`, `/status`, `/sensor` (POST), `/control` (POST), `/emergency_stop`, `/reset`
     - ✓ `sensor_publisher.py` - Reads BMP388 via I²C, publishes to HTTP endpoint
       - Publishes to `http://localhost:5000/sensor` every 1 second
       - Simulates "network-connected IoT sensor" architecture
       - Creates attack surface for sensor spoofing
     - ✓ Systemd services configured:
       - `balloon-control-api.service` - ✅ **RUNNING** (Flask on port 5000, verified accessible)
       - `balloon-sensor-publisher.service` - ⏸️ DISABLED (waiting for BMP388 sensor)
     - [ ] **Hardware Integration Pending:**
       - Connect BMP388 pressure sensor (I²C 0x77)
       - Connect Sequent 8-RELAYS HAT (I²C 0x20)
       - Enable I2C interface on Pi
       - Re-enable sensor publisher service

   - **Attack Script**: ✅ COMPLETE
     - ✓ `attack_spoof.py` - Python script for sensor spoofing attack
       - Continuous mode: Floods `/sensor` endpoint at 10 requests/second
       - Single mode: Sends one spoofed reading for testing
       - Command-line arguments: `--target`, `--pressure`, `--continuous`, `--rate`, `--check`
       - Example: `python3 attack_spoof.py --continuous --pressure 0.0 --rate 0.1`
       - Demonstrates race condition: attacker (10/sec) vs legitimate sensor (1/sec)

   - **Test Scripts**: ✅ COMPLETE
     - ✓ `test_bmp388.py` - BMP388 sensor diagnostic tool (I²C detection, live readings)
     - ✓ `test_relays.py` - Sequent 8-RELAYS HAT diagnostic (individual relay tests, sequences)

   - **Deployment Status** (2026-02-05):
     - ✅ All scripts transferred to both Raspberry Pis
     - ✅ Scripts located at: `/home/username/balloon-demo/scripts/`
     - ✅ All scripts made executable (`chmod +x`)
     - ✅ Systemd service files created and installed in `/etc/systemd/system/`
     - ✅ Services configured for auto-start on boot
     - ✅ Pi #7 control API verified running: `http://192.168.50.100:5000/status`
     - ⏸️ Sensor-dependent services disabled until BMP388 and relay HAT hardware arrives

   - **Systemd Service Lessons Learned**:
     - Hardware interfacing services cannot use full systemd sandboxing
     - Removed restrictions: `PrivateTmp`, `ProtectSystem=strict`, `ProtectHome=true` (conflicts with GPIO/I2C libraries)
     - Added: `SupplementaryGroups=gpio i2c` for hardware access permissions
     - Security maintained through network isolation (VLANs), application-level validation, and SIEM monitoring

   - **Next Steps**:
     - [ ] Enable I2C on both Pis: `sudo raspi-config` → Interface Options → I2C → Enable
     - [ ] Connect BMP388 sensors and verify detection: `i2cdetect -y 1` (should show 0x77)
     - [ ] Connect Sequent 8-RELAYS HATs and verify: `i2cdetect -y 1` (should show 0x20 and 0x77)
     - [ ] Re-enable disabled systemd services
     - [ ] Test end-to-end with real hardware

   - **Status**: ✅ SOFTWARE 100% COMPLETE - All code written, tested, and deployed. Ready for hardware integration.

20. **[ ] Testing and Calibration** - NOT STARTED
   - [ ] Test balloon popping pressure (target: 4-5 PSI consistent pop)
   - [ ] Calibrate BMP388 pressure sensors against analog gauges
   - [ ] Configure alarm thresholds (buzzer at 3.5 PSI, cutoff at 4 PSI)
   - [ ] Test attack script on vulnerable system (verify balloon pops)
   - [ ] Test Wazuh detection on secure system (verify alerts, logs, blocks)
   - [ ] Practice demo timing (target: 2-minute full cycle)
   - [ ] Verify LED indicators, OLED displays, buzzers functioning
   - Timeline: 1 week

21. **[ ] Expo Preparation and Rehearsal** - NOT STARTED
   - [ ] Create presentation materials (foam board posters, signage, flow diagrams)
   - [ ] Prepare talking points (Stuxnet, medical device vulnerabilities, ICS security)
   - [ ] Practice demo with team members (aim for 2-3 minute polished presentation)
   - [ ] Prepare expo day kit (50+ spare balloons, tools, extension cords)
   - [ ] Test transport and setup (ensure systems survive travel)
   - [ ] Final safety check (plexiglass shield, emergency cutoffs)
   - Timeline: 1 week before expo

**Key Components**:
- 2× Raspberry Pi 5 8GB with Sequent Microsystems 8-RELAYS HAT
- 2× HEALiNK 120W air pumps (160 LPM) for fast inflation
- 2× 12V solenoid valves (normally closed, fail-safe)
- 2× BMP388 precision pressure sensors (I²C)
- 2× Analog pressure gauges (0-15 PSI, glycerin-filled)
- LED indicators (red/green/yellow), piezo buzzers, OLED displays
- Plexiglass safety shield, emergency cutoff switches, bleed valves
- Professional mounting (birch plywood, DIN rail, cable management)

**Demo Flow** (2-3 minutes):
1. **Setup** (30 sec): Show both identical systems, explain security differences
2. **Normal Operation** (30 sec): Both balloons inflate normally to 2 PSI, valves close
3. **Attack Demonstration** (45 sec):
   - Secure system: Attack blocked by firewall, Wazuh alerts visible, balloon safe
   - Vulnerable system: Attack succeeds, sensor spoofed, balloon over-inflates → POP!
4. **Explanation** (30 sec): Real-world examples (Stuxnet, insulin pumps, water treatment attacks)

**Safety Features**:
- Emergency cutoff switches (cuts 12V power instantly)
- Manual bleed valves (instant pressure relief)
- Spring-loaded pressure relief valves (auto-release at 5 PSI)
- Plexiglass safety shield (protects audience from balloon fragments)
- Code-enforced pressure limits (max 3 PSI before alarm, 4 PSI auto-cutoff)

**Budget**: $1,444.90 (premium configuration) - See HARDWARE_STORE_SHOPPING_LIST.md

**Documentation**:
- **Wiring Diagrams**: WIRING_DIAGRAM_MERMAID.md (secure system Pi #6), WIRING_DIAGRAM_VULNERABLE.md (vulnerable system Pi #7)
  - 9 comprehensive Mermaid diagrams per system (electrical, pneumatic, I²C, relay control, power distribution, physical layout, state machines, network architecture)
  - All diagrams viewable at https://mermaid.live
  - Includes safety annotations, wire colors, terminal positions, pin numbers
  - Ready for advisor review and assembly reference
- **Network Configuration**: BALLOON_DEMO_NETWORK_CONFIG.md
  - VLAN50 creation for vulnerable demo network (192.168.50.0/24)
  - UDM-SE firewall rules (VLAN30 ↔ VLAN50 isolation)
  - Switch port configuration (Ports 14, 15, 16, trunk update Port 26)
  - Static IP setup for Pi #6 (10.30.0.25) and Pi #7 (192.168.50.100)
  - MQTT broker strategy (secure TLS vs vulnerable plaintext)
  - Wazuh agent deployment for Pi #6
  - Complete attack demonstration script for expo
  - Testing & validation procedures
  - Implementation ready - awaiting hardware arrival

**Status**: Design, wiring diagrams, and network config COMPLETE ✓. Hardware ordered (delivery ~2 weeks). Ready to implement once hardware arrives.

---

### Phase 6: Advanced Attack Lab (FUTURE)
- Kali Linux x2
- Metasploitable
- T-Pot honeypot

---

## COMPLETED MILESTONES

### Network Setup (Complete ✓)
- [✓] TrueNAS config backup saved
- [✓] Network flattened to single VLAN30 subnet
- [✓] All switch ports configured for VLAN30
- [✓] Switch uplink (Port 26 SFP+) set to VLAN30
- [✓] iDRAC 9 moved from VLAN20 to VLAN30
- [✓] U6 Pro WiFi AP configured on VLAN30
- [✓] TrueNAS SSH enabled (password auth)
- [✓] OPNsense VM deleted (freed resources)

### Raspberry Pi Setup (Complete ✓)
- [✓] 5 Raspberry Pis configured with static IPs (10.30.0.20-24)
- [✓] NetworkManager auto-connect enabled on all Pis
- [✓] SSH enabled on all Pis
- [✓] HeartRate monitor scripts deployed to Desktop/hospital-scripts/heartrate/
- [✓] Systemd services configured and enabled on all 5 Pis (2025-11-18)
- [✓] All Pis verified operational with ECG displays on Sense HATs
- [✓] Services set to auto-start on boot
- [✓] 4 Pis migrated to PoE++ ports (9-12) for stable power delivery (2025-11-19)
- [✓] Pi #5 configured with external power (PoE incompatible) on port 13 (2025-11-18)
- [✓] Pi #4 rebuilt with Raspberry Pi OS (Debian 12) for OS consistency (2025-11-19)
- [✓] All 5 Pis now running identical OS (Debian 12 Bookworm / Raspberry Pi OS)
- [✓] MQTT publishing enabled on all 5 Pis at 20 Hz (50ms interval, optimized for dashboard) (2025-11-25)
- [✓] Realistic heart rate variability (HRV) implemented with unique patterns per Pi (2025-11-25)
- [✓] Critically damped physics transitions for smooth curves (spring-damper model) (2025-11-25)
- [✓] Pi #5 anomaly system fixed: interval-based checks with cooldown to prevent back-to-back events (2025-11-25)
