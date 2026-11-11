# SECTION 13 UPDATED - March 2026 Completion Status

## 13.1 Project Limitations and Completed Remediations

The following table shows initial limitations identified during early development (Fall 2025) and their resolution status as of March 2026:

| Original Limitation | Impact | Solution Deployed | Status |
|---------------------|--------|-------------------|--------|
| **SSH Password Authentication** | Security risk; violated test criterion TC-09 | SSH key-based authentication deferred to future hardening phase | ⚠️ DEFERRED (documented in future work) |
| **Flat Network (Single VLAN)** | Insufficient segmentation for realistic hospital scenario | Deployed strategic dual-VLAN architecture: VLAN 2 (192.168.50.0/24) for vulnerable attack lab, VLAN 30 (10.30.0.0/24) for secure hospital infrastructure | ✅ COMPLETE (Feb 2026) |
| **No MQTT Data Pipeline** | Sensors generated data locally but couldn't transmit to central system | Deployed MQTT Broker VM (10.30.0.51), updated all 5 Pi scripts with paho-mqtt library, configured Node-RED subscriber flows | ✅ COMPLETE (Nov 2025) |
| **Manual Sensor Monitoring** | No automated alerting for sensor failures or anomalies | Deployed Grafana with real-time dashboards (ECG waveforms, heart rate gauges, IDS attack visualization, security status panel) | ✅ COMPLETE (Dec 2025) |
| **Limited Attack Scenarios** | Only network scanning planned; needed broader threat coverage | Deployed balloon demo dual-target attack system demonstrating sensor spoofing attacks (100% vulnerable compromise vs 100% secure protection) | ✅ COMPLETE (Mar 2026) |
| **No IDS/IPS Deployment** | Cannot detect/block malicious traffic in real-time | Deployed Suricata IDS on bare metal laptop (192.168.50.191), Elasticsearch log aggregation (10.30.0.60), Grafana IDS Dashboard, Wazuh SIEM integration | ✅ COMPLETE (Feb 2026) |

**Testing Gaps Resolved:**

**TC-05 (RAID Redundancy):** Originally deferred due to risk of data loss
- **Resolution:** Not tested in controlled environment (no hardware failures occurred naturally during project timeline)
- **Status:** ⚠️ DEFERRED to future disaster recovery drills
- **Risk Mitigation:** Daily ZFS scrubs verify pool integrity; 933M rows successfully stored without corruption

**TC-10 (System Recovery):** Backup created but restoration not validated
- **Resolution:** Full power cycle test completed March 24-25, 2026 (all VMs recovered successfully, cold start procedure validated)
- **Status:** ✅ COMPLETE
- **Evidence:** QUICK_STARTUP_PROCEDURE.md validated during air-gap expo preparation

---

## 13.2 Features Deployed vs. Originally Planned

### Deployed Features (Originally High-Priority, Now Operational)

**A. MQTT Data Pipeline** ✅ OPERATIONAL (Nov 2025)
- **Benefit Realized:** Enabled real-time data collection for all downstream analytics
- **Components Deployed:**
  - MQTT Broker VM (Mosquitto) at 10.30.0.51 with authentication (username user)
  - Updated all 5 Raspberry Pi scripts with paho-mqtt v2.1.0 library
  - Node-RED MQTT subscriber flows operational
- **Performance Metrics:** 50 msg/sec sustained throughput (5x original 10 msg/sec target)
- **Success Metric:** <0.004% data loss (2.7M+ readings collected)

**B. PostgreSQL Time-Series Database** ✅ OPERATIONAL (Nov 2025)
- **Benefit Realized:** Structured storage for historical analysis and compliance reporting
- **Schema Deployed:**
  ```sql
  CREATE TABLE heartrate_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    pi_id INTEGER NOT NULL,
    bpm INTEGER NOT NULL,
    status VARCHAR,
    anomaly_type VARCHAR
  );
  CREATE TABLE heartrate_data_archive (
    -- Same schema for long-term retention
  );
  ```
- **Scale Achieved:** 933M total rows (60M active + 873M archived), 180GB database size
- **Automation:** pg_cron archival runs daily at 2 AM UTC, maintains 7-day retention in active table

**C. Grafana Visualization Dashboards** ✅ OPERATIONAL (Dec 2025)
- **Benefit Realized:** Real-time monitoring and visual attack demonstration
- **Dashboards Deployed:**
  - Heart Rate Monitoring Dashboard (5 Pi gauges, ECG waveforms, historical trends)
  - IDS Dashboard (attack events timeline, source/destination IP tracking, protocol breakdown)
  - Security Status Panel (real-time attack visualization with pulsing red alarm)
  - Balloon Demo Dashboard (upstream/downstream pressure gauges for both systems)
- **Performance:** 30-second refresh rate, real-time ECG generation synchronized to live BPM data

**D. SIEM Integration (Wazuh)** ✅ OPERATIONAL (Jan-Feb 2026)
- **Benefit Realized:** Centralized security monitoring and compliance audit logging
- **Features Deployed:**
  - 14 agents monitoring (5 hospital Pis, 2 balloon Pis, 7 VMs)
  - CIS benchmark compliance checks running on all agents
  - Real-time attack detection logging (143 rejected spoofed packets logged March 2026 attack test)
- **Authentication:** Local admin login (SSO deferred - OpenID Connect certificate issues documented in TROUBLESHOOTING_HISTORY.md)

**E. IDS/IPS Deployment (Suricata)** ✅ OPERATIONAL (Feb 2026)
- **Benefit Realized:** Real-time threat detection for attack demonstrations
- **Configuration Deployed:**
  - Suricata IDS on bare metal laptop (192.168.50.191) - TrueNAS macvtap filtering prevented VM deployment
  - Port 7 monitoring interface receives mirrored traffic from Switch Port 15
  - EVE log shipping via Filebeat to Elasticsearch (10.30.0.60:9200)
  - Grafana IDS Dashboard visualizes attack events, top source/destination IPs, protocol breakdown
- **Attack Capture:** Successfully captured dual-target attack March 2026 (600 packets to each target logged)

**F. FHIR/HL7 Healthcare Data Integration** ✅ OPERATIONAL (Dec 2025)
- **Benefit Realized:** Realistic electronic health record (EHR) data flows demonstrating healthcare IT interoperability
- **Components Deployed:**
  - Mirth Connect interface engine (10.30.0.54:8443) - Channel `HeartRate_FHIR_Final` operational on port 8081
  - HAPI FHIR server (10.30.0.56:8080) with OAuth2 Proxy authentication on port 4180
  - Complete pipeline: Node-RED → Mirth Connect → HAPI FHIR (LOINC 8867-4 Observation resources)
  - Rate limiting: 1 FHIR message/sec (prevents HAPI overload while maintaining real-time clinical relevance)
- **Derby DB:** Mirth auto-prunes at 30 days, HAPI persistent storage at 35GB

**G. Zero Trust Architecture (Keycloak IDM + Vault)** ✅ OPERATIONAL (Jan 2026)
- **Benefit Realized:** Advanced authentication and secrets management demonstrating enterprise IAM
- **Components Deployed:**
  - Keycloak (10.30.0.57:8080) - Realm `hospital-homelab`, users `username`/`username`
  - Node-RED SSO integration ✅ working
  - Grafana SSO integration ✅ working
  - Wazuh SSO ⚠️ deferred (OpenID Connect issues - using basic auth)
  - HashiCorp Vault (10.30.0.58:8200) - Token auth for admin (root token stored securely)
  - Requires 3-of-5 unseal keys after VM restart (manual unseal procedure documented)
- **OIDC Support:** Available but limited permissions (Token auth preferred for admin operations)

### Features Deferred to Future Work

**H. PACS Medical Imaging (Orthanc)**
- **Status:** ⚠️ OUT OF SCOPE for current phase
- **Justification:** Project prioritized real-time vital monitoring and attack demonstrations; DICOM workflows add complexity without advancing core cybersecurity research objectives
- **Resources Required:** 40 hours deployment; 8GB RAM VM; 500GB storage
- **Future Timeline:** Summer 2026 or next semester

**I. Machine Learning Anomaly Detection**
- **Status:** ⚠️ DATA INFRASTRUCTURE READY, MODEL TRAINING DEFERRED
- **Justification:** PostgreSQL dataset (933M rows) provides sufficient training data, but ML model development required skills beyond project scope (would need statistics/data science course prerequisites)
- **Resources Ready:** Historical dataset with labeled anomalies (Pi #4 AFib patterns, Pi #5 rare events)
- **Future Timeline:** Could be senior capstone project for data science student

**J. Advanced Attack Scenarios (Kali Linux VMs)**
- **Status:** ⚠️ SINGLE ATTACK DEMONSTRATED (sensor spoofing), ADDITIONAL SCENARIOS DEFERRED
- **Justification:** Balloon demo sensor spoofing attack achieved 100% demonstration effectiveness; additional scenarios (ransomware, DoS, MitM) would duplicate existing work without novel insights
- **Resources Required:** 40 hours; 2 Kali VMs
- **Future Timeline:** Could be integrated into cybersecurity course lab exercises

---

## 13.3 Project Plan vs. Project Completion

### Original 12-Week Timeline (Preliminary Proposal) vs. Actual 28-Week Execution

| Week | Planned Milestone | Actual Status (March 2026) |
|------|-------------------|----------------------------|
| 1-2 | Hardware installation, network configuration | ✅ **COMPLETE** (Sept 2025) |
| 3-4 | TrueNAS setup, VM provisioning | ✅ **COMPLETE** - Node-RED, MQTT Broker, PostgreSQL, Grafana operational (Oct-Nov 2025) |
| 5-6 | Raspberry Pi sensor integration | ✅ **COMPLETE** - 5 sensors operational with 99.98-100% uptime (Oct 2025) |
| 7-8 | Firewalling, VLAN isolation, attack simulation | ✅ **COMPLETE** (Extended to Week 24) - UDM-SE firewall operational; dual-VLAN segmentation (VLAN 2+30) deployed Feb 2026; balloon attack demo operational Mar 2026 |
| 9-10 | ML research, data infrastructure | ✅ **DATA INFRASTRUCTURE COMPLETE, ML OUT OF SCOPE** - PostgreSQL operational with 933M rows; IDS/SIEM prioritized over ML model training |
| 11-12 | Compliance review, documentation, final testing | ✅ **COMPLETE** (Extended to Week 28) - Compliance matrix validated; full system cold start tested March 24-25, 2026 |

### Analysis: What We Aimed For vs. What We Achieved

**Significantly Exceeded Expectations:**
- ✅ **Network stability:** 99.98%+ uptime over 8-day continuous testing (original target: "operational")
- ✅ **Data pipeline scale:** 933M rows collected (50x initial estimate of ~20M rows/year)
- ✅ **Documentation quality:** 50+ pages including NETWORK_SETUP_PROGRESS.md, TROUBLESHOOTING_HISTORY.md, QUICK_STARTUP_PROCEDURE.md (original target: basic setup guide)
- ✅ **Air-gap capability:** Validated early (Week 2) with mock WAN discovery solving cross-VLAN routing (critical for expo portability)
- ✅ **VM count:** 10 production VMs deployed vs. 4-6 originally planned
- ✅ **Security demonstration:** Dual-system attack comparison (100% vulnerable compromise vs 100% secure protection) exceeded original "simulate attacks" goal

**Met Expectations:**
- ✅ **Hardware deployment:** Dell R740XD, UniFi networking, 5 Raspberry Pis all operational on schedule
- ✅ **IoT sensor deployment:** 5 sensors operational (target: 4-6)
- ✅ **Budget:** $11,843 complete system (preliminary proposal estimated $5,400 for server/storage only; full system cost expected)
- ✅ **Compliance mapping:** HIPAA, NIST CSF, NIST 800-53, IEC 62443, ISO 27001 all documented

**Scope Adjustments (Strategic Pivots):**
- ✅ **OPNsense Firewall → UDM-SE:** Switching to dedicated hardware firewall improved performance and freed VM resources (correct engineering decision)
- ✅ **Phased VLAN Deployment:** Starting with flat network prevented cascading troubleshooting issues; strategic dual-VLAN (2+30) architecture simpler and more effective than original 5-VLAN design
- ✅ **IDS on bare metal vs VM:** TrueNAS macvtap filtering blocked mirrored traffic to VMs; bare metal Suricata deployment solved issue
- ⚠️ **ML Deferred:** Data infrastructure ready (933M rows), but model training requires skills beyond project scope; deferred to future work

### Lessons Learned

**Technical Lessons:**
1. **Iterative validation works:** Flat network validation before VLAN complexity prevented cascading troubleshooting
2. **Documentation is critical:** Real-time NETWORK_SETUP_PROGRESS.md updates saved countless hours during troubleshooting
3. **Hardware decisions matter:** Used Dell R740XD has been rock-solid; PoE switch eliminates cable management complexity
4. **Bare metal > VM for network monitoring:** TrueNAS macvtap filtering taught us IDS/IPS belongs on dedicated hardware
5. **Mock WAN enables air-gap cross-VLAN:** Critical discovery for portable expo demonstrations (UDM-SE requires WAN interface configured even for local-only routing)

**Project Management Lessons:**
1. **Phased deployment beats perfect-first-time:** Validate core functionality before layering complexity
2. **Sunk cost fallacy is real:** OPNsense pivot (after 20 hours invested) was correct decision despite discomfort
3. **Buffer time for unknown unknowns:** 28 weeks vs 12 weeks planned (233% schedule extension) - hardware issues, software bugs, architectural pivots all consume time
4. **Advisor consultation accelerates progress:** Rob Kuschel's guidance on flat-network-first approach saved weeks of troubleshooting

### Extended Timeline: September 2025 - March 2026 (28 Weeks)

| Phase | Weeks | Focus | Status |
|-------|-------|-------|--------|
| **Phase 0: Planning** | Sept 2025 | Proposal, hardware procurement, literature review | ✅ COMPLETE |
| **Phase 1: Core Infrastructure** | Sept-Nov 2025 (Weeks 1-12) | Hardware setup, TrueNAS, 5 Raspberry Pi sensors, MQTT pipeline, Node-RED, PostgreSQL | ✅ COMPLETE |
| **Phase 2: Data & Visualization** | Nov-Dec 2025 (Weeks 13-16) | Grafana dashboards, Mirth Connect FHIR pipeline, HAPI FHIR integration | ✅ COMPLETE |
| **Phase 3: Security Infrastructure** | Jan-Feb 2026 (Weeks 17-24) | Keycloak SSO, Vault, Wazuh SIEM (14 agents), Suricata IDS, Elasticsearch, Grafana IDS Dashboard, VLAN segmentation (2+30) | ✅ COMPLETE |
| **Phase 4: Attack Demonstration** | Mar 2026 (Weeks 25-28) | Balloon demo hardware (vulnerable + secure Pi systems), DATAQ pressure sensors, attack scenarios, Node-RED Security Status Panel | ✅ COMPLETE |
| **Phase 5: System Verification** | Mar 24-25, 2026 | Full cold start testing, all 5 pipelines verified, PostgreSQL archival validation, air-gap operation with mock WAN | ✅ COMPLETE |

**Key Milestones Achieved:**
- **Nov 9, 2025:** MQTT pipeline operational, first 1M rows collected
- **Dec 15, 2025:** FHIR integration complete (Node-RED → Mirth → HAPI FHIR)
- **Feb 8, 2026:** Suricata IDS operational, Grafana IDS Dashboard deployed
- **Mar 8, 2026:** Balloon demo hardware complete (DATAQ sensors + relay HATs working)
- **Mar 23, 2026:** Dual-target attack test successful (vulnerable compromised, secure protected)
- **Mar 24-25, 2026:** Full system verification (all VMs cold start, all pipelines operational, air-gap validated)

---

## 13.4 Advice for Others

*[This section remains unchanged - already accurate]*

---

This updated Section 13 now accurately reflects the **March 2026 completion status** instead of the November 2025 "in progress" status.
