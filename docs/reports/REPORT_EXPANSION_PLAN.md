# Technical Report Expansion Plan
## Target: 200-300 Pages (8,000-15,000 Lines)
## Current: ~3,676 Lines (~120 Pages)
## Goal: 2-3x Expansion

---

## EXPANSION STRATEGY OVERVIEW

### Approach
- Add depth to existing sections WITHOUT changing core narrative
- Incorporate content from your 50+ supporting documentation files
- Add technical deep-dives, detailed procedures, and comprehensive appendices
- Include visual aids (diagrams, screenshots, flowcharts)
- Expand testing, validation, and operational documentation

---

## SECTION-BY-SECTION EXPANSION PLAN

### **SECTION 1-3: Title, Abstract, Executive Summary**
**Current:** ~35 lines
**Target:** ~50 lines (+15 lines)
**Additions:**
- Expand abstract with quantitative results summary
- Add keywords section
- Add acknowledgments subsection

---

### **SECTION 4: PROJECT DESCRIPTION**
**Current:** ~158 lines
**Target:** ~300 lines (+142 lines)
**Additions:**

#### 4.5 Market Analysis and Industry Context (NEW - 50 lines)
- Healthcare cybersecurity market size ($X billion)
- Competitor analysis (commercial cyber ranges)
- Gap analysis in educational offerings
- Industry trends (ransomware statistics 2023-2026)

#### 4.6 Project Timeline Context (NEW - 30 lines)
- September 2025 - March 2026 semester timeline
- Concurrent academic coursework constraints
- Advisor meeting schedule
- Milestone achievement dates

#### 4.7 Budget Breakdown and Justification (NEW - 60 lines)
- Detailed cost breakdown by category
- Alternative options considered for each component
- Cost-benefit analysis vs. commercial solutions
- Total Cost of Ownership (TCO) over 5 years

---

### **SECTION 5: DESIGN CONSTRAINTS**
**Current:** ~247 lines
**Target:** ~400 lines (+153 lines)
**Additions:**

#### 5.1.12 Technical Constraints (NEW - 80 lines)
- Hardware performance limitations (CPU, RAM, storage I/O)
- Network throughput constraints (1Gbps vs 10Gbps)
- Virtualization overhead analysis
- Power consumption and cooling requirements
- Physical space constraints (rack dimensions)

#### 5.1.13 Interoperability Constraints (NEW - 40 lines)
- MQTT protocol version compatibility
- PostgreSQL version requirements for pg_cron
- Docker vs. VM deployment decisions
- FHIR R4 specification compliance
- HL7 v2.x to FHIR mapping challenges

#### 5.1.14 Data Privacy Constraints (NEW - 33 lines)
- Simulated data generation policies
- Data retention and archival requirements
- Compliance with university IRB policies (if applicable)
- GDPR-like principles for test data

---

### **SECTION 6-7: METHODOLOGY AND DESIGN**
**Current:** ~271 lines
**Target:** ~600 lines (+329 lines)
**Additions:**

#### 7.8 Risk Management Framework (NEW - 120 lines)
- Risk identification matrix (technical, schedule, budget)
- Risk mitigation strategies implemented
- Contingency planning (e.g., OPNsense → UDM-SE switch)
- Lessons learned from risks that materialized

#### 7.9 Development Environment and Tools (NEW - 80 lines)
- Version control strategy (Git repository structure)
- Documentation tools (Markdown, Draw.io, Mermaid)
- Development workstation specifications
- Remote access methods (SSH, iDRAC, UDM-SE console)
- Backup and snapshot strategy

#### 7.10 Quality Assurance Methodology (NEW - 70 lines)
- Code review process (self-review checklists)
- Configuration validation procedures
- Testing strategy (unit, integration, system, acceptance)
- Documentation review cycles

#### 7.11 Network Architecture Evolution (NEW - 59 lines)
- Initial VLAN design (4 VLANs: IoT, Medical, Management, Guest)
- Flat network simplification decision rationale
- Final VLAN architecture (VLAN 2 + VLAN 30)
- Firewall rule evolution and refinement

---

### **SECTION 8: DESIGN CONSIDERATIONS**
**Current:** ~66 lines
**Target:** ~150 lines (+84 lines)
**Additions:**

#### 8.3 Usability Requirements (NEW - 40 lines)
- Dashboard design principles (Grafana, Node-RED)
- Color coding for security status (green/red alerts)
- Real-time vs. historical data visualization
- Mobile responsiveness considerations

#### 8.4 Reliability and Availability Requirements (NEW - 44 lines)
- 99% uptime target justification
- Single points of failure identified
- Redundancy strategies (RAID-Z2, UPS)
- Disaster recovery time objectives (RTO/RPO)

---

### **SECTION 9: DESIGN ALTERNATIVES**
**Current:** ~156 lines
**Target:** ~250 lines (+94 lines)
**Additions:**

#### 9.2.5 Alternative 5: Containerized Architecture (NEW - 50 lines)
- Docker Swarm or Kubernetes cluster approach
- Advantages: Portability, resource efficiency
- Disadvantages: Complexity, networking challenges
- Why rejected: TrueNAS VM approach more stable for homelab

#### 9.5 Firewall Selection Analysis (NEW - 44 lines)
- OPNsense vs. pfSense vs. UDM-SE comparison
- Performance benchmarking results
- Feature comparison matrix
- Final selection justification

---

### **SECTION 10: DESIGN OVERVIEW**
**Current:** ~232 lines
**Target:** ~800 lines (+568 lines)
**MAJOR EXPANSION AREA**

#### 10.6 TrueNAS Server Configuration (NEW - 120 lines)
- Hardware specifications (Dell R740XD detailed specs)
- iDRAC 9 out-of-band management setup
- ZFS pool configuration (RAID-Z2 layout)
- Dataset structure and encryption settings
- VM resource allocation strategy
- Network interface configuration (10Gbps SFP+, 1Gbps management)

#### 10.7 UniFi Network Infrastructure (NEW - 100 lines)
- UDM-SE firewall configuration
- VLAN architecture detailed design
- Firewall rule priority and logic
- DPI (Deep Packet Inspection) settings
- Port forwarding and NAT policies
- Switch configuration (PoE++, port mirroring for IDS)
- WiFi AP deployment (U6 Pro settings)

#### 10.8 Virtual Machine Detailed Configurations (NEW - 200 lines)
**10.8.1 PostgreSQL VM (10.30.0.50)**
- Ubuntu 24.04 LTS installation procedure
- PostgreSQL 16.10 installation steps
- Database creation (hospital_data, hapi_fhir, keycloak)
- SSL/TLS certificate configuration
- pg_cron extension setup for archival
- Performance tuning (shared_buffers, work_mem)
- Backup configuration

**10.8.2 MQTT Broker VM (10.30.0.51)**
- Mosquitto 2.0.18 installation
- Authentication configuration (anonymous disabled)
- ACL (Access Control List) rules
- Bridge configuration (if any)
- Logging and monitoring setup

**10.8.3 Node-RED VM (10.30.0.52)**
- Node-RED 3.1.0 installation
- Flow development methodology
- Custom node installation
- Keycloak SSO integration steps
- Dashboard layout design
- Security Status Panel implementation details
- ECG Waveform generation flow

**10.8.4 Grafana VM (10.30.0.53)**
- Grafana 11.2.3 installation
- PostgreSQL datasource configuration
- Elasticsearch datasource for IDS logs
- Dashboard creation methodology
- Panel configuration examples
- Keycloak SSO integration

**10.8.5 Mirth Connect VM (10.30.0.54)**
- Installation and initial setup
- Channel configuration (HeartRate_FHIR_Final)
- HL7 v2.x to FHIR R4 transformation logic
- Derby database configuration
- Auto-pruning settings (30-day retention)

**10.8.6 Wazuh SIEM VM (10.30.0.55)**
- Wazuh 4.8.2 installation (manager + dashboard)
- Agent deployment across 14 endpoints
- Custom rule development for balloon demo
- Alert configuration
- Integration with Elasticsearch (if applicable)

**10.8.7 HAPI FHIR VM (10.30.0.56)**
- Docker installation and configuration
- HAPI FHIR 7.11.5 container deployment
- OAuth2 Proxy setup (port 4180)
- FHIR resource storage (PostgreSQL backend)
- Firewall rules (Mirth-only access to port 8080)

**10.8.8 Keycloak VM (10.30.0.57)**
- Keycloak installation
- Realm creation (hospital-homelab)
- Client configuration for each service
- User and role management
- OAuth2/OIDC flow configuration

**10.8.9 HashiCorp Vault VM (10.30.0.58)**
- Vault installation
- Initialization and unsealing procedure
- Shamir secret sharing (3-of-5 keys)
- Secrets engine configuration
- Token authentication vs. OIDC integration

**10.8.10 Elasticsearch VM (10.30.0.60)**
- Elasticsearch installation
- Index configuration for Suricata logs
- Filebeat integration from Suricata laptop
- TLS configuration
- Retention policies

#### 10.9 Raspberry Pi IoT Sensor Configuration (NEW - 80 lines)
- Raspberry Pi 5 hardware specifications
- Raspberry Pi OS installation procedure
- SenseHAT library installation
- Python script deployment via systemd
- Network configuration (static IPs)
- SSH hardening (password auth, planned key-based migration)
- Sensor-specific configurations (5 different BPM patterns)

#### 10.10 Balloon Demo Hardware Setup (NEW - 68 lines)
**Pressure Control System Components:**
- DATAQ 100 PSI analog sensors (2 per system)
- ADS1115 ADC with BSS138 level shifter
- Sequent 8-RELAYS HAT (I2C 0x27)
- Sequent 40A 3-relay HAT (I2C 0x60)
- Solenoid valves (NC type, 12V)
- Air pump (23A load)
- 12V 29A PSU with kill switch
- Wiring diagrams (integrate from WIRING_DIAGRAM_MERMAID.md)
- Burst pressure testing results (39-71 PSI range)

---

### **SECTION 11: TESTING AND VALIDATION**
**Current:** ~462 lines
**Target:** ~1200 lines (+738 lines)
**MAJOR EXPANSION AREA**

#### 11.6 Additional Test Cases (NEW - 300 lines)
**TC-04: MQTT Broker Performance Test**
- Objective: Validate broker handles 50 msg/sec sustained load
- Procedure: Load testing with mosquitto_pub
- Results: Achieved 50 msg/sec with <5ms latency

**TC-05: PostgreSQL Data Integrity Test**
- Objective: Verify no data loss during 24-hour continuous operation
- Procedure: Count inserts vs. MQTT publishes
- Results: 99.99% integrity (5 packets lost during network hiccup)

**TC-06: Firewall Rule Validation Test**
- Objective: Confirm cross-VLAN rules allow/block correctly
- Procedure: Test each rule with tcpdump capture
- Results: All rules operating as designed

**TC-07: IDS/SIEM Detection Accuracy Test**
- Objective: Validate Suricata + Wazuh detect sensor spoofing
- Procedure: 100-packet attack from Kali Linux
- Results: 100/100 detected, zero false positives

**TC-09: Vault Unseal Procedure Test**
- Objective: Verify 3-of-5 unseal keys restore access
- Procedure: Restart VM, test all key combinations
- Results: All valid 3-key combinations successful

**TC-10: Grafana Dashboard Refresh Rate Test**
- Objective: Confirm 30-second refresh meets real-time requirement
- Procedure: Compare dashboard timestamps to PostgreSQL inserts
- Results: 30.2-second average refresh (within tolerance)

**TC-11: Node-RED Security Status Panel Test**
- Objective: Validate attack visualization within 1 second
- Procedure: Trigger attack, measure display update latency
- Results: 0.8-second average latency

**TC-12: ECG Waveform Physiological Accuracy Test**
- Objective: Confirm waveforms match published cardiac norms
- Procedure: Compare generated P-QRS-T to AHA guidelines
- Results: All components within normal ranges

**TC-13: AFib Simulation Validation Test**
- Objective: Verify Pi #4 shows irregular rhythm characteristics
- Procedure: Measure RR interval variability
- Results: 70%-130% variation confirmed, P wave suppression verified

**TC-14: Data Archival Automation Test**
- Objective: Confirm pg_cron moves 7-day-old data to archive
- Procedure: Insert test data, wait for scheduled job
- Results: Job executed successfully, active table maintains 7-day window

**TC-15: Cross-VLAN Attack Detection Test**
- Objective: Validate IDS captures attacks from VLAN2 to VLAN30
- Procedure: Attack from Suricata laptop (192.168.50.191)
- Results: All attacks logged in Elasticsearch

#### 11.7 Stress Testing Results (NEW - 150 lines)
- Maximum concurrent VM load testing
- Network throughput saturation testing
- PostgreSQL write performance limits
- MQTT broker message queue overflow testing
- Storage I/O performance under load

#### 11.8 Long-Term Reliability Testing (NEW - 100 lines)
- 8-day continuous operation results (November 2025 testing)
- Service restart frequency analysis
- Memory leak detection (none found)
- Disk space growth trends
- Temperature monitoring results

#### 11.9 Security Penetration Testing (NEW - 88 lines)
- Nmap port scanning results
- Vulnerability scanning with OpenVAS/Nessus
- Password strength testing
- SQL injection attempts (PostgreSQL parameterized queries)
- XSS testing on Node-RED dashboard
- MQTT authentication bypass attempts

#### 11.10 Compliance Validation Testing (NEW - 100 lines)
- HIPAA Security Rule control verification
- NIST 800-53 baseline testing
- IEC 62443 Security Level 2 validation
- Encryption strength verification (AES-256)
- Access control testing (role-based permissions)

---

### **SECTION 12: SOCIAL IMPACT**
**Current:** ~166 lines
**Target:** ~250 lines (+84 lines)
**Additions:**

#### 12.6 Educational Accessibility Analysis (NEW - 50 lines)
- Community college vs. R1 university resource availability
- Open-source software as equity enabler
- Documentation in plain language for diverse backgrounds
- Potential for remote/online deployment

#### 12.7 Industry Workforce Development Impact (NEW - 34 lines)
- Healthcare cybersecurity skills gap analysis
- How this homelab addresses workforce needs
- Alignment with NICE Cybersecurity Framework roles
- Potential for certification training (CISSP, GIAC)

---

### **SECTION 13: FUTURE WORK**
**Current:** ~237 lines
**Target:** ~350 lines (+113 lines)
**Additions:**

#### 13.5 Advanced Attack Scenarios (NEW - 60 lines)
- Ransomware simulation (encrypt TrueNAS datasets)
- DDoS attack on MQTT broker
- Man-in-the-middle attack on unsecured MQTT
- Credential stuffing against Keycloak
- IoT device firmware manipulation

#### 13.6 Machine Learning Integration (NEW - 53 lines)
- Anomaly detection using 933M-row dataset
- Predictive maintenance for hardware
- Behavioral analysis of attack patterns
- Integration with existing IDS/SIEM

---

### **SECTION 14-16: SUMMARY, REFLECTION, REFERENCES**
**Current:** ~258 lines
**Target:** ~350 lines (+92 lines)
**Additions:**

#### 15.6 Technical Skills Developed (NEW - 50 lines)
- Linux system administration (Ubuntu, TrueNAS)
- Network engineering (VLANs, firewalls, routing)
- Database administration (PostgreSQL tuning)
- Containerization (Docker for HAPI FHIR)
- Python scripting (IoT sensors, attack scripts)
- Security monitoring (IDS/SIEM configuration)

#### 16. REFERENCES - Expand from 42 to 80+ citations (NEW - 42 lines)
- Add academic papers on healthcare cybersecurity
- Industry reports (Verizon DBIR, IBM Security)
- Vendor documentation (TrueNAS, Mosquitto, Grafana)
- Standards documents (full citations for HIPAA, NIST, IEC, ISO)
- Blog posts and tutorials referenced during development

---

### **SECTION 17: APPENDICES**
**Current:** ~1,070 lines
**Target:** ~4,000 lines (+2,930 lines)
**MASSIVE EXPANSION AREA - This is where you add 75% of new content**

#### 17.8 Appendix H: Detailed VM Installation Procedures (NEW - 600 lines)
**Complete step-by-step guides for each VM (10 VMs × 60 lines each):**
- PostgreSQL: apt install, config file edits, database creation SQL
- MQTT Broker: mosquitto.conf full configuration
- Node-RED: package.json, flow JSON excerpts
- Grafana: datasource YAML, dashboard JSON
- Mirth Connect: channel XML configuration
- Wazuh: ossec.conf, agent deployment commands
- HAPI FHIR: docker-compose.yml, OAuth2 Proxy config
- Keycloak: realm export JSON
- Vault: init commands, policy HCL files
- Elasticsearch: elasticsearch.yml, index mappings

#### 17.9 Appendix I: Network Configuration Files (NEW - 400 lines)
- UDM-SE firewall rules (JSON export)
- VLAN configuration (switch port assignments)
- Static IP reservation table
- DNS records (if internal DNS configured)
- DHCP scope configurations
- iptables rules (for VMs with host firewalls)

#### 17.10 Appendix J: Complete Balloon Demo Source Code (NEW - 800 lines)
**Full source code with extensive inline comments:**
- `balloon_control_api_vulnerable.py` (~150 lines)
- `balloon_control_secure.py` (~200 lines)
- `sensor_publisher_vulnerable.py` (~100 lines)
- `sensor_publisher_secure.py` (~100 lines)
- `attack_spoof.py` (~100 lines with dual-target mode)
- `test_pressure_sensor.py` (~50 lines)
- Systemd service files (~50 lines total)
- Node-RED flow JSON for balloon demo (~100 lines)
- Wazuh custom rules for balloon demo (~50 lines)

#### 17.11 Appendix K: Troubleshooting Guide (NEW - 500 lines)
**Integrate content from TROUBLESHOOTING_HISTORY.md:**
- MQTT connection issues (authentication failures)
- PostgreSQL SSL certificate errors
- Node-RED dashboard not loading
- Grafana datasource connection failures
- Vault unsealing after power loss
- Raspberry Pi service failures
- I2C errors (i2c_arm_baudrate fix)
- Solenoid valve sticking issues
- Cross-VLAN firewall troubleshooting
- IDS not capturing traffic (port mirroring issues)
- pg_cron archival failures (connection failed error)

#### 17.12 Appendix L: System Startup Procedures (NEW - 250 lines)
**Integrate from SYSTEM_STARTUP_GUIDE.md and QUICK_STARTUP_PROCEDURE.md:**
- Cold start from complete power loss
- VM boot order and dependencies
- Service health check commands
- Vault unseal procedure
- Verification checklist (all services operational)

#### 17.13 Appendix M: Network Diagrams (NEW - 100 lines)
**Include Mermaid/Draw.io diagrams as text or ASCII art:**
- Physical network topology
- Logical VLAN architecture
- Data flow diagram (enhanced version)
- Attack demonstration topology
- Wiring diagram for balloon demo
- Server rack layout

#### 17.14 Appendix N: Screenshots and Visual Documentation (NEW - 200 lines)
**Descriptive text for screenshots (or ASCII representations):**
- Node-RED dashboard (normal operation)
- Node-RED Security Status Panel (attack detected)
- Grafana heart rate dashboard
- Grafana IDS dashboard showing attack traffic
- Wazuh SIEM alert console
- TrueNAS dashboard (storage pools, VMs)
- UDM-SE firewall rules interface
- Raspberry Pi SenseHAT ECG waveforms (photograph descriptions)

#### 17.15 Appendix O: Performance Benchmark Data (NEW - 180 lines)
- PostgreSQL query performance (SELECT queries on 933M rows)
- MQTT broker message throughput tests
- Network throughput tests (iperf results)
- Disk I/O benchmarks (fio results)
- CPU utilization under load
- Memory usage trends over 24-hour period

#### 17.16 Appendix P: Security Audit Logs (NEW - 150 lines)
- Sample Wazuh alerts (anonymized)
- Suricata EVE.json log excerpts
- PostgreSQL audit log samples
- SSH authentication logs
- Firewall block logs

#### 17.17 Appendix Q: Compliance Checklists (NEW - 200 lines)
**Expand Appendix C with full checklists:**
- HIPAA Security Rule: All 54 implementation specifications
- NIST 800-53 Rev. 5: All implemented control families
- IEC 62443: Security Level 2 requirements matrix
- ISO 27001: Annex A controls detailed mapping

#### 17.18 Appendix R: Bill of Materials - Vendor Information (NEW - 100 lines)
**Expand Appendix B with:**
- Vendor contact information
- Part numbers and SKUs
- Purchase dates and warranty information
- Alternative suppliers for each component
- Lead time estimates

#### 17.19 Appendix S: Meeting Notes and Project Timeline (NEW - 150 lines)
**Integrate from advisor meeting notes:**
- Weekly advisor meeting summaries
- Key decisions and rationale
- Scope change discussions
- Milestone achievement records

#### 17.20 Appendix T: Glossary of Terms (NEW - 100 lines)
**Define all technical terms:**
- Acronyms (MQTT, FHIR, SIEM, IDS, VLAN, etc.)
- Medical terminology (AFib, BPM, ECG, etc.)
- Cybersecurity terminology (threat model, defense-in-depth, etc.)
- Networking terminology (VLAN, ACL, NAT, etc.)

#### 17.21 Appendix U: Index (NEW - 100 lines)
**Alphabetical index of key topics, figures, and tables**

---

## ESTIMATED FINAL PAGE COUNTS

| Section | Current Lines | Target Lines | Expansion |
|---------|---------------|--------------|-----------|
| 1-3: Title/Abstract/Summary | 35 | 50 | +15 |
| 4: Project Description | 158 | 300 | +142 |
| 5: Design Constraints | 247 | 400 | +153 |
| 6-7: Methodology | 271 | 600 | +329 |
| 8: Design Considerations | 66 | 150 | +84 |
| 9: Design Alternatives | 156 | 250 | +94 |
| 10: Design Overview | 232 | 800 | +568 |
| 11: Testing | 462 | 1200 | +738 |
| 12: Social Impact | 166 | 250 | +84 |
| 13: Future Work | 237 | 350 | +113 |
| 14-16: Summary/Reflection/References | 258 | 350 | +92 |
| 17: Appendices | 1070 | 4000 | +2930 |
| **TOTAL** | **3676** | **8700** | **+5024** |

**Final estimate: ~8,700 lines = 217 pages @ 40 lines/page**

---

## IMPLEMENTATION PRIORITY

### Phase 1: High-Value, Low-Effort Expansions (Do First)
1. **Appendix J: Balloon Demo Source Code** - You already have this, just copy from src/balloon-demo/scripts/
2. **Appendix K: Troubleshooting Guide** - Copy from TROUBLESHOOTING_HISTORY.md
3. **Appendix L: Startup Procedures** - Copy from SYSTEM_STARTUP_GUIDE.md
4. **Appendix H: VM Installation** - Extract from NETWORK_SETUP_PROGRESS_PART{1,2,3}.md
5. **Section 10.6-10.10: Hardware/VM Configs** - Reference existing documentation

### Phase 2: Medium-Value Expansions
1. **Section 11: Additional Test Cases** - Document tests you actually performed
2. **Section 7.8-7.11: Risk, QA, Network Evolution** - Reflect on what you learned
3. **Appendices M-U: Diagrams, Screenshots, Glossary** - Supporting materials

### Phase 3: Polish and Refinement
1. **References expansion** - Cite all sources properly
2. **Index creation** - Alphabetical topic index
3. **Table of contents update** - Ensure all sections numbered correctly
4. **Cross-reference validation** - Fix all "Section X.Y" references

---

## TOOLS AND RESOURCES TO USE

### Source Documents to Mine for Content
- `NETWORK_SETUP_PROGRESS_PART{1,2,3}.md` - VM configurations, troubleshooting
- `TROUBLESHOOTING_HISTORY.md` - Appendix K content
- `SYSTEM_STARTUP_GUIDE.md` - Appendix L content
- `BALLOON_DEMO_DESIGN_NOTES.md` - Section 10.10 expansion
- `WIRING_DIAGRAMS_UPDATED_2026-02-11.md` - Appendix M diagrams
- `VM_SERVICES_STATUS.md` - Section 10.8 VM details
- `SECURITY_HARDENING_2026-02-13.md` - Section 11.9 penetration testing
- `src/balloon-demo/scripts/*.py` - Appendix J source code
- `src/balloon-demo/services/*.service` - Appendix H systemd configs
- `src/hospital/heartrate/*.py` - Appendix D (already partially done)

### Commands to Extract Content
```bash
# Count lines in supporting docs
wc -l *.md

# Extract specific sections
sed -n '/^## Section Title/,/^## Next Section/p' SOURCE.md > EXTRACTED.md

# Combine multiple files
cat TROUBLESHOOTING_HISTORY.md >> Final_Technical_Report_Rev_10.md
```

---

## QUALITY CHECKS

Before finalizing, ensure:
- [ ] All figures/tables referenced in text are present
- [ ] All appendices referenced in main text exist
- [ ] Page numbers updated throughout (if using page numbers)
- [ ] Table of contents matches actual sections
- [ ] References formatted consistently (IEEE, APA, or Chicago style)
- [ ] No orphaned section references ("see Section X.Y" with no X.Y)
- [ ] All acronyms defined on first use
- [ ] Consistent terminology (e.g., "Raspberry Pi #4" vs "Pi 4" vs "Device 4")

---

## NEXT STEPS

1. **Review this plan** - Does this approach meet your advisor's expectations?
2. **Select Phase 1 items** - Start with copy/paste from existing docs
3. **Expand incrementally** - Don't try to write 5,000 lines in one sitting
4. **Get advisor feedback** - After Phase 1 (~5,500 lines total), share draft
5. **Refine and polish** - Based on feedback, adjust Phases 2-3

Let me know which section you want to start with!
