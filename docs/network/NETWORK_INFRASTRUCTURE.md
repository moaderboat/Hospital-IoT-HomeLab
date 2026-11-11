# Hospital Homelab - Network Infrastructure

**Last Updated:** 2026-02-08
**Status:** Fully Operational

---

## Network Overview

### Core Network Devices

| Device | IP Address | Connection | Status |
|--------|------------|------------|--------|
| UDM-SE (Gateway) | 10.30.0.1 | N/A | ✓ Operational |
| UniFi Switch Pro Max 24 PoE | 10.30.0.10 | UDM-SE Port 11 (SFP+) | ✓ Operational |
| TrueNAS Server | 10.30.0.44 | UDM-SE Port 3 | ✓ Operational |
| iDRAC 9 (Server Mgmt) | 10.30.0.45 | UDM-SE Port 5 | ✓ Operational |
| U6 Pro WiFi AP | 10.30.0.246 | Switch Port 17 | ✓ Operational |
| Laptop "UltraMoad" | 10.30.0.122 | UDM-SE Port 1 | ✓ Connected |

---

## VLANs and Subnets

### VLAN 30 (Primary/Secure Network)
- **Subnet:** 10.30.0.0/24 (255.255.255.0)
- **Gateway:** 10.30.0.1 (UDM-SE)
- **DNS:** 10.30.0.1 (UDM-SE)
- **DHCP Range:** 10.30.0.6 - 10.30.0.254
- **Purpose:** Secure production network
- **Devices:**
  - All 5 heart rate monitor Raspberry Pis (10.30.0.20-24)
  - All VMs (10.30.0.50-58)
  - Secure balloon demo Pi #6 (10.30.0.25)
  - Admin laptop (10.30.0.122)

### VLAN 2 (Attack Lab / Vulnerable Network)
- **Subnet:** 192.168.50.0/24
- **VLAN ID:** 2
- **Gateway:** 192.168.50.1 (UDM-SE)
- **DHCP Range:** 192.168.50.10 - 192.168.50.254
- **Purpose:** Expo balloon demo - intentionally vulnerable for attack demonstrations
- **Devices:**
  - Vulnerable balloon demo Pi #7 (192.168.50.100 - static)
  - Attacker laptop (via Medical-IoT WiFi)
- **WiFi Network:** "Medical-IoT" (WPA2, SSID broadcasts, IoT optimization enabled)

---

## Firewall Rules

### VLAN Segmentation (UDM-SE)

**Rule 1: ALLOW_VLAN30_TO_VLAN2**
- **Type:** LAN In
- **Action:** Accept
- **Source:** Network 10.30.0.0/24 (VLAN30)
- **Destination:** Network 192.168.50.0/24 (VLAN2)
- **Protocol:** All
- **Match State:** New, Established, Related
- **Purpose:** Allow admin access from secure VLAN30 to vulnerable VLAN2
- **Status:** ✅ TESTED - WORKING

**Rule 2: BLOCK_VLAN2_TO_GATEWAY**
- **Type:** LAN Local (traffic TO router itself)
- **Action:** Drop
- **Source:** Network 192.168.50.0/24 (VLAN2)
- **Destination:** Router/Any
- **Protocol:** All
- **Match State:** New
- **Logging:** ✅ Enabled
- **Purpose:** Prevent compromised vulnerable Pi from accessing gateway
- **Status:** ✅ TESTED - WORKING

**Rule 3: BLOCK_VLAN2_TO_VLAN30**
- **Type:** LAN In
- **Action:** Drop
- **Source:** Network 192.168.50.0/24 (VLAN2)
- **Destination:** Network 10.30.0.0/24 (VLAN30)
- **Protocol:** All
- **Match State:** New (allows return traffic)
- **Logging:** ✅ Enabled
- **Purpose:** Block lateral movement from compromised VLAN2 to secure infrastructure
- **Status:** ✅ TESTED - WORKING

**Test Results:**
- ✅ Laptop (10.30.0.123) CAN ping and SSH to Pi #7 (192.168.50.100)
- ✅ Pi #7 CANNOT ping: 10.30.0.1 (gateway), 10.30.0.x (any VLAN30 device)
- ✅ Pi #7 CAN ping: 8.8.8.8 (internet access works)
- ✅ UDM-SE logs showing DROP events for blocked traffic

---

## Network Topology

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
            ├─ Port 5: Suricata IDS Laptop - Management Interface (10.30.0.191) [VLAN30, USB-C adapter #1] [PENDING]
            ├─ Port 6: Suricata IDS Laptop - Monitoring Interface (no IP) [Mirroring Port 15, USB-C adapter #2]
            ├─ Port 9: Raspberry Pi #1 (10.30.0.20) + PoE++ [Heart Rate Monitor]
            ├─ Port 10: Raspberry Pi #2 (10.30.0.21) + PoE++ [Heart Rate Monitor]
            ├─ Port 11: Raspberry Pi #3 (10.30.0.22) + PoE++ [Heart Rate Monitor]
            ├─ Port 12: Raspberry Pi #4 (10.30.0.23) + PoE++ [Heart Rate Monitor]
            ├─ Port 13: Raspberry Pi #5 (10.30.0.24) [External power] [Heart Rate Monitor]
            ├─ Port 14: Raspberry Pi #6 (10.30.0.25) [Secure Balloon Demo] + External Power (Pi 5)
            ├─ Port 15: Raspberry Pi #7 (192.168.50.100) [Vulnerable Balloon Demo, VLAN2] + External Power (Pi 5)
            ├─ Port 17: U6 Pro WiFi AP (10.30.0.246)
            └─ Port 26 (SFP+): Uplink to UDM-SE Port 11 [VLAN30]

         TrueNAS Server (10.30.0.44)
            ├─ Network: br0 interface → VLAN30
            ├─ Storage Pool: Hospital_Main
            └─ VMs: See VM_SERVICES_STATUS.md

         U6 Pro WiFi Access Point (10.30.0.246)
            ├─ Hospital_Admin (VLAN30) - WPA2/WPA3, admin devices
            ├─ Hospital_Guest (Open) - Guest network, isolated
            └─ Medical-IoT (VLAN2) - WPA2, IoT optimized, for vulnerable balloon demo
```

---

## IP Address Allocation

### Static Assignments (VLAN30)

**Infrastructure (10.30.0.1-19):**
- 10.30.0.1 - UDM-SE Gateway
- 10.30.0.10 - UniFi Switch Pro Max 24 PoE
- 10.30.0.44 - TrueNAS Server
- 10.30.0.45 - iDRAC 9

**Raspberry Pis (10.30.0.20-29):**
- 10.30.0.20 - Pi #1 (Heart Rate Monitor 1)
- 10.30.0.21 - Pi #2 (Heart Rate Monitor 2)
- 10.30.0.22 - Pi #3 (Heart Rate Monitor 3)
- 10.30.0.23 - Pi #4 (Heart Rate Monitor 4 - AFib simulation)
- 10.30.0.24 - Pi #5 (Heart Rate Monitor 5 - Anomaly detection)
- 10.30.0.25 - Pi #6 (Secure Balloon Demo)
- 10.30.0.26-29 - **AVAILABLE**

**VMs (10.30.0.50-99):**
- 10.30.0.50 - PostgreSQL Database VM
- 10.30.0.51 - MQTT Broker VM
- 10.30.0.52 - Node-RED VM
- 10.30.0.53 - Grafana VM
- 10.30.0.54 - Mirth Connect VM
- 10.30.0.55 - Wazuh SIEM VM
- 10.30.0.56 - HAPI FHIR Server VM
- 10.30.0.57 - Keycloak IDM VM
- 10.30.0.58 - HashiCorp Vault VM
- 10.30.0.59-99 - **AVAILABLE** for future VMs

**Workstations (10.30.0.100-149):**
- 10.30.0.122 - Laptop "UltraMoad"
- 10.30.0.123-149 - **AVAILABLE**

**WiFi/IoT (10.30.0.200-254):**
- 10.30.0.246 - U6 Pro WiFi AP

### Static Assignments (VLAN2)

**Balloon Demo (192.168.50.0/24):**
- 192.168.50.1 - Gateway (UDM-SE)
- 192.168.50.100 - Pi #7 (Vulnerable Balloon Demo)
- 192.168.50.10-254 - DHCP range (attacker laptop, etc.)

---

## Credentials

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

**UniFi Switch (10.30.0.10)**
- Managed via UDM-SE UniFi Controller
- Web: `https://10.30.0.1` → Devices → Switch

**U6 Pro WiFi AP (10.30.0.246)**
- Managed via UDM-SE UniFi Controller
- Web: `https://10.30.0.1` → Devices → WiFi

### WiFi Networks

**Hospital_Admin (VLAN30)**
- SSID: `Hospital_Admin`
- Security: WPA2/WPA3
- Password: `password`
- VLAN: 30 (Secure network)

**Hospital_Guest**
- SSID: `Hospital_Guest`
- Security: Open
- Purpose: Guest network (isolated)

**Medical-IoT (VLAN2)**
- SSID: `Medical-IoT`
- Security: WPA2
- Password: `password`
- VLAN: 2 (Vulnerable network)
- Purpose: Balloon demo attack lab

---

## Network Services

### DNS
- **Primary DNS:** 10.30.0.1 (UDM-SE)
- **Upstream DNS:** Cloudflare 1.1.1.1 (configured on UDM-SE)

### DHCP
- **VLAN30 DHCP Server:** UDM-SE (10.30.0.1)
  - Range: 10.30.0.6 - 10.30.0.254
  - Lease time: 86400 seconds (24 hours)
- **VLAN2 DHCP Server:** UDM-SE (192.168.50.1)
  - Range: 192.168.50.10 - 192.168.50.254
  - Lease time: 86400 seconds (24 hours)

### NTP
- **NTP Server:** UDM-SE syncs from pool.ntp.org
- **Clients:** All devices sync from UDM-SE (10.30.0.1)

---

## TODO / Future Network Improvements

- [ ] Deploy Wazuh agent to TrueNAS server (10.30.0.44)
- [ ] Configure UDM-SE syslog forwarding to Wazuh (10.30.0.55)
- [ ] Delete unused VLANs from UDM-SE (VLAN10, VLAN20, VLAN40)
- [ ] Configure PostgreSQL data retention policy (18+ months runway - not urgent)
- [ ] Consider adding IDS/IPS on VLAN2 for attack detection demos

---

**Document Created:** 2026-02-08
**Related Documents:**
- VM_SERVICES_STATUS.md - Virtual machine configurations
- RASPBERRY_PI_STATUS.md - Raspberry Pi configurations
- balloon-demo/CURRENT_STATUS_2026-02-06.md - Balloon demo specific status
