# Hospital Homelab Network Setup Progress

## Date: Started 2025-11-09, Last Updated 2026-02-03 (Phase 5 Expo Demo - Design Complete ✓, Network Config Complete ✓, Hardware Ordered ✓ - Partial Delivery ✅)

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
| U6 Pro WiFi AP | 10.30.0.246 | Switch Port 17 | ✓ Operational |
| Laptop "UltraMoad" | 10.30.0.122 | UDM-SE Port 1 | ✓ Connected |
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
            ├─ Port 9: Raspberry Pi #1 (10.30.0.20) + PoE++ [Heart Rate Monitor]
            ├─ Port 10: Raspberry Pi #2 (10.30.0.21) + PoE++ [Heart Rate Monitor]
            ├─ Port 11: Raspberry Pi #3 (10.30.0.22) + PoE++ [Heart Rate Monitor]
            ├─ Port 12: Raspberry Pi #4 (10.30.0.23) + PoE++ [Heart Rate Monitor]
            ├─ Port 13: Raspberry Pi #5 (10.30.0.24) [External power - PoE not compatible] [Heart Rate Monitor]
            ├─ Port 14: Raspberry Pi #6 (10.30.0.25) [PLANNED - Secure Balloon Demo] + External Power (Pi 5)
            ├─ Port 15: Raspberry Pi #7 (192.168.50.100) [PLANNED - Vulnerable Balloon Demo, VLAN50] + External Power (Pi 5)
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
               └─ HashiCorp Vault VM (10.30.0.58) ✓ OPERATIONAL
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
- Status: ✓ Tested and operational (2025-11-17)

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
- Status: ✓ Fully operational with data ingestion (2025-11-25)
- **Performance Optimization (2026-01-16)**:
  - 397,645,663 rows in heartrate_data table (46+ days of continuous data)
  - Created indexes: `idx_heartrate_pi_id`, `idx_heartrate_timestamp`, `idx_heartrate_pi_timestamp`
  - Query performance: Improved from 35 seconds to 79ms for time-range queries
  - HIPAA compliance: All data retained per 164.312.b audit requirements

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
- Timezone: Queries updated to use `AT TIME ZONE 'America/New_York'` for EST display (2026-01-04)
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
- Web (Direct API): `http://10.30.0.56:8080/fhir/` (unauthenticated - internal services only)
- SSH: `ssh username@10.30.0.56`
- User: `username` | Pass: `password`
- **Web Login Options:**
  - **SSO via Keycloak (OAuth2 Proxy):** Access `http://10.30.0.56:4180/fhir/` - redirects to Keycloak login
    - Use Keycloak users: `username` or `username` with Pass: `password`
    - Session timeout: 30 minutes (absolute), re-validation every 10 minutes
    - Logout: `http://10.30.0.56:4180/oauth2/sign_out?rd=/fhir/`
  - Direct API access: `http://10.30.0.56:8080/fhir/` (no authentication - for Mirth integration)
- VM Specs: 2 vCPUs, 4GB RAM, 50GB disk
- OS: Ubuntu Server 24.04 LTS
- Deployment: Docker (hapiproject/hapi:latest)
- Database: PostgreSQL (10.30.0.50:5432) - hapi_fhir database (2026-01-16)
- FHIR Version: R4 (HAPI FHIR Server v8.6.0)
- Purpose: Standards-compliant FHIR server for storing and querying health data
- Status: ✓ Fully operational with real-time data ingestion and SSO authentication (2026-01-28)
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
- Database: PostgreSQL (10.30.0.50:5432) - keycloak database
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
  - **Database** (`database/`) - Dynamic PostgreSQL credential generation
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
- Status: ✓ Fully operational with 14 agents deployed (2026-02-03)
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
- SSH: `ssh vulnerable_balloon_admin@192.168.50.100`
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

### Phase 4: Security/Monitoring (COMPLETE ✓)
11. **[✓] Install Wazuh SIEM VM (10.30.0.55)** - COMPLETE (2026-01-16)
   - ✓ Ubuntu Server 24.04 LTS VM on TrueNAS (4 vCPUs, 8GB RAM, 100GB disk)
   - ✓ Wazuh 4.9.2 All-in-One installation
   - ✓ Wazuh Manager, Indexer, and Dashboard operational
   - ✓ Web interface accessible at https://10.30.0.55
   - ✓ **13 agents deployed and active** (updated 2026-02-02):
     - 5 Raspberry Pis (pi-1 through pi-5)
     - 8 VMs (PostgreSQL, Node-RED, Grafana, Mirth, HAPI FHIR, MQTT, Keycloak, **Vault**)
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

**Current State (2026-02-02):**
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
