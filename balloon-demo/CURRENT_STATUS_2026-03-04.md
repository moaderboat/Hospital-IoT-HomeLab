# Balloon Demo - Current Implementation Status

**Last Updated:** 2026-03-04
**Session:** Burst Pressure Characterization Complete + 100 PSI Sensor Upgrade Ordered

---

## ✅ MAJOR MILESTONE: BURST TEST SCRIPT WORKING

### Burst Pressure Testing (Pi #7 - 2026-03-04)

**Test Script:** `test_burst_pressure.py` ✅ **FULLY OPERATIONAL**
- Automated burst pressure characterization
- Standardizes to atmospheric pressure before test
- Pulsed pump control (0.1s bursts) prevents overshoot
- Incremental 1 PSI steps with configurable hold time (default 7 seconds)
- Burst detection via 1.5 PSI sudden pressure drop
- Emergency stop on Ctrl+C
- Dual sensor monitoring (A0 upstream + A1 downstream)
- **Successfully tested to 26 PSI** before sensor saturation

**Test Results (2026-03-04):**
- ✅ Bottle survived to 26 PSI without burst
- ✅ 30 PSI sensor saturated at 26.9 PSI (voltage maxed at 4.5V)
- ✅ Test aborted at ceiling due to sensor limitation
- ✅ Pump control verified - NO spurious pump activation
- ✅ Emergency venting verified - system safely depressurizes
- **Conclusion:** Need higher-range sensors to find true burst pressure

**Sensor Upgrade Ordered:**
- **Model:** DATAQ 2000361-100H (0-100 PSI, 0.5-4.5V output)
- **Quantity:** 4 sensors @ $119 each = $476 total
- **Status:** Ordered 2026-03-04, awaiting delivery
- **Next Test:** Re-run to 70 PSI ceiling with new sensors

---

## ✅ CURRENTLY IMPLEMENTED (WORKING)

### Hardware - Pi #7 (Vulnerable System - 192.168.50.100) ✅ FULLY ASSEMBLED

**Relay HATs:**
- ✅ Sequent 8-RELAYS HAT (STACK=0, I2C 0x27) - solenoids
  - Relay 2: Inflate solenoid (NC type)
  - Relay 3: Vent solenoid (NC type)
  - Relay 4: Relief solenoid (NC type)
- ✅ Sequent 40A 3-relay HAT (STACK=0, I2C 0x60) - pump
  - Relay 3: Air pump (23A load)
  - Side-mounted via GPIO ribbon cable (physically too large to stack)
- ✅ Both HATs verified working via `lib8relind` and `lib3relind`
- ✅ I2C bus slowdown applied (`i2c_arm_baudrate=10000` in `/boot/config.txt`) - fixes sensor errors

**Pressure Sensors (CURRENT - pending upgrade):**
- ✅ DATAQ 15 PSI sensor (2000361-15H) on ADS1115 channel A1 (downstream, primary)
- ✅ DATAQ 30 PSI sensor (2000361-30H) on ADS1115 channel A0 (upstream, monitoring)
- ✅ ADS1115 ADC (I2C 0x48) via BSS138 level shifter (3.3V ↔ 5V)
- ✅ Voltage range: 0.5V (0 PSI) to 4.5V (full scale)
- ⏳ **UPGRADE IN PROGRESS:** 4× DATAQ 100 PSI sensors ordered (delivery pending)

**Pneumatics:**
- ✅ Air pump (23A, 12V) wired to 40A HAT relay 3
- ✅ 3× NC solenoid valves wired to 8-RELAYS HAT relays 2/3/4
- ✅ 1L plastic bottle pressure vessel
- ✅ Pneumatic tubing and fittings installed
- ✅ Emergency manual shutoff switch (inline with 12V PSU)

**Power:**
- ✅ 12V 29A power supply (pump + solenoids)
- ✅ Raspberry Pi 5 powered independently (USB-C)
- ✅ Terminal blocks for power distribution
- ✅ Kill switch tested and working

---

### Software - All Scripts Updated for 100 PSI Sensors ✅

**Location:** `/home/username/balloon-demo/scripts/` on both Pis

**Pi #7 (Vulnerable System - 192.168.50.100):**
- ✅ `balloon_control_api_vulnerable.py` - Flask API server (systemd service RUNNING on port 5000)
- ✅ `sensor_publisher.py` - **UPDATED** for 100 PSI sensors (ready for hardware swap)
- ✅ `test_burst_pressure.py` - **COMPLETED** burst characterization script (updated for 100 PSI, 70 PSI ceiling)
- ✅ `attack_spoof.py` - Sensor spoofing attack script
- ✅ `test_pressure_sensor.py` - Diagnostic for ADS1115 + DATAQ sensors
- ✅ `test_relays.py` - Relay HAT diagnostic
- ✅ Libraries: `adafruit-circuitpython-ads1x15`, `lib8relind`, `lib3relind`, `paho-mqtt`, `flask`

**Pi #6 (Secure System - 10.30.0.25):**
- ✅ `balloon_control_secure.py` - **UPDATED** for 100 PSI sensors (ready for hardware swap)
- ✅ `test_pressure_sensor.py` - Diagnostic for ADS1115 + DATAQ sensors
- ✅ `test_relays.py` - Relay HAT diagnostic
- ✅ Libraries: `adafruit-circuitpython-ads1x15`, `lib8relind`, `paho-mqtt`

**All scripts ready - just waiting for 100 PSI sensor hardware delivery!**

---

### Systemd Services ✅

**Pi #7 Services:**
- ✅ `balloon-control-api.service` - **RUNNING** on http://192.168.50.100:5000
- ⏸️ `balloon-sensor-publisher.service` - Ready to enable after sensor upgrade

**Pi #6 Services:**
- ⏸️ `balloon-control-secure.service` - Ready to enable after sensor upgrade

**All services configured for auto-start on boot!**

---

### Network Configuration ✅

**Pi #7 (Vulnerable System):**
- **Connection:** USB WiFi Adapter (Panda PAU0A, MediaTek chipset)
- **Interface:** wlan1
- **IP Address:** 192.168.50.100/24 (static)
- **SSID:** Medical-IoT (WPA2, VLAN2)
- **VLAN:** VLAN2 (192.168.50.0/24)
- **Gateway:** 192.168.50.1
- **Status:** ✅ ONLINE, stable, accessible from VLAN30

**Pi #6 (Secure System):**
- **Connection:** Wired Ethernet
- **IP Address:** 10.30.0.25/24 (static)
- **VLAN:** VLAN30 (10.30.0.0/24)
- **Gateway:** 10.30.0.1
- **Status:** ✅ ONLINE, stable

---

### Firewall Rules ✅ TESTED AND WORKING

**UDM-SE Configuration:**
1. **ALLOW_VLAN30_TO_VLAN2** - Admin access from secure network to vulnerable demo
   - ✅ Laptop (10.30.0.122) CAN ping/SSH Pi #7 (192.168.50.100)
2. **BLOCK_VLAN2_TO_GATEWAY** - Prevent compromised Pi from accessing router
   - ✅ Pi #7 CANNOT ping 10.30.0.1 (gateway)
3. **BLOCK_VLAN2_TO_VLAN30** - Prevent lateral movement from vulnerable network
   - ✅ Pi #7 CANNOT ping any 10.30.0.x devices
   - ✅ Pi #7 CAN access internet (8.8.8.8)

---

## 🔧 TROUBLESHOOTING SOLVED (2026-03-04)

### Issue 1: Pump Running During Standardization ✅ FIXED
**Symptom:** Pump turned on immediately when test started, ran during venting
**Root Cause:** Variable shadowing - `main()` created local copies of global state variables
**Fix:** Added `global pump_running, inflate_open, vent_open, relief_open` declaration in `main()`

### Issue 2: Confusing Code with `dry_run` Parameter ✅ FIXED
**Symptom:** Code hard to understand with `set_relay(RELAY_PUMP, False, dry_run)` pattern everywhere
**Root Cause:** Over-abstracted relay control functions
**Fix:** Complete refactor to simple explicit functions:
- `pump_on()` / `pump_off()`
- `open_inflate()` / `close_inflate()`
- `open_vent()` / `close_vent()`
- `open_relief()` / `close_relief()`
- `kill_all()` - Emergency stop everything
**Result:** Code is now crystal clear and self-documenting

### Issue 3: I2C Sensor Read Errors ✅ FIXED
**Symptom:** `[Errno 121] Remote I/O error` when reading ADS1115
**Root Cause:** Default I2C bus speed (100 kHz) too fast for long wiring runs
**Fix:** Slowed I2C to 10 kHz via `/boot/config.txt`:
```bash
dtparam=i2c_arm_baudrate=10000
```
**Result:** Sensors read reliably with zero errors

### Issue 4: 30 PSI Sensor Saturation ✅ IDENTIFIED
**Symptom:** Sensor maxed at 26.9 PSI, couldn't test higher
**Root Cause:** DATAQ sensors output 0.5-4.5V linearly - at max voltage (4.5V), sensor saturates
**Solution:** Ordered 4× DATAQ 100 PSI sensors for extended range

---

## ⏳ PENDING / NEXT STEPS

### Hardware
- ⏳ **CRITICAL:** Wait for 4× DATAQ 100 PSI sensors to arrive
- ⏳ Swap all 4 sensors (unplug old 15/30 PSI, plug in new 100 PSI - same connectors)
- ⏳ Verify I2C detection: `i2cdetect -y 1` (expect 0x27, 0x48, 0x60)
- ⏳ Re-run burst test to 70 PSI ceiling to find true burst pressure
- ⏳ Pi #6 hardware assembly (relay HATs + sensors + pneumatics)

### Software
- ✅ Scripts already updated for 100 PSI sensors - no code changes needed
- ⏳ SCP updated scripts to both Pis after sensor swap
- ⏳ Enable `balloon-sensor-publisher.service` on Pi #7
- ⏳ Enable `balloon-control-secure.service` on Pi #6

### Testing
- ⏳ Full burst characterization test (5-70 PSI, 1 PSI steps, 7s hold)
- ⏳ Attack demo test (spoof sensors on Pi #7 vulnerable system)
- ⏳ Secure system validation (anomaly detection on Pi #6)
- ⏳ Full expo demo dry run

---

## 📊 KEY METRICS

**Burst Test Performance (2026-03-04):**
- Start Pressure: 5.0 PSI
- Step Size: 1.0 PSI
- Hold Time: 7 seconds per step
- Test Ceiling: 26 PSI (sensor limitation)
- Pump Pulse Duration: 0.1 seconds
- Venting Time: ~5 seconds to reach <0.5 PSI
- Total Test Duration: ~5 minutes (5-26 PSI = 21 steps × ~14s/step)

**System Specifications:**
- Pump: 23A @ 12V (276W)
- Solenoids: ~0.5A each @ 12V (~6W each)
- Total Power: ~294W max
- Pressure Sensors: 0.5-4.5V linear output (5V supply)
- Control Loop: 10 Hz (0.1s cycle)

---

## 📝 DOCUMENTATION UPDATED

- ✅ `CLAUDE.md` - Updated hardware status, troubleshooting, pending work
- ✅ `test_burst_pressure.py` - Complete refactor, updated for 100 PSI sensors
- ✅ `sensor_publisher.py` - Updated for 100 PSI sensors
- ✅ This status document created

---

**Next Session:**
1. Receive 100 PSI sensors
2. Swap sensor hardware (4 sensors total)
3. Deploy updated scripts
4. Run burst test to 70 PSI
5. Set final safety thresholds based on burst pressure
6. Begin full attack demo testing
