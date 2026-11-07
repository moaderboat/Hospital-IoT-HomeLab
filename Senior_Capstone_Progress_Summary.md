# Senior Capstone Project: Hospital Homelab Network Infrastructure
## Technical Progress Summary & Timeline

**Student:** David Moad
**Project Start:** November 9, 2025
**Current Status:** Phase 4 (Security/Monitoring) - 85% Complete
**Last Updated:** January 28, 2026

---

## Executive Summary

This capstone project implements a production-grade healthcare IT infrastructure simulating a hospital network environment. The system demonstrates real-time patient monitoring, standards-compliant health data exchange (HL7 FHIR R4), HIPAA-compliant security controls, and enterprise-level identity management. The network architecture mirrors real-world healthcare IT deployments with emphasis on data persistence, fault tolerance, and regulatory compliance.

---

## Technical Architecture Overview

### Network Infrastructure
- **Topology:** Flat Layer 2/3 network (VLAN 30, 10.30.0.0/24 subnet)
- **Core Routing:** UniFi Dream Machine SE (gateway, firewall, DHCP)
- **Switching:** UniFi Switch Pro Max 24 PoE (SFP+ uplink @ 10 Gbps)
- **Wireless:** UniFi U6 Pro WiFi 6 Access Point
- **Power Delivery:** PoE++ (802.3bt) providing 60W per port to edge devices
- **Storage:** TrueNAS SCALE server with 80TB HDD ZFS pool (RAID-Z2)
- **Compute:** Dell PowerEdge server with iDRAC 9 management
- **Virtualization:** 8 KVM virtual machines on TrueNAS hypervisor

### Edge Computing Layer (IoT)
- **5× Raspberry Pi 4 Model B** (4GB RAM, Debian 12 Bookworm)
  - 4 units powered via PoE++ (802.3bt)
  - 1 unit external power (PoE incompatibility)
- **Sensor Hardware:** Raspberry Pi Sense HAT (IMU, environmental sensors, 8×8 LED matrix)
- **Application:** Custom Python-based ECG/heart rate simulation scripts
- **Service Management:** systemd units with auto-restart on boot
- **Data Publishing:** MQTT protocol @ 20 Hz (50ms intervals)

---

## Completed Implementation (Phases 1-4)

### Phase 1: IoT Data Acquisition & Pipeline (100% Complete)

**Raspberry Pi Patient Monitors:**
- **Data Rate:** 100 messages/second aggregate (20 Hz per device × 5 devices)
- **Message Format:** JSON over MQTT with fields: timestamp (EST), BPM, pi_id, status, anomaly_type
- **Simulation Models:**
  - **Pi #1:** 72 BPM baseline ± 2.5 BPM HRV (6-12 sec intervals) - normal sinus rhythm
  - **Pi #2:** 68 BPM baseline ± 3.5 BPM HRV (4-10 sec intervals) - high variability
  - **Pi #3:** 75 BPM baseline ± 2.0 BPM HRV (8-18 sec intervals) - athletic profile
  - **Pi #4:** 110 ± 40 BPM AFib simulation (critically damped oscillator model)
  - **Pi #5:** 70 BPM baseline with stochastic anomalies (λ = 1/5.5 hours, exponential distribution)
- **Physics Engine:** Critically damped spring-damper model (ζ = 1.0) for smooth physiological transitions
- **Display:** Real-time 60 FPS ECG waveform rendering on 8×8 LED matrices

**Message Broker:**
- **Software:** Eclipse Mosquitto MQTT v2.0
- **VM:** Ubuntu Server 24.04 LTS (10.30.0.51)
- **Topics:** `hospital/heartrate/pi{1-5}` with wildcard subscriptions
- **QoS:** Level 0 (fire-and-forget for real-time telemetry)

**Workflow Orchestration:**
- **Platform:** Node-RED v4.x with Node.js v20
- **VM:** Ubuntu Server 22.04 LTS (10.30.0.52, 2 vCPU, 2GB RAM)
- **Flows:** MQTT ingestion → JSON parsing → PostgreSQL insertion + Dashboard rendering
- **Dashboard:** Real-time UI at `http://10.30.0.52:1880/ui`
  - 5× BPM gauges (0-200 range with color zones: green <100, yellow 100-140, red >140)
  - 5× time-series charts (bezier interpolation, 5-minute sliding window, 40-160 BPM Y-axis)
  - Tachycardia alert system (threshold: BPM > 100, includes duration tracking, min/max values)
- **Authentication:** Keycloak SSO via OAuth2/OpenID Connect (passport-openidconnect)

**Data Persistence:**
- **RDBMS:** PostgreSQL 16.10 on Ubuntu Server 24.04 LTS (10.30.0.50)
- **Storage:** 1TB ZFS zvol (957GB available) on 80TB HDD array
- **Schema:** `hospital_data.heartrate_data` table
  - Columns: `id` (BIGSERIAL PK), `timestamp` (TIMESTAMPTZ), `pi_id` (INTEGER), `bpm` (INTEGER), `status` (VARCHAR), `anomaly_type` (VARCHAR), `created_at` (TIMESTAMPTZ)
- **Indexes:**
  - `idx_heartrate_pi_id` on `pi_id`
  - `idx_heartrate_timestamp` on `timestamp`
  - `idx_heartrate_pi_timestamp` composite on `(pi_id, timestamp)`
- **Performance Metrics:**
  - Current dataset: **397,645,663 rows** (46+ days continuous operation)
  - Insertion rate: 100 rows/second sustained
  - Query optimization: 35 seconds → 79 ms (445× improvement) after indexing
  - Disk growth: ~200 MB/day (~73 GB/year)
  - Capacity: 13+ years at current data rate
- **Timezone:** America/New_York (EST) for HIPAA audit compliance

---

### Phase 2: Visualization & Analytics (100% Complete)

**Real-Time Monitoring:**
- **Platform:** Node-RED Dashboard (dashboard 2.0 nodes)
- **Update Rate:** 20 Hz refresh (50ms latency)
- **Network Performance:** Stable at 100 msg/sec with zero packet loss
- **Alert Logic:** Rule-based threshold detection with hysteresis (BPM > 100 for >5 seconds)

**Historical Analytics:**
- **Platform:** Grafana OSS (latest stable) on Ubuntu Server 24.04 LTS (10.30.0.53)
- **Data Source:** PostgreSQL via pg_hba.conf trust authentication (10.30.0.50:5432)
- **Dashboards:**
  - "Heart Rate Monitoring - All Patients" (7 panels)
  - 5× patient-specific time-series (Pi #1-5 individual trends)
  - 1× AFib monitoring panel (Pi #4 irregular rhythm analysis)
  - 1× anomaly detection panel (Pi #5 rare event tracking)
  - 1× alert list panel (live Grafana alerting state)
- **Query Performance:** `timestamp AT TIME ZONE 'America/New_York'` for EST display
- **Auto-Refresh:** 30-second polling interval
- **Alerting:** Tachycardia rule (Pi #4 BPM > 120 for 1 minute) → Grafana UI notification
- **Authentication:** Keycloak SSO via OAuth2/OpenID Connect + local admin fallback
- **Known Limitation:** Panel auto-refresh disabled with 397M+ row dataset (query timeout prevention)

---

### Phase 3: Healthcare Data Standards (100% Complete)

**HL7/FHIR Integration Engine:**
- **Software:** Mirth Connect 4.5.2 (NextGen Connect) on Ubuntu Server 24.04 LTS (10.30.0.54)
- **Resources:** 4 vCPU, 8GB RAM, 100GB disk (21% utilization)
- **Java Runtime:** OpenJDK 11.0.29
- **Active Channel:** `HeartRate_FHIR_Final`
  - **Source:** HTTP Listener (port 8081, JSON inbound)
  - **Transformer:** JavaScript source transformer (custom heart rate → FHIR R4 Observation mapping)
  - **Destination:** HTTP Sender → HAPI FHIR server (`http://10.30.0.56:8080/fhir/Observation`)
  - **Data Flow:** MQTT → Node-RED → HTTP POST (rate-limited to 1/second) → Mirth → HAPI FHIR
  - **Content Field:** `${message.encodedData}` for HTTP body transmission in JSON mode
- **Database Maintenance:**
  - Derby embedded database at `/opt/mirthconnect/appdata/mirthdb`
  - Auto-pruning: 30-day retention policy, daily execution @ 2 AM
  - Prunes: events, message content, metadata (retains errors and queued messages)
  - Recovered from 100% disk usage (36GB → 10GB after database cleanup)
- **Service Management:** systemd unit `mirthconnect.service` + `/tmp/fhir-observations/` directory auto-creation
- **Authentication:** Basic auth (admin / password) - no SSO capability without commercial license

**FHIR R4 Server:**
- **Software:** HAPI FHIR Server v8.6.0 (Docker: hapiproject/hapi:latest)
- **VM:** Ubuntu Server 24.04 LTS (10.30.0.56, 2 vCPU, 4GB RAM, 50GB disk)
- **Java Heap:** -Xms512m -Xmx3072m (3GB max heap to prevent OutOfMemoryError)
- **Database:** PostgreSQL backend (10.30.0.50:5432/hapi_fhir) replacing H2 embedded DB
  - Dialect: `ca.uhn.fhir.jpa.model.dialect.HapiFhirPostgres94Dialect`
  - JDBC: `jdbc:postgresql://10.30.0.50:5432/hapi_fhir`
- **FHIR Version:** R4 (HL7 FHIR Release 4.0.1)
- **Patient Resources:** 5 patients created (Patient/pi-1 through Patient/pi-5)
- **Observation Ingestion:** 1 FHIR Observation/second from Mirth Connect
  - **LOINC Code:** 8867-4 (Heart rate)
  - **Units:** beats/minute (UCUM: /min)
  - **Structure:** valueQuantity with value, unit, system, code
- **REST API Endpoints:**
  - Base: `http://10.30.0.56:8080/fhir/`
  - Metadata: `http://10.30.0.56:8080/fhir/metadata` (CapabilityStatement)
  - Patient Search: `GET /fhir/Patient`
  - Observation Search: `GET /fhir/Observation?subject=Patient/pi-4&code=8867-4&_sort=-date&_count=50`
  - Value Filtering: `GET /fhir/Observation?value-quantity=gt100` (tachycardia detection)
- **Data Persistence:** PostgreSQL-backed storage survives container restarts and power loss
- **Docker Configuration:** `--restart unless-stopped` for automatic recovery
- **Compliance:** Full FHIR R4 specification adherence with HIPAA-compliant audit trail

**Complete Data Pipeline:**
```
Raspberry Pi (Python/MQTT) → Mosquitto Broker → Node-RED (rate limiter) →
Mirth Connect (FHIR transformer) → HAPI FHIR Server (PostgreSQL) → REST API
```

---

### Phase 4: Security & Identity Management (85% Complete)

**Security Information & Event Management (SIEM):**
- **Software:** Wazuh 4.9.2 All-in-One on Ubuntu Server 24.04 LTS (10.30.0.55)
- **Resources:** 4 vCPU, 8GB RAM, 100GB disk
- **Components:**
  - Wazuh Manager: Log analysis, rule correlation, alerting
  - Wazuh Indexer: OpenSearch-based log aggregation and storage
  - Wazuh Dashboard: Web UI for security visualization
- **Agent Deployment:** 12 agents active
  - 5× Raspberry Pi monitors (username through username)
  - 7× VMs (PostgreSQL, Node-RED, Grafana, Mirth, HAPI FHIR, MQTT, Keycloak)
- **Monitoring Capabilities:**
  - File Integrity Monitoring (FIM) on `/etc`, `/bin`, `/usr/bin`, `/opt`
  - Vulnerability detection (CVE scanning, package audit)
  - Log analysis and correlation (syslog, auth.log, application logs)
  - Authentication tracking (SSH, web logins, API access)
  - Anomaly detection (statistical baseline + rule-based)
- **HIPAA Compliance:** 164.312.b audit controls dashboard
  - Access logging for PHI (Protected Health Information)
  - Failed authentication attempts
  - File modification tracking
  - Privileged user activity monitoring
- **Authentication:** Keycloak SSO via OpenID Connect + local admin fallback
  - Local: admin / password
  - SSO: "Log in with OpenID Connect" button (username or username)

**Identity & Access Management (IDM):**
- **Software:** Keycloak 26.0.7 on Ubuntu Server 24.04 LTS (10.30.0.57)
- **Resources:** 2 vCPU, 4GB RAM, 50GB disk
- **Database:** PostgreSQL backend (10.30.0.50:5432/keycloak) for session persistence
- **Protocols:** OAuth2, OpenID Connect (OIDC), SAML 2.0
- **Realm Configuration:**
  - Realm: `hospital-homelab`
  - Display Name: "Hospital Homelab"
  - Users:
    - `username` (Admin User) - password: password
    - `username` (Doctor One) - password: password
- **Client Applications (OAuth2/OIDC):**
  - **Grafana** (`grafana` client):
    - Client Secret: `client-secret`
    - Redirect URI: `http://10.30.0.53:3000/*`
    - Flow: Authorization Code Flow
    - Status: ✓ SSO Working
  - **Node-RED** (`node-red` client):
    - Client Secret: `client-secret`
    - Redirect URI: `http://10.30.0.52:1880/auth/strategy/callback`
    - Strategy: passport-openidconnect
    - Status: ✓ SSO Working
  - **Wazuh** (`wazuh` client):
    - Client Secret: `client-secret`
    - Redirect URI: `https://10.30.0.55/*`
    - Realm roles mapper: Configured for authentication
    - Status: ✓ SSO Working (OpenID Connect)
- **SSO Integrations:** 3 of 5 applications integrated (Grafana, Node-RED, Wazuh)
- **Pending Integrations:** HAPI FHIR (OAuth2 Proxy planned), Mirth Connect (not supported without commercial license)
- **Features Enabled:**
  - Single Sign-On (SSO) across integrated applications
  - Single Logout (SLO)
  - Role-Based Access Control (RBAC)
  - Session management with configurable timeouts
  - Multi-Factor Authentication (MFA) capable (not yet configured)
  - HIPAA-compliant audit logging (login events, permission changes)

---

## System Resilience & Production Readiness

### Fault Tolerance
- **Power Loss Recovery:** All services auto-restart via systemd units
- **Data Durability:** PostgreSQL backend for HAPI FHIR prevents H2 data loss issue
- **Container Auto-Recovery:** Docker `--restart unless-stopped` policy on HAPI FHIR
- **Directory Auto-Creation:** Mirth FHIR output directory recreated on boot via systemd oneshot service
- **Network Auto-Connect:** NetworkManager with auto-connect enabled on all Raspberry Pis

### Performance Metrics
- **Database Query Optimization:** 35s → 79ms (445× speedup) via composite indexing
- **MQTT Throughput:** 100 msg/sec sustained with zero packet loss over 46 days
- **Dashboard Latency:** <50ms from sensor to UI display (20 Hz refresh rate)
- **Storage Efficiency:** 200 MB/day for 100 records/second (13+ years capacity on 1TB volume)
- **FHIR API Response Time:** <100ms for single resource GET, <500ms for search queries (N<1000)

### HIPAA Compliance Implementation
- **164.312.a.1 - Access Control:** Keycloak RBAC with unique user IDs (username, username)
- **164.312.b - Audit Controls:** Wazuh SIEM logging all access to PHI (PostgreSQL, FHIR API)
- **164.312.c.1 - Integrity:** File Integrity Monitoring (FIM) on 12 systems via Wazuh agents
- **164.312.d - Authentication:** Keycloak SSO with session management and password policies
- **164.312.e.1 - Transmission Security:** HTTPS for Mirth (8443), Wazuh (443); future: HAPI FHIR OAuth2 Proxy

---

## Current Limitations & Known Issues

1. **Grafana Panel Auto-Refresh:** Disabled for 397M+ row dataset to prevent query timeout
2. **Mirth Connect SSO:** Requires commercial LDAP plugin (Pro/Enterprise license)
3. **HAPI FHIR Authentication:** Currently unauthenticated REST API (OAuth2 Proxy planned)
4. **Timezone Display:** Grafana shows UTC (requires `AT TIME ZONE` in queries for EST)
5. **MFA Not Enabled:** Keycloak MFA capable but not yet configured for users

---

## Remaining Work & Timeline

### Progress Report 1 Deliverables (Due: February 17, 2026)
**Focus:** Documentation and HAPI FHIR SSO Integration

- [ ] Complete HAPI FHIR OAuth2 Proxy integration with Keycloak
- [ ] Update network topology diagrams with SSO authentication flows
- [ ] Document system performance benchmarks (query times, throughput, latency)
- [ ] Create HIPAA compliance matrix mapping controls to implementations
- [ ] Write Progress Report 1 narrative (accomplishments, challenges, next steps)

**Estimated Effort:** 20 hours (Jan 28 - Feb 16)

---

### Progress Report 2 Deliverables (Due: March 10, 2026)
**Focus:** Security Hardening and Additional Monitoring

- [ ] Deploy HashiCorp Vault VM for secrets management (10.30.0.58)
  - Migrate hardcoded credentials to Vault dynamic secrets
  - Integrate with PostgreSQL, Keycloak, MQTT broker
- [ ] Deploy Zeek/Suricata IDS/IPS VM for network intrusion detection (10.30.0.59)
  - Configure span port on UniFi switch for traffic mirroring
  - Create rulesets for HL7/FHIR protocol anomalies
  - Integrate alerts with Wazuh SIEM
- [ ] Configure Keycloak MFA (TOTP authenticator app)
- [ ] Implement PostgreSQL data retention policy (90-day rolling window)
- [ ] Write Progress Report 2 narrative

**Estimated Effort:** 30 hours (Feb 17 - Mar 9)

---

### Final Expo Preparation (Due: April 7, 2026)
**Focus:** Phase 5 Attack Lab and Demo Polish

#### Week 1-2 (Mar 10 - Mar 23): Attack Lab Deployment
- [ ] Deploy Kali Linux VM #1 (10.30.0.60) - External attacker perspective
- [ ] Deploy Kali Linux VM #2 (10.30.0.61) - Internal threat simulation
- [ ] Deploy Metasploitable 3 VM (10.30.0.62) - Vulnerable target system
- [ ] Deploy T-Pot Honeypot VM (10.30.0.63) - Threat intelligence gathering
- [ ] Configure firewall rules for isolated attack subnet (VLAN 40)

#### Week 3 (Mar 24 - Mar 30): Penetration Testing Scenarios
- [ ] Execute OWASP Top 10 attacks against FHIR API
- [ ] SQL injection testing on PostgreSQL database
- [ ] MQTT broker authentication bypass attempts
- [ ] Wazuh detection validation (verify alerts trigger)
- [ ] Document attack paths and detection coverage

#### Week 4 (Mar 31 - Apr 6): Final Documentation & Demo Prep
- [ ] Create system architecture diagrams (network topology, data flow, authentication flow)
- [ ] Record demonstration videos (data pipeline, SIEM alerts, SSO login flow)
- [ ] Write final technical report (architecture, implementation, testing, results)
- [ ] Prepare expo presentation slides (15-minute talk + Q&A)
- [ ] Create live demo script with fallback plans

**Estimated Effort:** 50 hours (Mar 10 - Apr 6)

---

## Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| Demo hardware failure during expo | Medium | High | Record backup demo videos, test all equipment 48hrs before |
| OAuth2 Proxy integration complexity | Low | Medium | Fallback: Document HAPI FHIR as "future work" if blocked |
| Vault/IDS/IPS VM resource constraints | Medium | Low | Deploy on external hardware if TrueNAS CPU/RAM exhausted |
| Attack lab causes network instability | Low | High | Isolate attack subnet (VLAN 40), implement strict firewall rules |
| Time constraints for Phase 5 | High | Medium | Prioritize 1 Kali + Metasploitable over full attack lab |

---

## Technical Metrics Summary

| Metric | Value | Significance |
|--------|-------|--------------|
| Total Systems Monitored | 17 devices | 5 IoT + 8 VMs + 4 network devices |
| Data Points Collected | 397,645,663 rows | 46+ days continuous operation |
| Real-Time Throughput | 100 msg/sec | 20 Hz × 5 devices |
| Database Query Performance | 79 ms | 445× improvement via indexing |
| Storage Capacity | 13+ years | At 200 MB/day growth rate |
| FHIR Compliance | R4 (v4.0.1) | Full HL7 specification adherence |
| SSO Integration Coverage | 60% (3/5 apps) | Grafana, Node-RED, Wazuh |
| SIEM Agent Deployment | 12 agents | 100% coverage of critical systems |
| Network Uptime | 99.8%+ | Single planned outage (power loss recovery test) |

---

## Deliverables Checklist

### Progress Report 1 (Feb 17)
- [x] Technical progress summary (this document)
- [ ] HAPI FHIR OAuth2 Proxy implementation
- [ ] Network topology diagrams
- [ ] HIPAA compliance matrix
- [ ] Performance benchmark report
- [ ] Progress narrative

### Progress Report 2 (Mar 10)
- [ ] HashiCorp Vault deployment
- [ ] Zeek/Suricata IDS/IPS deployment
- [ ] Keycloak MFA configuration
- [ ] Data retention policy implementation
- [ ] Updated system architecture diagrams
- [ ] Progress narrative

### Final Expo (Apr 7)
- [ ] Attack lab deployment (Kali, Metasploitable, T-Pot)
- [ ] Penetration testing report
- [ ] Final technical documentation
- [ ] Demonstration videos (backup)
- [ ] Presentation slides
- [ ] Live demo script
- [ ] System handoff documentation

---

## References & Standards Compliance

- **HL7 FHIR R4:** https://hl7.org/fhir/R4/
- **HIPAA Security Rule:** 45 CFR Part 164 Subpart C
- **MQTT v5.0 Specification:** OASIS Standard
- **OAuth 2.0 / OpenID Connect:** RFC 6749, RFC 7636, OIDC Core 1.0
- **LOINC Code 8867-4:** Heart rate (beats/minute)
- **UCUM Units:** Unified Code for Units of Measure
- **IEEE 802.3bt:** Power over Ethernet (PoE++) standard

---

**END OF TECHNICAL SUMMARY**
