# Queen City Con Hardware Checklist

**Conference:** Queen City Con 0x4 (November 13-15, 2026)
**Purpose:** Complete physical hardware inventory for live demo

---

## 🖥️ Core Rack Infrastructure

### Network Equipment

**1. UniFi Dream Machine SE (UDM-SE)**
- Model: UDM-SE
- Purpose: Network gateway, firewall, cross-VLAN routing
- Power: IEC C13 power cable (included with unit)
- Rack: 1U rack-mountable
- Web UI: https://10.30.0.1 (username / password)
- **Critical:** WAN port must have link-up for cross-VLAN routing

**2. UniFi Switch Pro Max 24 PoE**
- Model: USW-Pro-Max-24-PoE
- Purpose: Network backbone, PoE++ for Raspberry Pis
- Power: IEC C13 power cable (included with unit)
- Rack: 1U rack-mountable
- Ports: 24x RJ45 (PoE++), 2x SFP+ (10 Gbps uplinks)
- **Critical:** Port 15 mirrored to Port 7 for Suricata IDS

**3. Dell PowerEdge R720 (TrueNAS Server)**
- Model: Dell PowerEdge R720
- Purpose: TrueNAS host, runs all 7 VMs
- Power: 2x redundant PSUs, IEC C13 power cables
- Rack: 2U rack-mountable
- iDRAC: http://10.30.0.45
- TrueNAS Web UI: http://10.30.0.44 (username / password)
- Storage: 1TB+ for PostgreSQL (180 GB database), HAPI FHIR (35 GB)
- **Critical:** Must boot first, VMs auto-start after 5 minutes

---

## 🍓 Raspberry Pi Devices (7 Total)

### Hospital Heart Rate Monitors (5 Pis)

**Pi #1 - 72 BPM Patient**
- Model: Raspberry Pi 5 (4GB RAM)
- IP: 10.30.0.20 (VLAN 30, static)
- Power: PoE++ from switch (auto-power when switch is on)
- Sensors: Sense HAT (accelerometer-based heart rate simulation)
- Service: `heartrate1.service`
- SSH: `username@10.30.0.20` / `password`

**Pi #2 - 68 BPM Patient (Most Variable)**
- Model: Raspberry Pi 5 (4GB RAM)
- IP: 10.30.0.21 (VLAN 30, static)
- Power: PoE++ from switch
- Sensors: Sense HAT
- Service: `heartrate2.service`
- SSH: `username@10.30.0.21` / `password`

**Pi #3 - 75 BPM Patient (Most Stable)**
- Model: Raspberry Pi 5 (4GB RAM)
- IP: 10.30.0.22 (VLAN 30, static)
- Power: PoE++ from switch
- Sensors: Sense HAT
- Service: `heartrate3.service`
- SSH: `username@10.30.0.22` / `password`

**Pi #4 - AFib Simulation (70-150 BPM Irregular)**
- Model: Raspberry Pi 5 (4GB RAM)
- IP: 10.30.0.23 (VLAN 30, static)
- Power: PoE++ from switch
- Sensors: Sense HAT
- Service: `heartrate4.service`
- SSH: `username@10.30.0.23` / `password`
- **Visual:** Red ECG trace on Node-RED dashboard (vs. green for normal)

**Pi #5 - 70 BPM Patient (Rare Anomalies)**
- Model: Raspberry Pi 5 (4GB RAM)
- IP: 10.30.0.24 (VLAN 30, static)
- Power: **External USB-C power adapter** (NOT PoE)
- Sensors: Sense HAT
- Service: `heartrate5.service`
- SSH: `username@10.30.0.24` / `password`
- **Critical:** Must plug in power adapter manually

### Balloon Demo Pressure Control Systems (2 Pis)

**Secure Pi (Hardened System)**
- Model: Raspberry Pi 5 (4GB RAM)
- Hostname: `balloon-secure`
- IP: 10.30.0.25 (VLAN 30, static)
- Power: **External USB-C power adapter** (NOT PoE)
- Sensors:
  - 2x DATAQ 100 PSI analog pressure sensors
  - ADS1115 16-bit ADC (I2C address 0x48)
  - BSS138 bidirectional level shifter (3.3V ↔ 5V)
- Actuators: Direct I2C control (no network exposure for control decisions)
- Service: `balloon-control-secure.service`
- SSH: `username@10.30.0.25` / `password`
- MQTT: Publishes to 10.30.0.51 (authenticated)
  - `balloon/secure/status` (full telemetry + attack detection)
  - `balloon/secure/pressure` (I2C sensor)
  - `balloon/secure/pressure_network` (claimed network value)
  - `balloon/secure/attack_status` (attack detected flag)
- **Critical:** Target pressure 25 PSI, rejects spoofed data, I2C fallback

**Vulnerable Pi (Intentionally Insecure System)**
- Model: Raspberry Pi 5 (4GB RAM)
- Hostname: `balloon-vulnerable`
- IP: 192.168.50.100 (VLAN 2, static)
- Power: **External USB-C power adapter** (NOT PoE)
- Sensors:
  - 2x DATAQ 100 PSI analog pressure sensors
  - ADS1115 16-bit ADC (I2C address 0x48)
  - BSS138 bidirectional level shifter (3.3V ↔ 5V)
- Actuators:
  - Sequent 8-RELAYS HAT (I2C 0x27, STACK=0) - Solenoids
  - Sequent 40A 3-relay HAT (I2C 0x60, STACK=0) - Air pump
- Services:
  - `balloon-sensor-publisher.service` (reads sensors, POSTs to Flask API)
  - `balloon-control-api.service` (Flask API on port 5000, control loop)
- SSH: `username@192.168.50.100` / `password`
- MQTT: Publishes to 10.30.0.51 (authenticated, firewall exception required)
  - `balloon/vulnerable/pressure` (downstream sensor)
  - `balloon/vulnerable/relays` (pump/solenoid states)
  - `balloon/vulnerable/sensor_source` (data source indicator)
- **Critical:** NO validation, accepts spoofed data blindly, compromises at 100% attack success rate

---

## 🔌 Raspberry Pi Peripherals & Sensors

### Sense HATs (5x - Hospital Monitors)
- Model: Raspberry Pi Sense HAT
- Purpose: Accelerometer-based heart rate simulation
- Features: 8x8 RGB LED matrix, gyroscope, accelerometer, magnetometer
- Mounting: Stacks on top of Pi GPIO header (40-pin)

### Pressure Sensors (4x - Balloon Demo)
- Model: DATAQ DI-100 PSI analog pressure sensor
- Range: 0-100 PSI
- Output: 0.5-4.5V linear (ratiometric)
- Wiring:
  - RED: 12V+ (from PSU)
  - BLACK: GND
  - YELLOW: Signal (to ADS1115 ADC)
- Allocation:
  - **Secure Pi:** A0=upstream, A1=downstream
  - **Vulnerable Pi:** A0=upstream, A1=downstream

### ADC Modules (2x - Balloon Demo)
- Model: ADS1115 16-bit ADC
- Interface: I2C (address 0x48)
- Voltage: 5V input (from Pi Pin 2)
- Level Shifter: BSS138 (3.3V ↔ 5V, required for Pi 5)
- Channels: A0, A1 (A2/A3 unused)
- Library: `adafruit-circuitpython-ads1x15`

### BSS138 Level Shifters (2x - Balloon Demo)
- Model: BSS138 4-channel bidirectional level shifter
- Purpose: Convert 5V I2C (ADS1115) to 3.3V I2C (Raspberry Pi 5)
- Wiring:
  - LV: Pi Pin 1 (3.3V)
  - HV: Pi Pin 2 (5V)
  - A1 (LV side): Pi SCL (GPIO 3)
  - A2 (LV side): Pi SDA (GPIO 2)
  - B1 (HV side): ADS1115 SDA
  - B2 (HV side): ADS1115 SCL
  - GND: Common ground

### Relay HATs (2x - Vulnerable Pi Only)

**Sequent 8-RELAYS HAT**
- Model: Sequent Microsystems 8-RELAYS HAT for Raspberry Pi
- I2C Address: 0x27 (STACK=0, all ID switches ON)
- Relays:
  - Relay 2: Solenoid #1 Inflate (NC type)
  - Relay 3: Solenoid #2 Vent (NC type)
  - Relay 4: Solenoid #3 Relief (NC type)
  - Relays 1, 5-8: Unused
- Control: `lib8relind.set(0, relay_num, 0/1)` - 0=OFF/closed, 1=ON/open
- Library: `lib8relind` (Python, `pip install SMBus lib8relind`)
- Mounting: Stacks on Vulnerable Pi GPIO header

**Sequent 40A 3-Relay HAT (High-Current)**
- Model: Sequent Microsystems 3-relay HAT (40A rated)
- I2C Address: 0x60 (STACK=0)
- Relays:
  - Relay 3: Air pump (23A load)
  - Relays 1-2: Unused
- Control: `lib3relind.set(0, 3, 0/1)` - 0=pump OFF, 1=pump ON
- Library: `lib3relind` (Python, `pip install SMBus lib3relind`)
- Mounting: **Side-mounted via 40-pin GPIO ribbon cable** (too thick to stack with 8-RELAYS HAT)
- **Critical:** Must use separate power rail for 40A relay coil, do NOT power from Pi

---

## 🔩 Pneumatic Demo Hardware (Vulnerable Pi Physical System)

### Air Pump
- Model: 12V DC air pump (generic)
- Current Draw: 23A peak (inrush), ~18A sustained
- Power: 12V from main PSU (dedicated 29A rail)
- Control: Sequent 40A 3-relay HAT, Relay 3
- Purpose: Inflate pressure vessel to target 25 PSI
- **Critical:** High inrush current requires 40A-rated relay (standard 10A relays will weld closed)

### Solenoid Valves (3x - NC Type)
- Model: 12V DC solenoid valves (Normally Closed)
- Type: NC (energize to OPEN, de-energize to CLOSE)
- Power: 12V from main PSU
- Control: Sequent 8-RELAYS HAT
  - **Relay 2:** Inflate valve (upstream, allows air from pump to enter vessel)
  - **Relay 3:** Vent valve (downstream, releases air to atmosphere)
  - **Relay 4:** Relief valve (emergency, opens at 70 PSI via software safety)
- **Known Issue:** Valves occasionally stick closed under pressure (tap valve body or depressurize first)
- **Mitigation:** Valve exercise routine (rapid cycling), triple-send relay commands

### Pressure Vessel
- Model: 1L plastic bottle (soda bottle repurposed)
- Burst Pressure: 39-71 PSI (mean: 59.6 PSI, tested with 5 samples)
- Operating Pressure: Target 25 PSI (safe limit: 35 PSI)
- Safety Margin: Relief valve activates at 70 PSI (emergency failsafe)
- **Critical:** Do NOT exceed 35 PSI in demo (use relief valve as backstop)
- **Visual:** Clear plastic allows audience to see inflation during attack

### Power Supply (Pneumatic System)
- Model: 12V 29A DC power supply (generic switching PSU)
- Output: 12V DC, 29A max (348W)
- Distribution: Terminal blocks with kill switch
- Loads:
  - Air pump: 23A (primary load)
  - 3x solenoid valves: ~1A each (3A total)
  - Total: 26A sustained (3A headroom)
- **Critical:** Kill switch must be accessible for emergency shutoff
- Wiring: RED=12V+, BLACK=GND, use 14-16 AWG wire (minimum)

---

## 💻 Attack / IDS Hardware

### Suricata IDS Laptop
- Model: Generic laptop (user-provided)
- OS: Ubuntu 22.04 or newer (bare metal, NOT VM)
- IP: 192.168.50.191 (VLAN 2, static)
- Purpose: Network IDS monitoring, attack script execution
- Network Interfaces:
  - **Port 6 (Management):** VLAN 2, static IP 192.168.50.191
  - **Port 7 (Monitor):** Promiscuous mode, NO IP, receives mirrored traffic from Switch Port 15
- Software:
  - Suricata 7.x (IDS/IPS)
  - Filebeat 8.x (ships EVE logs to Elasticsearch)
  - Python 3.10+ (for `attack_spoof.py` script)
- SSH: `username@192.168.50.191` / `password`
- **Critical:** Must be bare metal (VMs can't receive mirrored traffic due to macvtap filtering)

### Attack Scripts (On Suricata Laptop)
- `attack_spoof.py` - Dual-target HTTP POST flood (spoofs pressure sensor data)
  - Usage: `python3 attack_spoof.py --dual --pressure 0.0 --rate 0.01` (`--rate` = seconds between requests)
  - Targets: 192.168.50.100:5000 (Vulnerable Pi), 10.30.0.25:5000 (Secure Pi)
  - Rate: 100 Hz per target (200 total requests/sec)
- **Critical:** Must run from VLAN 2 device for IDS to capture traffic (Layer 2 attack)

---

## 🔗 Cabling & Connectivity

### Ethernet Cables

**SFP+ DAC (Direct Attach Cable)**
- Quantity: 1x
- Length: 1 meter
- Type: 10G SFP+ passive copper DAC
- Model: Ubiquiti UDC-1 (or FS.com equivalent)
- Purpose: UDM-SE SFP+ port → Switch SFP+ uplink (10 Gbps backbone)
- **Critical:** Must be picked up from dad's house before conference

**Cat6a Patch Cables**
- Quantity: ~10-15x (various lengths)
- Type: Cat6a (10 Gbps rated, shielded preferred)
- Lengths: 1ft, 3ft, 6ft mix
- Purposes:
  - **Mock WAN:** UDM-SE WAN port → the **standalone dumb switch** (NOT a port on the main switch)
  - **PoE to Pis:** Pi #1-4 (hospital monitors). Port numbers changed after the Oct 2026 switch reset; see the port map in `CON_FIELD_GUIDE.md` §1B
  - **Suricata laptop:** Switch Port 6 (management), Switch Port 7 (monitor)
  - **Admin laptop:** its own VLAN 30 port (`CON_FIELD_GUIDE.md` §1C)
  - **Spares:** Always bring 3-5 extra cables

**USB-C Power Cables (for External-Powered Pis)**
- Quantity: 3x
- Type: USB-C to wall adapter (5V 3A minimum, 5V 5A recommended for Pi 5)
- Purpose:
  - Pi #5 (external power)
  - Secure Pi (external power)
  - Vulnerable Pi (external power)
- **Critical:** Pi 5 requires more power than PoE can provide when HATs are attached

**12V Power Wiring (Pneumatic System)**
- Quantity: ~10 feet total
- Type: 14-16 AWG stranded copper wire (RED for +12V, BLACK for GND)
- Terminals: Ring terminals, spade connectors, or terminal blocks
- Purpose: PSU → air pump, PSU → solenoid valves
- **Safety:** Fuse or circuit breaker on +12V rail (30A rating)

### GPIO Ribbon Cable
- Quantity: 1x
- Type: 40-pin GPIO ribbon cable (6-12 inches)
- Purpose: Vulnerable Pi → Sequent 40A 3-relay HAT (side-mounted, doesn't stack)
- **Critical:** Required because 8-RELAYS HAT + 40A HAT are too thick to stack directly

---

## 🧰 Tools & Accessories

### Hand Tools
- **Screwdrivers:** Phillips, flathead (for terminal blocks, relay HAT mounting)
- **Wire strippers:** 14-22 AWG range
- **Multimeter:** Voltage/continuity testing (verify 12V PSU, check for shorts)
- **Zip ties / Velcro straps:** Cable management

### Power Strips / PDUs
- Quantity: 2-3x
- Type: Surge-protected power strips (6-8 outlets each)
- Purpose:
  - Rack equipment (UDM-SE, Switch, Dell server)
  - Pi external power adapters (3x)
  - Laptop, monitors
  - 12V PSU (pneumatic system)
- **Critical:** Conference may only provide 1-2 outlets, bring power distribution

### Display / Presentation Equipment
- **HDMI cable:** Laptop → projector (bring 6ft + 10ft, conference AV varies)
- **USB keyboard/mouse:** Backup input devices (if laptop trackpad fails)
- **Extension cords:** 10-15 feet (reach from table to wall outlet)

### Demo Consumables
- **Spare 1L bottles:** 2-3x extra pressure vessels (in case of burst during setup)
- **Teflon tape:** Pipe thread sealing (pressure sensor fittings)
- **Isopropyl alcohol:** Clean stuck solenoid valve plungers
- **Paper towels:** Clean up after valve cycling tests

---

## 📦 Conference Packing Checklist (Organized by Category)

### Rack Equipment (3 items)
- [ ] UniFi Dream Machine SE (UDM-SE) + power cable
- [ ] UniFi Switch Pro Max 24 PoE + power cable
- [ ] Dell PowerEdge R720 (TrueNAS) + 2x power cables

### Raspberry Pis (7 devices)
- [ ] Pi #1 (10.30.0.20) + Sense HAT
- [ ] Pi #2 (10.30.0.21) + Sense HAT
- [ ] Pi #3 (10.30.0.22) + Sense HAT
- [ ] Pi #4 (10.30.0.23) + Sense HAT
- [ ] Pi #5 (10.30.0.24) + Sense HAT + USB-C power adapter
- [ ] Secure Pi (10.30.0.25) + sensors/ADC/level shifter + USB-C power adapter
- [ ] Vulnerable Pi (192.168.50.100) + sensors/ADC/level shifter/relay HATs + USB-C power adapter

### Pressure Control Hardware
- [ ] 2x DATAQ 100 PSI pressure sensors (Secure Pi)
- [ ] 2x DATAQ 100 PSI pressure sensors (Vulnerable Pi)
- [ ] 2x ADS1115 ADC modules
- [ ] 2x BSS138 level shifters
- [ ] Sequent 8-RELAYS HAT (Vulnerable Pi)
- [ ] Sequent 40A 3-relay HAT (Vulnerable Pi)
- [ ] 40-pin GPIO ribbon cable (for 40A HAT side-mount)

### Pneumatic System
- [ ] 12V 29A power supply (with IEC C13 power cable)
- [ ] Air pump (12V, 23A)
- [ ] 3x solenoid valves (NC type, 12V)
- [ ] 3-5x 1L plastic bottles (pressure vessels + spares)
- [ ] Terminal blocks + kill switch
- [ ] 12V power wiring (RED/BLACK, 14-16 AWG)
- [ ] Fuse/breaker (30A, 12V DC rated)

### Networking
- [ ] SFP+ DAC cable (1m, Ubiquiti UDC-1) - **Pick up from dad's house**
- [ ] 10-15x Cat6a patch cables (1ft, 3ft, 6ft mix)
- [ ] Suricata IDS laptop (192.168.50.191)

### Mock WAN Hardware (Air-Gap Mode)
- [ ] Small 5-port dumb switch (travel router) - **Buy before conference**
- [ ] 1x short Cat6a cable (1-3 feet, for UDM-SE WAN port)

### Power Distribution
- [ ] 2-3x surge-protected power strips (6-8 outlets each)
- [ ] 2x extension cords (10-15 feet)

### Presentation Equipment
- [ ] **Admin laptop** (slides, dashboards, SSH; replaces the desktop) + charger + any USB-Ethernet/HDMI adapters it needs
- [ ] Labeled Ethernet cable for the admin laptop's VLAN 30 port
- [ ] HDMI cables (6ft + 10ft)
- [ ] USB keyboard/mouse (backup)

### Tools & Consumables
- [ ] Screwdrivers (Phillips, flathead)
- [ ] Wire strippers
- [ ] Multimeter
- [ ] Zip ties / Velcro straps
- [ ] Spare 1L bottles (2-3x)
- [ ] Teflon tape
- [ ] Isopropyl alcohol
- [ ] Paper towels

### Documentation (Digital + Printed)
- [ ] `CON_FIELD_GUIDE.md` (printed): the venue runbook, replaces `QUICK_STARTUP_PROCEDURE.md`
- [ ] `CON_CREDENTIALS.md` (printed, kept in a pocket, not on the table)
- [ ] `When the Sensor Lies.pptx` on the admin laptop + a PDF export as backup (the old `QueenCityCon_Presentation.md` is superseded)
- [ ] Rack cabling photos + filled-in switch port map (field guide §1B)
- [ ] Safety glasses + bottle shield/enclosure (if bursting bottles)

---

## 🚨 Critical Items (Do Not Forget!)

1. **SFP+ DAC cable** - Pick up from dad's house (no backbone without this)
2. **Mock WAN dumb switch** - Buy before conference (cross-VLAN routing fails without this)
3. **3x USB-C power adapters** - Pi #5, Secure Pi, Vulnerable Pi (PoE insufficient)
4. **12V PSU + wiring** - Pneumatic system won't work without this
5. **Suricata laptop** - Must be bare metal, can't use VM
6. **Credentials cheat sheet** - 20+ passwords, don't rely on memory
7. **Spare bottles** - Murphy's Law says one will burst during setup

---

## 📋 Pre-Conference Testing (1 Week Before)

- [ ] Full cold boot test with Mock WAN setup (air-gap mode)
- [ ] Run attack demo end-to-end (vulnerable compromised, secure protected)
- [ ] Verify all 5 hospital Pi ECG waveforms on Node-RED dashboard
- [ ] Test Grafana IDS dashboard shows attack traffic
- [ ] Verify Wazuh SIEM logs secure Pi rejections
- [ ] Practice presentation with live demo (15-minute target)
- [ ] Test HDMI output to external monitor (simulate projector)
- [ ] Verify all credentials work (Vault, Grafana, Node-RED, Wazuh)
- [ ] Pack spare consumables (bottles, cables, power strips)

---

## 🎯 Day-of-Conference Setup Timeline

**2 hours before session:**
- Unpack and rack mount equipment (UDM-SE, Switch, Dell server)
- Connect Mock WAN (UDM-SE WAN → dumb switch)
- Connect SFP+ DAC (UDM-SE → Switch backbone)
- Connect power to all rack equipment
- Power on in order: UDM-SE → Switch → TrueNAS

**1.5 hours before:**
- Wait 15 minutes for VMs to boot
- Unseal Vault (3 keys via web UI)
- Restart all Raspberry Pi services (SSH loop)

**1 hour before:**
- Verify Node-RED dashboard (5 ECG waveforms, 4 pressure gauges, Security Status Panel)
- Verify Grafana hospital dashboard (historical data loading)
- Verify Grafana IDS dashboard (ready for attack)
- Verify Wazuh SIEM login (basic auth)

**30 minutes before:**
- Run 5-second test attack (`attack_spoof.py --dual`, then stop)
- Verify vulnerable system responds (gauge drops to 0)
- Verify secure system rejects (Security Status Panel goes red)
- Verify IDS dashboard shows spike
- Let system return to normal (Security Status Panel green)

**15 minutes before:**
- Connect laptop HDMI to projector
- Open browser tabs (Node-RED, Grafana Hospital, Grafana IDS, Wazuh)
- Load presentation slides
- Test microphone
- Deep breath

**Showtime!**

---

**Last Updated:** 2026-10-26
**Status:** Ready for Queen City Con 0x4 (November 13-15, 2026)
