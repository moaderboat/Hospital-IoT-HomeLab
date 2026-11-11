# Hospital Homelab - VM Services Status

**Last Updated:** 2026-02-09
**Host:** TrueNAS Server (10.30.0.44)
**Total VMs:** 10
**Status:** All Operational ✅

---

## VM Overview

| VM Name | IP Address | Purpose | Status | CPU | RAM | Disk |
|---------|------------|---------|--------|-----|-----|------|
| PostgreSQL | 10.30.0.50 | Database server | ✅ Operational | 2 vCPU | 4GB | 50GB |
| MQTT Broker | 10.30.0.51 | IoT message broker | ✅ Operational | 2 vCPU | 2GB | 20GB |
| Node-RED | 10.30.0.52 | Workflow automation | ✅ Operational | 2 vCPU | 2GB | 20GB |
| Grafana | 10.30.0.53 | Monitoring dashboards | ✅ Operational | 2 vCPU | 4GB | 30GB |
| Mirth Connect | 10.30.0.54 | HL7 interface engine | ✅ Operational | 4 vCPU | 8GB | 50GB |
| Wazuh SIEM | 10.30.0.55 | Security monitoring | ✅ Operational | 4 vCPU | 8GB | 100GB |
| HAPI FHIR | 10.30.0.56 | FHIR server | ✅ Operational | 4 vCPU | 8GB | 50GB |
| Keycloak IDM | 10.30.0.57 | Identity management | ✅ Operational | 2 vCPU | 4GB | 30GB |
| HashiCorp Vault | 10.30.0.58 | Secrets management | ✅ Operational | 2 vCPU | 4GB | 30GB |
| Suricata IDS/IPS | 10.30.0.59 | Network intrusion detection | ✅ Operational | 2 vCPU | 4GB | 50GB |

---

## Detailed VM Configurations

### PostgreSQL Database (10.30.0.50)

**Purpose:** Central database for all hospital homelab services

**Services:**
- PostgreSQL 15
- Multiple databases:
  - `heartrate_monitoring` - Heart rate data from 5 Raspberry Pis
  - `grafana` - Grafana configuration
  - `keycloak` - Keycloak IDM data
  - `fhir` - FHIR server data

**Access:**
- SSH: `ssh postgres_admin@10.30.0.50`
- Database: `psql -h 10.30.0.50 -U postgres -d heartrate_monitoring`
- Credentials: See secure credential store

**Data Retention:**
- Current: ~18 months of runway before storage concerns
- Retention policy: TBD (not urgent)

**Backup:**
- TBD - Need to configure pg_dump automated backups

**TODO:**
- [ ] Configure automated PostgreSQL backups
- [ ] Implement data retention policy for old heart rate data
- [ ] Set up replication/HA (future consideration)

---

### MQTT Broker (10.30.0.51)

**Purpose:** Message broker for IoT devices (Raspberry Pi heart rate monitors)

**Services:**
- Mosquitto MQTT broker
- Topics:
  - `hospital/heartrate/monitor1` - Pi #1
  - `hospital/heartrate/monitor2` - Pi #2
  - `hospital/heartrate/monitor3` - Pi #3
  - `hospital/heartrate/monitor4` - Pi #4 (AFib simulation)
  - `hospital/heartrate/monitor5` - Pi #5 (Anomaly detection)

**Access:**
- SSH: `ssh username@10.30.0.51`
- MQTT: Port 1883 (no TLS - internal network)
- Web: N/A (no web interface)

**Clients:**
- 5× Raspberry Pi heart rate monitors (publishers)
- Node-RED (subscriber)
- Grafana (via Node-RED)

**Security:**
- No authentication (internal trusted network only)
- Future: Add TLS + authentication for production

**Monitoring:**
- Topic activity visible in Node-RED
- Message rate: ~1 message/second per Pi (5 total)

**TODO:**
- [ ] Add authentication/ACLs for production use
- [ ] Configure TLS encryption
- [ ] Set up MQTT monitoring/metrics

---

### Node-RED (10.30.0.52)

**Purpose:** Workflow automation and data pipeline orchestration

**Services:**
- Node-RED flow-based programming
- Flows:
  - MQTT → PostgreSQL data pipeline
  - Heart rate anomaly detection
  - Data transformation for Grafana
  - Alerts/notifications (future)

**Access:**
- Web: `http://10.30.0.52:1880`
- SSH: `ssh nodered_admin@10.30.0.52`
- Credentials: See secure credential store

**Integrations:**
- MQTT Broker (10.30.0.51) - Input
- PostgreSQL (10.30.0.50) - Output/storage
- Grafana (10.30.0.53) - Visualization

**Key Flows:**
- Heart rate data ingestion from all 5 Pis
- Real-time anomaly detection (Pi #4 AFib, Pi #5 rare anomalies)
- Data aggregation and statistics

**TODO:**
- [ ] Add alerting for critical heart rate anomalies
- [ ] Integrate with Wazuh for security event correlation
- [ ] Create backup/restore procedure for flows

---

### Grafana (10.30.0.53)

**Purpose:** Monitoring dashboards and data visualization

**Services:**
- Grafana 10.x
- Dashboards:
  - Heart Rate Monitoring (all 5 Pis)
  - Network monitoring
  - System health metrics

**Access:**
- Web: `http://10.30.0.53:3000`
- SSH: `ssh username@10.30.0.53`
- Credentials: See secure credential store

**Data Sources:**
- PostgreSQL (10.30.0.50) - Heart rate data
- Node-RED (10.30.0.52) - Real-time metrics

**Dashboards:**
- Heart Rate Monitor Overview - All 5 Pis, real-time BPM
- AFib Detection (Pi #4) - Critically damped oscillation visualization
- Anomaly Detection (Pi #5) - Rare event tracking (~5.5hr intervals)

**TODO:**
- [ ] Add system metrics (CPU, memory, network)
- [ ] Create alerting rules
- [ ] Configure SMTP for email alerts

---

### Mirth Connect (10.30.0.54)

**Purpose:** HL7 interface engine for healthcare data exchange

**Services:**
- Mirth Connect 4.x
- Channels: TBD (placeholder for future HL7 integrations)

**Access:**
- Web: `https://10.30.0.54:8443`
- SSH: `ssh username@10.30.0.54`
- Credentials: See secure credential store

**Current Status:**
- ✅ Installed and running
- ⏸️ No active channels configured yet
- Purpose: Future HL7 v2/FHIR conversion demos

**Planned Integrations:**
- HAPI FHIR Server (10.30.0.56) - FHIR resource exchange
- HL7 v2 test messages
- EHR integration demos

**TODO:**
- [ ] Create sample HL7 v2 → FHIR conversion channel
- [ ] Configure secure TLS connections
- [ ] Set up HL7 test message library

---

### Wazuh SIEM (10.30.0.55)

**Purpose:** Security Information and Event Management

**Services:**
- Wazuh Manager
- Wazuh Indexer (OpenSearch)
- Wazuh Dashboard (web UI)

**Access:**
- Web: `https://10.30.0.55:443`
- SSH: `ssh username@10.30.0.55`
- Credentials: See secure credential store

**Wazuh Version:** 4.14.2 (upgraded 2026-02-09)

**Agents Deployed:**
- ✅ Pi #6 (Secure Balloon Demo) - 10.30.0.25 - **ACTIVE**
- [ ] TrueNAS Server - **NEEDS DEPLOYMENT**

**Current Status:**
- ✅ Wazuh server operational (v4.14.2)
- ✅ Pi #6 agent connected and logging
- ✅ Ready for balloon demo security monitoring

**Monitoring:**
- Security events from balloon demo (when Pi #6 agent deployed)
- Syslog forwarding from UDM-SE (future)
- File integrity monitoring
- Intrusion detection

**TODO:**
- [x] Deploy Wazuh agent to Pi #6 (secure balloon system) - **COMPLETED 2026-02-09**
- [x] Upgrade Wazuh server to 4.14.2 - **COMPLETED 2026-02-09**
- [ ] Deploy Wazuh agent to TrueNAS
- [ ] Configure UDM-SE syslog forwarding to Wazuh
- [ ] Create custom rules for balloon demo attack detection
- [ ] Set up alerting (email/Slack/etc.)
- [ ] Configure Suricata alert forwarding to Wazuh

---

### HAPI FHIR Server (10.30.0.56)

**Purpose:** HL7 FHIR (Fast Healthcare Interoperability Resources) server

**Services:**
- HAPI FHIR JPA Server
- PostgreSQL backend (on 10.30.0.50)

**Access:**
- Web: `http://10.30.0.56:8080`
- FHIR Base URL: `http://10.30.0.56:8080/fhir`
- SSH: `ssh fhir_admin@10.30.0.56`

**Current Status:**
- ✅ Installed and running
- ⏸️ No test data loaded yet
- Purpose: FHIR resource storage and retrieval

**Supported Resources:**
- Patient, Practitioner, Observation, etc.
- Full FHIR R4 spec support

**Planned Usage:**
- Heart rate data as FHIR Observations
- Mirth Connect integration
- SMART-on-FHIR app demos

**TODO:**
- [ ] Load sample FHIR test data
- [ ] Create heart rate → FHIR Observation converter
- [ ] Integrate with Keycloak for SMART-on-FHIR auth
- [ ] Set up Mirth Connect → FHIR pipeline

---

### Keycloak IDM (10.30.0.57)

**Purpose:** Identity and Access Management (IAM)

**Services:**
- Keycloak 23.x
- Realms:
  - `hospital` - Main realm for hospital homelab

**Access:**
- Web: `http://10.30.0.57:8080`
- Admin Console: `http://10.30.0.57:8080/admin`
- SSH: `ssh username@10.30.0.57`
- Credentials: See secure credential store

**Current Status:**
- ✅ Installed and running
- ⏸️ Minimal configuration (default realm only)

**Planned Integrations:**
- Grafana (SSO authentication)
- HAPI FHIR (SMART-on-FHIR)
- Node-RED (user authentication)

**Features:**
- SAML 2.0, OpenID Connect (OIDC)
- Social login providers (Google, GitHub, etc.)
- Multi-factor authentication (MFA)

**TODO:**
- [ ] Create `hospital` realm with proper configuration
- [ ] Add test users and roles
- [ ] Integrate Grafana with Keycloak SSO
- [ ] Configure SMART-on-FHIR for HAPI FHIR

---

### HashiCorp Vault (10.30.0.58)

**Purpose:** Secrets management and encryption as a service

**Services:**
- HashiCorp Vault 1.15.x
- Storage backend: File (integrated storage)

**Access:**
- Web: `https://10.30.0.58:8200`
- CLI: `export VAULT_ADDR="https://10.30.0.58:8200"`
- SSH: `ssh username@10.30.0.58`

**Current Status:**
- ✅ Installed and running
- ⏸️ Minimal configuration
- ⚠️ **IMPORTANT:** Vault unsealed? Root token stored securely?

**Planned Usage:**
- Database credentials (PostgreSQL, MQTT)
- API keys and tokens
- TLS certificate management
- Encryption as a service

**Secret Engines:**
- KV v2 (key-value secrets)
- Database (dynamic credentials)
- PKI (certificate authority)

**TODO:**
- [ ] Document unseal keys and root token (CRITICAL)
- [ ] Create secret paths for each service
- [ ] Migrate hardcoded credentials to Vault
- [ ] Set up dynamic database credentials
- [ ] Configure PKI for internal TLS certificates

---

### Suricata IDS/IPS (10.30.0.59)

**Purpose:** Network Intrusion Detection and Prevention System for balloon demo monitoring

**Services:**
- Suricata 7.0.3 RELEASE
- AF_PACKET capture mode on ens3
- 48,188 total detection rules (ET Open ruleset + custom rules)

**Access:**
- SSH: `ssh suricata_admin@10.30.0.59`
- Password: `password`
- No web UI (log-based monitoring)

**Current Status:**
- ✅ Installed and operational
- ✅ Monitoring network traffic on VLAN30
- ✅ Custom rules deployed for balloon demo
- ✅ Logging to fast.log and eve.json

**Network Configuration:**
- Interface: ens3 (primary monitoring interface)
- Network: VLAN30 (10.30.0.0/24 + routed traffic to VLAN2)
- HOME_NET: [10.30.0.0/24, 192.168.50.0/24]

**Custom Detection Rules:**
Located in `/var/lib/suricata/rules/local.rules`:

1. **Traffic to Vulnerable Balloon Pi** (sid:1000001)
   - `alert ip any any -> 192.168.50.100 any`
   - Detects all traffic to vulnerable balloon system on VLAN2
   - Purpose: Monitor attack attempts during expo demo

2. **ICMP Packet Detection** (sid:1000002)
   - `alert icmp any any -> any any`
   - General ICMP monitoring for testing
   - Purpose: Verify IDS alerting is functional

3. **Traffic to Secure Balloon Pi** (sid:1000003)
   - `alert ip any any -> 10.30.0.25 any`
   - Detects all traffic to secure balloon system on VLAN30
   - Purpose: Compare attack attempts against hardened system

4. **SSH to Secure Balloon Pi** (sid:1000004)
   - `alert tcp any any -> 10.30.0.25 22`
   - Detects SSH connections to secure Pi #6
   - Purpose: Monitor administrative access

**Log Files:**
- `/var/log/suricata/fast.log` - Alert summaries (human-readable)
- `/var/log/suricata/eve.json` - Full event data (JSON format)
- `/var/log/suricata/stats.log` - Performance statistics
- `/var/log/suricata/suricata.log` - Service logs

**Integration with Balloon Demo:**
- **Defense in Depth Architecture:**
  - **Network Layer:** Suricata IDS detects attack traffic
  - **Host Layer:** Wazuh SIEM on Pi #6 logs validation failures
  - **Application Layer:** Python code validates sensor inputs

- **Demo Scenario:**
  1. Attacker sends spoofed pressure data to both Pis
  2. Suricata logs traffic to 192.168.50.100 (vulnerable) and 10.30.0.25 (secure)
  3. Vulnerable Pi accepts bad data → balloon over-inflates
  4. Secure Pi rejects bad data → Wazuh logs validation failure → balloon stays safe

**Tested Functionality:**
- ✅ ICMP detection working (tested with ping to 8.8.8.8)
- ✅ Traffic to vulnerable Pi detection working (192.168.50.100)
- ✅ Traffic to secure Pi detection working (10.30.0.25)
- ✅ Capturing routed cross-VLAN traffic
- ✅ Rules loading successfully on restart

**Monitoring Commands:**
```bash
# Watch alerts in real-time
sudo tail -f /var/log/suricata/fast.log

# Check if Suricata is capturing traffic
sudo tail -20 /var/log/suricata/stats.log

# Verify rule count
sudo suricata -T -c /etc/suricata/suricata.yaml -v 2>&1 | grep "rules successfully"

# Restart after rule changes
sudo systemctl restart suricata
```

**TODO:**
- [ ] Configure Suricata to forward alerts to Wazuh SIEM
- [ ] Create more specific attack detection rules (HTTP spoofing, etc.)
- [ ] Set up email/Slack alerting for critical events
- [ ] Tune rules to reduce false positives

---

## VM Maintenance

### Backup Strategy
- **TrueNAS Snapshots:** VMs backed up via ZFS snapshots
- **Frequency:** TBD - need to configure snapshot schedule
- **Retention:** TBD

### Updates
- **OS Updates:** Manual `apt update && apt upgrade` on each VM
- **Service Updates:** Manual (PostgreSQL, Mosquitto, etc.)
- **Automation:** TBD - consider Ansible playbooks

### Monitoring
- **VM Health:** TrueNAS web UI shows CPU/RAM usage
- **Service Health:** Manual checks via web UIs
- **Future:** Prometheus + Grafana for VM metrics

---

## Future VMs (Available IPs: 10.30.0.60-99)

**Potential Future Services:**
- **Prometheus** (10.30.0.60) - Metrics collection
- **Alertmanager** (10.30.0.61) - Alert routing
- **Loki** (10.30.0.62) - Log aggregation
- **Jenkins** (10.30.0.63) - CI/CD pipeline
- **GitLab** (10.30.0.64) - Code repository
- **ELK Stack** (10.30.0.65-67) - Alternative to Wazuh
- **Pi-hole** (10.30.0.68) - DNS ad-blocking
- **OpenVPN** (10.30.0.69) - VPN server for remote access
- **Nextcloud** (10.30.0.70) - File sharing
- **Uptime Kuma** (10.30.0.71) - Uptime monitoring

---

## TODO - VM Integration Tasks

### High Priority
- [x] Deploy Wazuh agent to Pi #6 (secure balloon demo) - **COMPLETED 2026-02-09**
- [x] Upgrade Wazuh server to 4.14.2 - **COMPLETED 2026-02-09**
- [x] Create Suricata IDS/IPS VM - **COMPLETED 2026-02-09**
- [ ] Deploy Wazuh agent to TrueNAS server
- [ ] Configure PostgreSQL automated backups
- [ ] Document Vault unseal procedure and root token

### Medium Priority
- [ ] Load FHIR test data into HAPI FHIR server
- [ ] Create Mirth Connect HL7 → FHIR channel
- [ ] Integrate Grafana with Keycloak SSO
- [ ] Add Node-RED alerting flows
- [ ] Configure TrueNAS snapshot schedule for VMs

### Low Priority
- [ ] Migrate credentials to HashiCorp Vault
- [ ] Add MQTT authentication/TLS
- [ ] Set up Prometheus for VM monitoring
- [ ] Create Ansible playbooks for VM updates

---

**Document Created:** 2026-02-08
**Last Major Update:** 2026-02-09 - Added Suricata IDS/IPS VM, updated Wazuh status

**Related Documents:**
- NETWORK_INFRASTRUCTURE.md - Network topology and firewall rules
- RASPBERRY_PI_STATUS.md - Raspberry Pi configurations
- balloon-demo/CURRENT_STATUS_2026-02-06.md - Balloon demo status

**Recent Changes (2026-02-09):**
- Added Suricata IDS/IPS VM (10.30.0.59) with custom balloon demo detection rules
- Upgraded Wazuh SIEM from 4.9.2 to 4.14.2
- Deployed Wazuh agent to Pi #6 (secure balloon demo)
- Configured custom Suricata rules for vulnerable and secure balloon Pis
- Total VMs increased from 9 to 10
