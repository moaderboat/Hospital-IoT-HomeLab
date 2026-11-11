# Suricata IDS - Port Mirroring Configuration

**Last Updated:** 2026-02-09
**Status:** In Progress - Configuring SPAN port on UDM-SE

---

## Decision: IDS Mode (Not IPS)

**For healthcare systems, we use IDS (Intrusion Detection System) mode:**
- ✅ Monitors and logs all traffic
- ✅ Alerts on suspicious activity
- ✅ Does NOT block traffic (critical for healthcare - no false positive blocking)
- ✅ Cannot cause downtime
- ✅ Allows forensic analysis of attacks
- ✅ Perfect for demonstrations

**NOT using IPS (Intrusion Prevention System):**
- ❌ Actively blocks traffic (dangerous in healthcare)
- ❌ Can cause false positives blocking legitimate medical data
- ❌ Single point of failure
- ❌ Liability risk in healthcare environment

---

## Current Problem

Suricata VM (10.30.0.59) is on VLAN30 but only sees:
- Traffic TO/FROM itself (its own SSH sessions, curls, etc.)
- Does NOT see traffic between other devices (laptop ↔ Pis, VMs ↔ VMs)

**Root Cause:** Switched network - devices communicate directly through switch without Suricata in the path.

**Solution:** Configure port mirroring (SPAN) on UDM-SE to copy all traffic to Suricata.

---

## UDM-SE Network Topology Discovered

**Physical Interfaces:**
- `eth0-eth7` - Individual switch ports (virtualized from switch0)
- `eth8` - 2.5G WAN port (NO-CARRIER - not used)
- `eth9` - 10G WAN port (uplink to Dream Router 7)
- `eth10` - 10G SFP+ port (uplink to UniFi Switch)
- `switch0` - Internal switch fabric (8 ports)

**VLAN Bridges:**
- `br0` - Default/Management (VLAN 1)
- `br2` - VLAN 2 (Vulnerable balloon demo - 192.168.50.0/24)
- `br10` - VLAN 10
- `br20` - VLAN 20
- `br30` - **VLAN 30 (Our primary network - 10.30.0.0/24)**
- `br40` - VLAN 40
- `br50` - VLAN 50

**VLAN Interfaces:**
- `switch0.30` - Switch fabric VLAN30 interface (member of br30)
- `eth10.1` - SFP+ uplink VLAN1 (to UniFi Switch)
- Other VLANs similarly configured

---

## Port Assignments (From NETWORK_INFRASTRUCTURE.md)

| UDM-SE Port | Device | Network | Interface |
|-------------|--------|---------|-----------|
| Port 1 | Laptop "UltraMoad" | 10.30.0.122 | eth0 |
| Port 3 | **TrueNAS Server** | 10.30.0.44 | eth2 |
| Port 5 | iDRAC 9 | 10.30.0.45 | eth4 |
| Port 10 | WAN to Dream Router 7 | - | eth9 |
| Port 11 | SFP+ Uplink to Switch | - | eth10 |

**Note:** Physical port numbers are **1-indexed** (Port 1, Port 3, etc.) but interface names are **0-indexed** (eth0, eth2, etc.)
- Port 1 = eth0
- Port 3 = eth2 ← **TrueNAS (includes Suricata VM)**
- Port 5 = eth4

---

## Port Mirroring Strategy

**Goal:** Mirror all VLAN30 traffic to the TrueNAS server port so Suricata can monitor it.

**Source Traffic:**
- Bridge br30 (entire VLAN30 network)
- Specific ports with VLAN30 devices

**Destination:**
- eth2 (Port 3) - TrueNAS server connection

**Challenge:** TrueNAS is on same network (br30) as devices being monitored. We'll mirror traffic from br30 to a dedicated monitoring interface on Suricata VM.

---

## Next Steps (In Progress)

1. ✅ SSH into UDM-SE as root
2. ✅ Identify network interfaces and VLANs
3. ⏳ **Configure port mirroring using tc (traffic control)**
4. ⏳ Add second NIC to Suricata VM for dedicated monitoring
5. ⏳ Configure Suricata to monitor mirrored traffic
6. ⏳ Make configuration persistent across reboots
7. ⏳ Test and verify all traffic is visible

---

## UDM-SE Access

**SSH:**
```bash
ssh root@10.30.0.1
```
Password: `password`

---

## References

- Suricata VM: 10.30.0.59 (VLAN30)
- TrueNAS: 10.30.0.44 on UDM-SE Port 3 (eth2)
- Suricata currently monitoring: ens3 (single interface)
- Custom rules in: `/var/lib/suricata/rules/local.rules`
- Alerts log: `/var/log/suricata/fast.log` (328 alerts captured so far)

---

**Document Created:** 2026-02-09
**Status:** Port mirroring configuration in progress
