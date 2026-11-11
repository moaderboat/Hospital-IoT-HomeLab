# Balloon Security Demo - UDM-SE Network Configuration

**Purpose:** Network segmentation for security demonstration comparing secure vs vulnerable industrial control systems

**Date Created:** 2026-02-01
**Last Updated:** 2026-02-01

---

## OVERVIEW

This configuration adds **VLAN50** (Vulnerable Demo Network) to the existing hospital homelab infrastructure while maintaining **VLAN30** (Secure Production Network). The two systems run identical hardware but with different security postures to demonstrate the importance of defense-in-depth.

### Demo Systems

| System | Raspberry Pi | IP Address | VLAN | Security Posture |
|--------|--------------|------------|------|------------------|
| **Secure System** | Pi #6 (new) | 10.30.0.25 | VLAN30 | ✓ Firewall, ✓ Keycloak Auth, ✓ MQTT TLS, ✓ Wazuh Logging |
| **Vulnerable System** | Pi #7 (new) | 192.168.50.100 | VLAN50 | ✗ No Firewall, ✗ No Auth, ✗ No Encryption, ✗ No Logging |

---

## NETWORK ARCHITECTURE

```
Internet → Dream Router 7 (Home ISP)
            ↓ Port 10
         UDM-SE (Gateway/Router/Firewall)
            ├─ VLAN30 (10.30.0.0/24) - SECURE PRODUCTION NETWORK
            │  ├─ Gateway: 10.30.0.1
            │  ├─ 5× Heart Rate Monitor Pis (10.30.0.20-24)
            │  ├─ Pi #6 Secure Balloon Demo (10.30.0.25) **NEW**
            │  ├─ 8× VMs (PostgreSQL, MQTT, Node-RED, Grafana, Mirth, HAPI FHIR, Wazuh, Keycloak)
            │  └─ Firewall Rules: DENY from VLAN50, ALLOW to VLAN20 services
            │
            ├─ VLAN50 (192.168.50.0/24) - VULNERABLE DEMO NETWORK **NEW**
            │  ├─ Gateway: 192.168.50.1
            │  ├─ Pi #7 Vulnerable Balloon Demo (192.168.50.100) **NEW**
            │  ├─ Attacker Laptop (192.168.50.10) - for demo attacks
            │  └─ Firewall Rules: BLOCKED from VLAN30, NO PROTECTION
            │
            └─ Port 11: Uplink to Switch Pro Max Port 26 (SFP+) - Trunk VLAN30+VLAN50
```

---

## VLAN CONFIGURATION

### VLAN30 - Secure Production Network (EXISTING)
**Purpose:** Production hospital homelab infrastructure + secure balloon demo

| Parameter | Value |
|-----------|-------|
| VLAN ID | 30 |
| Network | 10.30.0.0/24 |
| Gateway | 10.30.0.1 |
| DNS | 10.30.0.1 (UDM-SE) |
| DHCP Range | 10.30.0.6 - 10.30.0.254 |
| DHCP Enabled | Yes |
| Firewall | Enabled (default allow, explicit denies) |

**Static IP Reservations:**
- 10.30.0.10: UniFi Switch Pro Max 24 PoE
- 10.30.0.20-24: Raspberry Pi #1-5 (Heart Rate Monitors)
- **10.30.0.25: Raspberry Pi #6 (Secure Balloon Demo)** ← NEW
- 10.30.0.44: TrueNAS Server
- 10.30.0.45: iDRAC 9
- 10.30.0.50: PostgreSQL VM
- 10.30.0.51: MQTT Broker VM
- 10.30.0.52: Node-RED VM
- 10.30.0.53: Grafana VM
- 10.30.0.54: Mirth Connect VM
- 10.30.0.55: Wazuh SIEM VM
- 10.30.0.56: HAPI FHIR Server VM
- 10.30.0.57: Keycloak IDM VM
- 10.30.0.246: U6 Pro WiFi AP

---

### VLAN50 - Vulnerable Demo Network (NEW)
**Purpose:** Isolated vulnerable balloon demo for security attack demonstrations

| Parameter | Value |
|-----------|-------|
| VLAN ID | 50 |
| Network | 192.168.50.0/24 |
| Gateway | 192.168.50.1 |
| DNS | 192.168.50.1 (UDM-SE, forwarding to 10.30.0.1) |
| DHCP Range | 192.168.50.2 - 192.168.50.99 |
| DHCP Enabled | Yes (for attacker laptop) |
| Firewall | **INTENTIONALLY MINIMAL** (for demo purposes) |

**Static IP Reservations:**
- **192.168.50.100: Raspberry Pi #7 (Vulnerable Balloon Demo)** ← NEW
- 192.168.50.10-20: Reserved for attacker laptops (DHCP or static)

**Security Posture:**
- ⚠️ **NO firewall protection from internet**
- ⚠️ **NO inter-VLAN routing to VLAN30** (isolated from production)
- ⚠️ **NO Wazuh monitoring**
- ⚠️ **NO Keycloak authentication**
- ⚠️ **NO MQTT encryption**
- ⚠️ Direct internet access allowed (for demo purposes)

---

## UDM-SE FIREWALL RULES

### Rule Set: Protect VLAN30 from VLAN50

**Rule 1: Block VLAN50 → VLAN30**
```
Name: BLOCK_VLAN50_TO_VLAN30
Type: LAN IN
Action: DROP
Source: VLAN50 Network (192.168.50.0/24)
Destination: VLAN30 Network (10.30.0.0/24)
Protocol: All
Logging: Enabled (log blocked attempts)
Priority: 1000 (high priority)
```

**Purpose:** Prevent vulnerable system and attackers from accessing production infrastructure

**Rule 2: Block VLAN50 → VLAN30 Services (Specific)**
```
Name: BLOCK_VLAN50_TO_KEYCLOAK
Type: LAN IN
Action: DROP
Source: VLAN50 Network (192.168.50.0/24)
Destination: 10.30.0.57 (Keycloak)
Protocol: TCP
Port: 8080
Logging: Enabled
Priority: 1001
```

```
Name: BLOCK_VLAN50_TO_WAZUH
Type: LAN IN
Action: DROP
Source: VLAN50 Network (192.168.50.0/24)
Destination: 10.30.0.55 (Wazuh)
Protocol: TCP
Port: 443, 1514, 1515
Logging: Enabled
Priority: 1002
```

```
Name: BLOCK_VLAN50_TO_MQTT
Type: LAN IN
Action: DROP
Source: VLAN50 Network (192.168.50.0/24)
Destination: 10.30.0.51 (MQTT Broker)
Protocol: TCP
Port: 1883, 8883
Logging: Enabled
Priority: 1003
```

### Rule Set: Allow VLAN30 → All (Production Access)

**Rule 3: Allow VLAN30 to Internet**
```
Name: ALLOW_VLAN30_TO_INTERNET
Type: LAN OUT
Action: ACCEPT
Source: VLAN30 Network (10.30.0.0/24)
Destination: Any
Protocol: All
Logging: Disabled (too verbose)
Priority: 2000
```

**Rule 4: Allow VLAN30 Inter-VLAN Communication**
```
Name: ALLOW_VLAN30_INTERNAL
Type: LAN LOCAL
Action: ACCEPT
Source: VLAN30 Network (10.30.0.0/24)
Destination: VLAN30 Network (10.30.0.0/24)
Protocol: All
Logging: Disabled
Priority: 2001
```

### Rule Set: VLAN50 Isolation (Minimal Security)

**Rule 5: Allow VLAN50 to Internet (Vulnerable)**
```
Name: ALLOW_VLAN50_TO_INTERNET
Type: LAN OUT
Action: ACCEPT
Source: VLAN50 Network (192.168.50.0/24)
Destination: Any
Protocol: All
Logging: Enabled (track attacker traffic)
Priority: 3000
```

**Rule 6: Allow VLAN50 Internal (Attack Scenario)**
```
Name: ALLOW_VLAN50_INTERNAL
Type: LAN LOCAL
Action: ACCEPT
Source: VLAN50 Network (192.168.50.0/24)
Destination: VLAN50 Network (192.168.50.0/24)
Protocol: All
Logging: Disabled
Priority: 3001
```

**Purpose:** Allow attacker laptop to communicate with vulnerable Pi #7 for demonstration

---

## SWITCH CONFIGURATION

### UniFi Switch Pro Max 24 PoE - Port Assignments

**Existing Ports (VLAN30):**
- Port 9: Raspberry Pi #1 (10.30.0.20) - PoE++
- Port 10: Raspberry Pi #2 (10.30.0.21) - PoE++
- Port 11: Raspberry Pi #3 (10.30.0.22) - PoE++
- Port 12: Raspberry Pi #4 (10.30.0.23) - PoE++
- Port 13: Raspberry Pi #5 (10.30.0.24) - External Power
- Port 17: U6 Pro WiFi AP (10.30.0.246) - PoE+
- Port 26: Uplink to UDM-SE Port 11 (SFP+ Trunk)

**New Ports for Balloon Demo:**

**Port 14: Raspberry Pi #6 - Secure Balloon Demo** ← NEW
```
Port: 14
VLAN: 30 (Native/Untagged)
PoE: PoE++ (25.5W)
Device: Raspberry Pi 5 8GB
IP: 10.30.0.25
Purpose: Secure balloon control system
Security: Full protection (firewall, auth, encryption, logging)
```

**Port 15: Raspberry Pi #7 - Vulnerable Balloon Demo** ← NEW
```
Port: 15
VLAN: 50 (Native/Untagged)
PoE: PoE++ (25.5W)
Device: Raspberry Pi 5 8GB
IP: 192.168.50.100
Purpose: Vulnerable balloon control system (DEMO TARGET)
Security: NONE (intentionally vulnerable for demonstration)
```

**Port 16: Attacker Laptop Port** ← NEW (OPTIONAL)
```
Port: 16
VLAN: 50 (Native/Untagged)
PoE: No
Device: Laptop for attack demonstrations
IP: 192.168.50.10 (DHCP)
Purpose: Launch attacks against Pi #7 during expo
Security: NONE (attacker access)
```

**Port 26: Uplink Configuration** (UPDATED)
```
Port: 26 (SFP+ to UDM-SE Port 11)
Mode: Trunk
Tagged VLANs: 30, 50
Native VLAN: 30
Purpose: Carry both production and demo traffic
```

---

## MQTT BROKER CONFIGURATION

### Existing Broker - VLAN30 (10.30.0.51) - SECURE

**Current Configuration:**
- IP: 10.30.0.51 (VLAN30)
- Port: 1883 (unencrypted - internal only)
- Port: 8883 (TLS encrypted - for production)
- Authentication: None currently (internal trust model)
- Encryption: TLS 1.3 for port 8883
- Purpose: Production heart rate monitoring

**Update for Secure Pi #6:**
- Pi #6 connects to: `mqtt://10.30.0.51:8883` (TLS encrypted)
- Client certificate required
- Topics: `secure/pi6/pressure`, `secure/pi6/command`, `secure/pi6/status`

### New Broker - VLAN50 (192.168.50.1) - VULNERABLE (OPTIONAL)

**Option 1: Dedicated Vulnerable Broker** (Recommended for isolation)
```
IP: 192.168.50.1 (run on UDM-SE or lightweight container)
Port: 1883 (unencrypted - NO TLS)
Authentication: NONE (allow anonymous)
Encryption: NONE (plaintext traffic)
Topics: pressure/sensor, valve/command, pump/command
Purpose: Demonstrate insecure MQTT (easy to sniff/inject)
```

**Option 2: Mosquitto on Pi #7 Itself** (Simpler for demo)
```
IP: 192.168.50.100 (localhost + LAN access)
Port: 1883 (unencrypted)
Authentication: NONE
Configuration: Allow anonymous, bind to 0.0.0.0
Purpose: Self-contained vulnerable system
Advantage: Portable demo (all-in-one Pi)
```

**Recommendation:** Use Option 2 (local broker on Pi #7) for simplicity and portability

---

## SECURITY ARCHITECTURE COMPARISON

### Secure System (Pi #6 on VLAN30) - Defense in Depth

```
Layer 1: Network Segmentation
├─ VLAN30 isolated from VLAN50
├─ UDM-SE firewall rules (DROP from VLAN50)
└─ Inter-VLAN routing denied

Layer 2: Authentication & Authorization
├─ Keycloak OAuth2 token required for commands
├─ User roles enforced (balloon-operator)
└─ Session timeout: 5 minutes

Layer 3: Encryption
├─ MQTT over TLS 1.3 (port 8883)
├─ Client certificates validated
└─ Message payload encryption

Layer 4: Monitoring & Logging
├─ Wazuh agent sends all events to SIEM (10.30.0.55)
├─ Authentication attempts logged
├─ Pressure anomalies logged
└─ Command execution audit trail

Layer 5: Input Validation
├─ Pressure sensor bounds checking (0-15 PSI)
├─ Command validation (authorized users only)
├─ Rate limiting (max 1 command/second)
└─ Sensor data anomaly detection

Layer 6: Fail-Safe Design
├─ Normally-closed solenoid valve (closes on power loss)
├─ Software pressure limits (3.5 PSI emergency stop)
├─ Hardware relief valve (5 PSI mechanical safety)
└─ Emergency cutoff switch (physical kill switch)
```

**Result:** PROTECTED - Attack attempts blocked and logged

---

### Vulnerable System (Pi #7 on VLAN50) - No Security

```
Layer 1: Network Segmentation
├─ VLAN50 has NO firewall protection
├─ Direct internet access (if needed for demo)
└─ Attackers can join VLAN50 freely

Layer 2: Authentication & Authorization
└─ NONE - No Keycloak, no tokens, no access control

Layer 3: Encryption
└─ NONE - Plaintext MQTT (port 1883), no TLS

Layer 4: Monitoring & Logging
└─ NONE - No Wazuh agent, no SIEM logging

Layer 5: Input Validation
└─ NONE - Trusts all sensor data, no bounds checking

Layer 6: Fail-Safe Design
├─ Normally-closed valve (ONLY safety layer)
├─ Software limits (bypassed by fake sensor data)
├─ Hardware relief valve (5 PSI mechanical - last resort)
└─ Emergency cutoff switch (physical kill switch)
```

**Result:** COMPROMISED - Attacker injects fake pressure data, balloon pops

---

## ATTACK DEMONSTRATION FLOW

### Setup (Before Expo)
1. Both Pi #6 and Pi #7 running identical hardware
2. Pi #6 on VLAN30 (10.30.0.25) - fully secured
3. Pi #7 on VLAN50 (192.168.50.100) - no security
4. Attacker laptop on VLAN50 (192.168.50.10)

### Demo Script

**Step 1: Show Secure System (Pi #6)**
```bash
# On attacker laptop (VLAN30 attempt)
mosquitto_pub -h 10.30.0.51 -p 8883 -t "secure/pi6/command" -m "START_INFLATE"

# Result: CONNECTION REFUSED (firewall blocks VLAN50→VLAN30)
# Wazuh logs the attempt: "Unauthorized access attempt from 192.168.50.10"
```

**Step 2: Attack Vulnerable System (Pi #7)**
```bash
# On attacker laptop (VLAN50 - same network as Pi #7)
# Scan for MQTT broker
nmap -p 1883 192.168.50.100

# Subscribe to see real pressure data
mosquitto_sub -h 192.168.50.100 -p 1883 -t "pressure/sensor"
# Output: {"pressure_psi": 2.5, "timestamp": "2026-02-01T10:30:00"}

# Inject fake LOW pressure reading
mosquitto_pub -h 192.168.50.100 -p 1883 -t "pressure/sensor" -m '{"pressure_psi": 0.5}'

# Pi #7 believes pressure is LOW (0.5 PSI)
# Software keeps pump running
# Actual balloon pressure climbs to 4.5 PSI
# BALLOON POPS! 💥
```

**Step 3: Show Aftermath**
- Secure system (Pi #6): Balloon intact, attack logged in Wazuh
- Vulnerable system (Pi #7): Balloon popped, no logs, no detection
- Audience sees visual proof of security importance

---

## IMPLEMENTATION STEPS

### 1. UDM-SE Configuration

**Create VLAN50:**
```
Navigate to: Settings → Networks → Create New Network
Name: VLAN50-Vulnerable-Demo
VLAN ID: 50
Gateway/Subnet: 192.168.50.1/24
DHCP:
  - Mode: DHCP Server
  - Range: 192.168.50.2 - 192.168.50.99
  - Lease Time: 86400 seconds (24 hours)
DNS: Auto (use gateway)
Domain Name: vlan50.local
IGMP Snooping: Disabled
Multicast DNS: Disabled
IPv6: Disabled
```

**Add Firewall Rules:**
```
Navigate to: Settings → Security → Firewall → Rules → Create Entry

Rule 1:
  Name: BLOCK_VLAN50_TO_VLAN30
  Type: LAN In
  Action: Drop
  Source: Network - VLAN50-Vulnerable-Demo
  Destination: Network - VLAN30 (Default)
  Protocol: All
  Logging: Enabled

Rule 2:
  Name: ALLOW_VLAN50_INTERNET
  Type: LAN Out
  Action: Accept
  Source: Network - VLAN50-Vulnerable-Demo
  Destination: Any
  Protocol: All
  Logging: Enabled (for demo visibility)
```

**Add Static IP Reservations:**
```
Navigate to: Settings → Networks → VLAN30 → DHCP → Static IP

New Reservation:
  IP Address: 10.30.0.25
  MAC Address: [Pi #6 MAC address]
  Name: Pi-6-Secure-Balloon-Demo
  Fixed IP: Enabled

Navigate to: Settings → Networks → VLAN50-Vulnerable-Demo → DHCP → Static IP

New Reservation:
  IP Address: 192.168.50.100
  MAC Address: [Pi #7 MAC address]
  Name: Pi-7-Vulnerable-Balloon-Demo
  Fixed IP: Enabled
```

### 2. Switch Configuration

**Configure Port 14 (Pi #6 - Secure):**
```
Navigate to: UniFi Devices → Switch Pro Max → Ports → Port 14
Name: Pi-6-Secure-Balloon
Profile Override: Enabled
  - Native Network: VLAN30 (Default)
  - Tagged Networks: None
  - Port Isolation: Disabled
  - PoE Mode: PoE++ (25.5W)
  - PoE Priority: High
Link Aggregation: Disabled
Apply Changes
```

**Configure Port 15 (Pi #7 - Vulnerable):**
```
Navigate to: UniFi Devices → Switch Pro Max → Ports → Port 15
Name: Pi-7-Vulnerable-Balloon
Profile Override: Enabled
  - Native Network: VLAN50-Vulnerable-Demo
  - Tagged Networks: None
  - Port Isolation: Disabled
  - PoE Mode: PoE++ (25.5W)
  - PoE Priority: High
Link Aggregation: Disabled
Apply Changes
```

**Update Port 26 (Trunk Uplink):**
```
Navigate to: UniFi Devices → Switch Pro Max → Ports → Port 26
Name: Uplink-to-UDM-SE
Profile Override: Enabled
  - Port Profile: Trunk
  - Native Network: VLAN30 (Default)
  - Tagged Networks: VLAN30, VLAN50
  - Link Aggregation: Disabled
Apply Changes
```

### 3. Raspberry Pi Network Configuration

**Pi #6 (Secure System) - Static IP on VLAN30:**
```bash
# SSH to Pi #6
ssh pi@<temporary-ip>

# Install NetworkManager if not present
sudo apt update && sudo apt install -y network-manager

# Configure static IP
sudo nmcli con mod "Wired connection 1" \
  ipv4.addresses "10.30.0.25/24" \
  ipv4.gateway "10.30.0.1" \
  ipv4.dns "10.30.0.1" \
  ipv4.method manual \
  connection.autoconnect yes

# Apply configuration
sudo nmcli con up "Wired connection 1"

# Verify
ip addr show eth0
ping 10.30.0.1
```

**Pi #7 (Vulnerable System) - Static IP on VLAN50:**
```bash
# SSH to Pi #7
ssh pi@<temporary-ip>

# Install NetworkManager
sudo apt update && sudo apt install -y network-manager

# Configure static IP
sudo nmcli con mod "Wired connection 1" \
  ipv4.addresses "192.168.50.100/24" \
  ipv4.gateway "192.168.50.1" \
  ipv4.dns "192.168.50.1" \
  ipv4.method manual \
  connection.autoconnect yes

# Apply configuration
sudo nmcli con up "Wired connection 1"

# Verify
ip addr show eth0
ping 192.168.50.1
```

---

## TESTING & VALIDATION

### Test 1: Network Connectivity

**From Pi #6 (VLAN30):**
```bash
# Should succeed
ping 10.30.0.1        # Gateway
ping 10.30.0.51       # MQTT Broker
ping 10.30.0.55       # Wazuh SIEM
ping 10.30.0.57       # Keycloak

# Should fail (VLAN isolation)
ping 192.168.50.100   # Pi #7 on VLAN50
```

**From Pi #7 (VLAN50):**
```bash
# Should succeed
ping 192.168.50.1     # Gateway
ping 8.8.8.8          # Internet (for demo purposes)

# Should fail (firewall blocks)
ping 10.30.0.25       # Pi #6 on VLAN30
ping 10.30.0.51       # MQTT Broker on VLAN30
ping 10.30.0.55       # Wazuh on VLAN30
```

### Test 2: Firewall Rules

**From Attacker Laptop (VLAN50):**
```bash
# Should timeout (blocked by firewall)
telnet 10.30.0.51 1883   # MQTT on VLAN30
curl http://10.30.0.57:8080  # Keycloak on VLAN30

# Should succeed (same VLAN)
telnet 192.168.50.100 1883   # Pi #7 MQTT (vulnerable)
```

**Check UDM-SE Firewall Logs:**
```
Navigate to: Settings → System → Logs → Firewall
Filter: Source = 192.168.50.0/24
Verify: DROP events logged for VLAN50 → VLAN30 attempts
```

### Test 3: MQTT Communication

**Secure System (Pi #6):**
```bash
# From laptop on VLAN30
mosquitto_sub -h 10.30.0.51 -p 8883 \
  --cafile mqtt_ca.crt \
  --cert client.crt \
  --key client.key \
  -t "secure/pi6/#"

# Should see encrypted telemetry from Pi #6
```

**Vulnerable System (Pi #7):**
```bash
# From attacker laptop on VLAN50
mosquitto_sub -h 192.168.50.100 -p 1883 -t "#"

# Should see PLAINTEXT telemetry (no encryption, no auth)
```

### Test 4: Attack Simulation

**Step 1: Baseline (normal operation)**
```bash
# Pi #7 operating normally
# Pressure sensor reading: 2.0 PSI
# Balloon inflating safely
```

**Step 2: Inject fake data**
```bash
# From attacker laptop on VLAN50
mosquitto_pub -h 192.168.50.100 -p 1883 \
  -t "pressure/sensor" \
  -m '{"pressure_psi": 0.5, "timestamp": "2026-02-01T12:00:00"}'

# Pi #7 receives fake reading: 0.5 PSI
# Software thinks pressure is LOW
# Pump continues running
# Actual pressure rises to 4.5 PSI
# Balloon pops! 💥
```

**Step 3: Verify secure system protected**
```bash
# Try same attack on Pi #6 (should fail)
mosquitto_pub -h 10.30.0.25 -p 1883 \
  -t "secure/pi6/command" \
  -m "START_INFLATE"

# Result: Connection refused (firewall blocked)
# Wazuh logs the attempt
```

---

## WAZUH MONITORING CONFIGURATION

### Pi #6 (Secure System) - Install Wazuh Agent

**Install Agent:**
```bash
# SSH to Pi #6
ssh r-pi-6@10.30.0.25

# Download and install Wazuh agent
curl -s https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.9.2-1_arm64.deb \
  -o wazuh-agent.deb

sudo WAZUH_MANAGER='10.30.0.55' \
  WAZUH_AGENT_NAME='pi-6-secure-balloon' \
  dpkg -i wazuh-agent.deb

# Start agent
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent

# Verify
sudo systemctl status wazuh-agent
```

**Configure Monitoring Rules:**
```xml
<!-- /var/ossec/etc/ossec.conf on Wazuh Manager (10.30.0.55) -->
<group name="balloon-demo">
  <rule id="100010" level="5">
    <decoded_as>json</decoded_as>
    <field name="system_id">PI6_SECURE</field>
    <field name="event_type">authentication</field>
    <description>Balloon demo authentication event</description>
  </rule>

  <rule id="100011" level="10">
    <if_sid>100010</if_sid>
    <field name="severity">warning</field>
    <description>Balloon demo authentication failure</description>
  </rule>

  <rule id="100012" level="12">
    <decoded_as>json</decoded_as>
    <field name="system_id">PI6_SECURE</field>
    <field name="event_type">safety</field>
    <field name="severity">critical</field>
    <description>Balloon demo emergency stop triggered</description>
  </rule>
</group>
```

### Pi #7 (Vulnerable System) - NO Wazuh Agent

**Intentionally Unmonitored:**
- No Wazuh agent installed
- No logging to SIEM
- Attack goes undetected (demonstrates blind spot)

---

## DOCUMENTATION & LABELING

### Physical Labels for Expo

**Pi #6 (Secure System) - Green Labels:**
```
Front Label:
  SECURE BALLOON SYSTEM
  Raspberry Pi #6
  IP: 10.30.0.25
  VLAN: 30 (Protected)

  ✓ Firewall Protected
  ✓ Keycloak Authentication
  ✓ MQTT TLS Encryption
  ✓ Wazuh SIEM Monitoring
  ✓ Input Validation

  STATUS: PROTECTED
```

**Pi #7 (Vulnerable System) - Red Labels:**
```
Front Label:
  VULNERABLE BALLOON SYSTEM
  Raspberry Pi #7
  IP: 192.168.50.100
  VLAN: 50 (Exposed)

  ✗ NO Firewall
  ✗ NO Authentication
  ✗ NO Encryption
  ✗ NO Monitoring
  ✗ NO Input Validation

  ⚠️ WARNING: ATTACK TARGET ⚠️
```

### Network Diagram for Display

Create a poster showing:
1. Side-by-side comparison of both systems
2. Network topology with VLAN segregation
3. Attack flow diagram (attacker → VLAN50 → Pi #7)
4. Defense layers for Pi #6
5. Security gaps for Pi #7

---

## BILL OF MATERIALS UPDATE

### Additional Network Equipment Needed

| Item | Qty | Purpose | Cost |
|------|-----|---------|------|
| Cat6a Ethernet Cable (6 ft) | 2 | Pi #6 and Pi #7 to switch | Included in main BOM |
| VLAN Labels (printed vinyl) | 2 sets | Physical system identification | Included in main BOM |

**Total Additional Cost:** $0 (already covered in BALLOON_DEMO_BOM_FINAL.md)

---

## ROLLBACK PLAN

If network configuration causes issues with production infrastructure:

**Quick Rollback Steps:**
1. Navigate to UDM-SE → Settings → Networks
2. Disable VLAN50 network
3. Revert Switch Port 26 to VLAN30 only (remove VLAN50 from trunk)
4. Power off Pi #6 and Pi #7
5. Production network (VLAN30) continues unaffected

**Full Rollback:**
1. Delete VLAN50 network from UDM-SE
2. Delete firewall rules (BLOCK_VLAN50_TO_VLAN30, etc.)
3. Reset Switch Ports 14-16 to default settings
4. Remove static IP reservations for Pi #6 and Pi #7
5. Archive balloon demo scripts for future use

---

## MAINTENANCE

### Regular Checks Before Expo

- [ ] Verify Pi #6 connected to VLAN30 (10.30.0.25)
- [ ] Verify Pi #7 connected to VLAN50 (192.168.50.100)
- [ ] Test firewall rules (VLAN50 → VLAN30 blocked)
- [ ] Verify Wazuh agent active on Pi #6
- [ ] Test MQTT TLS connection to 10.30.0.51:8883
- [ ] Test vulnerable MQTT on Pi #7 (port 1883, no auth)
- [ ] Verify both balloons inflated and ready
- [ ] Test emergency cutoff switches on both systems
- [ ] Check plexiglass shields secured
- [ ] Test attack script from laptop on VLAN50

### Post-Demo Cleanup

- [ ] Power off both balloon demo systems
- [ ] Disconnect Pi #6 and Pi #7 from switch
- [ ] Optionally: Disable VLAN50 if not needed for future demos
- [ ] Keep firewall rules in place for security
- [ ] Document any lessons learned or improvements
- [ ] Save Wazuh logs for analysis/reporting

---

**Document Version:** 1.0 - Initial Network Configuration
**Last Tested:** Not yet implemented
**Status:** Ready for deployment
**Approved By:** Team 41

**Next Steps:**
1. Deploy VLAN50 on UDM-SE
2. Configure switch ports 14-15
3. Set up Pi #6 and Pi #7 with static IPs
4. Install Wazuh agent on Pi #6
5. Test firewall rules
6. Deploy balloon control scripts
7. Run full attack simulation test
