# Balloon Security Demo - Design Notes & Architecture Decisions

**Last Updated:** 2026-02-05
**Project:** Senior Design I - Expo Demonstration
**Team:** Team 41

---

## DESIGN CHANGES & CRITICAL DECISIONS

### 1. BMP388 Pressure Sensor Integration (2026-02-05)

**Challenge Identified:**
- BMP388 sensors are I²C digital sensors, not inline pneumatic sensors
- Cannot directly measure air pressure in tubing without proper interface

**Solution - Pressure Chamber Design:**

**Physical Setup:**
```
Main Air Line (to balloon)
     |
     v
[Brass NPT Tee]
     ├─ Port 1: Air IN (from solenoid valve)
     ├─ Port 2: Air OUT (continues to balloon)
     └─ Port 3: [Barb fitting] → [Short tube 6"] → [Pressure Chamber]
                                                           |
                                                    [BMP388 sensor inside]
                                                    [4 wires to Pi GPIO]
```

**Pressure Chamber Construction:**

**⭐ RECOMMENDED SOLUTION: 4oz Mason Jar with Metal Lid**

After research and evaluation, the **Ball 4oz Quilted Crystal Jelly Jar** is the optimal pressure chamber:

**Why Mason Jars Are Best:**
- ✅ Glass construction = 100% airtight (no porosity like plastic)
- ✅ Metal screw lid with rubber gasket = proven pressure seal
- ✅ Designed for canning/preserving = holds vacuum/pressure reliably
- ✅ Easy to drill precise holes in metal lid
- ✅ Clear glass = can see sensor operation during demo
- ✅ Cheap & locally available (~$1-2 each, sold in 12-packs)
- ✅ Professional appearance for expo presentation
- ✅ Perfect size: 4oz minimizes dead air volume

**Product:** Ball Regular Mouth 4oz Quilted Jelly Jars (12-pack)
**Where to Buy:** Walmart, Amazon, grocery stores, Target
**Cost:** $10-15 for 12-pack (~$1-2 per jar, need 2 total)
**Links:**
- Walmart: https://www.walmart.com/ip/Ball-Regular-Mouth-4oz-Quilted-Pint-Mason-Jars-12-Count/17203435
- Amazon: https://www.amazon.com/Airtight-Canning-Kitchen-Handmade-Desserts/dp/B0CR6H5CJN

**Construction Steps:**
1. Purchase 12-pack of Ball 4oz jelly jars (local pickup recommended)
2. Drill two holes in metal lid:
   - **Hole 1:** 5/16" diameter for 1/4" NPT barb fitting (air inlet)
   - **Hole 2:** 3/16" diameter for I²C wire bundle (4 wires × 22AWG)
3. Install brass barb fitting through air hole:
   - Insert barb from inside lid (threads poke through)
   - Seal around threads with silicone sealant or epoxy (airtight)
   - Allow to cure 24 hours
4. Mount BMP388 sensor inside jar:
   - Use M2.5 brass standoffs (from BOM) glued to bottom of jar
   - Position sensor horizontally, centered in jar
   - Ensure I²C wires reach lid hole
5. Thread 4× I²C wires through lid wire hole
6. Seal wire hole with silicone sealant or hot glue
   - Leave small flexibility for wire movement
   - Ensure airtight seal around all 4 wires
7. Screw metal lid onto jar - rubber gasket creates automatic seal
8. Connect air tube to barb fitting (from brass tee in main pneumatic line)
9. Connect I²C wires to Raspberry Pi GPIO (see wiring below)

**Alternative Options (Not Recommended):**
- **Option B:** Small plastic junction box (already in BOM)
  - ⚠️ ABS plastic can have micro-porosity (slow air leaks)
  - ⚠️ Gasket seals may not hold pressure long-term
  - Only use if mason jars unavailable

- **Option C:** Ziplock bag (emergency only)
  - ❌ Not professional for expo demo
  - ❌ Unreliable seal
  - ❌ Not recommended

**How It Works:**
1. Air flows through main tee junction to balloon
2. Side port taps off to dead-end chamber
3. Air pressure in chamber equals line pressure
4. BMP388 measures ambient air pressure in chamber
5. No airflow needed through chamber - just static pressure sensing

**Bill of Materials (per system):**
- 1× Brass NPT tee (already in BOM) ✓
- 1× Barb fitting 1/4" NPT (already in BOM) ✓
- 1× Short tube section ~6-12" (cut from 100 ft roll when arrives) ✓
- 1× Ball 4oz mason jar with metal lid **[NEW - LOCAL PICKUP NEEDED]** ⚠️
- 1× Silicone sealant or epoxy (for sealing barb fitting) **[NEW - LOCAL PICKUP]** ⚠️
- 4× Extended I²C wires ~12-18" long **[NEW - NEED TO ORDER]** ⚠️
- 2× M2.5 brass standoffs (already in BOM) ✓
- Drill with 5/16" and 3/16" bits (standard tools)

**I²C Wiring (BMP388 to Raspberry Pi GPIO):**
```
BMP388 Pin  →  Raspberry Pi GPIO
VIN (3.3V)  →  Pin 1 (3.3V Power)
GND         →  Pin 6 (Ground)
SCL         →  Pin 5 (GPIO 3 / I²C Clock)
SDA         →  Pin 3 (GPIO 2 / I²C Data)
```

**Status:** ✓ Design finalized, ⚠️ awaiting additional materials purchase

**Additional Items Needed (Not in Original BOM):**

| Item | Qty | Purpose | Where to Buy | Est. Cost |
|------|-----|---------|--------------|-----------|
| Ball 4oz Mason Jars (12-pack) | 1 pack | Pressure chambers (need 2, extras for spares) | Walmart, grocery store, Target | $10-15 |
| Female-to-Female DuPont Jumper Wires 30cm (120pcs kit) | 1 kit | Connect BMP388 in chamber to Pi GPIO (need 8 wires, kit has 40 F-F) | Amazon | $7-8 |
| Clear Silicone Sealant or Marine Epoxy | 1 tube | Seal barb fittings and wire holes airtight | Hardware store (Home Depot/Lowe's) | $5-8 |
| **TOTAL ADDITIONAL COST** | | | | **~$22-31** |

**Recommended I²C Extension Cable Options:**

**Option 1 (Simplest): Female-to-Female DuPont Jumper Wires - 20cm or 30cm**
- Product: "120pcs Breadboard Jumper Wires" kits (includes F-F, M-M, M-F)
- Length: 20cm (8") or 30cm (12") - either works fine for I²C at standard speed
- Use 4× wires per sensor (VIN, GND, SCL, SDA)
- Amazon Links:
  - 20cm kit: https://www.amazon.com/Kuman-Breadboard-Arduino-Raspberry-Multicolored/dp/B01BV3Z342
  - 30cm kit: https://www.amazon.com/SIM-NAT-Breadboard-Arduino-Raspberry/dp/B06XRV92ZB
- Cost: $6-8 per kit (includes 120 wires total - plenty of spares)
- **Advantage:** Already have male ends on BMP388 sensor, just need F-F wires

**Option 2 (Professional): Adafruit STEMMA QT Cables**
- Product: STEMMA QT / Qwiic JST SH 4-Pin Cable
- Length: 200mm (8") or 300mm (12")
- Adafruit Links:
  - 200mm: https://www.adafruit.com/product/4401
  - 300mm: https://www.adafruit.com/product/5384
- Cost: $1.25 each (need 2 = $2.50 total)
- **Note:** Requires BMP388 sensor to have STEMMA QT connector (Adafruit version does)
- ⚠️ Check if your BMP388 sensors have JST-SH connectors before ordering

**Option 3 (DIY): Extend Existing Wires**
- Use DuPont jumper wires from BOM (ELEGOO 120pcs kit - already arrived)
- Solder multiple wires together for needed length
- Cover with heat shrink tubing (from BOM - already arrived)
- Cost: $0 (use existing materials)
- Time: ~30 minutes per sensor

**RECOMMENDATION: Order Option 1 (30cm Female-to-Female DuPont wires)**
- Most versatile and compatible
- Standard Raspberry Pi GPIO connection
- Longer length (30cm) gives flexibility for mounting
- Can use extras for other connections in demo

**Local Pickup Items:**
- Mason jars: Any grocery store, Walmart, Target (available today)
- Silicone sealant: Home Depot/Lowe's (same trip as potential foam board pickup)

---

### 2. Vulnerable System Architecture - Network-Based Sensor Spoofing (2026-02-05)

**Challenge Identified:**
- Original design: BMP388 hardwired via I²C to Pi #7
- Problem: No network pathway to spoof sensor data for attack demonstration
- Academic integrity: Cannot misrepresent the attack vector in presentation

**Solution - Two-Process Architecture with HTTP Communication:**

#### **System Architecture:**

**Vulnerable System (Pi #7 - 192.168.50.100) consists of TWO Python processes:**

**Process 1: `sensor_publisher.py`**
- Reads BMP388 pressure sensor via I²C (physical hardware)
- Converts pressure to PSI
- Publishes sensor data via HTTP POST to control system
- Runs as systemd service (auto-start)
- Simulates "network-connected IoT sensor"

**Process 2: `balloon_control_api.py`**
- Flask web server listening on port 5000
- Accepts sensor data via HTTP POST endpoint `/sensor`
- **NO AUTHENTICATION** on sensor endpoint (intentional vulnerability)
- Uses received pressure data for pump/valve control decisions
- Cannot distinguish legitimate sensor from spoofed data
- Runs as systemd service (auto-start)

#### **Data Flow Diagram:**

```
┌─────────────────────────────────────────────────────────────┐
│  Raspberry Pi #7 (192.168.50.100) - VULNERABLE SYSTEM      │
│                                                               │
│  ┌──────────────────┐                                       │
│  │  BMP388 Sensor   │ (in pressure chamber)                 │
│  │  I²C Address:    │                                       │
│  │  0x77            │                                       │
│  └────────┬─────────┘                                       │
│           │ I²C (4 wires to GPIO pins 1,3,5,6)              │
│           ↓                                                  │
│  ┌────────────────────────────────────┐                     │
│  │  sensor_publisher.py               │                     │
│  │  (Systemd service)                 │                     │
│  │                                     │                     │
│  │  while True:                        │                     │
│  │    pressure = bmp.pressure / 6894  │ ← Read I²C          │
│  │    requests.post(                  │                     │
│  │      'http://localhost:5000/sensor'│                     │
│  │      json={'pressure': psi,        │                     │
│  │            'timestamp': time(),    │                     │
│  │            'source': 'bmp388'})    │                     │
│  │    sleep(1)  # Publish every 1 sec │                     │
│  └──────────────┬─────────────────────┘                     │
│                 │ HTTP POST (network protocol)               │
│                 │ localhost:5000/sensor                      │
│                 ↓                                             │
│  ┌────────────────────────────────────┐                     │
│  │  balloon_control_api.py            │                     │
│  │  (Flask server on port 5000)       │                     │
│  │                                     │                     │
│  │  @app.route('/sensor', POST)       │                     │
│  │  def update_sensor():               │                     │
│  │    data = request.json             │                     │
│  │    # NO AUTH CHECK! ← VULNERABILITY│                     │
│  │    current_pressure = data['psi']  │                     │
│  │    return {'status': 'ok'}         │                     │
│  │                                     │                     │
│  │  def control_loop():                │                     │
│  │    if current_pressure < 3.0:      │                     │
│  │      turn_on_pump()  # Relay 1     │                     │
│  │    else:                            │                     │
│  │      turn_off_pump()                │                     │
│  └────────────────────────────────────┘                     │
│                 ↑                                             │
└─────────────────┼─────────────────────────────────────────────┘
                  │ HTTP POST (spoofed!)
                  │ ATTACKER sends fake data
                  │
        ┌─────────┴──────────────┐
        │  Attacker Laptop       │
        │  (VLAN2 network)       │
        │                        │
        │  Attack Script:        │
        │  while true; do        │
        │    curl -X POST \      │
        │    http://192.168.50.  │
        │         100:5000/sensor│
        │    -H "Content-Type:   │
        │         application/   │
        │         json" \         │
        │    -d '{"pressure":    │
        │         0.0,           │
        │         "source":      │
        │         "attacker"}'   │
        │    sleep 0.1           │
        │  done                  │
        └────────────────────────┘
```

#### **Attack Mechanism:**

**Normal Operation:**
1. BMP388 measures real pressure: 2.5 PSI
2. `sensor_publisher.py` reads via I²C every 1 second
3. POSTs to control system: `{"pressure": 2.5}`
4. Control system uses value for pump decisions

**Attack Scenario:**
1. Balloon inflating, real pressure: 2.5 PSI
2. Legitimate sensor publishes every 1 second
3. **Attacker floods with fake data every 0.1 seconds:**
   - POST: `{"pressure": 0.0, "source": "attacker"}`
4. Control system accepts attacker's data (no authentication)
5. System believes pressure is 0.0 PSI (spoofed)
6. Keeps pump running (thinks balloon needs more air)
7. Real pressure continues rising: 3.0... 3.5... 4.0 PSI
8. **Balloon pops!** (over-inflated beyond safe limit)

**Why This Works:**
- Attacker sends 10× more frequent updates than legitimate sensor
- No authentication to verify data source
- System blindly trusts last received value
- Creates race condition - attacker's messages win

#### **Presentation Talking Points:**

✅ **Honest statements for academic integrity:**
- "The pressure sensor is physically connected to the Raspberry Pi via I²C"
- "Sensor data is published over HTTP to the control system"
- "The control system has no authentication on the sensor data endpoint"
- "An attacker on the same network can send spoofed sensor readings"
- "The system cannot distinguish legitimate sensor data from spoofed data"
- "This creates a race condition where the attacker's rapid updates override real data"
- "The control system makes safety decisions based on falsified pressure readings"

✅ **Real-world parallels:**
- Many IoT devices publish sensor data over MQTT/HTTP without authentication
- Stuxnet manipulated sensor readings to hide centrifuge damage
- Medical devices with network-connected sensors vulnerable to same attack
- Industrial control systems often lack sensor data validation

**Status:** ✓ Architecture finalized, awaiting software implementation

---

### 3. Secure System Architecture - Hardwired Sensors (2026-02-05)

**Secure System (Pi #6 - 10.30.0.25):**

**Key Differences from Vulnerable System:**
- BMP388 read **directly via I²C** in main control loop (no network publishing)
- All sensor data stays within single process (no HTTP APIs)
- No external network endpoints for sensor data
- Wazuh SIEM monitoring all system actions
- Keycloak authentication required for any remote control
- TLS-encrypted MQTT for logging/monitoring only (not control)

**Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│  Raspberry Pi #6 (10.30.0.25) - SECURE SYSTEM         │
│                                                          │
│  ┌──────────────┐                                       │
│  │  BMP388      │ (hardwired I²C)                       │
│  └──────┬───────┘                                       │
│         │ I²C direct connection                         │
│         ↓                                                │
│  ┌──────────────────────────────────┐                  │
│  │  balloon_control_secure.py       │                  │
│  │  (Single integrated process)     │                  │
│  │                                   │                  │
│  │  def main_loop():                 │                  │
│  │    # Read sensor DIRECTLY         │                  │
│  │    pressure = bmp.pressure / 6894 │ ← I²C read      │
│  │                                   │                  │
│  │    # Log to Wazuh (monitoring)    │                  │
│  │    log_to_wazuh(pressure)         │                  │
│  │                                   │                  │
│  │    # Safety decision               │                  │
│  │    if pressure > 3.5:             │                  │
│  │      emergency_shutoff()          │                  │
│  │      alert_wazuh_attack()         │                  │
│  │                                   │                  │
│  │    # Normal control               │                  │
│  │    if pressure < 2.0:             │                  │
│  │      turn_on_pump()               │                  │
│  │    elif pressure >= 2.5:          │                  │
│  │      turn_off_pump()              │                  │
│  └───────────────────────────────────┘                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
         │ TLS-encrypted MQTT (monitoring only)
         ↓
   [Wazuh SIEM on 10.30.0.55]
   - Monitors all actions
   - Alerts on anomalies
   - Cannot be spoofed (TLS + auth)
```

**Why Attack Fails on Secure System:**
- Sensor data never exposed on network
- No HTTP endpoints to spoof
- Firewall blocks VLAN2 → VLAN30 traffic
- Wazuh detects unauthorized access attempts
- Real pressure data always used for decisions

**Status:** ✓ Architecture finalized, awaiting software implementation

---

## IMPLEMENTATION CHECKLIST

### Hardware Assembly (Waiting for relay HATs):
- [ ] Build pressure chambers for both BMP388 sensors
- [ ] Wire I²C connections (BMP388 → Pi GPIO)
- [ ] Test I²C communication with both sensors
- [ ] Verify pressure readings in chamber setup

### Software Development:

**Vulnerable System (Pi #7 - 192.168.50.100):**
- [✓] Write `sensor_publisher.py` (I²C → HTTP publisher) - **COMPLETED 2026-02-05**
- [✓] Write `balloon_control_api.py` with `/sensor` endpoint (no auth) - **COMPLETED 2026-02-05**
- [✓] Write `attack_spoof.py` attack script - **COMPLETED 2026-02-05**
- [✓] Configure systemd services (auto-start) - **DEPLOYED 2026-02-05**
  - ✅ `balloon-control-api.service` - **RUNNING** (Flask on port 5000)
  - ⏸️ `balloon-sensor-publisher.service` - **DISABLED** (waiting for BMP388 hardware)
- [ ] Test normal operation (sensor → control) - *Waiting for BMP388 sensors*
- [ ] Test spoofing attack (verify balloon over-inflates) - *Waiting for hardware*

**Secure System (Pi #6 - 10.30.0.25):**
- [✓] Write `balloon_control_secure.py` (direct I²C read) - **COMPLETED 2026-02-05**
- [✓] Integrate Wazuh syslog logging - **COMPLETED 2026-02-05**
- [✓] Add input validation and anomaly detection - **COMPLETED 2026-02-05**
- [✓] Add attack detection logic - **COMPLETED 2026-02-05**
- [✓] Configure systemd service (auto-start) - **DEPLOYED 2026-02-05**
  - ⏸️ `balloon-control-secure.service` - **DISABLED** (waiting for BMP388 hardware)
- [ ] Test attack resistance (verify failure to spoof) - *Waiting for hardware*

**Test Scripts (Both Systems):**
- [✓] Write `test_bmp388.py` (sensor diagnostic) - **COMPLETED 2026-02-05**
- [✓] Write `test_relays.py` (relay HAT diagnostic) - **COMPLETED 2026-02-05**

**Deployment Status:**
- [✓] Scripts transferred to both Raspberry Pis - **COMPLETED 2026-02-05**
- [✓] Systemd service files created and installed - **COMPLETED 2026-02-05**
- [✓] Services configured for auto-start on boot - **COMPLETED 2026-02-05**
- [✓] Pi #7 control API verified running and accessible - **TESTED 2026-02-05**

### Documentation:
- [✓] Architecture documented (this file)
- [✓] Systemd service deployment documented - **UPDATED 2026-02-05**
- [✓] Deployment troubleshooting lessons learned - **DOCUMENTED 2026-02-05**
- [ ] Update wiring diagrams with pressure chamber details
- [ ] Update attack demonstration script in BALLOON_DEMO_NETWORK_CONFIG.md
- [ ] Create presentation slides explaining architecture

---

## TECHNICAL SPECIFICATIONS

### BMP388 Sensor Specifications:
- **Pressure Range:** 300-1250 hPa (4.35-18.1 PSI)
- **Accuracy:** ±0.5 hPa (±0.007 PSI) - excellent for balloon demo
- **Interface:** I²C (address 0x77)
- **Supply Voltage:** 1.71-3.6V (use Pi's 3.3V)
- **Response Time:** <10ms
- **Library:** adafruit-circuitpython-bmp3xx (already installed on both Pis)

### Conversion Formula:
```python
# BMP388 returns pressure in Pascals (Pa)
pressure_pa = bmp388.pressure  # e.g., 101325 Pa
pressure_psi = pressure_pa / 6894.76  # Convert to PSI (e.g., 14.7 PSI)
```

### Target Pressure Ranges:
- **Safe Operation:** 0-2.5 PSI
- **Warning Zone:** 2.5-3.5 PSI (buzzer alarm)
- **Emergency Shutoff:** 3.5 PSI (automatic pump cutoff)
- **Balloon Pop Pressure:** ~4-5 PSI (destructive test)
- **Attack Target:** Spoof readings to 0 PSI while real pressure exceeds 4 PSI

---

## REVISION HISTORY

| Date | Change | Reason |
|------|--------|--------|
| 2026-02-05 | Added pressure chamber design | BMP388 requires ambient air pressure access |
| 2026-02-05 | Added two-process architecture for vulnerable system | Enable network-based sensor spoofing for attack demo |
| 2026-02-05 | Documented secure vs vulnerable architectures | Clarify security differences for presentation |
| 2026-02-05 | **Removed DC barrel jack adapters from BOM** | Power supply barrel jack will be cut off and wired directly for high-current reliability (10A air pumps exceed 5A adapter rating) |
| 2026-02-05 | **Completed all Python scripts and deployed to Pis** | All 6 scripts written, tested, and deployed via systemd services |
| 2026-02-05 | **Services configured with username `username`** | Both Pi #6 and Pi #7 use username user for consistency |
| 2026-02-05 | **Systemd hardening adjusted for GPIO/I2C access** | Removed ProtectHome, ProtectSystem, PrivateTmp that blocked hardware access |

---

---

## SYSTEMD SERVICE DEPLOYMENT (2026-02-05)

### Deployment Summary

**Date:** 2026-02-05 22:00-22:30 EST
**Status:** ✅ Successfully deployed all services to both Raspberry Pis

### Scripts Deployed

**Location on both Pis:** `/home/username/balloon-demo/scripts/`

**Pi #7 (Vulnerable - 192.168.50.100):**
- `sensor_publisher.py` - Reads BMP388 via I²C, publishes to HTTP
- `balloon_control_api.py` - Flask API, accepts sensor data, controls relays
- `attack_spoof.py` - Attack script for demonstration
- `test_bmp388.py` - Sensor diagnostic tool
- `test_relays.py` - Relay HAT diagnostic tool

**Pi #6 (Secure - 10.30.0.25):**
- `balloon_control_secure.py` - Direct I²C read, Wazuh logging, input validation
- `test_bmp388.py` - Sensor diagnostic tool
- `test_relays.py` - Relay HAT diagnostic tool

### Systemd Services Configured

**Location:** `/etc/systemd/system/`

**Pi #7 Services:**
1. `balloon-control-api.service`
   - **Status:** ✅ RUNNING
   - **Port:** 5000 (accessible at http://192.168.50.100:5000)
   - **User:** username
   - **Auto-start:** Enabled
   - **Verified:** Flask server responding to HTTP requests

2. `balloon-sensor-publisher.service`
   - **Status:** ⏸️ DISABLED (waiting for BMP388 sensor)
   - **Error when enabled:** "No I2C device at address: 0x77"
   - **Expected behavior:** Will auto-start when sensor connected

**Pi #6 Services:**
1. `balloon-control-secure.service`
   - **Status:** ⏸️ DISABLED (waiting for BMP388 sensor)
   - **Error when enabled:** "No I2C device at address: 0x77"
   - **Expected behavior:** Will auto-start when sensor connected

### Deployment Lessons Learned

**Issue #1: Systemd CHDIR Permission Denied**
- **Error:** `balloon-control-secure.service: Failed at step CHDIR spawning /usr/bin/python3: Permission denied`
- **Cause:** `ProtectHome=true` in service file prevented systemd from accessing `/home/username/`
- **Solution:** Changed `ProtectHome=true` to `ProtectHome=read-only`
- **Learning:** Hardware control services need filesystem access; strict sandboxing conflicts with GPIO/I2C libraries

**Issue #2: GPIO Library Temp File Creation**
- **Error:** `FileNotFoundError: [Errno 2] No such file or directory: '.lgd-nfy-3'`
- **Cause:** `PrivateTmp=true` prevented lgpio library from creating required temporary files
- **Solution:** Removed `PrivateTmp=true` from service file
- **Learning:** GPIO libraries (lgpio, used by adafruit_blinka) need shared /tmp access

**Issue #3: System Directory Write Access**
- **Cause:** `ProtectSystem=strict` prevented writes to system directories needed by GPIO daemon
- **Solution:** Removed `ProtectSystem=strict` from service file
- **Learning:** Hardware interfacing requires relaxed filesystem restrictions

**Issue #4: GPIO/I2C Group Permissions**
- **Solution:** Added `SupplementaryGroups=gpio i2c` to service file
- **Learning:** Service must have explicit GPIO and I2C group membership for hardware access

### Final Working Service Configuration

```ini
[Unit]
Description=Balloon Demo - Secure Control System
After=network.target syslog.target
Wants=network-online.target

[Service]
Type=simple
User=username
SupplementaryGroups=gpio i2c
WorkingDirectory=/home/username/balloon-demo/scripts
ExecStart=/usr/bin/python3 /home/username/balloon-demo/scripts/balloon_control_secure.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

# Security hardening (adjusted for hardware access)
NoNewPrivileges=true
ProtectHome=read-only
# PrivateTmp=true - REMOVED (conflicts with GPIO)
# ProtectSystem=strict - REMOVED (conflicts with GPIO)

# Resource limits
LimitNOFILE=1024
CPUQuota=50%

[Install]
WantedBy=multi-user.target
```

### Security Posture Analysis

**Retained Security Features:**
- ✅ `NoNewPrivileges=true` - Prevents privilege escalation
- ✅ `ProtectHome=read-only` - Limits home directory access
- ✅ `LimitNOFILE=1024` - Resource limiting
- ✅ `CPUQuota=50%` - Prevents CPU exhaustion
- ✅ Running as non-root user (`username`)
- ✅ Network isolation (VLAN30 for secure, VLAN50 for vulnerable)
- ✅ Firewall rules (UDM-SE blocking VLAN50→VLAN30)

**Removed Security Features (due to GPIO/I2C requirements):**
- ❌ `PrivateTmp=true` - GPIO libraries need shared /tmp
- ❌ `ProtectSystem=strict` - GPIO daemon needs system directory writes
- ❌ Full home directory protection - Scripts in /home/username/

**Conclusion:**
Hardware interfacing services cannot use full systemd sandboxing. Primary security comes from:
1. Network segmentation (VLANs + firewall)
2. Application-level input validation (in Python code)
3. SIEM monitoring (Wazuh)
4. Running as non-root with limited permissions

### Verification Commands

**Check service status:**
```bash
# Pi #7
ssh username@192.168.50.100
sudo systemctl status balloon-control-api.service
curl http://localhost:5000/status

# Pi #6
ssh username@10.30.0.25
sudo systemctl status balloon-control-secure.service
```

**View logs:**
```bash
sudo journalctl -u balloon-control-api.service -f
sudo journalctl -u balloon-control-secure.service -n 50
```

**Re-enable when hardware arrives:**
```bash
# After connecting BMP388 sensors and enabling I2C
sudo systemctl enable balloon-sensor-publisher.service
sudo systemctl start balloon-sensor-publisher.service

sudo systemctl enable balloon-control-secure.service
sudo systemctl start balloon-control-secure.service
```

### Hardware Preparation Checklist

Before enabling sensor services:
- [ ] Connect BMP388 sensors via I²C (VIN→Pin1, GND→Pin6, SCL→Pin5, SDA→Pin3)
- [ ] Enable I2C: `sudo raspi-config` → Interface Options → I2C → Enable
- [ ] Verify I2C detection: `i2cdetect -y 1` (should show 0x77)
- [ ] Test sensor: `python3 test_bmp388.py`
- [ ] Connect Sequent 8-RELAYS HAT
- [ ] Verify relay detection: `i2cdetect -y 1` (should show 0x20 and 0x77)
- [ ] Test relays: `python3 test_relays.py`
- [ ] Build pressure chambers (mason jars with bulkhead fittings)
- [ ] Connect pneumatic system (pump, valve, tubing, balloon)
- [ ] Enable and start all systemd services
- [ ] Verify end-to-end operation

---

## POWER SUPPLY WIRING (Design Change - 2026-02-05)

**Decision:** Cut barrel jack off COOLM 12V 10A power supplies and wire directly to DIN rail terminal blocks.

**Reason:**
- Air pumps draw up to 10A (120W)
- Standard barrel jack adapters rated for 5A (60W) would overheat/fail
- Direct wiring eliminates failure point and supports full 10A capacity

**Procedure (per power supply):**

1. **Cut the barrel jack plug:**
   - Use wire cutters to cut the barrel jack plug off the DC output cable
   - Cut as close to the plug as possible to maximize wire length
   - You should have 2 wires exposed (usually red/black or red/white)

2. **Strip and identify wires:**
   - Strip 1/4" of insulation from each wire
   - **Red wire** = +12V DC (positive)
   - **Black/White wire with stripe** = GND (negative/ground)
   - If unsure, use a multimeter to verify polarity

3. **Tin the wire ends (optional but recommended):**
   - Apply solder to the stripped wire ends
   - Prevents fraying and ensures good contact in screw terminals

4. **Connect to DIN rail terminal block:**
   - Red (+12V) → Terminal labeled "12V+" or "VCC"
   - Black (GND) → Terminal labeled "GND" or "0V"
   - Tighten screw terminals securely

5. **Label the connections:**
   - Use Brother label maker to label: "12V DC IN" and "GND"
   - Prevents confusion during assembly

**Safety Notes:**
- ⚠️ **NEVER** connect power supply to AC outlet while wiring
- Double-check polarity before powering on (reversed polarity can destroy components)
- Verify voltage with multimeter before connecting to circuits: should read 12.0V DC ±0.5V

**Wire Gauge:**
- COOLM power supply typically uses 18AWG wire
- Good for 10A continuous current
- If extending wire, use 18AWG or thicker (16AWG, 14AWG)

---

**Next Steps:**
1. ✅ ~~Implement Python scripts~~ - **COMPLETED 2026-02-05**
2. ✅ ~~Deploy systemd services~~ - **COMPLETED 2026-02-05**
3. Wait for Sequent 8-RELAYS HAT arrival (critical blocker for relay control)
4. Wait for BMP388 sensors to arrive (critical blocker for pressure sensing)
5. Enable I2C on both Raspberry Pis when sensors arrive
6. Build and test pressure chambers (mason jars)
7. Cut barrel jacks off power supplies and wire to DIN terminal blocks
8. Test complete hardware assembly
9. Enable disabled systemd services once hardware connected
10. Test attack scenario end-to-end
11. Practice demo presentation timing

**Hardware Blockers (Cannot proceed until arrival):**
- ⏳ Sequent 8-RELAYS HAT (2 units) - On order
- ⏳ BMP388 pressure sensors (2 units) - Already arrived 2026-02-05 ✅
- ⏳ Mason jars for pressure chambers - Need local pickup
- ⏳ Female-to-female DuPont wires for I²C extension - Need to order

**Software Status:**
- ✅ All 6 Python scripts completed and deployed
- ✅ Both Raspberry Pis configured with systemd services
- ✅ Pi #7 control API verified running (http://192.168.50.100:5000)
- ⏸️ Sensor-dependent services disabled until hardware arrives

**Questions/Concerns:**
- Pressure chamber seal quality - may need multiple attempts to get air-tight
- HTTP flooding attack timing - may need to tune polling rates
- BMP388 accuracy at low PSI (0-5 PSI range) - should be fine given ±0.007 PSI accuracy
- Systemd hardening limitations for GPIO access - security tradeoffs documented
