# 5-Minute Final Presentation Outline
## Hospital IoT Simulation Homelab for Cybersecurity and ML Research

**Presenter:** David Moad
**Time Limit:** 5 minutes (strict 6-minute cutoff)
**Q&A:** 2 minutes after presentation
**Audience:** Classmates (peer review determines 20% of final grade)

---

## ⏱️ **Timing Breakdown**

| Slide | Topic | Time | Cumulative |
|-------|-------|------|------------|
| 1 | Title Slide | 0:10 | 0:10 |
| 2 | Team Bio & The Problem | 0:40 | 0:50 |
| 3 | Background & Why This Matters | 0:50 | 1:40 |
| 4 | Proposed Solution & Design | 1:00 | 2:40 |
| 5 | Standards Compliance | 0:30 | 3:10 |
| 6 | Timeline & Budget | 0:40 | 3:50 |
| 7 | Progress to Date (DEMO) | 0:50 | 4:40 |
| 8 | Future Plans | 0:20 | 5:00 |
| **TOTAL** | | **5:00** | |

---

# 📊 SLIDE-BY-SLIDE BREAKDOWN

---

## **SLIDE 1: Title Slide** (0:10 / 0:10 cumulative)

### Visual Layout:
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   Hospital IoT Simulation Homelab                  │
│   for Cybersecurity & Machine Learning Research    │
│                                                     │
│   [Photo of your rack setup with Raspberry Pis]    │
│                                                     │
│   David Moad                                        │
│   Computer Engineering                             │
│   University of Cincinnati                         │
│   Fall 2025                                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Speaker Notes:
> "Good morning everyone. My name is David Moad, and today I'm presenting my senior design project: a professional-grade hospital IoT simulation homelab for cybersecurity and machine learning research."

**[Advance slide immediately - don't linger]**

---

## **SLIDE 2: Team Bio & The Problem** (0:40 / 0:50 cumulative)

### Visual Layout:
```
┌─────────────────────────────────────────────────────┐
│  TEAM & PROBLEM STATEMENT                          │
│                                                     │
│  David Moad - Solo Project                         │
│  └─ Computer Engineering                           │
│  └─ Roles: System Designer, Network Engineer,      │
│            Security Analyst, ML Developer          │
│                                                     │
│  THE PROBLEM:                                      │
│  ┌───────────────────────────────────────────┐    │
│  │ Hospitals are prime ransomware targets    │    │
│  │ • 45% more cyberattacks than avg industry │    │
│  │ • Can't safely test defenses on live      │    │
│  │   patient systems (safety risk!)          │    │
│  │ • Students lack realistic training labs   │    │
│  └───────────────────────────────────────────┘    │
│                                                     │
│  [Icon: Hospital + Lock + Warning Symbol]          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Speaker Notes:
> "This is a solo project where I'm serving as system designer, network engineer, security analyst, and ML developer.
>
> The problem we're addressing is critical: Hospitals experience 45% more cyberattacks than the average industry. Recent examples include the Kettering Health ransomware attack right here in Ohio and the CommonSpirit breach affecting 140 hospitals. But here's the catch—you can't safely test cybersecurity defenses on production hospital systems because patient lives are at stake. And most students lack access to realistic healthcare IT infrastructure for training. That's the gap this project fills."

**Timing Tip:** Speak at moderate pace (150 words/minute). This section is ~80 words = ~30 seconds + slide advance time.

---

## **SLIDE 3: Background & Why This Matters** (0:50 / 1:40 cumulative)

### Visual Layout:
```
┌─────────────────────────────────────────────────────┐
│  WHY THIS MATTERS                                   │
│                                                     │
│  Hospital IoT Attack Surface:                      │
│  ┌──────────────────────────────────────────┐     │
│  │ Patient Monitors    Infusion Pumps       │     │
│  │ Ventilators        MRI/CT Scanners       │     │
│  │ IV Controllers     Temperature Sensors    │     │
│  └──────────────────────────────────────────┘     │
│                                                     │
│  Each device = Potential attack vector             │
│                                                     │
│  Real-World Consequences:                          │
│  • Ransomware encrypts monitors → Can't see vitals│
│  • Tampered dosage data → Patient overdose        │
│  • Network spread → Widespread device failure     │
│                                                     │
│  [Diagram: Network of medical devices with        │
│   one compromised node spreading malware]         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Speaker Notes:
> "Why does this matter? Modern hospitals rely on dozens of IoT medical devices—patient monitors, infusion pumps, ventilators, imaging equipment. Each one is a potential attack vector.
>
> The consequences are severe: Ransomware can encrypt patient monitors, preventing clinicians from seeing vital signs. Attackers could tamper with infusion pump dosage data, causing overdoses. And because these devices are networked, malware spreads quickly, causing widespread failures.
>
> We need safe environments to train the next generation of healthcare cybersecurity professionals. That's what this homelab provides."

**Timing Tip:** ~125 words = ~50 seconds. Pace yourself and gesture to the visual.

---

## **SLIDE 4: Proposed Solution & Design** (1:00 / 2:40 cumulative)

### Visual Layout:
```
┌─────────────────────────────────────────────────────┐
│  PROPOSED SOLUTION: Hybrid Homelab                 │
│                                                     │
│  [Network Topology Diagram - from hospital_homelab.drawio] │
│                                                     │
│  Key Components:                                   │
│  ┌────────────────────────────────────────┐       │
│  │ Hardware:                              │       │
│  │ • Dell R740XD Server (TrueNAS)        │       │
│  │ • UniFi Dream Machine SE (Firewall)   │       │
│  │ • 24-Port PoE Switch                  │       │
│  │ • 4 Raspberry Pi 5s (IoT Sensors)     │       │
│  │                                        │       │
│  │ Software (All Open-Source):            │       │
│  │ • Node-RED (Data Pipeline)            │       │
│  │ • PostgreSQL (Time-Series DB)         │       │
│  │ • Grafana (Visualization)             │       │
│  │ • Wazuh SIEM (Security Monitoring)    │       │
│  └────────────────────────────────────────┘       │
│                                                     │
│  Design Alternatives Considered:                   │
│  ❌ Cloud Lab (ongoing costs, no air-gap)         │
│  ❌ Real Medical Devices (too expensive)          │
│  ❌ Software-Only (lacks realism)                 │
│  ✅ Hybrid Physical/Virtual (SELECTED)            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Speaker Notes:
> "My solution is a hybrid physical and virtual homelab.
>
> The hardware includes a Dell R740XD server running TrueNAS for storage and VM hosting, a UniFi Dream Machine for enterprise-grade firewall and routing, a 24-port Power-over-Ethernet switch, and four Raspberry Pi 5s simulating patient vital monitors. All software is open-source: Node-RED for data processing, PostgreSQL for storage, Grafana for visualization, and Wazuh for security monitoring.
>
> I evaluated four design alternatives. Cloud labs have ongoing costs and can't demonstrate air-gapped operation—critical for hospital scenarios. Real medical devices were too expensive at $5,000-plus each and not replicable by other students. Software-only simulations lack hands-on hardware experience. So I selected a hybrid approach that balances cost, realism, and educational value at a total budget of $5,400."

**Timing Tip:** ~150 words = ~60 seconds. Point to diagram elements as you speak.

---

## **SLIDE 5: Standards Compliance** (0:30 / 3:10 cumulative)

### Visual Layout:
```
┌─────────────────────────────────────────────────────┐
│  HEALTHCARE CYBERSECURITY STANDARDS COMPLIANCE      │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ 1. HIPAA Security Rule                       │ │
│  │    └─ Encryption, Access Control, Audit      │ │
│  │                                               │ │
│  │ 2. NIST Cybersecurity Framework              │ │
│  │    └─ Identify, Protect, Detect, Respond     │ │
│  │                                               │ │
│  │ 3. NIST SP 800-53 (Security Controls)        │ │
│  │    └─ 20 control families implemented        │ │
│  │                                               │ │
│  │ 4. IEC 62443 (IoT/OT Security)               │ │
│  │    └─ Zone segmentation, device hardening    │ │
│  │                                               │ │
│  │ 5. ISO/IEC 27001 (InfoSec Management)        │ │
│  │    └─ ISMS documentation, risk assessment    │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  [Checkmark icons next to each standard]           │
│                                                     │
│  Result: Comprehensive compliance training         │
│          environment for future healthcare IT      │
│          professionals                             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Speaker Notes:
> "This project enforces compliance with five major healthcare cybersecurity standards.
>
> HIPAA requires encryption and access controls—we implement AES-256 dataset encryption and SSH key-based authentication. The NIST Cybersecurity Framework's five functions are embedded in the architecture: identify, protect, detect, respond, and recover. NIST 800-53 security controls guide our firewall rules and VLAN segmentation. IEC 62443 for industrial control systems—applicable to medical IoT—informs our zone-based network isolation. And ISO 27001 provides our information security management system framework.
>
> The result is a comprehensive compliance training environment."

**Timing Tip:** ~90 words = ~30-35 seconds. This is dense content, so speak clearly.

---

## **SLIDE 6: Timeline & Budget** (0:40 / 3:50 cumulative)

### Visual Layout:
```
┌─────────────────────────────────────────────────────┐
│  TIMELINE & BUDGET                                  │
│                                                     │
│  [Gantt Chart - Phase 1 Highlight Version]         │
│  (Show Aug-Dec 2025 with completed tasks in green) │
│                                                     │
│  Budget Breakdown:                                 │
│  ┌────────────────────────────────────┐           │
│  │ Dell R740XD Server      $1,800     │           │
│  │ 10× 8TB HDDs            $1,200     │           │
│  │ 2× 960GB SSDs           $  200     │           │
│  │ UniFi Networking        $1,200     │           │
│  │ 5× Raspberry Pi Kits    $  500     │           │
│  │ Cables, Rack, UPS       $  500     │           │
│  │ ─────────────────────────────────  │           │
│  │ TOTAL:                  $5,400     │           │
│  │ Software (Open-Source): $    0     │           │
│  └────────────────────────────────────┘           │
│                                                     │
│  5-Year TCO Comparison:                            │
│  • This Homelab:  $7,900                           │
│  • Cloud Lab:     $18,000  ← 2.3× more expensive  │
│  • Commercial:    $45,000  ← 5.7× more expensive  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Speaker Notes:
> "Here's our timeline and budget. The Gantt chart shows we've completed Phase 1—core infrastructure—represented by the green completed tasks. We're currently on schedule with the next critical milestone being MQTT pipeline deployment in December.
>
> The total budget is $5,400. The biggest investments are the Dell server at $1,800, storage drives at $1,400, and UniFi networking at $1,200. All software is open-source, so zero licensing costs.
>
> Over five years, this homelab costs $7,900 including electricity. A comparable cloud lab would cost $18,000—more than twice as expensive. And commercial cyber range solutions run $45,000 or more. This demonstrates that professional-grade training infrastructure is achievable at student budgets."

**Timing Tip:** ~120 words = ~40-45 seconds. Pause briefly at dollar amounts for emphasis.

---

## **SLIDE 7: Progress to Date (DEMO)** (0:50 / 4:40 cumulative)

### Visual Layout:
```
┌─────────────────────────────────────────────────────┐
│  PROGRESS TO DATE: LIVE SYSTEM                      │
│                                                     │
│  [SPLIT SCREEN]                                    │
│  Left: Photo of physical setup (rack, Pis, switch) │
│  Right: Screenshot of Node-RED dashboard OR        │
│         Live demo if network available             │
│                                                     │
│  Key Achievements:                                 │
│  ✅ Network Infrastructure Operational             │
│     • 10Gbps SFP+ backbone                         │
│     • Sub-5ms latency (exceeded spec)              │
│                                                     │
│  ✅ 4 IoT Sensors Running Continuously             │
│     • 99.98% uptime over 8-day validation          │
│     • 2.7M+ data points collected                  │
│     • 3 normal sensors (62 BPM)                    │
│     • 1 AFib sensor (110±40 BPM)                   │
│                                                     │
│  ✅ Air-Gap Capability Validated                   │
│     • Full operation without internet              │
│     • Portable for demos/field deployment          │
│                                                     │
│  ✅ 64TB Encrypted Storage (RAID-Z2)               │
│     • AES-256 encryption                           │
│     • 2-disk failure tolerance                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Speaker Notes:
> "Let me show you what's working today.
>
> [POINT TO VISUAL] On the left is my physical setup: the server rack with Raspberry Pi sensors. On the right is the Node-RED dashboard showing real-time data flow.
>
> Key achievements: The network infrastructure is fully operational with a 10-gigabit backbone and sub-5-millisecond latency—exceeding our specification. Four IoT sensors have been running continuously with 99.98% uptime over an 8-day validation period, generating 2.7 million data points. Three sensors simulate normal resting heart rate at 62 beats per minute, and one simulates atrial fibrillation with high variability.
>
> We've validated air-gap capability—the entire system operates without internet, making it portable for demonstrations. And we have 64 terabytes of encrypted storage with RAID-Z2, meaning the system can tolerate two simultaneous disk failures without data loss."

**IF YOU HAVE LIVE DEMO ACCESS:**
> "Let me quickly show you the live system. [Navigate to http://10.30.0.52:1880] Here you can see Node-RED running with real-time heartbeat data from all four sensors. [Point to flow] This is the data pipeline we built."

**Timing Tip:** ~180 words = ~50-60 seconds. Slow down for live demo if showing. Speed up if just presenting slide.

---

## **SLIDE 8: Future Plans** (0:20 / 5:00 cumulative)

### Visual Layout:
```
┌─────────────────────────────────────────────────────┐
│  FUTURE DEVELOPMENT PHASES                          │
│                                                     │
│  Phase 2: Network Segmentation (Dec-Feb)           │
│  • Multi-VLAN architecture (IoT, Mgmt, Secure)     │
│  • Grafana real-time dashboards                   │
│                                                     │
│  Phase 3: Machine Learning (Feb-Mar)               │
│  • Anomaly detection models                        │
│  • Differentiate medical vs. cyber anomalies       │
│                                                     │
│  Phase 4: Security Tools (Mar-May)                 │
│  • Wazuh SIEM deployment                           │
│  • Zeek + Suricata IDS/IPS                        │
│                                                     │
│  Phase 5: Attack Simulation (May-Jun)              │
│  • Kali Linux penetration testing                  │
│  • 10+ documented attack scenarios                 │
│  • Honeypot deployment                             │
│                                                     │
│  Long-Term Vision:                                 │
│  → Replicable framework for healthcare cyber       │
│     education                                      │
│  → Open-source documentation for other students    │
│  → Conference presentations & publications         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Speaker Notes:
> "Looking ahead, we have four more development phases planned.
>
> Phase 2 implements multi-VLAN network segmentation and Grafana visualization dashboards. Phase 3 focuses on machine learning to detect anomalies and differentiate between medical events—like atrial fibrillation—and cyberattacks. Phase 4 adds security tools including a SIEM and intrusion detection system. And Phase 5 deploys attack simulation with penetration testing and honeypots.
>
> The long-term vision is to create a replicable framework that other universities can adopt, with full open-source documentation. I'm also planning conference presentations to share these findings with the cybersecurity community.
>
> Thank you. I'm happy to take questions."

**Timing Tip:** ~100 words = ~35-40 seconds. End at exactly 5:00.

---

# 🎯 **PRESENTATION TIPS**

## **Before Presentation Day:**

### **1. Practice Timing (3× minimum)**
- **First run:** Read script naturally → likely 6-7 minutes (too long!)
- **Second run:** Speed up, cut filler words → aim for 5:30
- **Third run:** Finalize timing → hit 4:50-5:00 exactly
- **Use timer:** Set phone timer; practice hitting marks

### **2. Create Visual Slides**
**Tools:**
- PowerPoint (recommended for peer review audience)
- Google Slides (cloud backup)
- LaTeX Beamer (if you want to impress)

**Visual Design Tips:**
- **Use high-quality images:** Export `hospital_homelab.drawio` as PNG at 300 DPI
- **Minimal text per slide:** Max 3-4 bullet points
- **Large fonts:** 24pt minimum for body text, 36pt+ for titles
- **Consistent theme:** Use UC colors (red/black) or professional blue/gray
- **Icons over text:** Use visual icons for concepts (lock = security, network = connectivity)

### **3. Prepare Backup Materials**
- **Slide deck on USB drive** (in case Wi-Fi fails)
- **PDF version** (in case PowerPoint version doesn't work)
- **Printed notes** (1-page cheat sheet with timing marks)

### **4. Test Equipment**
- **If doing live demo:** Test Wi-Fi connection in presentation room
- **Backup plan:** Have screenshots ready if live demo fails
- **Clicker/remote:** Practice advancing slides smoothly

---

## **During Presentation:**

### **Body Language:**
- ✅ **Stand confidently:** Shoulders back, feet shoulder-width apart
- ✅ **Make eye contact:** Scan the room, don't stare at slides
- ✅ **Use hand gestures:** Point to elements on slides naturally
- ✅ **Move purposefully:** Don't pace, but don't stand frozen
- ❌ **Avoid:** Hands in pockets, fidgeting, reading directly from slides

### **Voice Control:**
- ✅ **Speak clearly:** Enunciate technical terms (Suricata, PostgreSQL)
- ✅ **Vary pace:** Slow down for key points, speed up for transitions
- ✅ **Project voice:** Speak to back row, not front row
- ✅ **Pause strategically:** After major points, let audience absorb
- ❌ **Avoid:** Filler words (um, uh, like, so, basically)

### **Handling Time:**
- **If running AHEAD (4:30 at Slide 8):** Expand on Future Plans, mention specific ML algorithms
- **If running BEHIND (4:00 at Slide 6):** Skip live demo, use screenshot only; shorten Future Plans
- **Emergency:** If at 5:30 and still on Slide 7, skip to Slide 8 immediately

### **Technical Difficulties:**
- **Laptop crashes:** "Let me switch to my backup PDF"
- **Live demo fails:** "Here's a screenshot from this morning's test"
- **Clicker fails:** Ask someone to advance slides for you
- **Blank slide:** Don't panic—describe what should be there, move on

---

## **Q&A Session (2 minutes after):**

### **Likely Questions & Prepared Answers:**

**Q1: "Why not just use real medical devices?"**
> "Great question. Real medical devices cost $5,000 to $50,000 each, making the project budget prohibitive and not replicable by other students. Additionally, there are ethical and legal concerns around disclosing vulnerabilities in FDA-approved medical devices. Our Raspberry Pi sensors provide realistic network behavior and data patterns at 1/50th the cost, while still teaching the core cybersecurity principles."

**Q2: "How do you ensure the lab stays isolated from the real network?"**
> "Two layers of protection. First, the UniFi Dream Machine firewall has strict egress rules preventing unintended traffic. Second, we've validated air-gap operation—disconnecting the WAN cable—and confirmed all services continue operating on the local 10.30.0.0/24 network. For attack simulation in Phase 5, the Kali Linux VMs will be on a dedicated Attack VLAN with zero routes to external networks."

**Q3: "What happens if you lose power?"**
> "The system includes an APC UPS rated for 30 minutes of runtime, giving me time to gracefully shut down the server. TrueNAS uses ZFS, which is a copy-on-write filesystem that protects against corruption even during sudden power loss. I also have daily snapshots and weekly configuration backups stored on the encrypted datasets. In testing, I can fully restore the system from backup in under one hour."

**Q4: "How accurate are your simulated heart rate patterns?"**
> "Excellent question. The normal sensors generate 62 BPM with ±5 variation, which matches published medical literature for resting adult heart rate. The AFib sensor uses a random distribution of 110 BPM ±40, simulating the high variability characteristic of atrial fibrillation. I validated this against real patient data patterns from published cardiology studies. For Phase 3 machine learning, we'll train on these baseline patterns to detect deviations."

**Q5: "Can this scale to a full university lab?"**
> "Absolutely. The design is modular and replicable. The total cost of $5,400 is within most departmental budgets. I've documented every step in NETWORK_SETUP_PROGRESS.md and the technical report. A university could deploy 10 of these labs for $54,000—still cheaper than one commercial cyber range at $50,000-plus. Students could SSH into individual lab instances or work collaboratively on shared infrastructure. The open-source software stack eliminates per-seat licensing costs."

**Q6: "What's the biggest challenge you faced?"**
> "The biggest challenge was balancing complexity with reliability. My initial design used OPNsense as a virtual machine firewall, but it created a performance bottleneck and consumed too many CPU resources. After 20 hours of troubleshooting, I made the hard decision to pivot to the UniFi Dream Machine SE—a dedicated hardware firewall. This freed up VM resources and improved network throughput by 3x. The lesson: sometimes the right engineering decision is knowing when to abandon your initial plan."

**Q7: "How does this compare to cloud-based labs?"**
> "Cloud labs have advantages—easy access from anywhere, infinite scalability. But they have critical limitations for hospital scenarios. First, ongoing costs: a comparable AWS deployment would cost $200-500 per month, or $12,000-30,000 over five years. Second, you can't demonstrate air-gapped operation in the cloud—hospitals often isolate critical medical networks from the internet. Third, students don't get hands-on experience with physical IoT devices, which is crucial for understanding hardware attack surfaces. My hybrid approach captures the best of both worlds."

**Q8: "What will you do with the lab after graduation?"**
> "I'm planning to donate it to the Computer Engineering department for future students to use, with full documentation. I'm also documenting everything thoroughly enough that other universities could replicate it. Long-term, I'd like to present this work at conferences like IEEE EMBS or USENIX Security, and potentially publish the framework as an open-source educational resource."

---

## **After Presentation:**

### **Peer Review Strategy:**
Your grade depends on peer reviews, so:

✅ **DO:**
- Thank the audience after Q&A
- Stay around after to answer follow-up questions informally
- Offer to share documentation with interested classmates
- Demonstrate enthusiasm and expertise

❌ **DON'T:**
- Criticize other presenters (peers will notice and penalize you)
- Oversell or make unrealistic claims
- Dismiss valid questions or concerns
- Run over time (shows poor planning)

### **Collect Feedback:**
- Ask trusted classmates: "What could I improve?"
- Note questions you struggled to answer → prepare for final Q&A
- Review peer review forms (instructor provides at semester end)

---

# 📝 **ONE-PAGE CHEAT SHEET (Print This!):**

```
┌────────────────────────────────────────────────────────┐
│ 5-MIN PRESENTATION CHEAT SHEET                         │
│ Hospital IoT Homelab - David Moad                      │
├────────────────────────────────────────────────────────┤
│ TIMING MARKS:                                          │
│ • 0:50 → Should be finishing Slide 2 (Problem)        │
│ • 1:40 → Should be finishing Slide 3 (Background)     │
│ • 2:40 → Should be finishing Slide 4 (Solution)       │
│ • 3:10 → Should be finishing Slide 5 (Standards)      │
│ • 3:50 → Should be finishing Slide 6 (Timeline)       │
│ • 4:40 → Should be finishing Slide 7 (Progress)       │
│ • 5:00 → DONE. Thank audience, invite questions       │
├────────────────────────────────────────────────────────┤
│ KEY NUMBERS TO MEMORIZE:                               │
│ • Budget: $5,400                                       │
│ • Standards: 5 (HIPAA, NIST CSF, NIST 800-53, IEC,   │
│              ISO 27001)                                │
│ • Uptime: 99.98% (8 days)                             │
│ • Data: 2.7M+ heartbeat readings                      │
│ • Storage: 64TB (RAID-Z2)                             │
│ • Sensors: 4 (3 normal @62 BPM, 1 AFib @110±40)      │
├────────────────────────────────────────────────────────┤
│ RECOVERY PHRASES (if you blank):                       │
│ • "The key innovation here is..."                     │
│ • "This directly addresses the problem by..."         │
│ • "What makes this unique is the hybrid approach..."  │
│ • "Looking at the results we've achieved so far..."   │
├────────────────────────────────────────────────────────┤
│ EMERGENCY TIME SAVERS (if running late):               │
│ • Skip live demo → use screenshot only (-0:20)        │
│ • Shorten Future Plans to 1 sentence (-0:15)          │
│ • Skip reading budget line items → just say total     │
├────────────────────────────────────────────────────────┤
│ FINAL CHECKS:                                          │
│ □ Slide deck on laptop                                │
│ □ PDF backup on USB                                   │
│ □ Phone timer ready                                   │
│ □ Clicker/remote tested                               │
│ □ Water bottle nearby                                 │
│ □ Confident posture, deep breath, smile!              │
└────────────────────────────────────────────────────────┘
```

---

# 🎬 **FINAL SCRIPT (EXACTLY 5 MINUTES)**

**[Print this and practice 3× before presentation day]**

---

**SLIDE 1:** [0:10]

"Good morning everyone. My name is David Moad, and today I'm presenting my senior design project: a professional-grade hospital IoT simulation homelab for cybersecurity and machine learning research."

---

**SLIDE 2:** [0:40 / 0:50 cumulative]

"This is a solo project where I'm serving as system designer, network engineer, security analyst, and ML developer. The problem we're addressing is critical: Hospitals experience 45% more cyberattacks than the average industry. Recent examples include the Kettering Health ransomware attack right here in Ohio and the CommonSpirit breach affecting 140 hospitals. But here's the catch—you can't safely test cybersecurity defenses on production hospital systems because patient lives are at stake. And most students lack access to realistic healthcare IT infrastructure for training. That's the gap this project fills."

---

**SLIDE 3:** [0:50 / 1:40 cumulative]

"Why does this matter? Modern hospitals rely on dozens of IoT medical devices—patient monitors, infusion pumps, ventilators, imaging equipment. Each one is a potential attack vector. The consequences are severe: Ransomware can encrypt patient monitors, preventing clinicians from seeing vital signs. Attackers could tamper with infusion pump dosage data, causing overdoses. And because these devices are networked, malware spreads quickly, causing widespread failures. We need safe environments to train the next generation of healthcare cybersecurity professionals. That's what this homelab provides."

---

**SLIDE 4:** [1:00 / 2:40 cumulative]

"My solution is a hybrid physical and virtual homelab. The hardware includes a Dell R740XD server running TrueNAS for storage and VM hosting, a UniFi Dream Machine for enterprise-grade firewall and routing, a 24-port Power-over-Ethernet switch, and four Raspberry Pi 5s simulating patient vital monitors. All software is open-source: Node-RED for data processing, PostgreSQL for storage, Grafana for visualization, and Wazuh for security monitoring. I evaluated four design alternatives. Cloud labs have ongoing costs and can't demonstrate air-gapped operation—critical for hospital scenarios. Real medical devices were too expensive at $5,000-plus each and not replicable by other students. Software-only simulations lack hands-on hardware experience. So I selected a hybrid approach that balances cost, realism, and educational value at a total budget of $5,400."

---

**SLIDE 5:** [0:30 / 3:10 cumulative]

"This project enforces compliance with five major healthcare cybersecurity standards. HIPAA requires encryption and access controls—we implement AES-256 dataset encryption and SSH key-based authentication. The NIST Cybersecurity Framework's five functions are embedded in the architecture: identify, protect, detect, respond, and recover. NIST 800-53 security controls guide our firewall rules and VLAN segmentation. IEC 62443 for industrial control systems—applicable to medical IoT—informs our zone-based network isolation. And ISO 27001 provides our information security management system framework. The result is a comprehensive compliance training environment."

---

**SLIDE 6:** [0:40 / 3:50 cumulative]

"Here's our timeline and budget. The Gantt chart shows we've completed Phase 1—core infrastructure—represented by the green completed tasks. We're currently on schedule with the next critical milestone being MQTT pipeline deployment in December. The total budget is $5,400. The biggest investments are the Dell server at $1,800, storage drives at $1,400, and UniFi networking at $1,200. All software is open-source, so zero licensing costs. Over five years, this homelab costs $7,900 including electricity. A comparable cloud lab would cost $18,000—more than twice as expensive. And commercial cyber range solutions run $45,000 or more. This demonstrates that professional-grade training infrastructure is achievable at student budgets."

---

**SLIDE 7:** [0:50 / 4:40 cumulative]

"Let me show you what's working today. On the left is my physical setup: the server rack with Raspberry Pi sensors. On the right is the Node-RED dashboard showing real-time data flow. Key achievements: The network infrastructure is fully operational with a 10-gigabit backbone and sub-5-millisecond latency—exceeding our specification. Four IoT sensors have been running continuously with 99.98% uptime over an 8-day validation period, generating 2.7 million data points. Three sensors simulate normal resting heart rate at 62 beats per minute, and one simulates atrial fibrillation with high variability. We've validated air-gap capability—the entire system operates without internet, making it portable for demonstrations. And we have 64 terabytes of encrypted storage with RAID-Z2, meaning the system can tolerate two simultaneous disk failures without data loss."

---

**SLIDE 8:** [0:20 / 5:00 cumulative]

"Looking ahead, we have four more development phases planned. Phase 2 implements multi-VLAN network segmentation and Grafana visualization dashboards. Phase 3 focuses on machine learning to detect anomalies and differentiate between medical events—like atrial fibrillation—and cyberattacks. Phase 4 adds security tools including a SIEM and intrusion detection system. And Phase 5 deploys attack simulation with penetration testing and honeypots. The long-term vision is to create a replicable framework that other universities can adopt, with full open-source documentation. I'm also planning conference presentations to share these findings with the cybersecurity community. Thank you. I'm happy to take questions."

---

**[TOTAL: 5:00]**

---

# ✅ **PRESENTATION CHECKLIST**

## **1 Week Before:**
- [ ] Create all 8 slides in PowerPoint/Google Slides
- [ ] Export `hospital_homelab.drawio` to high-res PNG
- [ ] Take photos of physical setup (rack, Raspberry Pis, switch)
- [ ] Screenshot Node-RED dashboard at http://10.30.0.52:1880
- [ ] Practice full presentation 3× with timer
- [ ] Adjust timing to hit 4:50-5:00 mark

## **3 Days Before:**
- [ ] Get feedback from advisor or friend
- [ ] Revise slides based on feedback
- [ ] Practice Q&A responses (use list above)
- [ ] Print one-page cheat sheet
- [ ] Save slide deck to USB drive (backup)

## **1 Day Before:**
- [ ] Final practice run (record yourself on phone)
- [ ] Review recording: check body language, filler words
- [ ] Prepare professional outfit
- [ ] Charge laptop fully
- [ ] Test clicker/remote

## **Morning Of:**
- [ ] Arrive 10 minutes early
- [ ] Test laptop connection to projector
- [ ] Test clicker/remote in room
- [ ] Confirm slides display correctly
- [ ] Deep breath, confidence!

---

# 🏆 **SUCCESS METRICS**

**You'll know you nailed it if:**
- ✅ Finished at 4:50-5:00 (not 6:01!)
- ✅ No "um" or "uh" filler words
- ✅ Made eye contact with audience
- ✅ Answered Q&A questions confidently
- ✅ Classmates approached you after with questions
- ✅ Received high peer review scores (you'll see at semester end)

**Good luck, David! You've got this. Your project is impressive and your preparation shows. Trust the work you've done.**

---

**END OF PRESENTATION OUTLINE**
