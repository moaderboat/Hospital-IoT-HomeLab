# Hospital Homelab Project - Gantt Chart Timeline
## Spring 2026 Semester (January 28 - April 7, 2026)

---

## Timeline Overview (10 Weeks)

```
Week 1-3: Progress Report 1 Period (Jan 28 - Feb 16)
Week 4-6: Progress Report 2 Period (Feb 17 - Mar 9)
Week 7-10: Final Expo Preparation (Mar 10 - Apr 7)
```

---

## Gantt Chart - Task Timeline

### Legend
- `████` Completed
- `▓▓▓▓` In Progress / Planned
- `░░░░` Buffer / Testing Time
- `◆` Milestone/Deadline

---

### Week-by-Week Breakdown

```
                    Jan 28 - Feb 2 | Feb 3 - Feb 9 | Feb 10 - Feb 16 | Feb 17 - Feb 23 | Feb 24 - Mar 2 | Mar 3 - Mar 9 | Mar 10 - Mar 16 | Mar 17 - Mar 23 | Mar 24 - Mar 30 | Mar 31 - Apr 6
Task                Week 1          Week 2          Week 3 ◆PR1      Week 4            Week 5          Week 6 ◆PR2     Week 7            Week 8            Week 9            Week 10 ◆EXPO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROGRESS REPORT 1 PERIOD (Due Feb 17)
─────────────────────────────────────────────────────────────────────
HAPI FHIR SSO      ▓▓▓▓▓▓▓▓▓▓▓▓    ░░░░░░
  - Keycloak client   ▓▓▓
  - OAuth2 Proxy          ▓▓▓▓
  - Testing/Debug             ▓▓▓▓  ░░░░

Network Diagrams    ▓▓▓▓            ░░░░
  - Topology                  ▓▓▓
  - Auth flows                    ▓▓

Performance Docs        ▓▓▓▓▓▓▓▓    ░░░░
  - Benchmarking              ▓▓▓▓
  - Metrics collection    ▓▓▓▓

HIPAA Compliance        ▓▓▓▓▓▓▓▓    ░░░░
  - Matrix mapping            ▓▓▓▓
  - Controls audit        ▓▓▓▓

Progress Report 1               ▓▓▓▓░░░░  ◆
  - Writing                         ▓▓▓
  - Review/Edit                         ▓ ░
                                          ◆ (Feb 17)

PROGRESS REPORT 2 PERIOD (Due Mar 10)
─────────────────────────────────────────────────────────────────────
HashiCorp Vault                         ▓▓▓▓▓▓▓▓▓▓▓▓    ░░░░
  - VM deployment                           ▓▓▓
  - Secret migration                            ▓▓▓▓▓▓
  - Integration test                                    ▓▓▓ ░

Zeek/Suricata IDS                       ▓▓▓▓▓▓▓▓▓▓▓▓    ░░░░
  - VM deployment                           ▓▓▓
  - SPAN config                                 ▓▓
  - Ruleset creation                                ▓▓▓▓
  - Wazuh integration                                   ▓▓▓ ░

Keycloak MFA                                ▓▓▓▓▓▓      ░░
  - TOTP setup                                    ▓▓▓
  - User enrollment                                   ▓▓▓ ░

PostgreSQL Policy                           ▓▓▓▓▓▓      ░░
  - Retention script                              ▓▓▓
  - Cron scheduling                                   ▓▓ ░
  - Testing                                           ▓  ░

Progress Report 2                                   ▓▓▓▓░░  ◆
  - Writing                                             ▓▓
  - Review/Edit                                           ▓░
                                                            ◆ (Mar 10)

FINAL EXPO PREPARATION (Due Apr 7)
─────────────────────────────────────────────────────────────────────
Attack Lab Setup                                        ▓▓▓▓▓▓▓▓▓▓▓▓
  - Kali Linux #1                                           ▓▓▓
  - Kali Linux #2                                           ▓▓▓
  - Metasploitable                                              ▓▓▓
  - T-Pot Honeypot                                              ▓▓▓
  - VLAN 40 isolation                                       ▓▓▓
  - Firewall rules                                              ▓▓▓

Penetration Testing                                             ▓▓▓▓▓▓▓▓    ░░░░
  - OWASP Top 10                                                    ▓▓▓▓
  - SQL injection                                                       ▓▓
  - MQTT attacks                                                        ▓▓
  - FHIR API testing                                                    ▓▓▓
  - Wazuh validation                                                        ▓▓▓

Documentation                                                   ▓▓▓▓▓▓▓▓▓▓▓▓░░░░
  - Architecture diagrams                                         ▓▓▓▓
  - Attack report                                                         ▓▓▓▓
  - Final tech doc                                                            ▓▓▓▓▓▓
  - Executive summary                                                             ▓▓▓

Demo Preparation                                                        ▓▓▓▓▓▓▓▓░░░░
  - Video recording                                                           ▓▓▓
  - Presentation slides                                                       ▓▓▓▓
  - Demo script                                                                   ▓▓▓
  - Equipment testing                                                                 ▓░░
  - Rehearsal                                                                         ░░░

Final Expo Day                                                                            ◆
                                                                                          ◆ (Apr 7)
```

---

## Detailed Task Breakdown by Milestone

### ◆ Progress Report 1 (February 17, 2026)

**Week 1 (Jan 28 - Feb 2): HAPI FHIR SSO & Documentation Start**
- Days 1-2: Create Keycloak client for HAPI FHIR (hapi-fhir-oauth2)
- Days 3-5: Install and configure OAuth2 Proxy on HAPI FHIR VM
- Days 5-7: Begin network topology diagrams and performance benchmarking

**Week 2 (Feb 3 - Feb 9): Integration & Metrics**
- Days 1-3: Complete OAuth2 Proxy configuration and testing
- Days 4-5: Finalize network diagrams (topology, authentication flows)
- Days 6-7: Collect performance metrics (query times, throughput, latency)

**Week 3 (Feb 10 - Feb 16): HIPAA Compliance & Report Writing**
- Days 1-3: Create HIPAA compliance matrix (map 164.312 controls to implementations)
- Days 4-5: Write Progress Report 1 narrative
- Days 6-7: Review, edit, and submit Progress Report 1

**Deliverables:**
- ✓ HAPI FHIR OAuth2 Proxy operational
- ✓ Network topology diagrams (Visio/draw.io)
- ✓ Performance benchmark report
- ✓ HIPAA compliance matrix
- ✓ Progress Report 1 document (PDF)

---

### ◆ Progress Report 2 (March 10, 2026)

**Week 4 (Feb 17 - Feb 23): HashiCorp Vault & Zeek/Suricata Deployment**
- Days 1-2: Deploy HashiCorp Vault VM (10.30.0.58) on TrueNAS
- Days 3-5: Deploy Zeek/Suricata IDS/IPS VM (10.30.0.59)
- Days 6-7: Configure SPAN port on UniFi switch for traffic mirroring

**Week 5 (Feb 24 - Mar 2): Secrets Migration & IDS Rulesets**
- Days 1-3: Migrate credentials to Vault (PostgreSQL, Keycloak, MQTT broker)
- Days 4-5: Create Zeek/Suricata rulesets for HL7/FHIR protocol anomalies
- Days 6-7: Configure Keycloak MFA (TOTP authenticator)

**Week 6 (Mar 3 - Mar 9): Integration Testing & Report Writing**
- Days 1-2: Integrate Zeek/Suricata alerts with Wazuh SIEM
- Days 3-4: Implement PostgreSQL data retention policy (90-day rolling window)
- Days 5-7: Write, review, and submit Progress Report 2

**Deliverables:**
- ✓ HashiCorp Vault operational with secret rotation
- ✓ Zeek/Suricata IDS/IPS with custom rulesets
- ✓ Keycloak MFA enabled for all users
- ✓ PostgreSQL retention policy automated
- ✓ Progress Report 2 document (PDF)

---

### ◆ Final Expo (April 7, 2026)

**Week 7 (Mar 10 - Mar 16): Attack Lab Infrastructure**
- Days 1-2: Deploy Kali Linux VM #1 (external attacker perspective)
- Days 3-4: Deploy Kali Linux VM #2 (internal threat simulation)
- Days 5-6: Deploy Metasploitable 3 and T-Pot Honeypot VMs
- Day 7: Configure VLAN 40 isolation and firewall rules

**Week 8 (Mar 17 - Mar 23): Attack Lab Configuration & Initial Testing**
- Days 1-2: Configure attack tools on Kali Linux instances
- Days 3-5: Metasploitable configuration and vulnerability verification
- Days 6-7: T-Pot honeypot configuration and alert testing

**Week 9 (Mar 24 - Mar 30): Penetration Testing Execution**
- Days 1-2: OWASP Top 10 attacks against FHIR API (SQL injection, XSS, auth bypass)
- Days 3-4: MQTT broker authentication bypass attempts
- Days 5-6: Network-level attacks (port scanning, man-in-the-middle)
- Day 7: Wazuh SIEM detection validation and attack documentation

**Week 10 (Mar 31 - Apr 6): Final Documentation & Demo Preparation**
- Days 1-2: Create system architecture diagrams and attack flow diagrams
- Days 3-4: Write penetration testing report and final technical documentation
- Days 5-6: Record backup demo videos and create presentation slides
- Day 7: Equipment testing, demo rehearsal, and final preparation

**Day of Expo (April 7, 2026):**
- Morning: Setup booth, test all equipment
- Afternoon: Live demonstrations and Q&A with faculty/industry partners

**Deliverables:**
- ✓ Fully operational attack lab (4 VMs on isolated subnet)
- ✓ Penetration testing report with OWASP Top 10 coverage
- ✓ Final technical documentation (30+ page report)
- ✓ System architecture diagrams (network, data flow, authentication)
- ✓ Presentation slides (15-minute talk)
- ✓ Backup demo videos (3-5 minutes each)
- ✓ Live demonstration script with fallback plans

---

## Critical Path Analysis

**Must-Complete Tasks (Cannot be delayed):**
1. HAPI FHIR OAuth2 Proxy (Week 1-2) → Blocks PR1
2. Progress Report 1 writing (Week 3) → Hard deadline Feb 17
3. Vault/IDS deployment (Week 4-5) → Blocks PR2
4. Progress Report 2 writing (Week 6) → Hard deadline Mar 10
5. Attack lab deployment (Week 7-8) → Blocks penetration testing
6. Final documentation (Week 10) → Hard deadline Apr 7

**Flexible Tasks (Can be descoped if time constrained):**
- T-Pot Honeypot → Nice-to-have, not critical for demo
- PostgreSQL retention policy → Can document as "future work"
- Kali Linux #2 → One Kali instance sufficient for demo
- MFA configuration → Can demonstrate capability without full rollout

**Parallel Execution Opportunities:**
- Week 4: Vault deployment + IDS deployment (independent tasks)
- Week 7: Kali #1 + Kali #2 + Metasploitable (can deploy simultaneously)
- Week 10: Documentation + Demo video recording (different work streams)

---

## Resource Allocation & Time Budget

| Milestone | Total Hours | Breakdown |
|-----------|-------------|-----------|
| Progress Report 1 | 20 hours | 8h implementation, 6h documentation, 6h report writing |
| Progress Report 2 | 30 hours | 14h implementation, 8h testing, 8h report writing |
| Final Expo Prep | 50 hours | 16h attack lab, 12h pentesting, 12h documentation, 10h demo prep |
| **Total Semester** | **100 hours** | ~10 hours/week average |

**Weekly Time Commitment:**
- Weeks 1-3: 6-8 hours/week (PR1 period, lighter workload)
- Weeks 4-6: 10-12 hours/week (PR2 period, VM deployments)
- Weeks 7-10: 12-15 hours/week (Expo prep, heavy documentation)

---

## Contingency Plans

**If Behind Schedule:**
1. **By Feb 10** (Week 3): Skip OAuth2 Proxy, document HAPI FHIR SSO as "future work" in PR1
2. **By Feb 24** (Week 5): Deploy only Vault OR IDS/IPS (not both) for PR2
3. **By Mar 17** (Week 8): Reduce attack lab to 1 Kali + Metasploitable (skip T-Pot)
4. **By Mar 31** (Week 10): Simplify penetration testing to 3-4 OWASP attacks instead of full Top 10

**If Ahead of Schedule:**
1. **By Feb 10** (Week 3): Add Orthanc PACS VM for medical imaging (DICOM)
2. **By Feb 24** (Week 5): Implement email/Slack alerting for Grafana/Wazuh
3. **By Mar 17** (Week 8): Add STIG compliance scanning with OpenSCAP
4. **By Mar 31** (Week 10): Create interactive Jupyter notebook for data analysis demos

---

## Risk Mitigation Timeline

| Week | Primary Risk | Mitigation Action |
|------|-------------|-------------------|
| Week 1-2 | OAuth2 Proxy complexity | Allocate 2 days for troubleshooting, have skip plan ready |
| Week 4-5 | VM resource exhaustion | Monitor TrueNAS CPU/RAM, prepare external hardware if needed |
| Week 7-8 | Attack lab network instability | Deploy VLAN 40 early, test isolation before full deployment |
| Week 9 | Penetration testing fails to trigger alerts | Review Wazuh rules proactively, adjust sensitivity |
| Week 10 | Demo hardware failure | Record backup videos by Apr 4, test equipment Apr 5-6 |

---

## Milestones & Deadlines Summary

```
◆ Feb 17, 2026 - Progress Report 1 Due
   └─ 3 weeks from today (Jan 28)
   └─ Deliverables: HAPI FHIR SSO, diagrams, HIPAA matrix, PR1 document

◆ Mar 10, 2026 - Progress Report 2 Due
   └─ 6 weeks from today (3 weeks after PR1)
   └─ Deliverables: Vault, IDS/IPS, MFA, retention policy, PR2 document

◆ Apr 7, 2026 - Final Expo & Documentation Due
   └─ 10 weeks from today (4 weeks after PR2)
   └─ Deliverables: Attack lab, pentest report, final docs, presentation, live demo

◆ Apr 7, 2026 - Semester Ends
   └─ All work must be completed by this date
```

---

**END OF GANTT CHART**

---

## Quick Reference: Key Dates

- **Today:** January 28, 2026 (Week 1, Day 1)
- **PR1 Due:** February 17, 2026 (Week 3, Day 7) - 20 days away
- **PR2 Due:** March 10, 2026 (Week 6, Day 7) - 41 days away
- **Final Expo:** April 7, 2026 (Week 10, Day 7) - 69 days away
- **Days Remaining:** 69 days total, 10 weeks, 2.5 months
