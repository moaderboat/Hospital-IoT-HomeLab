# Balloon Demo - Current Implementation Status

**Last Updated:** 2026-02-08 (Software Updates Complete)
**Session:** WiFi Setup + ADS1115 Python Script Updates

---

## ✅ CURRENTLY IMPLEMENTED (WORKING)

### Software - All Scripts Deployed ✅

**Location:** `/home/username/balloon-demo/scripts/` on both Pis

**Pi #7 (Vulnerable System - 192.168.50.100):**
- ✅ `balloon_control_api.py` - Flask API server (systemd service RUNNING on port 5000)
- ✅ `sensor_publisher.py` - **UPDATED** for ADS1115 ADC + DATAQ sensors (ready to test)
- ✅ `attack_spoof.py` - Sensor spoofing attack script
- ✅ `test_pressure_sensor.py` - **NEW** diagnostic for ADS1115 + DATAQ (ready to test)
- ✅ `test_relays.py` - Relay HAT diagnostic
- ✅ `adafruit-circuitpython-ads1x15` library installed

**Pi #6 (Secure System - 10.30.0.25):**
- ✅ `balloon_control_secure.py` - **UPDATED** for ADS1115 ADC + DATAQ sensors (ready to test)
- ✅ `test_pressure_sensor.py` - **NEW** diagnostic for ADS1115 + DATAQ (ready to test)
- ✅ `test_relays.py` - Relay HAT diagnostic
- ✅ `adafruit-circuitpython-ads1x15` library installed

**All scripts updated and ready to test when DATAQ sensors arrive!**

---

### Systemd Services ✅

**Pi #7 Services:**
- ✅ `balloon-control-api.service` - **RUNNING** on http://192.168.50.100:5000
- ⏸️ `balloon-sensor-publisher.service` - DISABLED (waiting for DATAQ sensors + ADS1115 ADC)

**Pi #6 Services:**
- ⏸️ `balloon-control-secure.service` - DISABLED (waiting for DATAQ sensors + ADS1115 ADC + relay HAT)

**All services configured for auto-start on boot!**

---

### Network Configuration ✅

**Pi #7 (Vulnerable System):**
- **Current Connection:** ✅ **USB WiFi Adapter (Panda PAU0A)** - MediaTek chipset
- **Interface:** wlan1 (built-in wlan0 disabled - hardware defect)
- **IP Address:** 192.168.50.100/24 (static via NetworkManager)
- **SSID:** Medical-IoT (WPA2, VLAN2)
- **VLAN:** VLAN2 (192.168.50.0/24)
- **Gateway:** 192.168.50.1
- **Auto-connect:** ✅ Enabled and tested (survives reboot)
- **Status:** ✅ ONLINE, wireless, stable, accessible from VLAN30

**Pi #6 (Secure System):**
- **Connection:** Wired Ethernet (permanent)
- **IP Address:** 10.30.0.25/24 (static)
- **VLAN:** VLAN30 (10.30.0.0/24)
- **Gateway:** 10.30.0.1
- **Status:** ✅ ONLINE, stable

**UDM-SE WiFi Network:**
- **SSID:** "Medical-IoT"
- **VLAN:** VLAN2 (192.168.50.0/24)
- **Security:** WPA2-Personal
- **Password:** password
- **Optimization:** IoT mode
- **Client Isolation:** DISABLED (allows device-to-device communication)
- **Status:** ✅ OPERATIONAL (verified from Windows laptop)

---

### Firewall Rules ✅ WORKING PERFECTLY

**Rule Order (critical - first match wins):**

1. **ALLOW_VLAN30_TO_VLAN2**
   - **Type:** LAN In
   - **Action:** Accept
   - **Source:** Network 10.30.0.0/24 (VLAN30)
   - **Destination:** Network 192.168.50.0/24 (VLAN2)
   - **Protocol:** All
   - **Match State:** New, Established, Related
   - **Logging:** Disabled
   - **Purpose:** Allow admin access from secure VLAN30 to vulnerable VLAN2
   - **Status:** ✅ **TESTED - WORKING** (can SSH from 10.30.0.123 → 192.168.50.100)

2. **BLOCK_VLAN2_TO_GATEWAY**
   - **Type:** LAN Local (traffic TO the router itself)
   - **Action:** Drop
   - **Source:** Network 192.168.50.0/24 (VLAN2)
   - **Destination:** Router/Any
   - **Protocol:** All
   - **Match State:** New
   - **Logging:** Enabled
   - **Purpose:** Prevent compromised vulnerable Pi from accessing gateway
   - **Status:** ✅ **TESTED - WORKING** (Pi #7 cannot ping 10.30.0.1)

3. **BLOCK_VLAN2_TO_VLAN30**
   - **Type:** LAN In
   - **Action:** Drop
   - **Source:** Network 192.168.50.0/24 (VLAN2)
   - **Destination:** Network 10.30.0.0/24 (VLAN30)
   - **Protocol:** All
   - **Match State:** New (allows return traffic for existing connections)
   - **Logging:** ✅ Enabled (critical for demo - shows blocked attacks!)
   - **Purpose:** Block lateral movement from compromised VLAN2 to secure infrastructure
   - **Status:** ✅ **TESTED - WORKING** (Pi #7 cannot reach any VLAN30 devices)

**Firewall Test Results:**
- ✅ Pi #7 CANNOT ping: 10.30.0.1 (gateway), 10.30.0.123 (laptop), 10.30.0.55 (Wazuh), 10.30.0.51 (MQTT), 10.30.0.52 (PostgreSQL), 10.30.0.25 (Pi #6)
- ✅ Pi #7 CAN ping: 8.8.8.8 (internet access works)
- ✅ Laptop (10.30.0.123) CAN ping and SSH to Pi #7 (192.168.50.100)
- ✅ UDM-SE logs showing DROP events for blocked traffic from VLAN2

**Key Learning:** LAN Local rule type required to block traffic TO the gateway itself (not just THROUGH it)

---

### Hardware Status ✅

**✅ ARRIVED (Ready to Install):**
- 📦 2× Panda PAU0A AC600 USB WiFi adapters (arrived 2026-02-08)
  - Linux plug-and-play, Realtek chipset
  - Purpose: Pi #7 wireless connection + attacker laptop wireless
- 📦 12× LED Indicators - 22mm panel mount, 12-24V, 20mA (arrived 2026-02-08)
  - 3× Red, 3× Yellow, 3× Blue, 3× Green
  - Purpose: Visual status indicators
  - **Needs:** Custom housing design
- 📦 3× Adafruit BSS138 Level Shifters (arrived 2026-02-08)
  - 4-channel I²C-safe bidirectional level converter
  - Purpose: 3.3V Raspberry Pi ↔ 5V ADS1115 ADC
  - Need 2, have 3 (perfect spare)
- 📦 2× Mini HDMI to Micro HDMI cables (arrived 2026-02-08)
  - Purpose: Display connections for Raspberry Pis (if needed for demo/debugging)
- 📦 50cm GPIO extension cables (arrived 2026-02-08)
  - Purpose: Extended GPIO connections for flexible hardware placement
- 📦 6× 90-degree brass elbows (arrived 2026-02-08)
  - Purpose: Pneumatic system air line routing (tight corners, clean installation)
- 📦 Hose clamps - proper sizes, multiple qty (arrived 2026-02-08)
  - Purpose: Secure air hose connections to fittings (prevent leaks)
- 📦 2× Sheathed 4-wire GPIO cables (female-to-female) (arrived 2026-02-08)
  - Purpose: TBD - may be useful for I²C extensions or custom wiring
- 📦 Air pumps, solenoid valves, brass fittings, buzzers (arrived previously)

**🚚 ON THE WAY (DATAQ Inline Pressure Sensor System):**
- 2× DATAQ 2000361-30H Pressure Transducers (0-30 PSI, 0.5-4.5V, 1/8" NPT threaded)
- 2× DATAQ 2006030 Pigtail Cables (6-pin Molex to bare wire, 10 ft)
- 2× Adafruit ADS1115 16-Bit ADC Breakout Boards (I²C interface)
- 2× 1/8"F × 1/4"M NPT Brass Bushings (adapter for hose fittings)
- **Total Cost:** $210.70
- **Purpose:** Direct inline pressure measurement (replaces pressure chamber design)
- **ETA:** Unknown (ordered 2026-02-08)

**⏳ WAITING ON:**
- Sequent 8-RELAYS HAT (ordered 2026-02-05, ETA 5-7 business days)

**❌ OBSOLETE / CANCELED:**
- Mason jars (canceled 2026-02-08 - order stopped before shipping)
- PG7 cable glands (canceled if not shipped)
- Bulkhead fittings (canceled if not shipped)
- Silicone sealant (canceled if not shipped)
- BMP388 atmospheric sensors (owned, but now obsolete for this project)

---

## ⚠️ KNOWN ISSUES (RESOLVED OR TEMPORARY)

### Pi #7 Built-In WiFi - BROKEN ❌ (Workaround Planned)

**Issue:** Pi #7's built-in WiFi adapter has severe hardware/firmware problems
- 92% packet loss
- 3000ms ping times (3 seconds!)
- Randomly goes "unavailable" in NetworkManager
- Power management issues
- Unreliable for demo

**Root Cause:** Hardware defect or firmware bug in Pi's onboard WiFi chipset

**Attempted Fixes (All Failed):**
- ✗ Disabled power management
- ✗ Forced 2.4GHz band only
- ✗ Created multiple systemd services for auto-connect
- ✗ Tried dhcpcd, NetworkManager, wpa_supplicant manually
- ✗ Fixed rfkill soft-blocking
- ✗ Updated firmware

**Workaround:** ✅ **USB WiFi adapter (Panda PAU0A) arriving in few days**
- Plug into Pi #7's USB port
- Linux plug-and-play (no driver installation needed)
- Will replace broken built-in WiFi
- Pi #7 currently on **wired Ethernet as temporary measure**

**Cleanup Completed:** All broken WiFi services, rc.local entries, and NetworkManager profiles removed - Pi #7 ready for USB adapter

---

### Ethernet Cable Must Remain Connected to Pi #7 ⏳ (Temporary)

**Current State:** Pi #7 using wired Ethernet at 192.168.50.100

**Reason:** Waiting for USB WiFi adapters to arrive

**Timeline:** Will switch to WiFi once Panda PAU0A adapters arrive (few days)

---

## 🔄 IN PROGRESS (DESIGN CHANGE)

### ⚠️ MAJOR DESIGN CHANGE: Pressure Chambers → Inline Pressure Sensors ⚠️

**Date:** 2026-02-08

**Old Design (ABANDONED):**
- BMP388 atmospheric sensors in sealed mason jar chambers
- Required: drilling, sealing, leak testing, complex assembly
- Problems: Indirect measurement, potential leaks, bulky

**New Design (ACTIVE):**
- **DATAQ 2000361-30H Inline Pressure Transducers**
  - 0-30 PSI measurement range
  - 0.5-4.5V analog output (0.5V = 0 PSI, 4.5V = 30 PSI)
  - 1/8" NPT threaded connection
  - ±0.5% accuracy
  - Industrial-grade, rated for pneumatic systems
- **Installation:** Screw directly into 1/8" NPT tee junction in air line
- **Interface:** Analog voltage → ADS1115 16-bit ADC → I²C → Raspberry Pi
- **Wiring:** 6-pin Molex connector with pigtail cable (bare wire ends)

**Advantages:**
- ✅ Much simpler installation (no drilling, sealing, chambers)
- ✅ More reliable (industrial sensor vs atmospheric hack)
- ✅ Better accuracy (±0.5% vs ±1-2%)
- ✅ Faster response time (no dead volume)
- ✅ Professional appearance
- ✅ Direct measurement (not indirect via atmospheric pressure)

**Hardware Changes Required:**
- Add: ADS1115 16-bit I²C ADC (converts 0.5-4.5V analog to digital)
- Add: BSS138 level shifter (3.3V Pi ↔ 5V ADC) - ✅ Already arrived!
- Add: 1/8"F × 1/4"M NPT brass bushing (adapter for hose fittings)
- Remove: Mason jars, cable glands, bulkhead fittings, sealant

**Software Changes Required:**
- Replace BMP388 I²C library with ADS1115 I²C library
- Update `sensor_publisher.py` (Pi #7)
- Update `balloon_control_secure.py` (Pi #6)
- Rename/replace `test_bmp388.py` → `test_pressure_sensor.py`

**Status:**
- ✅ Hardware ordered (2026-02-08)
- ✅ Level shifters already in stock
- ⏳ Waiting for DATAQ sensors + ADC to arrive
- ⏳ Software updates pending (can write now, test when hardware arrives)

---

### USB WiFi Adapter Installation ✅ READY TO INSTALL

**✅ Hardware Arrived:** 2× Panda PAU0A adapters (arrived 2026-02-08)

**Next Steps (Can Do Now):**

**On Pi #7:**
1. Plug Panda PAU0A into USB port
2. Verify detection: `lsusb | grep -i realtek`
3. Check interface name: `ip link show` (probably wlan1)
4. Disable built-in WiFi: `sudo nmcli dev set wlan0 managed no`
5. Connect USB adapter to Medical-IoT:
   ```bash
   sudo nmcli dev wifi connect "Medical-IoT" password "password" ifname wlan1
   ```
6. Set static IP on wlan1:
   ```bash
   sudo nmcli con mod "Medical-IoT" ipv4.addresses 192.168.50.100/24
   sudo nmcli con mod "Medical-IoT" ipv4.gateway 192.168.50.1
   sudo nmcli con mod "Medical-IoT" ipv4.method manual
   sudo nmcli con mod "Medical-IoT" connection.autoconnect yes
   ```
7. Disable Ethernet connection:
   ```bash
   sudo nmcli con mod "Ethernet connection 1" connection.autoconnect no
   sudo nmcli con down "Ethernet connection 1"
   ```
8. Unplug Ethernet cable
9. Reboot and verify auto-connect works

**On Attacker Laptop:**
1. Plug 2nd Panda PAU0A into USB port
2. Windows should auto-detect
3. Connect to "Medical-IoT" WiFi via Windows WiFi settings
4. Verify IP: `ipconfig` (should show 192.168.50.x)
5. Test connectivity: `ping 192.168.50.100`

**Estimated Time:** 30 minutes per device

**Status:** ✅ **READY - Hardware in hand, Pi #7 is clean and ready to configure**

---

### Relay HAT Installation & Testing ⏳

**Waiting For:** Sequent 8-RELAYS HAT (ETA 5-7 days from 2026-02-05)

**Next Steps When HAT Arrives:**

**On Both Pis:**
1. Power down Pi
2. Install Sequent 8-RELAYS HAT on GPIO pins
3. Power up Pi
4. Verify I²C detection: `i2cdetect -y 1` (should show 0x20)
5. Install library if needed:
   ```bash
   cd ~
   git clone https://github.com/SequentMicrosystems/8relind-rpi.git
   cd 8relind-rpi/python
   sudo python3 setup.py install
   ```
6. Test relays:
   ```bash
   python3 test_relays.py
   ```
7. Connect relay outputs to air pump and solenoid valve
8. Test pneumatic system (pump inflates, valve controls airflow)

**Estimated Time:** 1 hour per Pi + pneumatic testing

**Status:** Waiting for delivery

---

### Full System Integration Testing ⏳

**Waiting For:** All hardware (relay HAT + DATAQ sensors + ADS1115 ADC)

**Cannot Test Until:**
- ⏳ DATAQ pressure sensors + ADS1115 ADC installed
- ⏳ Relay HATs installed and connected to pneumatics
- ✅ WiFi adapters installed (Pi #7 wireless, laptop wireless) - **READY NOW**
- ⏳ Python scripts updated for ADS1115
- ⏳ All systemd services enabled

**Next Steps When Hardware Complete:**

**Pi #7 (Vulnerable System):**
1. Enable services:
   ```bash
   sudo systemctl enable balloon-sensor-publisher.service
   sudo systemctl enable balloon-control-api.service
   sudo systemctl start balloon-sensor-publisher.service
   sudo systemctl start balloon-control-api.service
   ```
2. Verify Flask API accessible: `curl http://192.168.50.100:5000/status`
3. Verify sensor publishing: `sudo journalctl -u balloon-sensor-publisher.service -f`
4. Test balloon inflation (normal operation without attack)

**Pi #6 (Secure System):**
1. Enable service:
   ```bash
   sudo systemctl enable balloon-control-secure.service
   sudo systemctl start balloon-control-secure.service
   ```
2. Verify Wazuh logging: `sudo journalctl -u balloon-control-secure.service -f`
3. Test balloon inflation (secure operation)

**Attack Test:**
1. Connect attacker laptop to "Medical-IoT" WiFi
2. Verify connectivity: `ping 192.168.50.100`
3. Run attack script: `python3 attack_spoof.py`
4. Verify vulnerable balloon over-inflates and pops
5. Verify secure balloon stops at safe pressure
6. Check Wazuh SIEM for logged events
7. Check UDM-SE firewall logs for blocked lateral movement attempts

**Estimated Time:** 2-3 hours full testing + demo rehearsal

**Status:** All software ready, waiting for hardware integration

---

## 📋 TODO - REMAINING TASKS

### High Priority (Can Do Now)

**Attacker Laptop WiFi Setup:**
- [ ] Install 2nd Panda PAU0A on attacker laptop
- [ ] Connect to Medical-IoT WiFi network
- [ ] Test wireless attack connectivity to Pi #7

**LED Indicators (Hardware Ready - Design/Build Phase):**
- [ ] Design custom housing for 22mm panel mount LEDs
- [ ] Determine control method (relay-direct vs GPIO)
- [ ] Check if current-limiting resistors needed (or built-in)
- [ ] Wire LEDs to control system
- [ ] Test LED operation

**Software Updates:**
- [x] Update `sensor_publisher.py` for ADS1115 ADC (done 2026-02-08)
- [x] Update `balloon_control_secure.py` for ADS1115 ADC (done 2026-02-08)
- [x] Create new `test_pressure_sensor.py` (done 2026-02-08)
- [x] Install `adafruit-circuitpython-ads1x15` library on both Pis (done 2026-02-08)
- [ ] Test sensor reading code when DATAQ sensors arrive

**WiFi Setup:**
- [x] Install Panda PAU0A on Pi #7 (done 2026-02-08)
- [x] Configure Pi #7 WiFi connection to Medical-IoT (done 2026-02-08)
- [x] Set static IP 192.168.50.100 on WiFi (done 2026-02-08)
- [x] Disable Ethernet connection (done 2026-02-08)
- [x] Test auto-connect after reboot (done 2026-02-08)

### Medium Priority (Waiting on Hardware)

**When DATAQ Sensors + ADC Arrive:**
- [ ] Wire ADS1115 ADC with BSS138 level shifter
- [ ] Connect DATAQ sensor pigtail to ADC
- [ ] Install 1/8" NPT bushing adapters
- [ ] Screw DATAQ sensors into NPT tee junctions in air lines
- [ ] Test sensor readings: `python3 test_pressure_sensor.py`
- [ ] Verify voltage range: 0.5V (0 PSI) to 4.5V (30 PSI)
- [ ] Calibrate pressure conversion algorithm

**When Relay HAT Arrives (5-7 Days from 2026-02-05):**
- [ ] Install relay HATs on both Pis
- [ ] Test relay control: `python3 test_relays.py`
- [ ] Connect relays to air pumps and solenoid valves
- [ ] Test pneumatic system (pump/valve operation)

### Lower Priority (Full Integration - Week 2)

**Full System Testing (When All Hardware Installed):**
- [ ] Enable all systemd services on both Pis
- [ ] Test normal balloon inflation (no attack)
- [ ] Test sensor spoofing attack on vulnerable system
- [ ] Verify secure system resists attack
- [ ] Verify Wazuh SIEM logging
- [ ] Verify firewall blocks lateral movement
- [ ] Check UDM-SE firewall logs for DROP events
- [ ] Practice full demo presentation

**Documentation:**
- [x] Update CURRENT_STATUS.md with design change (done 2026-02-08)
- [ ] Update WIRELESS_ATTACK_ARCHITECTURE.md with final USB WiFi adapter setup
- [ ] Document inline pressure sensor wiring and setup
- [ ] Create expo presentation slides
- [ ] Document attack demonstration script (step-by-step for live demo)
- [ ] Create troubleshooting guide for expo day
- [ ] Print network diagrams for poster

**Network Improvements (Not Critical for Balloon Demo):**
- [ ] Deploy Wazuh agent to TrueNAS server (10.30.0.44)
- [ ] Configure UDM-SE syslog forwarding to Wazuh (10.30.0.55)
- [ ] Delete unused VLANs from UDM-SE (VLAN10, VLAN20, VLAN40)
- [ ] Implement PostgreSQL data retention policy (18+ months runway - not urgent)

---

## 🎯 EXPO DEMONSTRATION READINESS

### Current Status: 60% Complete (Software Ready, Hardware Arriving)

**✅ What's Working:**
- ✅ All software written, tested, deployed (needs minor updates for ADS1115)
- ✅ Network segmentation configured (VLAN2 vulnerable, VLAN30 secure)
- ✅ Firewall rules working perfectly (tested and verified)
- ✅ Pi #7 and Pi #6 online and accessible
- ✅ Flask API running on Pi #7
- ✅ Attack script ready to execute

**✅ Hardware Ready to Install:**
- 📦 2× Panda PAU0A USB WiFi adapters (arrived 2026-02-08)
- 📦 3× BSS138 level shifters (arrived 2026-02-08)
- 📦 12× LED indicators (arrived 2026-02-08)

**⏳ Hardware On Order:**
- 🚚 DATAQ inline pressure sensors + ADS1115 ADC + pigtails + bushings
- 🚚 Sequent 8-RELAYS HAT (ordered 2026-02-05, ETA ~Feb 10-12)

**📝 Software Updates Needed:**
- Minor: Update sensor reading code from BMP388 I²C to ADS1115 I²C
- Minor: Create new test script for inline pressure sensors
- Estimated: 1-2 hours work, can do now, test when sensors arrive

**⚠️ Design Changes Completed:**
- ✅ Switched from pressure chambers to inline DATAQ sensors (2026-02-08)
- ✅ Canceled mason jar orders
- ✅ Ordered professional pressure transducers

**Estimated Days Until Fully Operational:**
- Optimistic: 7-10 days (if DATAQ sensors ship quickly)
- Realistic: 10-14 days (standard shipping + assembly/testing)

**Blocking Issues:**
- None critical - can install WiFi adapters now
- Software updates can be written now, tested when sensors arrive
- Relay HAT should arrive within a week

---

## 📝 SESSION NOTES

### 2026-02-08 - WiFi Setup Complete + Python Scripts Updated

**WiFi Configuration (Pi #7):**
- ✅ Panda PAU0A USB WiFi adapter installed and detected (MediaTek chipset)
- ✅ Connected to Medical-IoT network on VLAN2
- ✅ Static IP configured: 192.168.50.100
- ✅ Fixed gateway/DNS typos during setup (102.160.50.1 → 192.168.50.1, 192.169.50.1 → 192.168.50.1)
- ✅ Auto-connect on boot tested and working
- ✅ Ethernet disabled - Pi #7 now fully wireless
- ✅ Accessible from VLAN30 admin laptop via firewall rules

**Python Script Updates:**
- ✅ Updated `sensor_publisher.py` for ADS1115 + DATAQ sensors
- ✅ Updated `balloon_control_secure.py` for ADS1115 + DATAQ sensors
- ✅ Created new `test_pressure_sensor.py` diagnostic script
- ✅ Installed `adafruit-circuitpython-ads1x15` library on both Pis (using --break-system-packages)
- ✅ All code ready to test when DATAQ sensors arrive

---

### 2026-02-08 - Major Design Change: Inline Pressure Sensors

**Decision:** Abandoning pressure chamber design in favor of inline pressure transducers

**Rationale:**
- Pressure chambers were complex (drilling, sealing, leak testing)
- Mason jar approach was a hack (using atmospheric sensor in chamber)
- DATAQ 2000361-30H is professional industrial solution
- Simpler installation (screw into NPT tee junction)
- More reliable and accurate (±0.5% vs ±1-2%)
- Faster response time

**Actions Taken:**
- ✅ Canceled mason jar orders (stopped before shipping)
- ✅ Ordered DATAQ sensors, ADC, level shifters, pigtails, bushings ($210.70)
- ✅ Updated documentation with new design
- ⏳ Need to update Python scripts for ADS1115 ADC

**Hardware Arrivals (2026-02-08):**
- ✅ Panda PAU0A USB WiFi adapters (2×) - ready to install
- ✅ BSS138 level shifters (3×) - needed for ADC, arrived just in time!
- ✅ LED indicators (12×) - need housing design
- ✅ Mini-to-Micro HDMI cables (2×) - for Pi displays if needed
- ✅ 50cm GPIO extension cables - for flexible component placement
- ✅ 90-degree brass elbows (6×) - for clean pneumatic routing
- ✅ Hose clamps (multiple) - for secure air line connections
- ✅ Sheathed 4-wire GPIO cables (2×) - spare/future use

**Pneumatic System Ready:**
With brass elbows and hose clamps arrived, pneumatic assembly can now be done professionally with:
- Clean 90-degree turns (no kinked hoses)
- Secure clamped connections (no leaks)
- Proper air flow routing

**Impact:**
- Software: Minor updates needed (1-2 hours)
- Hardware: Waiting on DATAQ sensors + ADC + relay HAT
- Pneumatic assembly: Can route hoses and plan layout now
- Timeline: Similar to original plan, but simpler installation

---

### 2026-02-06 Evening - WiFi Troubleshooting (3+ Hours)

**Problem:** Pi #7 built-in WiFi completely unreliable (92% packet loss, 3-second ping times)

**Attempted Fixes:**
- Disabled WiFi power management
- Forced 2.4GHz band
- Created multiple systemd auto-connect services
- Fixed rfkill soft-blocking
- Updated firmware
- Tried every network manager (dhcpcd, NetworkManager, wpa_supplicant)

**Conclusion:** Hardware defect - cannot be fixed via software

**Solution:** Order USB WiFi adapters (Panda PAU0A) - plug-and-play with Linux

**Cleanup:** Removed all broken WiFi configurations from Pi #7 to prepare for USB adapter

**Lesson Learned:** Don't waste time fixing broken hardware - replace it

---

### Firewall Configuration (1 Hour)

**Discovered:** Existing firewall rules from previous session, but had wrong VLAN (VLAN20 instead of VLAN2)

**Fixed:** Updated BLOCK rule to correct VLAN2

**Issue:** ALLOW rule was working, but BLOCK rule blocked EVERYTHING (including return packets)

**Solution:** Added **Match State: New** to BLOCK rule (allows established/related traffic)

**Issue:** Gateway (10.30.0.1) was still reachable from Pi #7

**Solution:** Created separate **LAN Local** rule to block traffic TO the gateway itself (not just THROUGH it)

**Final Configuration:**
1. ALLOW_VLAN30_TO_VLAN2 (LAN In, all states)
2. BLOCK_VLAN2_TO_GATEWAY (LAN Local, state: new)
3. BLOCK_VLAN2_TO_VLAN30 (LAN In, state: new)

**Testing:** All firewall rules verified working correctly

**Key Learning:**
- **LAN In** = traffic passing THROUGH router between networks
- **LAN Local** = traffic destined TO the router itself
- Match State is critical to allow return traffic while blocking new connections

---

## 🔑 KEY LEARNINGS

**2026-02-08:**
1. **Don't over-engineer when professional solutions exist** - DATAQ sensors are better than DIY pressure chambers
2. **Order backup components** - Having 3 level shifters instead of 2 provides peace of mind
3. **Design changes are okay mid-project** - Better to switch now than build something suboptimal
4. **Order pneumatic hardware early** - Brass elbows and hose clamps enable professional installation
5. **Plan for flexibility** - GPIO extensions and HDMI cables provide setup options

**2026-02-06:**
1. **Pi built-in WiFi is unreliable** - Use USB adapters for critical demos
2. **LAN Local vs LAN In rule types** - Different purposes, both needed
3. **Match State in firewall rules** - Essential for stateful filtering
4. **NetworkManager is finicky** - Cleaning up old configs prevents conflicts
5. **Always test firewall rules thoroughly** - Don't assume they work without verification
6. **Order hardware early** - Shipping delays can block progress

---

## 📞 PARTS TRACKING & ORDER HISTORY

**✅ Arrived (2026-02-08):**
- Panda PAU0A WiFi Adapters (2×) - Ready to install
- BSS138 Level Shifters (3×) - Ready to use
- 22mm LED Indicators (12×) - Need housing
- Mini-to-Micro HDMI cables (2×) - Ready to use
- 50cm GPIO extension cables - Ready to use
- 90-degree brass elbows (6×) - Ready for pneumatic assembly
- Hose clamps (multiple) - Ready for pneumatic assembly
- Sheathed 4-wire GPIO cables (2×) - Spare/TBD

**🚚 In Transit:**
- DATAQ 2000361-30H Pressure Sensors (2×)
- DATAQ Pigtail Cables (2×)
- ADS1115 ADC Breakouts (2×)
- 1/8"F × 1/4"M NPT Bushings (2×)
- Sequent 8-RELAYS HAT (ordered 2026-02-05, ETA Feb 10-12)

**❌ Canceled (2026-02-08):**
- Mason jars (stopped before shipping)
- PG7 cable glands (stopped if not shipped)
- Bulkhead fittings (stopped if not shipped)
- Silicone sealant (stopped if not shipped)

---

**Next Session Goals:**
1. ✅ Install USB WiFi adapters on Pi #7 and attacker laptop (hardware ready now)
2. Design custom housing for LED indicators
3. Update Python scripts for ADS1115 ADC (can write now, test when sensors arrive)
4. Install relay HAT when it arrives (~Feb 10-12)
5. Install DATAQ sensors + ADC when they arrive

**Estimated Time to Demo-Ready:** 10-14 days (hardware dependent, but on track)

---

**Document Created:** 2026-02-06 23:45 EST
**Last Major Update:** 2026-02-08 - Design Change to Inline Sensors
**Next Update:** When DATAQ sensors or relay HAT arrive
