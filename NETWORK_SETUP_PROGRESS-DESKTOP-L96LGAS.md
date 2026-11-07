# Hospital Homelab Network Setup Progress

## Date: Started 2025-11-09, Last Updated 2025-11-12

## STATUS: FLAT NETWORK COMPLETE ✓
All devices successfully migrated to VLAN30 (10.30.0.0/24)

---

## NETWORK INFRASTRUCTURE

### Core Network Devices
| Device | IP Address | Connection | Status |
|--------|------------|------------|--------|
| UDM-SE (Gateway) | 10.30.0.1 | N/A | ✓ Operational |
| TrueNAS Server | 10.30.0.44 | UDM-SE Port 3 | ✓ Operational |
| iDRAC 9 (Server Mgmt) | 10.30.0.45 | UDM-SE Port 5 | ✓ Operational |
| Node-RED VM | 10.30.0.52 | Virtual (TrueNAS) | ✓ Operational |
| U6 Pro WiFi AP | 10.30.0.246 | Switch Port 17 | ✓ Operational |
| Laptop "UltraMoad" | 10.30.0.122 | UDM-SE Port 1 | ✓ Connected |

### Raspberry Pi Devices (All on Switch Ports 2-5 with PoE)
| Device | IP Address | Script | BPM Pattern | Status |
|--------|------------|--------|-------------|--------|
| Pi #1 | 10.30.0.20 | HeartRate1Monitor.py | 62 BPM Normal | ✓ Running |
| Pi #2 | 10.30.0.21 | HeartRate2Monitor.py | 62 BPM Normal | ✓ Running |
| Pi #3 | 10.30.0.22 | HeartRate3Monitor.py | 62 BPM Normal | ✓ Running |
| Pi #4 | 10.30.0.23 | HeartRate4Monitor.py | 110±40 BPM AFib | ✓ Running |
| Pi #5-6 | TBD | Not configured | N/A | Pending |

### Network Configuration
- **Subnet**: 10.30.0.0/24 (255.255.255.0)
- **Gateway**: 10.30.0.1 (UDM-SE)
- **DNS**: 10.30.0.1 (UDM-SE)
- **DHCP Range**: 10.30.0.6 - 10.30.0.254
- **VLAN**: 30 (All devices)

---

## NETWORK TOPOLOGY

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
            ├─ Port 2: Raspberry Pi #1 (10.30.0.20) + PoE
            ├─ Port 3: Raspberry Pi #2 (10.30.0.21) + PoE
            ├─ Port 4: Raspberry Pi #3 (10.30.0.22) + PoE
            ├─ Port 5: Raspberry Pi #4 (10.30.0.23) + PoE
            ├─ Port 17: U6 Pro WiFi AP (10.30.0.246)
            └─ Port 26 (SFP+): Uplink to UDM-SE Port 11 [VLAN30]

         TrueNAS Server (10.30.0.44)
            ├─ Network: br0 interface → VLAN30
            ├─ Storage Pool: Hospital_Main
            │  ├─ Admin_Data dataset
            │  ├─ Guest_Access dataset
            │  ├─ IoT_Data dataset
            │  ├─ ISOs dataset
            │  └─ ML_Training dataset
            └─ VMs:
               ├─ node_red_vm (10.30.0.52) ✓ OPERATIONAL
               ├─ PostgreSQL VM (10.30.0.50) - Planned
               ├─ MQTT Broker VM (10.30.0.51) - Planned
               └─ Grafana VM (10.30.0.53) - Planned
```

---

## CREDENTIALS

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

**Node-RED VM (10.30.0.52)**
- Web: `http://10.30.0.52:1880`
- SSH: `ssh username@10.30.0.52`
- User: `username` | Pass: `password`
- VM Specs: 2 vCPUs, 2GB RAM, 20GB disk
- OS: Ubuntu Server 22.04 LTS
- Software: Node.js v20.x, npm v11.6.2
- Service: `nodered.service` (auto-starts on boot)

### Raspberry Pis (All use same password)
**Pi #1-4 SSH Access**
- SSH: `ssh r-pi-{1,2,3,4}@10.30.0.{20,21,22,23}`
- Pass: `password`
- Network: NetworkManager with auto-connect enabled
- Services: `heartrate{1,2,3,4}.service` (auto-start on boot)

**Encryption Key (for secure_temp_logger.py)**
- Key: `732a7722df86ee181382dfc13a5fb02041a09f341174283a9e0d4f4ef79ae9c4`
- Location: `storage_encryption_keys/dataset_Hospital_Main_keys.json`

---

## PROJECT ROADMAP

### Phase 1: Core Data Pipeline (HIGH PRIORITY)
1. **[ ] Install MQTT Broker VM (10.30.0.51)**
   - Ubuntu Server VM on TrueNAS
   - Install Mosquitto MQTT broker
   - Configure for 10.30.0.0/24 network
   - Auto-start systemd service

2. **[ ] Update Raspberry Pi Scripts for MQTT**
   - Install paho-mqtt library on all Pis
   - Modify HeartRate{1-4}Monitor.py scripts
   - Publish to topics: `hospital/heartrate/pi{1-4}`
   - Include: timestamp, BPM, Pi ID, status

3. **[ ] Create Node-RED MQTT Flows**
   - Subscribe to all Pi MQTT topics
   - Process and transform data
   - Build monitoring dashboard

4. **[ ] Install PostgreSQL VM (10.30.0.50)**
   - Ubuntu Server VM on TrueNAS
   - Configure time-series data storage
   - Create heartbeat data schema
   - Auto-start systemd service

5. **[ ] Node-RED → PostgreSQL Integration**
   - Install PostgreSQL node in Node-RED
   - Create data storage flows
   - Set up retention policies

### Phase 2: Visualization (MEDIUM PRIORITY)
6. **[ ] Install Grafana VM (10.30.0.53)**
   - Ubuntu Server VM on TrueNAS
   - Connect to PostgreSQL data source
   - Auto-start systemd service

7. **[ ] Build Grafana Dashboards**
   - Real-time heartbeat visualization
   - Panels for all 4 Raspberry Pis
   - Alerts for irregular heartbeats
   - Historical trends

8. **[ ] Configure Raspberry Pis #5-6**
   - Static IPs: 10.30.0.24, 10.30.0.25
   - Install monitoring scripts
   - Add to data pipeline

### Phase 3: Healthcare Layer (FUTURE)
- FHIR/Mirth Connect VM
- Orthanc PACS VM

### Phase 4: Security/Monitoring (FUTURE)
- Wazuh SIEM VM
- Keycloak IDM VM
- HashiCorp Vault VM
- Zeek/Suricata IDS-IPS VM
- ML-Automation VM

### Phase 5: Attack Lab (FUTURE)
- Kali Linux x2
- Metasploitable
- T-Pot honeypot

---

## COMPLETED MILESTONES

### Network Setup (Complete ✓)
- [✓] TrueNAS config backup saved
- [✓] Network flattened to single VLAN30 subnet
- [✓] All switch ports configured for VLAN30
- [✓] Switch uplink (Port 26 SFP+) set to VLAN30
- [✓] iDRAC 9 moved from VLAN20 to VLAN30
- [✓] U6 Pro WiFi AP configured on VLAN30
- [✓] TrueNAS SSH enabled (password auth)
- [✓] OPNsense VM deleted (freed resources)

### Raspberry Pi Setup (Complete ✓)
- [✓] 4 Raspberry Pis configured with static IPs
- [✓] NetworkManager auto-connect enabled on all Pis
- [✓] SSH enabled on all Pis
- [✓] HeartRate monitor scripts deployed
- [✓] Systemd services created for auto-start
- [✓] All Pis verified operational

### VM Infrastructure (Partial ✓)
- [✓] Node-RED VM operational (10.30.0.52)
- [ ] MQTT Broker VM (10.30.0.51) - Next priority
- [ ] PostgreSQL VM (10.30.0.50)
- [ ] Grafana VM (10.30.0.53)

---

## MAINTENANCE TASKS

### Documentation Needed
- [ ] Cloud Key G2 Plus IP address
- [ ] TrueNAS physical server hardware specs
- [ ] TrueNAS br0 physical NIC identification
- [ ] Dream Router 7 WAN IP from ISP
- [ ] UDM-SE WAN IP from Dream Router

### Network Cleanup
- [ ] Delete unused VLANs (10, 20, 40, 50) from UDM-SE
- [ ] Test air-gapped mode (disconnect WAN, verify operation)
- [ ] Delete opnsense dataset from TrueNAS

---

## TROUBLESHOOTING NOTES

### Common Issues
- **Devices on switch can't reach network**: Verify Switch Port 26 (SFP+ uplink) is set to correct VLAN
- **Pi not responding**: Check PoE power delivery and NetworkManager connection status
- **TrueNAS not accessible**: Verify br0 interface has correct IP and gateway

### Air-Gap Goal
System designed to operate fully isolated from internet once setup complete:
- Unplug WAN cable from UDM-SE Port 10
- All services continue on 10.30.0.0/24 network
- Portable for demos/presentations
- Simulates real isolated healthcare network
- Reconnect for updates when needed

---

## QUICK REFERENCE

### SSH One-Liners
```bash
# Ping all Raspberry Pis
for /L %i in (20,1,23) do @ping -n 1 10.30.0.%i | findstr "Reply TTL"

# Test all key devices
ping 10.30.0.1 && ping 10.30.0.44 && ping 10.30.0.45 && ping 10.30.0.52
```

### Network Summary
- **Gateway**: 10.30.0.1 (UDM-SE)
- **Raspberry Pis**: 10.30.0.20-23 (HeartRate monitors)
- **TrueNAS**: 10.30.0.44 (Storage + VM host)
- **iDRAC 9**: 10.30.0.45 (Server management)
- **VMs (Planned)**: 10.30.0.50-53 (PostgreSQL, MQTT, Node-RED, Grafana)
- **WiFi AP**: 10.30.0.246 (U6 Pro)

---

## WHEN RESUMING WORK

**Current State (2025-11-12):**
- ✓ Flat network complete - all devices on 10.30.0.0/24 (VLAN30)
- ✓ 4 Raspberry Pis operational with HeartRate monitors
- ✓ TrueNAS + iDRAC 9 + Node-RED VM all accessible
- **Next step**: Install MQTT Broker VM (10.30.0.51) to begin data pipeline

Tell Claude: "I'm continuing my hospital homelab setup. Read NETWORK_SETUP_PROGRESS.md for current status."
