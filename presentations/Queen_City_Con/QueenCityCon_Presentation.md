> **SUPERSEDED (2026-11-06).** The talk is now `When the Sensor Lies.pptx` (14 slides) in this folder. This is an older draft; don't present from it. Known errors here: the secure threshold is **10.0 PSI**, not 1.0. The 70 PSI relief valve does **not** keep the bottle from bursting (average burst is 59.6 PSI). The Slide 20 offer to let attendees SSH into the live system should not be made. Venue procedures are in `CON_FIELD_GUIDE.md`.

# IoT Security in Healthcare: Bridging IT, OT, and Medical Device Networks

**Presenter:** David Moaddel Ghahfarokhi
**Advisor:** Rob Kuschel, CTH / GE Aerospace
**Institution:** University of Cincinnati, Computer Engineering
**Conference:** Queen City Con 0x4 (November 13-15, 2026)

---

## Slide 1: Title Slide

**IoT Security in Healthcare: Bridging IT, OT, and Medical Device Networks**

*A Live Demonstration of Attack Detection and Defense in Hospital IoT Systems*

University of Cincinnati Senior Capstone Project

---

## Slide 2: The Problem - Healthcare Under Attack

**Healthcare is the #1 Target for Cyberattacks**

- **670+ healthcare data breaches in 2023** (OCR reports)
- **Average cost: $10.93M per breach** (IBM 2023 Cost of Data Breach Report)
- **Medical devices = blind spots** in traditional IT security

**Real-World Incidents:**
- 2017: WannaCry ransomware crippled NHS hospitals, canceled 19,000 appointments
- 2020: Universal Health Services hit by Ryuk ransomware, $67M impact
- 2021: Scripps Health breach exposed 150,000 patient records via IoT device

**The Gap:** Medical IoT devices operate in a gray area between IT and OT networks

---

## Slide 3: IoT vs IT vs OT - What's the Difference?

### **IT (Information Technology)**
- **Focus:** Data processing, storage, communication
- **Examples:** Servers, workstations, databases, email systems
- **Security Priority:** Confidentiality, Integrity, Availability (CIA Triad)
- **Patch Cycle:** Frequent (monthly security updates)
- **Downtime Tolerance:** Moderate (scheduled maintenance windows)

### **OT (Operational Technology)**
- **Focus:** Physical process control, industrial operations
- **Examples:** SCADA systems, PLCs, building automation, power grids
- **Security Priority:** Safety, Availability, Integrity (inverted CIA)
- **Patch Cycle:** Rare (annual or only during planned outages)
- **Downtime Tolerance:** Very low (24/7 critical operations)

### **IoT (Internet of Things)**
- **Focus:** Sensor data collection, real-time monitoring, automation
- **Examples:** Medical monitors, smart thermostats, industrial sensors
- **Security Priority:** Varies by context (blurs IT and OT boundaries)
- **Patch Cycle:** Inconsistent (vendor-dependent, often neglected)
- **Downtime Tolerance:** Context-dependent (medical = critical, smart bulb = low)

---

## Slide 4: The Convergence Problem

**Why Healthcare IoT is Uniquely Vulnerable**

Traditional IT Security Controls Don't Fit:
- Medical devices can't be patched without FDA re-certification
- Antivirus/EDR breaks medical device warranties
- Network segmentation often bypassed for "clinical workflows"
- Devices run outdated OS (Windows XP, embedded Linux 2.6)

Traditional OT Security Controls Don't Fit:
- Medical devices aren't safety-critical like power plants (different risk model)
- Clinical staff need faster access than industrial operators
- PHI (Protected Health Information) adds regulatory complexity
- Medical devices have shorter lifecycles than SCADA (5-10 years vs 20-30 years)

**Result:** Medical IoT falls into a security gap - too critical to patch aggressively, too networked to isolate completely.

---

## Slide 5: Project Goals

**Objective:** Design and demonstrate a realistic hospital IoT security architecture

**Key Requirements:**
1. **Operational hospital pipeline** - Real patient vital monitoring (5 simulated patients)
2. **Attack demonstration** - Vulnerable vs. hardened IoT system comparison
3. **Detection and response** - SIEM, IDS, real-time alerting
4. **Standards compliance** - FHIR (Fast Healthcare Interoperability Resources)
5. **Physical demonstration** - Visible consequences of successful attacks

**Scope:**
- 14 networked devices (5 heart rate monitors, 2 pressure control systems, 7 infrastructure VMs)
- 2 VLANs (secure hospital network vs. vulnerable attack lab)
- Full data pipeline: Sensors → MQTT → Node-RED → PostgreSQL → FHIR → Grafana
- Intrusion detection: Suricata IDS → Elasticsearch → Grafana dashboards
- Security monitoring: Wazuh SIEM with 14 agents

---

## Slide 6: Architecture Overview - Hospital Network

**Hospital Homelab Infrastructure (VLAN 30 - Secure)**

**Physical Layer:**
- 5x Raspberry Pi 5 with Sense HAT (accelerometer-based heart rate simulation)
- TrueNAS server (Dell PowerEdge) hosting 7 VMs
- UniFi Switch Pro Max 24 PoE (network segmentation)
- UDM-SE Gateway (firewall, cross-VLAN routing)

**Data Pipeline:**
```
[Raspberry Pi Sense HAT]
    ↓ (MQTT - paho-mqtt v2.1.0)
[MQTT Broker - Mosquitto] (10.30.0.51, authenticated)
    ↓
[Node-RED] (10.30.0.52, Keycloak SSO)
    ↓ (100 inserts/sec)
[PostgreSQL 16] (10.30.0.50, 933M rows, 180GB database)
    ↓ (rate-limited 1/sec)
[Mirth Connect] (10.30.0.54, HL7/FHIR converter)
    ↓
[HAPI FHIR Server] (10.30.0.56, LOINC 8867-4 Observations)
```

**Monitoring Stack:**
- Grafana dashboards (real-time ECG waveforms, 30s historical refresh)
- Wazuh SIEM (14 agents, centralized logging)
- HashiCorp Vault (secrets management)
- Keycloak (SSO for clinical users)

---

## Slide 7: Architecture Overview - Attack Demo Network

**Balloon Demo Infrastructure (VLAN 2 - Vulnerable vs. VLAN 30 - Secure)**

**Physical System:**
- 2x Raspberry Pi 5 with custom sensor/relay HATs
- DATAQ 100 PSI analog pressure sensors (via ADS1115 ADC + BSS138 level shifter)
- Sequent 8-RELAYS HAT (solenoids: inflate, vent, relief)
- Sequent 40A 3-relay HAT (23A air pump)
- 1L plastic pressure vessel (burst pressure: 39-71 PSI, mean 59.6 PSI)

**Two Parallel Systems:**

**Vulnerable Pi (192.168.50.100 - VLAN 2):**
- Flask API on port 5000 (NO auth, NO validation, NO rate limiting)
- `sensor_publisher.py` reads sensors, POSTs to `/sensor` endpoint
- Control loop uses network data **blindly** (no cross-check with I2C sensors)
- Target pressure: 25 PSI
- **Attack vector:** Spoofed pressure readings accepted without validation

**Secure Pi (10.30.0.25 - VLAN 30):**
- Reads sensors directly via I2C (no network exposure for control decisions)
- Input validation (network data cross-checked against I2C sensors)
- Rate-of-change anomaly detection (5 PSI/sec threshold)
- Wazuh SIEM integration (forensic logging of all rejections)
- Target pressure: 25 PSI
- **Defense:** Rejects spoofed data, uses I2C fallback

---

## Slide 8: Attack Methodology

**Simulated Threat Actor: Insider with Network Access**

**Attack Tool:** `attack_spoof.py --dual --pressure 0.0 --rate 0.1`

**Attack Flow:**
1. Attacker runs script from compromised device on VLAN 2 (Suricata laptop 192.168.50.191)
2. Script sends spoofed HTTP POST requests to BOTH systems at 10 Hz each:
   - **Target 1:** Vulnerable Pi (192.168.50.100) `/sensor` endpoint
   - **Target 2:** Secure Pi (10.30.0.25) `/sensor` endpoint
3. Spoofed payload: `{"pressure": 0.0, "upstream": 0.0}`

**Vulnerable System Response:**
- Accepts `0.0 PSI` reading
- Control loop believes pressure is empty
- Pump continues running
- **Real pressure exceeds safe limits** (>35 PSI)
- Bottle bursts at ~60 PSI (demonstrated in testing)

**Secure System Response:**
- Compares network value (0.0 PSI) vs. I2C sensor (25.0 PSI)
- Detects mismatch: `|0.0 - 25.0| = 25 > 1.0 threshold`
- **Rejects spoofed data**
- Falls back to I2C sensor for control decisions
- Pump stays off, bottle remains at safe 25 PSI
- Logs attack to Wazuh SIEM with full forensic details

---

## Slide 9: Detection Capabilities

**Multi-Layer Defense and Monitoring**

**Layer 1: Network IDS (Suricata)**
- Bare-metal laptop on VLAN 2 (192.168.50.191)
- Monitors mirrored traffic from Switch Port 15 (Vulnerable Pi uplink)
- EVE JSON logs shipped to Elasticsearch via Filebeat
- Grafana IDS dashboard shows:
  - Events over time (line graph)
  - Top source IPs (attacker: 192.168.50.191)
  - Top destination IPs (targets: 192.168.50.100, 10.30.0.25)
  - Network protocols (HTTP POST floods)

**Layer 2: Application-Level Validation (Secure Pi Only)**
- Cross-checks network sensor data vs. I2C sensor data
- Rate-of-change detection (5 PSI/sec threshold)
- Attack counter: `rejected_network_count` vs. `accepted_network_count`

**Layer 3: SIEM (Wazuh)**
- Real-time logging of all validation rejections
- Forensic data: timestamp, claimed value, actual value, mismatch delta
- Alert thresholds configurable (e.g., >10 rejections/minute = critical)

**Layer 4: Visual Monitoring (Node-RED Dashboard)**
- **Security Status Panel** (bottom-right, 6x4 widget):
  - **Normal state:** Green gradient, shield emoji, "SYSTEM SECURE"
  - **Attack state:** Red pulsing glow, blinking alarm, "ATTACK IN PROGRESS"
  - Real-time metrics: blocked attacks, validated packets, pressure, control source

---

## Slide 10: Live Demo - What You'll See

**Demo Flow (10-15 minutes):**

### **Part 1: Baseline - Normal Operations (2 minutes)**
- **Node-RED Dashboard:** http://10.30.0.52:1880/ui
  - 5 ECG waveforms (hospital monitors) scrolling in real-time
  - Pi #4 showing irregular AFib rhythm (red trace)
  - 4 pressure gauges (vulnerable upstream/downstream, secure upstream/downstream)
  - Security Status Panel: GREEN "SYSTEM SECURE"
- **Grafana Hospital Dashboard:** http://10.30.0.53:3000
  - Historical heart rate trends (7 days, 933M database rows)
  - Tachycardia alert firing for Pi #4 (AFib simulation)

### **Part 2: Attack Initiation (1 minute)**
- **Attacker laptop:** Run `python3 attack_spoof.py --dual --pressure 0.0 --rate 0.1`
- **Screen shows:** Real-time attack stats (packets sent, success rate)

### **Part 3: Vulnerable System Compromised (3 minutes)**
- **Node-RED Dashboard:**
  - Vulnerable Pi pressure gauge shows **0.0 PSI** (spoofed)
  - Pump relay indicator: **ON** (continuous inflation)
  - Real upstream sensor climbing: 26...30...35...40...50 PSI
- **Physical observation:**
  - Bottle visibly inflating
  - Pump running continuously
  - **Pressure exceeds safe threshold** (>35 PSI)
  - Relief valve activates at 70 PSI (emergency failsafe)
  - Demonstration: This would burst the bottle at ~60 PSI (pre-tested range: 39-71 PSI)

### **Part 4: Secure System Protected (2 minutes)**
- **Node-RED Dashboard:**
  - Secure Pi pressure gauge shows **25.0 PSI** (I2C sensor, accurate)
  - Security Status Panel: **RED** "ATTACK IN PROGRESS"
  - Blocked attacks counter: 143 (and climbing)
  - Validated packets counter: 0 (all rejected)
  - Control source: **I2C fallback** (network data discarded)
  - Pump relay indicator: **OFF** (safe pressure maintained)

### **Part 5: Detection and Forensics (3 minutes)**
- **Grafana IDS Dashboard:** http://10.30.0.53:3000
  - Events Over Time: Sharp spike at attack start
  - Top Source IPs: 192.168.50.191 (attacker)
  - Top Destination IPs: 192.168.50.100 (vulnerable), 10.30.0.25 (secure)
  - Event Types: HTTP POST floods
- **Wazuh SIEM:** https://10.30.0.55
  - Search: `rule.id:100001` (custom sensor validation rule)
  - Shows all 143 rejected packets with forensic details:
    - Timestamp, claimed pressure (0.0), actual pressure (25.0), mismatch delta (25.0)
    - Source IP, validation result ("REJECTED_MISMATCH")

### **Part 6: Attack Stop and Recovery (1 minute)**
- **Stop attack script** (Ctrl+C)
- **Node-RED Dashboard:**
  - Security Status Panel: Returns to GREEN "SYSTEM SECURE" (1-second timeout)
  - Vulnerable system vents to safe pressure (post-attack safety feature)
  - Secure system: No action needed (remained at 25 PSI throughout)

---

## Slide 11: Results - Attack Success vs. Failure

**Vulnerable System (No Validation):**
- **Attack Success Rate:** 100% (all spoofed packets accepted)
- **Peak Pressure Achieved:** 67.97 PSI (documented in testing)
- **Burst Threshold:** Mean 59.6 PSI (range: 39-71 PSI from testing)
- **Outcome:** System compromised, physical damage likely without emergency relief valve

**Secure System (Validated):**
- **Attack Success Rate:** 0% (all spoofed packets rejected)
- **Total Attacks Blocked:** 143 in 14 seconds (10 Hz attack rate)
- **Pressure Deviation:** 0.0 PSI (remained at 25 PSI target)
- **Outcome:** System protected, control loop maintained safe operation via I2C fallback

**Detection Timeline:**
- **IDS Detection:** Immediate (Suricata captured first packet at T+0ms)
- **Application Detection:** Immediate (first validation rejection at T+0ms)
- **SIEM Alert:** <1 second (Wazuh agent ships logs in near-real-time)
- **Visual Dashboard Update:** <100ms (MQTT → Node-RED → browser WebSocket)

---

## Slide 12: Key Takeaways

**1. Defense in Depth is Critical**
- Single-layer security (network firewall alone) is insufficient
- Application-level validation caught attacks that bypassed network controls
- Redundant sensors enable cross-validation (network vs. I2C)

**2. IoT Requires Different Security Patterns**
- Traditional IT approach (patch everything, EDR on every endpoint) doesn't work
- OT approach (air-gap everything) breaks clinical workflows
- **Solution:** Hybrid strategy - validate inputs, monitor anomalies, fail-safe defaults

**3. Visibility = Security**
- Real-time dashboards enabled immediate attack recognition
- SIEM forensics provided incident response data (who, what, when)
- Physical indicators (visual pressure changes) helped non-technical stakeholders understand risk

**4. Standards Matter**
- FHIR enabled interoperability (any EHR could consume our data)
- MQTT provided reliable pub/sub for 17 msg/sec sustained throughput
- PostgreSQL + pg_cron automated data lifecycle (7-day retention, 933M archived rows)

**5. Security Can't Be Bolted On**
- Vulnerable system can't be "fixed" without architectural changes
- Secure system designed with validation from day 1
- Retrofitting security into legacy medical devices is extremely difficult

---

## Slide 13: Real-World Applications

**How This Translates to Production Environments**

**Sensor Validation Pattern (Generalizable):**
- Any IoT device with redundant sensors can cross-validate
- Examples: Dual temperature probes, multiple flow sensors, redundant pressure transducers
- Cost: Minimal (sensors are cheap, physics is free)

**Rate-of-Change Detection:**
- Physical systems have known change rates (temperature, pressure, flow)
- Anomaly: Sensor reports instantaneous change that violates physics
- Example: Room temperature sensor reports 72°F → 150°F in 1 second = spoofed

**Network Segmentation + Selective Exceptions:**
- Default-deny between VLANs (VLAN 2 ↔ VLAN 30 blocked)
- Explicit exceptions for required services (Vulnerable Pi → MQTT broker only)
- Reduces attack surface (attacker can't pivot to entire hospital network)

**Zero-Trust for Medical Devices:**
- Even "trusted" devices must validate inputs
- Assume network is compromised (insider threat, supply chain attack)
- Fail-safe defaults (use I2C fallback if network data is suspect)

**Challenges in Production:**
- Many medical devices are black boxes (no source code access)
- Vendors often prohibit modifications (warranty/regulatory concerns)
- Solution: Deploy validation at network perimeter or gateway devices

---

## Slide 14: Limitations and Future Work

**Current Limitations:**

**Scale:**
- 5 simulated patients vs. 500-bed hospital
- Single-site deployment vs. multi-campus health system
- Lab environment vs. 24/7 clinical operations

**Realism:**
- Simulated heart rate (accelerometer) vs. real patient telemetry
- Pneumatic demo vs. actual medical device (e.g., ventilator, infusion pump)
- Controlled attack vs. APT with persistence and lateral movement

**Regulatory:**
- Not FDA-certified (research prototype only)
- No HIPAA compliance testing (simulated data, no real PHI)
- No clinical validation (proof-of-concept, not patient-ready)

**Future Enhancements:**

**1. Machine Learning Anomaly Detection**
- Baseline normal behavior per patient
- Detect subtle deviations (gradual drift attacks)
- Reduce false positives (current 1.0 PSI threshold is static)

**2. Automated Incident Response**
- SOAR (Security Orchestration, Automation, Response) integration
- Auto-isolate compromised devices (dynamic VLAN assignment)
- Alert clinical engineering team via pager/SMS

**3. Supply Chain Security**
- Firmware signature verification (prevent malicious updates)
- Cryptographic device attestation (prove device identity)
- Secure boot (prevent bootkit/rootkit persistence)

**4. Multi-Site Federation**
- Share threat intelligence across hospitals
- Centralized SOC monitoring 10+ health systems
- Standardized FHIR-based security event reporting

---

## Slide 15: Lessons Learned - Technical

**What Went Right:**

**MQTT as IoT Backbone:**
- Reliable pub/sub handled 17 msg/sec continuous load (6 months uptime)
- Mosquitto authentication prevented unauthorized publishers
- Topic structure enabled granular subscriptions (`balloon/vulnerable/*` vs. `balloon/secure/*`)

**PostgreSQL at Scale:**
- 933M rows, 180 GB database, 100 inserts/sec sustained
- pg_cron automated archival (7-day retention, daily at 2 AM)
- Self-signed SSL worked fine with `sslmode=require, rejectUnauthorized=false`

**Node-RED for Rapid Prototyping:**
- Visual flow editor accelerated development (non-programmers could understand logic)
- Keycloak SSO integration secured dashboard access
- Real-time dashboard via WebSocket (no polling overhead)

**What Went Wrong:**

**Solenoid Valves Sticking:**
- NC (normally closed) solenoids occasionally stuck under pressure
- Root cause: Long 12V wiring runs caused voltage drop, mechanical wear
- Mitigation: Valve exercise routine, triple-send relay commands, depressurize before closing

**Pi Services Didn't Auto-Start Reliably:**
- systemd `network-online.target` + 15s delay still insufficient after cold boot
- MQTT broker took 20-30s to fully initialize
- Solution: Manual restart via SSH (documented in startup guide)

**Wazuh SSO Broke After Config Change:**
- Running `securityadmin.sh` altered OpenSearch SSL cert requirements
- No backup of working configuration, couldn't rollback
- Workaround: Use basic auth (`admin` / complex password)

**Cross-VLAN Routing Required WAN Link:**
- UDM-SE disabled inter-VLAN routing when WAN disconnected
- Broke expo/air-gap demo scenarios
- Solution: Mock WAN setup (plug dummy cable into WAN port)

---

## Slide 16: Lessons Learned - Non-Technical

**Communication is Key:**
- Cybersecurity people don't speak "clinical workflows"
- Clinicians don't speak "defense in depth"
- **Bridge:** Use physical demos (visible pressure changes), real-world analogies (seatbelts = defense in depth)

**Security vs. Usability Trade-offs:**
- Keycloak SSO added friction (login required for Node-RED dashboard)
- Clinicians prioritize patient care over security (understandably)
- **Balance:** SSO for administrative access, read-only public dashboard for clinical staff

**Documentation = Force Multiplier:**
- 50+ markdown files enabled rapid troubleshooting
- `QUICK_STARTUP_PROCEDURE.md` reduced boot time from 90 min (first attempt) to 30 min (verified)
- `TROUBLESHOOTING_HISTORY.md` prevented re-solving same problems

**Physical Demos Matter:**
- Bottle inflation is visceral (non-technical stakeholders understand risk immediately)
- ECG waveforms on dashboard look "medical" (builds credibility)
- Red pulsing "ATTACK IN PROGRESS" panel gets attention (better than syslog entries)

---

## Slide 17: Call to Action - For Defenders

**If You're Securing IoT Systems:**

**1. Inventory Your Shadow IT/OT**
- You can't secure what you don't know exists
- Passive network discovery (Shodan, nmap, NetFlow analysis)
- Asset management database (device type, firmware version, EOL date)

**2. Implement Network Segmentation**
- VLANs are cheap, breaches are expensive
- Default-deny between zones, explicit allow rules only
- Monitor cross-zone traffic (IDS on inter-VLAN routing)

**3. Demand Vendor Security Transparency**
- Ask: Can we validate inputs? Can we monitor traffic? Can we patch without voiding warranty?
- Prefer open protocols (MQTT, FHIR) over proprietary black boxes
- Build contractual requirements for security updates (SLAs for CVE patches)

**4. Test Your Defenses**
- Purple team exercises (attackers + defenders collaborate)
- Tabletop scenarios (what if ventilator is compromised?)
- Red team your own IoT (this project = self-red-teaming)

**5. Plan for Failure**
- Security controls will fail eventually (assume breach mindset)
- Fail-safe defaults (I2C fallback, emergency relief valves)
- Incident response runbooks (who to call, how to isolate, how to restore)

---

## Slide 18: Call to Action - For Researchers

**Open Problems Worth Solving:**

**1. Retrofitting Security into Legacy Devices**
- 80% of hospital medical devices run unsupported OS
- Can't patch, can't replace (too expensive, FDA certification takes years)
- **Need:** Non-invasive security overlays (bump-in-the-wire validation, ML anomaly detection)

**2. Standardized Security Event Formats**
- Every vendor has proprietary syslog format
- SIEM correlation rules break across device types
- **Need:** FHIR-like standard for security events (STIX/TAXII is close but not IoT-specific)

**3. Physics-Based Anomaly Detection**
- Current ML models need months of training data
- Medical devices have known physical constraints (temp change rates, pressure limits)
- **Need:** Hybrid models (physics + ML) for faster deployment

**4. Privacy-Preserving Threat Intelligence Sharing**
- Hospitals reluctant to share breach data (HIPAA, reputation risk)
- Limits collective defense (can't learn from others' incidents)
- **Need:** Federated learning, differential privacy for medical IoT telemetry

**5. Secure-By-Default IoT Frameworks**
- Developers shouldn't have to be security experts
- Need libraries/SDKs with validation, rate limiting, auth built-in
- **Example:** "Express.js for IoT" with security guardrails

---

## Slide 19: Acknowledgments

**Advisor:**
- Rob Kuschel, CTH / GE Aerospace - Project guidance and real-world OT security insights

**University of Cincinnati:**
- Computer Engineering Department - Capstone program structure and resources

**Open Source Community:**
- Mosquitto MQTT, Node-RED, Grafana, PostgreSQL, Suricata, Wazuh, Elasticsearch
- Without open-source tools, this project would have been impossible on student budget

**Documentation References:**
- NIST Cybersecurity Framework (healthcare profile)
- MITRE ATT&CK for ICS (attack methodology)
- HL7 FHIR specification (interoperability standards)

---

## Slide 20: Questions & Contact

**Thank you for attending!**

**Questions?**

**Contact Information:**
- Email: [Your Email]
- GitHub: [Your GitHub - if you plan to open-source this]
- LinkedIn: [Your LinkedIn]

**Project Documentation:**
- Full technical report, architecture diagrams, and code available on request
- 50+ markdown files covering every aspect of design, deployment, and troubleshooting

**Demo Hardware:**
- Available for hands-on exploration after session (if time permits)
- Feel free to SSH into the live system and explore (credentials provided on request)

**Follow-Up:**
- Interested in collaborating on medical IoT security research?
- Want to deploy similar architecture at your organization?
- Let's connect!

---

## APPENDIX: Demo Script (For Presenter Reference)

**Pre-Demo Checklist (30 minutes before session):**
- [ ] Boot TrueNAS, UDM-SE, Switch (Step 1)
- [ ] Wait 15 min for VMs (Step 2)
- [ ] Unseal Vault (Step 3)
- [ ] Restart Pi services (Step 4)
- [ ] Verify Node-RED dashboard shows live data
- [ ] Verify Grafana hospital dashboard loads
- [ ] Verify Grafana IDS dashboard loads
- [ ] Verify Wazuh SIEM login works (basic auth)
- [ ] Test attack script runs: `python3 attack_spoof.py --dual --pressure 0.0 --rate 0.1` (run for 5 sec, then stop)
- [ ] Connect laptop HDMI to projector, test display
- [ ] Open browser tabs (in order): Node-RED dashboard, Grafana hospital, Grafana IDS, Wazuh SIEM
- [ ] Mock WAN cable plugged into UDM-SE (if no internet at venue)

**Demo Talking Points:**

**Opening (Slide 10 transition to demo):**
> "Alright, enough slides. Let's see this in action. On my screen you're looking at a live hospital IoT network - these 5 ECG traces are real Raspberry Pis publishing heart rate data right now. Notice Pi #4 has an irregular rhythm - that's our AFib simulation. This data is flowing through MQTT, into Node-RED, being stored in PostgreSQL with 933 million rows, converted to FHIR, and visualized in Grafana. This is a complete production-grade pipeline."

**Baseline State (Part 1):**
> "Bottom right, you see our Security Status Panel - currently green, 'SYSTEM SECURE'. The two pressure gauges on the right are our balloon demo systems - vulnerable on the left, secure on the right. Both are sitting at 25 PSI, our target pressure. Everything nominal."

**Attack Start (Part 2):**
> "Now I'm switching to my attacker laptop. I'm on VLAN 2, same network as the vulnerable system. I'm going to run our attack script with the --dual flag to target BOTH systems simultaneously. The attack spoofs pressure sensor readings, claiming the pressure is 0 PSI when it's actually 25 PSI. Watch what happens."

> [Run command, show terminal output]

> "Script is running, sending 10 spoofed packets per second to each target. Now watch the dashboard..."

**Vulnerable Compromise (Part 3):**
> "The vulnerable system believed the fake 0 PSI reading - its gauge dropped to zero. The control loop thinks the bottle is empty, so the pump turned on. But look at the upstream sensor - that's a REAL sensor reading the actual pressure. It's climbing... 26... 30... 35... This is dangerous. The bottle's burst pressure is around 60 PSI. At 35 PSI, we've exceeded safe limits."

> [Point to physical bottle if visible]

> "In our testing, these bottles burst between 39 and 71 PSI. We're not going to burst one today - we have an emergency relief valve that opens at 70 PSI - but in a real medical device scenario, this could be catastrophic. Imagine this is an infusion pump overdosing a patient, or a ventilator over-pressurizing lungs."

**Secure Protection (Part 4):**
> "Now look at the secure system. Same attack hitting it at 10 Hz. But watch - the pressure gauge stayed at 25 PSI. The Security Status Panel turned RED - 'ATTACK IN PROGRESS'. It's counted 143 blocked attacks so far. The control source switched to 'I2C fallback' - it's ignoring the network entirely and using the local sensor directly. The pump stayed off. The system is completely protected."

**Detection (Part 5):**
> "Let's look at our detection stack. Switching to the Grafana IDS dashboard - you can see the spike in events right when I started the attack. Top source IP: 192.168.50.191, that's me, the attacker. Top destination IPs: both the vulnerable and secure systems. Suricata captured every malicious packet."

> "Now the SIEM - Wazuh has logged all 143 rejected packets from the secure system. Each log entry has forensic details: timestamp, what the attacker claimed (0.0 PSI), what the sensor actually read (25.0 PSI), the mismatch delta (25.0 PSI), and the decision (REJECTED_MISMATCH). If this were a real hospital SOC, they'd have everything needed for incident response."

**Recovery (Part 6):**
> "I'm stopping the attack now. Watch the Security Status Panel... it returns to green within one second. The vulnerable system is venting down to safe pressure via our post-attack safety feature. The secure system didn't need to do anything - it never left 25 PSI."

**Closing:**
> "That's the power of defense in depth. Network IDS caught the attack. Application-level validation blocked it. SIEM logged it. The dashboard made it visible to non-technical stakeholders. And most importantly - the secure system kept operating safely despite an active attacker on the network."

> "Questions?"

---

## APPENDIX: Technical Specifications (For Q&A)

**Hardware:**
- 7x Raspberry Pi 5 (4GB RAM, PoE+ or external PSU)
- 5x Sense HAT (accelerometer, gyroscope, LED matrix)
- 2x DATAQ 100 PSI analog pressure sensors
- 2x ADS1115 16-bit ADC (I2C, 0x48)
- 2x BSS138 level shifter (3.3V ↔ 5V)
- Sequent 8-RELAYS HAT (I2C 0x27, solenoids)
- Sequent 40A 3-relay HAT (I2C 0x60, pump)
- Dell PowerEdge R720 (TrueNAS, 7 VMs, 180 GB PostgreSQL)
- UniFi UDM-SE (10 Gbps gateway, firewall)
- UniFi Switch Pro Max 24 PoE (802.3bt, 2.5G uplinks)

**Software Stack:**
- OS: Ubuntu 24.04 LTS (VMs), Raspberry Pi OS Bookworm (Pis)
- MQTT: Mosquitto 2.0.18, paho-mqtt 2.1.0 (Python client)
- Database: PostgreSQL 16.10, pg_cron 1.6 (automated archival)
- Automation: Node-RED 3.x, Keycloak 24.x (SSO)
- Monitoring: Grafana 10.x, Wazuh 4.x, Suricata 7.x, Elasticsearch 8.x
- HL7/FHIR: Mirth Connect 4.x, HAPI FHIR 7.x
- Security: HashiCorp Vault 1.15.x, OAuth2 Proxy

**Network:**
- VLAN 30 (10.30.0.0/24): Secure hospital infrastructure
- VLAN 2 (192.168.50.0/24): Vulnerable attack lab
- Firewall: Default-deny between VLANs, explicit allow rules for MQTT + Elasticsearch
- Monitoring: Port mirroring (Switch Port 15 → Suricata Port 7)

**Data Volumes:**
- PostgreSQL: 933M rows, 180 GB (active: 60M rows/7 days, archive: 873M rows)
- MQTT throughput: 17 msg/sec sustained (5 hospital + 12 balloon demo)
- PostgreSQL writes: 100 inserts/sec (hospital data), 1 insert/sec (FHIR via Mirth)
- Retention: 7-day rolling window (pg_cron archival daily at 2 AM UTC)

**Attack Stats:**
- Attack rate: 10 Hz per target (20 total packets/sec for dual-target)
- Vulnerable success: 100% (all packets accepted)
- Secure success: 0% (all packets rejected)
- Detection latency: <100ms (MQTT → Node-RED → dashboard)
- SIEM logging latency: <1 second (Wazuh agent → manager)
