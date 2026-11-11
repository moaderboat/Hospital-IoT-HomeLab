# Expo Poster Panels Reference

**Last Updated:** 2026-03-05  
**Purpose:** Content guide for two tri-fold poster boards (6 panels total)

---

## TRI-FOLD 1: THE SYSTEM

### Left Panel - The Problem
**Title:** "Why Healthcare IoT Security Matters"

**Content:**

- **The Crisis:** 88% healthcare data breaches from IoT, $10.93M average cost
- **Real Examples:** 2017 FDA pacemaker recall, 2020 UVM ransomware
- **Our Mission:** Build functional hospital network → demonstrate vulnerabilities → prove defense strategies

---

### Center Panel - Network Architecture
**Title:** "A Real Hospital Network in Miniature"

**Content:**

**VLAN 30 (Secure Hospital - 10.30.0.0/24):**
- 5× Raspberry Pi heart rate monitors → MQTT → Node-RED → PostgreSQL (397M+ records)
- Keycloak SSO (4 apps), Wazuh SIEM (14 agents), Suricata IDS
- HAPI FHIR server with OAuth2 protection

**VLAN 2 (Attack Lab - 192.168.50.0/24):**
- Pi #7 (vulnerable balloon demo, Switch Port 15)
- Port mirroring: Port 6 mirrors Port 15 for IDS monitoring
- Admin laptop (10.30.0.123) for attack simulation

**Firewall Segmentation:** VLAN30 → VLAN2 (admin only), VLAN2 ✗ VLAN30 (blocked)

---

### Right Panel - Data Pipeline & Security
**Title:** "From Heartbeat to FHIR Record"

**Content:**

**Pipeline:** SenseHat → MQTT → Node-RED → PostgreSQL + Mirth → FHIR Server → Grafana

**Security Stack:**
- Keycloak (SSO, 80% coverage)
- Vault (3-of-5 unseal, secrets management)
- Wazuh (centralized logging, anomaly detection)
- Suricata (IDS on bare-metal, port mirroring)

**Scale:** 100 readings/sec, 397M+ records, 7-day retention + 87GB archive

---

## TRI-FOLD 2: THE DEMO

### Left Panel - The Vulnerable System
**Title:** "How Sensor Spoofing Works"

**Content:**

**Hardware Chain:**
- DATAQ 100 PSI sensor → ADS1115 ADC → Raspberry Pi #7 → Flask API (port 5000)
- Sequent relay HATs → pump (23A) + 3× solenoid valves
- 1L plastic bottle pressure vessel

**The Vulnerability:**
- Unauthenticated `/sensor` POST endpoint
- No input validation or rate limiting
- Trusts network pressure readings blindly

**The Attack:** Laptop sends fake "0.0 PSI" at 10 Hz → system believes bottle is empty → keeps pump running → real pressure exceeds safe limits → **BURST**

---

### Center Panel - Live Demo
**Title:** "Vulnerable vs. Secure: Side-by-Side"

**Content:**

**LEFT - Vulnerable System (Pi #7):**
- ❌ Network sensor readings (HTTP API)
- ❌ No authentication
- ❌ No input validation
- ⚠️ Attack sends 0.0 PSI → pump runs continuously → pressure climbs dangerously

**RIGHT - Secure System (Pi #6):**
- ✅ Direct sensor reading (I2C, no network exposure)
- ✅ Input validation (0.5-4.5V range check)
- ✅ Rate-of-change detection (5.0 PSI/sec threshold)
- ✅ Dual-sensor cross-validation
- ✅ Wazuh SIEM logging
- 🛡️ Same attack → anomaly detected → pump disabled → pressure controlled

---

### Right Panel - Defense Strategies
**Title:** "Lessons Learned: Hardening IoT Systems"

**Content:**

**What Worked:**
1. **Input Validation** - range checks, sanity checks
2. **Anomaly Detection** - rate-of-change thresholds
3. **Sensor Redundancy** - cross-validation between dual sensors
4. **Network Segmentation** - firewall isolation prevents lateral movement
5. **Centralized Logging** - Wazuh SIEM for forensics

**Key Takeaways:**
- Never trust network data without validation
- Physical sensors should connect directly when possible
- Defense-in-depth: no single point of failure
- Real-time monitoring catches attacks before damage

**Real-World Impact:** These techniques apply to pacemakers, insulin pumps, ventilators, and all critical medical IoT devices.
