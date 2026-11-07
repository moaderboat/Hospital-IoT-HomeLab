# Hospital Homelab Network Setup Progress - PART 1 (Lines 1-500)

## Date: Started 2025-11-09, Last Updated 2026-02-13 (Phase 5 Expo Demo - IDS Infrastructure Complete ✓, Security Hardening Complete ✓, Data Archival In Progress 🔄)

## STATUS: ALL SYSTEMS STANDARDIZED ✓
All 5 Raspberry Pis running Debian 12 (Raspberry Pi OS) with systemd services (4 on PoE++, 1 external power)

---

## NETWORK INFRASTRUCTURE

### Core Network Devices
| Device | IP Address | Connection | Status |
|--------|------------|------------|--------|
| UDM-SE (Gateway) | 10.30.0.1 | N/A | ✓ Operational |
| UniFi Switch Pro Max 24 PoE | 10.30.0.10 | UDM-SE Port 11 (SFP+) | ✓ Operational |
| TrueNAS Server | 10.30.0.44 | UDM-SE Port 3 | ✓ Operational |
| iDRAC 9 (Server Mgmt) | 10.30.0.45 | UDM-SE Port 5 | ✓ Operational |
| Node-RED VM | 10.30.0.52 | Virtual (TrueNAS) | ✓ Operational |
| MQTT Broker VM | 10.30.0.51 | Virtual (TrueNAS) | ✓ Operational |
| Grafana VM | 10.30.0.53 | Virtual (TrueNAS) | ✓ Operational |
| Mirth Connect VM | 10.30.0.54 | Virtual (TrueNAS) | ✓ Operational |
| HAPI FHIR Server VM | 10.30.0.56 | Virtual (TrueNAS) | ✓ Operational |
| Wazuh SIEM VM | 10.30.0.55 | Virtual (TrueNAS) | ✓ Operational |
| Keycloak IDM VM | 10.30.0.57 | Virtual (TrueNAS) | ✓ Operational |
| HashiCorp Vault VM | 10.30.0.58 | Virtual (TrueNAS) | ✓ Operational |
| Suricata IDS VM | 10.30.0.59 | Virtual (TrueNAS) | ⚠️ Deprecated - replaced by bare metal |
| Elasticsearch VM | 10.30.0.60 | Virtual (TrueNAS) | ✓ Operational |
| U6 Pro WiFi AP | 10.30.0.246 | Switch Port 17 | ✓ Operational |
| Laptop "UltraMoad" | 10.30.0.122 | UDM-SE Port 1 | ✓ Connected |
| Suricata IDS Laptop | 10.30.0.191 (pending) | Switch Ports 5+6 (dual interface) | ⚠️ In Progress - awaiting 2nd adapter |
| WSL (on UltraMoad) | 10.30.0.122 | Virtual | ✓ mosquitto-clients installed |

### Raspberry Pi Devices (Heart Rate Monitors on Switch PoE++ Ports 9-14)
| Device | IP Address | OS | Switch Port | Script | BPM Pattern | Systemd Service | Status |
|--------|------------|-------|-------------|--------|-------------|-----------------|--------|
| Pi #1 | 10.30.0.20 | Debian 12 | Port 9 (PoE++) | HeartRate1Monitor.py | 72 BPM (±2.5 HRV) | heartrate1.service ✓ | ✓ Running |
| Pi #2 | 10.30.0.21 | Debian 12 | Port 10 (PoE++) | HeartRate2Monitor.py | 68 BPM (±3.5 HRV) | heartrate2.service ✓ | ✓ Running |
| Pi #3 | 10.30.0.22 | Debian 12 | Port 11 (PoE++) | HeartRate3Monitor.py | 75 BPM (±2.0 HRV) | heartrate3.service ✓ | ✓ Running |
| Pi #4 | 10.30.0.23 | Debian 12 | Port 12 (PoE++) | HeartRate4Monitor.py | 110±40 BPM AFib (critically damped) | heartrate4.service ✓ | ✓ Running |
| Pi #5 | 10.30.0.24 | Debian 12 | Port 13 (External Power) | HeartRate5Monitor.py | 70 BPM (rare anomalies ~5.5hr) | heartrate5.service ✓ | ✓ Running |

### Raspberry Pi Devices (Expo Balloon Security Demo - IN PROGRESS)
| Device | IP Address | OS | Network | Purpose | Hardware | Status |
|--------|------------|-------|---------|---------|----------|--------|
| Pi #6 | 10.30.0.25 | Raspberry Pi OS (Debian 12) | VLAN30 (Secure) | Secured balloon control system | Pi 5 8GB + Sequent 8-RELAYS HAT | ✅ CONFIGURED (2026-02-03) |
| Pi #7 | 192.168.50.100 | Raspberry Pi OS (Debian 12) | VLAN2 (Vulnerable) | Vulnerable balloon control system | Pi 5 8GB + Sequent 8-RELAYS HAT | ✅ CONFIGURED (2026-02-03) |

### Network Configuration
- **Primary Subnet (VLAN30)**: 10.30.0.0/24 (255.255.255.0) - Secure production network
  - **Gateway**: 10.30.0.1 (UDM-SE)
  - **DNS**: 10.30.0.1 (UDM-SE)
  - **DHCP Range**: 10.30.0.6 - 10.30.0.254
  - **Devices**: All 5 heart rate monitor Pis, VMs, secured balloon demo Pi #6
- **Attack Lab Subnet (VLAN2)**: 192.168.50.0/24 - Vulnerable/exposed network ✓ CREATED (2026-02-03)
  - **VLAN ID**: 2 (VLAN50 was taken by "RED TEAM")
  - **Gateway**: 192.168.50.1 (UDM-SE)
  - **DHCP Range**: 192.168.50.10 - 192.168.50.254
  - **Purpose**: Expo balloon demo - intentionally vulnerable for attack demonstrations
  - **Devices**: Vulnerable balloon demo Pi #7, attacker laptop
  - **Firewall**: VLAN30 → VLAN2 blocked, VLAN2 → VLAN30 blocked (to be configured)

---

## NETWORK TOPOLOGY

```
Internet → Dream Router 7 (Home ISP)
            ↓ Port 10
         UDM-SE (10.30.0.1) - Gateway/Router/Firewall/DHCP
            ├─ Port 1: Laptop (10.30.0.122)
            ├─ Port 3: TrueNAS Server (10.30.0.44)
            ├─ Port 5: iDRAC 9 (10.30.0.45)
            ├─ Port 10: WAN to Dream Router 7
            └─ Port 11: Uplink to Switch Port 26 (SFP+) ↓

         UniFi Switch Pro Max 24 PoE (24 ports + 2 SFP+)
            ├─ Port 1: UniFi Cloud Key G2 Plus [IP TBD]
            ├─ Port 5: Suricata IDS Laptop - Management Interface (USB-C adapter #1) [VLAN30] [PENDING - awaiting 2nd adapter]
            ├─ Port 6: Suricata IDS Laptop - Monitoring Interface (USB-C adapter #2) [Mirroring Port 15]
            ├─ Port 9: Raspberry Pi #1 (10.30.0.20) + PoE++ [Heart Rate Monitor]
            ├─ Port 10: Raspberry Pi #2 (10.30.0.21) + PoE++ [Heart Rate Monitor]
            ├─ Port 11: Raspberry Pi #3 (10.30.0.22) + PoE++ [Heart Rate Monitor]
            ├─ Port 12: Raspberry Pi #4 (10.30.0.23) + PoE++ [Heart Rate Monitor]
            ├─ Port 13: Raspberry Pi #5 (10.30.0.24) [External power - PoE not compatible] [Heart Rate Monitor]
            ├─ Port 14: Raspberry Pi #6 (10.30.0.25) [PLANNED - Secure Balloon Demo] + External Power (Pi 5)
            ├─ Port 15: Raspberry Pi #7 (192.168.50.100) [PLANNED - Vulnerable Balloon Demo, VLAN2] + External Power (Pi 5)
            ├─ Port 17: U6 Pro WiFi AP (10.30.0.246)
            └─ Port 26 (SFP+): Uplink to UDM-SE Port 11 [VLAN30]

         TrueNAS Server (10.30.0.44)
            ├─ Network: br0 interface → VLAN30
            ├─ Storage Pool: Hospital_Main
            │  ├─ Admin_Data dataset
            │  ├─ Guest_Access dataset
            │  ├─ IoT_Data dataset
            │  ├─ ISOs dataset
            │  └─ ML_Training dataset
            └─ VMs:
               ├─ node_red_vm (10.30.0.52) ✓ OPERATIONAL
               ├─ MQTT Broker VM (10.30.0.51) ✓ OPERATIONAL
               ├─ PostgreSQL VM (10.30.0.50) ✓ OPERATIONAL
               ├─ Grafana VM (10.30.0.53) ✓ OPERATIONAL
               ├─ Mirth Connect VM (10.30.0.54) ✓ OPERATIONAL
               ├─ Wazuh SIEM VM (10.30.0.55) ✓ OPERATIONAL
               ├─ HAPI FHIR VM (10.30.0.56) ✓ OPERATIONAL
               ├─ Keycloak IDM VM (10.30.0.57) ✓ OPERATIONAL
               ├─ HashiCorp Vault VM (10.30.0.58) ✓ OPERATIONAL
               ├─ Suricata IDS VM (10.30.0.59) ⚠️ DEPRECATED (replaced by bare metal)
               └─ Elasticsearch VM (10.30.0.60) ✓ OPERATIONAL
```

---

## CREDENTIALS

### Network Devices
**UDM-SE (10.30.0.1)**
- Web: `https://10.30.0.1`
- User: `username` | Pass: `password`

**TrueNAS (10.30.0.44)**
- Web: `http://10.30.0.44`
- SSH: `ssh username@10.30.0.44`
- User: `username` | Pass: `password`

**iDRAC 9 (10.30.0.45)**
- Web: `http://10.30.0.45`
- Purpose: TrueNAS physical server management

**Node-RED VM (10.30.0.52)**
- Web: `http://10.30.0.52:1880`
- SSH: `ssh username@10.30.0.52`
- User: `username` | Pass: `password`
- **Node-RED Login Options:**
  - **SSO via Keycloak:** "Sign in with Keycloak" button (recommended)
    - Use Keycloak users: `username` or `username` with Pass: `password`
- VM Specs: 2 vCPUs, 2GB RAM, 20GB disk
- OS: Ubuntu Server 22.04 LTS
- Software: Node.js v20.x, npm v11.6.2
- Timezone: America/New_York (EST) configured (2026-02-14)
- Service: `nodered.service` (auto-starts on boot)
- **SSO Integration (2026-01-21):**
  - ✓ Keycloak OAuth2/OpenID Connect configured
  - passport-openidconnect strategy installed
  - Centralized authentication via hospital-homelab realm
  - Single Sign-On working for Keycloak users

**MQTT Broker VM (10.30.0.51)**
- MQTT: `10.30.0.51:1883`
- SSH: `ssh username@10.30.0.51`
- User: `username` | Pass: `password`
- Port: 1883 (MQTT)
- Software: Mosquitto MQTT Broker
- Status: ✓ Operational with authentication enabled (2026-02-13)
- **Security Hardening (2026-02-13)**:
  - ✓ Authentication enabled: Username/password required for all connections
  - ✓ Anonymous access disabled
  - MQTT User: `username` | Pass: `password`
  - ACL file configured for topic permissions
  - Password file: `/etc/mosquitto/passwd`
  - All 5 Raspberry Pis publishing with authentication
  - Node-RED connected with authentication
  - ⚠️ TLS encryption not yet enabled (port 8883) - planned upgrade

**PostgreSQL VM (10.30.0.50)**
- Web: N/A (database server)
- SSH: `ssh username@10.30.0.50`
- User: `username` | Pass: `password`
- Database: `hospital_data`
- DB User: `nodered` | Pass: `password`
- VM Specs: 2 vCPUs, 4GB RAM, 1TB disk (957GB available)
- OS: Ubuntu Server 24.04 LTS
- Software: PostgreSQL 16.10
- Storage: ZFS zvol on Hospital_Main pool (80TB HDD array)
- Timezone: America/New_York (EST) - configured 2026-01-04
- Status: ✓ Fully operational with SSL encryption and data archival (2026-02-13)
- **Performance Optimization (2026-01-16)**:
  - 397,645,663 rows in heartrate_data table (46+ days of continuous data)
  - Created indexes: `idx_heartrate_pi_id`, `idx_heartrate_timestamp`, `idx_heartrate_pi_timestamp`
  - Query performance: Improved from 35 seconds to 79ms for time-range queries
  - HIPAA compliance: All data retained per 164.312.b audit requirements
- **Security Hardening (2026-02-13)**:
  - ✓ SSL/TLS encryption enabled for all client connections
  - ✓ Self-signed certificate generated (10-year validity)
  - SSL Certificate: `/etc/postgresql/16/main/server.crt`
  - SSL Key: `/etc/postgresql/16/main/server.key`
  - All clients verified using SSL:
    - Node-RED (10.30.0.52): SSL enabled with `rejectUnauthorized: false`
    - Grafana (10.30.0.53): SSL mode set to `require`
    - HAPI FHIR (10.30.0.56): SSL enabled
  - 630M+ PHI records now encrypted in transit
- **Data Archival (2026-02-14) - ✅ COMPLETE**:
  - Original database size: 630,769,921 rows (96 GB) - 79 days of data
  - Growth rate: 7.3 million rows/day (~1.2 GB/day)
  - Archive strategy: 7-day active retention + long-term archive
  - ✅ Archive table created: `heartrate_data_archive`
  - ✅ Bulk insert complete: 584,615,442 rows archived (~4 hours runtime)
  - ✅ Archive made durable: ALTER TABLE SET LOGGED complete (~60 min runtime)
  - ✅ DELETE complete: 587,408,300 rows removed from main table (~15 min runtime)
  - ✅ VACUUM FULL complete: ~88 GB disk space reclaimed (~10 min runtime)
  - ✅ Automated daily archival: pg_cron configured (runs daily at 2 AM EST)
  - **Final Results:**
    - Main table: 53,026,804 rows, 8 GB (last 7 days, fast queries)
    - Archive table: 584,615,442 rows, 87 GB (historical data retained)
    - Performance: 91.6% reduction in main table size (630M → 53M rows)
    - Data pipeline verified operational with fresh data flowing

**Grafana VM (10.30.0.53)**
- Web: `http://10.30.0.53:3000`
- SSH: `ssh username@10.30.0.53`
- User: `username` | Pass: `password`
- **Grafana Web Login Options:**
  - Local: `admin` | Pass: `password`
  - **SSO via Keycloak:** "Sign in with Keycloak" button (recommended)
    - Use Keycloak users: `username` or `username` with Pass: `password`
- VM Specs: 2 vCPUs, 4GB RAM, 50GB disk
- OS: Ubuntu Server 24.04 LTS
- Software: Grafana (latest from APT repo)
- Data Source: PostgreSQL (10.30.0.50:5432) - hospital_data database
- Purpose: Historical visualization and analytics (complements Node-RED real-time dashboard)
- Service: `grafana-server.service` (auto-starts on boot)
- Timezone: America/New_York (EST) configured at system and query level (2026-02-14)
- Status: ✓ Operational with PostgreSQL connected (2025-12-08)
- **SSO Integration (2026-01-16):**
  - ✓ Keycloak OAuth2/OpenID Connect configured
  - Centralized authentication via hospital-homelab realm
  - Single Sign-On working for Keycloak users
- **Known Limitation (2026-01-16)**:
  - Dashboard panels may not auto-refresh with 397M+ row dataset
  - Alert rules working correctly (tachycardia detection functional)
  - Recommend using Node-RED dashboard (10.30.0.52:1880/ui) for real-time monitoring
  - Grafana best used for historical analysis and alerting

**Mirth Connect VM (10.30.0.54)**
- Web: `https://10.30.0.54:8443` (HTTPS required)
- SSH: `ssh username@10.30.0.54`
- User: `username` | Pass: `password`
- Mirth Admin Login: `admin` | Pass: `password`
- VM Specs: 4 vCPUs, 8GB RAM, 100GB disk
- OS: Ubuntu Server 24.04 LTS
- Software: Mirth Connect 4.5.2 (NextGen Connect)
- Java: OpenJDK 11.0.29
- Installation Path: `/opt/mirthconnect`
- Service: `mirthconnect.service` (auto-starts on boot)
- Purpose: HL7/FHIR healthcare data integration engine
- Status: ✓ Fully operational with HTTP→FHIR transformation (2026-01-22)
- Active Channel: `HeartRate_FHIR_Final`
  - HTTP Listener on port 8081
  - Receives JSON from Node-RED (rate-limited to 1/second)
  - Transforms to FHIR R4 Observation resources with JavaScript
  - Sends directly to HAPI FHIR server (10.30.0.56:8080/fhir/Observation)
  - Data Types: Inbound JSON, Outbound JSON
  - Content field: `${message.encodedData}` for HTTP POST body
- Data Flow: Raspberry Pi → MQTT → Node-RED → HTTP (8081) → Mirth → HAPI FHIR
- **Database Maintenance (2026-01-22)**:
  - Derby database auto-pruning configured (30 days retention)
  - Prunes message metadata and content older than 30 days
  - Runs daily to prevent disk space exhaustion
  - Database recovered from 100% disk usage (36GB Derby logs cleared)
  - Current disk usage: 21% (10GB used of 48GB)

**HAPI FHIR Server VM (10.30.0.56)**
- Web (SSO Protected): `http://10.30.0.56:4180/fhir/` (via OAuth2 Proxy - recommended)
- Web (Direct API): `http://10.30.0.56:8080/fhir/` (firewall restricted - Mirth only)
- SSH: `ssh username@10.30.0.56`
- User: `username` | Pass: `password`
- **Web Login Options:**
  - **SSO via Keycloak (OAuth2 Proxy):** Access `http://10.30.0.56:4180/fhir/` - redirects to Keycloak login
    - Use Keycloak users: `username` or `username` with Pass: `password`
    - Session timeout: 30 minutes (absolute), re-validation every 10 minutes
    - Logout: `http://10.30.0.56:4180/oauth2/sign_out?rd=/fhir/`
  - Direct API access: `http://10.30.0.56:8080/fhir/` (firewall restricted to 10.30.0.54)
- VM Specs: 2 vCPUs, 4GB RAM, 50GB disk
- OS: Ubuntu Server 24.04 LTS
- Deployment: Docker (hapiproject/hapi:latest)
- Database: PostgreSQL (10.30.0.50:5432) - hapi_fhir database with SSL encryption
- FHIR Version: R4 (HAPI FHIR Server v8.6.0)
- Purpose: Standards-compliant FHIR server for storing and querying health data
- Status: ✓ Fully operational with real-time data ingestion, SSO, and hardened security (2026-02-13)
- **Security Hardening (2026-02-13)**:
  - ✓ UFW firewall configured to restrict port 8080 access
  - Port 8080 allowed only from Mirth Connect (10.30.0.54)
  - Port 8080 denied from all other sources
  - SSH access allowed from 10.30.0.0/24 (rule priority fixed)
  - PostgreSQL connection using SSL/TLS encryption
  - Firewall rule ordering: SSH allow → Port 8080 allow (Mirth) → Port 8080 deny (all)
- Docker Configuration:
  - Container: hapi-fhir (auto-restart enabled)
  - Java Memory: -Xms512m -Xmx3072m (3GB heap)
  - Fixed OutOfMemoryError issue (2026-01-15)
- **SSO Integration (2026-01-28):**
  - ✓ OAuth2 Proxy v7.6.0 installed and configured
  - Listens on port 4180, proxies to HAPI FHIR Docker on port 8080
  - Keycloak OIDC provider with PKCE enabled (code_challenge_method=S256)
  - Cookie-based session storage (30min expiry, 10min refresh for HIPAA compliance)
  - Configuration: `/etc/oauth2-proxy/oauth2-proxy.cfg`
  - Systemd service: `oauth2-proxy.service` (auto-start enabled)
  - Keycloak client: `hapi-fhir-oauth2` with audience mapper configured
  - Single Sign-On working with Keycloak users
- REST API Endpoints:
  - Base (SSO): `http://10.30.0.56:4180/fhir/`
  - Metadata: `http://10.30.0.56:4180/fhir/metadata`
  - Patients: `http://10.30.0.56:4180/fhir/Patient`
  - Observations: `http://10.30.0.56:4180/fhir/Observation`
  - Base (Direct): `http://10.30.0.56:8080/fhir/` (internal use only)
- Patient Resources: pi-1, pi-2, pi-3, pi-4, pi-5 (created 2026-01-15)
- Data Ingestion: Receiving FHIR Observations from Mirth (1/second rate-limited via direct port 8080)
- Query Capabilities: ✓ Tested and validated
  - Filter by patient: `?subject=Patient/pi-4`
  - Filter by LOINC code: `?code=8867-4`
  - Filter by value: `?value-quantity=gt100`
  - Sorting: `&_sort=-date`
  - Pagination: `&_count=N`
- Complete Pipeline: Raspberry Pi → MQTT → Node-RED → Mirth → HAPI FHIR ✓ OPERATIONAL

**Keycloak IDM VM (10.30.0.57)**
- Web: `http://10.30.0.57:8080`
- SSH: `ssh username@10.30.0.57`
- SSH User: `username` | Pass: `password`
- **Keycloak Admin Console:** `admin` | Pass: `password`
- VM Specs: 2 vCPUs, 4GB RAM, 50GB disk
- OS: Ubuntu Server 24.04 LTS
- Software: Keycloak 26.0.7 (OpenID Connect / OAuth2 / SAML)
- Database: PostgreSQL (10.30.0.50:5432) - keycloak database with SSL/TLS encryption (2026-02-14)
- Purpose: Centralized Identity and Access Management (IDM)
- Status: ✓ Fully operational with SSO integrations (2026-01-16)
- **Realm Configuration:**
  - Realm: `hospital-homelab`
  - Display Name: Hospital Homelab
  - Users:
    - `username` (Admin User) - Pass: `password`
    - `username` (Doctor One) - Pass: `password`
- **Client Applications:**
  - **Grafana OAuth2 client:**
    - Client ID: `grafana`
    - Client Secret: `client-secret`
    - Redirect URI: `http://10.30.0.53:3000/*`
  - **Node-RED OAuth2 client:**
    - Client ID: `node-red`
    - Client Secret: `client-secret`
    - Redirect URI: `http://10.30.0.52:1880/auth/strategy/callback`
  - **Wazuh OpenID Connect client:**
    - Client ID: `wazuh`
    - Client Secret: `client-secret`
    - Redirect URI: `https://10.30.0.55/*`
    - Realm roles mapper configured for authentication
  - **HAPI FHIR OAuth2 client (via OAuth2 Proxy):**
    - Client ID: `hapi-fhir-oauth2`
    - Client Secret: `client-secret`
    - Redirect URI: `http://10.30.0.56:4180/oauth2/callback`
    - PKCE enabled: S256 code challenge method
    - Audience mapper: `hapi-fhir-audience` (adds client ID to aud claim)
    - Backchannel logout: Disabled (OAuth2 Proxy compatibility)
  - **Vault OIDC client:**
    - Client ID: `vault`
    - Client Secret: `client-secret`
    - Redirect URIs: `http://10.30.0.58:8200/ui/vault/auth/oidc/oidc/callback`, `http://10.30.0.58:8200/oidc/callback`
- **Integrated Applications:**
  - ✓ Grafana (10.30.0.53) - OAuth2/OpenID Connect SSO working
  - ✓ Node-RED (10.30.0.52) - OAuth2/OpenID Connect SSO working (2026-01-21)
  - ✓ Wazuh (10.30.0.55) - OpenID Connect SSO working (2026-01-22)
  - ✓ HAPI FHIR (10.30.0.56) - OAuth2/OpenID Connect SSO via OAuth2 Proxy working (2026-01-28)
  - ✓ HashiCorp Vault (10.30.0.58) - OIDC SSO working (2026-02-02) - **NEW**
- Features:
  - Single Sign-On (SSO) across applications
  - OAuth2 and OpenID Connect support
  - SAML 2.0 support
  - Centralized user management
  - Role-Based Access Control (RBAC)
  - Multi-Factor Authentication (MFA) capable
  - Session management and single logout
  - HIPAA-compliant audit logging

**HashiCorp Vault VM (10.30.0.58)**
- Web: `http://10.30.0.58:8200`
- SSH: `ssh username@10.30.0.58`
- SSH User: `username` | Pass: `password`
- **Vault Web Login Options:**
  - **OIDC (Recommended):** Select "OIDC" method, role "default", click "Sign in with OIDC"
    - Use Keycloak users: `username` or `username` with Pass: `password`
  - **Token (Emergency):** Use root token below for direct access
- **Root Token:** `password`
- **Unseal Keys (Need 3 of 5 to unseal after restart):**
  - Unseal Key 1: `password`
  - Unseal Key 2: `password`
  - Unseal Key 3: `password`
  - Unseal Key 4: `password`
  - Unseal Key 5: `password`
- VM Specs: 2 vCPUs, 4GB RAM, 50GB disk
- OS: Ubuntu Server 24.04 LTS
- Software: HashiCorp Vault (latest stable from APT repo)
- Storage Backend: Integrated Raft storage
- Purpose: Centralized secrets management and credential lifecycle
- Status: ✓ Fully operational with Keycloak SSO integration (2026-02-02)
- **Keycloak Client Configuration:**
  - Client ID: `vault`
  - Client Secret: `client-secret`
  - Redirect URIs: `http://10.30.0.58:8200/ui/vault/auth/oidc/oidc/callback`, `http://10.30.0.58:8200/oidc/callback`
- **Secrets Engines Enabled:**
  - **KV v2** (`kv/`) - Versioned key-value storage for static secrets
  - **Database** (`database/`) - Dynamic PostgreSQL credential generation with SSL/TLS encryption (2026-02-14)
- **Stored Secrets:**
  - `kv/database/postgresql` - PostgreSQL admin credentials
  - `kv/mqtt/broker` - MQTT broker credentials
  - `kv/keycloak/clients/grafana` - Grafana OAuth2 client secret
  - `kv/keycloak/clients/node-red` - Node-RED OAuth2 client secret
  - `kv/keycloak/clients/hapi-fhir-oauth2` - HAPI FHIR OAuth2 client secret
  - `kv/wazuh/admin` - Wazuh admin password
- **Dynamic Database Roles:**
  - `database/roles/nodered` - Read/write access to hospital_data (1hr TTL, 24hr max)
  - Generate temp creds: `vault read database/creds/nodered`
- **Audit Logging:**
  - File audit enabled: `/var/log/vault/audit.log`
  - Monitored by Wazuh agent for all access attempts
- **Automated Backups:**
  - Daily backups at 2:00 AM to `/opt/vault/backups/`
  - Retention: 30 days
  - Includes: Raft data, config files, audit logs
- **Wazuh Integration:**
  - Agent deployed and monitoring Vault access
  - All authentication attempts logged to SIEM
  - Vault audit logs analyzed for security events
- **CLI Access:**
  ```bash
  export VAULT_ADDR='http://10.30.0.58:8200'
  vault login -method=oidc  # SSO login
  vault login <TOKEN>        # Token login
  vault secrets list         # List secret engines
  vault kv list kv/          # List KV secrets
  vault read database/creds/nodered  # Generate temp DB creds
  ```
- **Unseal Procedure (after VM restart):**
  ```bash
  export VAULT_ADDR='http://10.30.0.58:8200'
  vault operator unseal password
  vault operator unseal password
  vault operator unseal password
  vault status  # Should show Sealed: false
  ```
- Features:
  - Centralized secrets storage with AES-256-GCM encryption
  - Dynamic database credentials with automatic rotation
  - Keycloak OIDC/OAuth2 authentication integration
  - Policy-based access control (RBAC)
  - Complete audit trail of all secret access
  - Automated daily backups with 30-day retention
  - HIPAA-compliant credential management
  - Versioned secret storage (rollback capability)

**Elasticsearch VM (10.30.0.60)**
- Web API: `https://10.30.0.60:9200`
- SSH: `ssh username@10.30.0.60`
- SSH User: `username` | Pass: `password`
- **Elasticsearch Login:**
  - Username: `elastic`
  - Password: `password`
- VM Specs: 4 vCPUs, 4GB RAM, 100GB disk
- OS: Ubuntu Server 24.04 LTS
- Software: Elasticsearch 8.19.11 (single-node cluster)
- Purpose: Log aggregation and search engine for Suricata IDS alerts
- Status: ✓ Fully operational (2026-02-10)
- **Configuration:**
  - Cluster name: `elasticsearch`
  - Network: Listening on 0.0.0.0:9200 (accepts external connections)
  - Discovery type: single-node
  - Security: TLS enabled, HTTP authentication required
- **API Access Test:**
  ```bash
  curl -k -u elastic:password https://10.30.0.60:9200
  ```
- **Integration:**
  - Receives logs from: Suricata IDS (via Filebeat - pending configuration)
  - Queried by: Grafana (for IDS dashboard visualization)
- Features:
  - Full-text search across security logs
  - JSON document storage optimized for Suricata EVE logs
  - RESTful API for log ingestion and queries
  - Scalable architecture (currently single-node)

**Wazuh SIEM VM (10.30.0.55)**
- Web: `https://10.30.0.55`
- SSH: `ssh username@10.30.0.55`
- SSH User: `username` | Pass: `password`
- **Web Login Options:**
  - Local: `admin` | Pass: `password`
  - **SSO via Keycloak:** "Log in with OpenID Connect" button (recommended)
    - Use Keycloak users: `username` or `username` with Pass: `password`
- VM Specs: 4 vCPUs, 8GB RAM, 100GB disk
- OS: Ubuntu Server 24.04 LTS
- Software: Wazuh 4.9.2 (All-in-One deployment)
- Components:
  - Wazuh Manager (analysis & correlation)
  - Wazuh Indexer (OpenSearch-based log storage)
  - Wazuh Dashboard (web UI)
- Purpose: Security Information and Event Management (SIEM)
- Status: ✓ Fully operational with 14 agents deployed (2026-02-14)
- **SSO Integration (2026-01-22):**
  - ✓ Keycloak OpenID Connect configured
  - Multiple authentication enabled (basic auth + OpenID)
  - Centralized authentication via hospital-homelab realm
  - Single Sign-On working for Keycloak users
- Monitored Systems (14 agents total):
  - All 5 Raspberry Pis (heart rate monitors)
  - PostgreSQL VM (database security)
  - Node-RED VM (workflow security)
  - Grafana VM (dashboard access)
  - Mirth Connect VM (healthcare data integration)
  - HAPI FHIR VM (FHIR API security)
  - MQTT Broker VM (messaging security)
  - Keycloak IDM VM (identity management security)
  - HashiCorp Vault VM (secrets management security)
  - **Pi #6 - balloon-secure (balloon demo secure system)** - **NEW 2026-02-03**
- Features:
  - Real-time security event monitoring
  - File integrity monitoring (FIM)
  - Vulnerability detection and patching alerts
  - HIPAA compliance dashboards (164.312.b audit controls)
  - Authentication tracking and anomaly detection
  - Log analysis and correlation across all systems

### Raspberry Pis (Heart Rate Monitors - Pi #1-5)
**Pi #1-5 SSH Access**
- SSH: `ssh r-pi-{1,2,3,4,5}@10.30.0.{20,21,22,23,24}`
- Pass: `password`
- Network: NetworkManager with auto-connect enabled

### Raspberry Pi 5 (Balloon Demo Systems - Pi #6-7)
**Pi #6 (Secure System) - balloon-secure**
- SSH: `ssh username@10.30.0.25`
- Pass: `password`
- IP: 10.30.0.25 (Static, VLAN30)
- OS: Raspberry Pi OS (Debian 12 Bookworm)
- Hostname: balloon-secure
- Status: ✅ FULLY CONFIGURED (2026-02-03)
- **Configuration Complete:**
  - ✓ I2C enabled (ready for Sequent 8-RELAYS HAT + BMP388 sensor)
  - ✓ Python libraries installed (paho-mqtt, RPi.GPIO, gpiozero, adafruit-circuitpython-bmp3xx, adafruit-circuitpython-ssd1306)
  - ✓ MQTT client working (tested with broker 10.30.0.51)
  - ✓ Network connectivity verified (all VLAN30 services reachable)
  - ✓ Wazuh agent installed and active (Agent ID: 014, Wazuh 4.9.2)
  - ✓ Project directory structure created at `~/balloon-demo/`
  - ✓ Configuration file: `~/balloon-demo/config/settings.json`
  - ✓ Directories: secure/, logs/, config/, lib/, tests/
- **Security Features:**
  - Wazuh SIEM monitoring active
  - Keycloak authentication ready (configured in settings.json)
  - TLS-encrypted MQTT planned (configured in settings.json)
  - All actions will be logged to Wazuh
- **Hardware Ready For:**
  - Sequent Microsystems 8-RELAYS HAT (I2C address 0x20)
  - BMP388 pressure sensor (I2C address 0x77)
  - OLED status display
  - Relay-controlled air pump and solenoid valve

**Pi #7 (Vulnerable System) - balloon-vulnerable**
- SSH: `ssh username@192.168.50.100`
- Pass: `password`
- IP: 192.168.50.100 (Static, VLAN2)
- OS: Raspberry Pi OS (Debian 12 Bookworm)
- Hostname: balloon-vulnerable
- Status: ✅ FULLY CONFIGURED (2026-02-03)
- **Configuration Complete:**
  - ✓ I2C enabled (ready for Sequent 8-RELAYS HAT + BMP388 sensor)
  - ✓ Python libraries installed (Flask, paho-mqtt, RPi.GPIO, gpiozero, adafruit sensors)
  - ✓ Network connectivity verified (internet access working)
  - ✓ HTTP API running on port 5000 (tested and functional)
  - ✓ Project directory structure created at `~/balloon-demo/`
  - ✓ Configuration file: `~/balloon-demo/config/settings.json`
  - ✓ Vulnerable control script: `~/balloon-demo/vulnerable/balloon_control_api.py`
  - ✓ Directories: vulnerable/, logs/, config/
- **Intentional Vulnerabilities (for demo):**
  - ❌ NO authentication required for API access
  - ❌ NO input validation on sensor data
  - ❌ NO Wazuh SIEM monitoring
  - ❌ NO TLS encryption
  - ❌ Trusts external sensor data blindly (CRITICAL VULNERABILITY)
  - ❌ NO rate limiting

---

## SECURITY HARDENING SUMMARY (2026-02-13)

### Completed Security Improvements ✅

**1. MQTT Authentication & Authorization**
- Date: 2026-02-13
- Impact: Prevents unauthorized access to heart rate telemetry
- Changes:
  - Enabled Mosquitto password authentication
  - Configured ACL for topic permissions
  - Disabled anonymous access
  - Updated all 5 Raspberry Pis with credentials
  - Updated Node-RED MQTT broker configurations
- Credentials: `username` / `password`
- Status: ✅ All 5 Pis publishing with authentication, anonymous access blocked

**2. PostgreSQL SSL/TLS Encryption**
- Date: 2026-02-13
- Impact: Encrypts 630M+ PHI records in transit (HIPAA 164.312(a)(2)(iv) compliance)
- Changes:
  - Generated self-signed SSL certificate (10-year validity)
  - Enabled SSL in PostgreSQL 16.10 configuration
  - Configured Node-RED with `rejectUnauthorized: false` for self-signed cert
  - Configured Grafana with `sslmode: require`
  - Verified HAPI FHIR using SSL
- SSL Files: `/etc/postgresql/16/main/server.{crt,key}`
- Status: ✅ All connections (Node-RED, Grafana, HAPI FHIR) using SSL

**3. HAPI FHIR Port 8080 Firewall Protection**
- Date: 2026-02-13
- Impact: Prevents unauthorized access to unauthenticated FHIR API
- Changes:
  - Added UFW firewall rules on HAPI FHIR VM
  - Restricted port 8080 to Mirth Connect only (10.30.0.54)
  - Fixed firewall rule ordering (SSH allow before deny rules)
- Status: ✅ Port 8080 accessible only from Mirth, SSH access working

**4. Data Pipeline Integrity Verification**
- Date: 2026-02-13
- Impact: Ensures security changes didn't break production
- Tests Performed:
  - ✅ All 5 Pis publishing to MQTT with authentication
  - ✅ PostgreSQL receiving data with SSL encryption
  - ✅ Node-RED, Grafana, HAPI FHIR connections all using SSL
  - ✅ HAPI FHIR API responding correctly
  - ✅ Complete data flow: Pi → MQTT → Node-RED → PostgreSQL → Mirth → HAPI FHIR
- Status: ✅ Full pipeline operational with enhanced security

### In Progress Security Work 🔄

**5. PostgreSQL Data Archival & Retention**
- Date Started: 2026-02-13
- Impact: Improve Grafana query performance, implement data lifecycle
- Current Status:
  - Database: 630,769,921 rows (96 GB), 79 days of data
  - Growth: 7.3M rows/day (~1.2 GB/day)
  - Strategy: 7-day active retention + archive table
  - Archive table: `heartrate_data_archive` (UNLOGGED for bulk insert speed)
  - Archiving: 582M rows (>7 days old) - IN PROGRESS (est. 3-4 hours)
  - Result: Main table will have ~48M rows (last 7 days) for fast Grafana queries
- Next Steps:
  - Complete bulk insert to archive
  - Make archive table LOGGED for durability
  - Delete old data from main table
  - VACUUM FULL to reclaim disk space
  - Install pg_cron for automated daily archival

### Remaining Security Priorities 📋

**High Priority:**
1. MQTT TLS Encryption (port 1883 → 8883)
2. PostgreSQL Automated Backups (pg_dump to TrueNAS)
3. Service HTTPS/TLS (Node-RED, Keycloak, Grafana, Vault)

**Medium Priority:**
4. Wazuh SIEM Full Integration
5. HashiCorp Vault Secrets Management
6. VLAN Firewall Hardening (VLAN30 ↔ VLAN2 isolation)

### HIPAA Compliance Status

**Implemented Controls:**
- ✅ 164.312(a)(2)(iv) - Encryption in Transit (PostgreSQL SSL, MQTT auth)
- ✅ 164.308(a)(4)(i) - Access Control (HAPI FHIR firewall)
- ✅ 164.312(d) - Authentication (MQTT credentials)
- ✅ 164.312(b) - Audit Controls (syslog logging)

**Partially Implemented:**
- ⚠️ 164.308(a)(7)(ii)(A) - Backup (retention yes, automated no)
- ⚠️ 164.312(a)(1) - Access Control (firewall yes, RBAC pending)

**Not Yet Implemented:**
- ❌ 164.312(a)(2)(iv) - Encryption at Rest
- ❌ 164.308(a)(1)(ii)(D) - Audit Logs (SIEM deployed but not integrated)
- ❌ 164.308(a)(5)(ii)(C) - Access Review

**Detailed Security Report:** See `SECURITY_HARDENING_2026-02-13.md`
  - ❌ NO logging of access attempts

### Suricata IDS Laptop (Bare Metal - Expo Demo)
**Suricata IDS Sensor**
- OS: Ubuntu 24.04 Desktop (dual boot with Windows 11)
- SSH User: `suricata-admin` | Pass: (set during installation)
- Hostname: suricata-laptop
- Status: ⚠️ In Progress - Dual-interface architecture migration (2026-03-01)
- **Purpose**: Dedicated IDS sensor for balloon demo - monitors all traffic to/from vulnerable Pi

- **Dual Network Interface Architecture (Standard IDS Design):**
  - **Interface 1 - Management (NEW - Pending second USB-C adapter purchase)**:
    - Purpose: SSH access, Filebeat log shipping, internet access, system updates
    - Hardware: Second USB-C Ethernet adapter (to be purchased)
    - Connection: Switch Port 5 (or any available port)
    - Port Config: Operation = Switching, Native VLAN = VLAN30
    - IP Assignment: DHCP (10.30.0.191 or similar in 10.30.0.0/24 range)
    - Services: SSH server, Filebeat (ships logs to Elasticsearch)
  - **Interface 2 - IDS Monitoring (EXISTING)**:
    - Purpose: Passive packet capture from mirrored traffic (promiscuous mode)
    - Hardware: USB-C Ethernet adapter (enx00051b514370)
    - Connection: Switch Port 6 (mirror destination for Port 15)
    - Port Config: Operation = Mirroring, Mirror Port = 15
    - IP Assignment: None (no IP needed for passive capture)
    - Services: Suricata IDS (packet capture and analysis)

- **Data Flow Architecture:**
  ```
  Port 15 (Vulnerable Pi) ──[mirror]──> Port 6 ──> USB-C Adapter #2 (monitoring)
                                                          ↓
                                                     Suricata Process
                                                     (captures packets)
                                                          ↓
                                                  Writes to local disk:
                                                  /var/log/suricata/eve.json
                                                          ↓
                                                     Filebeat Process
                                                     (reads local file)
                                                          ↓
                                             USB-C Adapter #1 (management) ──> Port 5 ──> Elasticsearch
                                                     (IP: 10.30.0.191)
  ```

- **Configuration:**
  - Suricata version: Latest from Ubuntu repos
  - Monitoring interface: enx00051b514370 (USB-C Ethernet - monitoring only)
  - Mode: IDS only (passive monitoring, no blocking)
  - Capture mode: af-packet with promiscuous mode
  - HOME_NET: [10.30.0.0/24, 192.168.50.0/24]

- **Custom Detection Rules** (`/var/lib/suricata/rules/local.rules`):
  - Traffic to Vulnerable Balloon Pi (192.168.50.100)
  - Traffic to VLAN30 network
  - ICMP packet detection

- **Logging:**
  - Fast log: `/var/log/suricata/fast.log` (plain text alerts)
  - EVE JSON: `/var/log/suricata/eve.json` (structured logs for Elasticsearch)
  - 324 rules loaded (321 default + 3 custom)

- **Port Mirroring Setup:**
  - Source: Switch Port 15 (Vulnerable Pi #7 at 192.168.50.100)
  - Destination: Switch Port 6 → Suricata laptop monitoring interface (USB-C adapter #2)
  - All traffic to/from vulnerable Pi is captured and analyzed

- **Current Status (2026-03-01):**
  - ✓ Suricata installed and configured
  - ✓ Custom detection rules created
  - ✓ Port mirroring configured on switch
  - ✓ Single USB-C adapter working for monitoring
  - ⚠️ Waiting for second USB-C Ethernet adapter for management interface
  - ⚠️ Cannot SSH or run Filebeat until management interface added
  - ⏳ Next: Purchase second USB-C adapter, configure Port 5 for VLAN30

- **Next Steps:**
  - [ ] Purchase second USB-C Ethernet adapter (~$15-30)
  - [ ] Configure Switch Port 5: Operation=Switching, Native VLAN=VLAN30
  - [ ] Connect second adapter to Port 5, verify DHCP lease (10.30.0.x)
  - [ ] Install Filebeat to ship eve.json to Elasticsearch (10.30.0.60)
  - [ ] Build Grafana IDS dashboard for live attack visualization during expo

- **Why Bare Metal:**
  - TrueNAS macvtap filtering blocked mirrored traffic in virtualized setup
  - Bare metal bypasses all virtualization layers
  - Direct hardware access ensures 100% packet capture reliability

- **Why Dual Interface (Industry Standard IDS Architecture):**
  - Separates management traffic from monitored traffic (prevents contamination)
  - Monitoring interface has no IP (invisible to attackers)
  - Management interface allows remote access, log shipping, updates
  - Port mirroring can't provide bidirectional communication (mirror-only mode)
  - Standard practice for Suricata/Snort/Zeek deployments
