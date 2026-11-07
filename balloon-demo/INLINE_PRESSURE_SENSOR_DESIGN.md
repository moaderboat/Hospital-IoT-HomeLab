# Inline Pressure Sensor Design Documentation

**Date:** 2026-02-08
**Status:** Design finalized, hardware ordered, software updates pending

---

## Overview

This document describes the inline pressure sensor system that replaces the original pressure chamber design using BMP388 atmospheric sensors.

### Design Change Rationale

**Old Design (Abandoned):**
- BMP388 atmospheric pressure sensor (I²C)
- Sealed in mason jar "pressure chamber"
- Air pumped into chamber, sensor reads atmospheric pressure change
- Required: drilling holes, cable glands, bulkhead fittings, silicone sealing
- Concerns: Potential leaks, indirect measurement, complex assembly

**New Design (Active):**
- DATAQ 2000361-30H inline pressure transducer (analog)
- Screws directly into air line via NPT threaded fitting
- Reads pressure directly from pneumatic system
- Industrial-grade sensor designed for this exact application

**Advantages:**
- ✅ Simpler installation (screw in, plug in - no drilling/sealing)
- ✅ More reliable (industrial sensor vs DIY hack)
- ✅ Better accuracy (±0.5% vs ±1-2%)
- ✅ Faster response time (no dead volume in chamber)
- ✅ Professional appearance for expo
- ✅ Direct measurement (not indirect via atmospheric pressure)

---

## Hardware Components

### Primary Sensor: DATAQ 2000361-30H Pressure Transducer

**Specifications:**
- **Measurement Range:** 0-30 PSI
- **Output:** 0.5-4.5V analog voltage
  - 0.5V = 0 PSI
  - 4.5V = 30 PSI
  - Linear relationship: `PSI = (voltage - 0.5) / 4.0 * 30.0`
- **Connection:** 1/8" NPT (pipe thread)
- **Interface:** 6-pin Molex connector
- **Cable:** DATAQ 2006030 pigtail (10 ft, bare wire ends)
- **Accuracy:** ±0.5% full scale
- **Supply Voltage:** 8-30 VDC (excitation)
- **Response Time:** <1ms

**Pinout (6-pin Molex):**
1. +Excitation (red) - 8-30 VDC power supply
2. -Excitation (black) - Ground
3. +Signal (white) - 0.5-4.5V output
4. -Signal (green) - Signal ground
5. Shield (bare wire) - Optional EMI shield
6. Not used

**Quantity Needed:** 2 (one per balloon system)

**Purchase Link:** https://www.dataq.com/products/transducers/2000361-30h.html

---

### ADC: Adafruit ADS1115 16-Bit ADC

**Why Needed:**
Raspberry Pi GPIO pins can only read digital signals (0V or 3.3V). The DATAQ sensor outputs an analog voltage (0.5-4.5V). The ADS1115 converts this analog voltage to a digital value that the Pi can read via I²C.

**Specifications:**
- **Resolution:** 16-bit (65536 discrete values)
- **Interface:** I²C (SCL, SDA)
- **I²C Address:** 0x48 (default, configurable to 0x49, 0x4A, 0x4B)
- **Input Voltage Range:** ±6.144V (programmable gain)
- **Sample Rate:** Up to 860 samples/sec
- **Operating Voltage:** 2.0-5.5V
- **Logic Level:** 3.3V or 5V compatible

**Pin Connections:**
- VDD: 5V from Pi (Pin 2 or 4)
- GND: Ground from Pi (Pin 6, 9, 14, 20, 25, 30, 34, 39)
- SCL: I²C clock (Pi Pin 5 via level shifter)
- SDA: I²C data (Pi Pin 3 via level shifter)
- ADDR: Address select (connect to GND for 0x48)
- ALRT: Alert output (not used)
- A0: Analog input channel 0 (DATAQ +Signal white wire)
- A1-A3: Unused analog inputs
- GND: Analog ground (DATAQ -Signal green wire)

**Quantity Needed:** 2 (one per Pi)

**Purchase Link:** https://www.adafruit.com/product/1085

---

### Level Shifter: Adafruit BSS138 4-Channel Bidirectional

**Why Needed:**
- Raspberry Pi uses 3.3V logic levels
- ADS1115 can operate at 5V (more stable, better noise immunity)
- I²C communication requires matching voltage levels
- BSS138 safely converts between 3.3V (Pi side) and 5V (ADC side)

**Specifications:**
- **Channels:** 4 (we use 2: SCL and SDA)
- **Low Voltage Side:** 3.3V (Raspberry Pi)
- **High Voltage Side:** 5V (ADS1115 ADC)
- **Bidirectional:** Works for both read and write
- **I²C Safe:** Includes pull-up resistors

**Pin Connections:**

**Low Voltage Side (3.3V - Raspberry Pi):**
- LV: 3.3V from Pi (Pin 1)
- GND: Ground from Pi (Pin 6, 9, 14, 20, 25, 30, 34, 39)
- A1: Pi SCL (Pin 5, GPIO 3)
- A2: Pi SDA (Pin 3, GPIO 2)
- A3-A4: Unused

**High Voltage Side (5V - ADS1115):**
- HV: 5V from Pi (Pin 2 or 4)
- GND: Ground from Pi (shared with LV GND)
- B1: ADS1115 SCL
- B2: ADS1115 SDA
- B3-B4: Unused

**Quantity Needed:** 2 (one per Pi)
**Quantity Owned:** 3 (arrived 2026-02-08 - have spare!)

**Purchase Link:** https://www.adafruit.com/product/757

---

### NPT Adapter: 1/8"F × 1/4"M Brass Bushing

**Why Needed:**
- DATAQ sensor has 1/8" NPT male threads
- Existing pneumatic fittings may be 1/4" NPT
- Brass bushing adapts between the two sizes

**Specifications:**
- **Type:** Hex bushing
- **Material:** Brass
- **Female End:** 1/8" NPT (fits DATAQ sensor)
- **Male End:** 1/4" NPT (fits into tee junction)

**Quantity Needed:** 2 (one per sensor)

---

## Wiring Diagram

### Complete System Connection

```
DATAQ Sensor (1/8" NPT)
    |
    | (Pigtail cable - 6 wires)
    |
    v
[Power Supply]          [ADS1115 ADC]
  12V ---> Red (+Exc)     VDD <--- 5V (Pi Pin 2)
  GND ---> Black (-Exc)   GND <--- GND (Pi Pin 6)
                          A0 <---- White (+Signal from DATAQ)
                          GND <--- Green (-Signal from DATAQ)
                          SCL <--┐
                          SDA <--┤
                                 │
                        [BSS138 Level Shifter]
                          HV <---- 5V (Pi Pin 2)
                          B1 (SCL) ---> ADS1115 SCL
                          B2 (SDA) ---> ADS1115 SDA
                          GND <---- GND (Pi Pin 6)
                          LV <----- 3.3V (Pi Pin 1)
                          A1 (SCL) <--- Pi Pin 5 (GPIO 3 - SCL)
                          A2 (SDA) <--- Pi Pin 3 (GPIO 2 - SDA)
                          GND <---- GND (Pi Pin 6)

Raspberry Pi GPIO Pins:
  Pin 1: 3.3V ---> BSS138 LV
  Pin 2: 5V -----> ADS1115 VDD, BSS138 HV
  Pin 3: SDA ----> BSS138 A2
  Pin 5: SCL ----> BSS138 A1
  Pin 6: GND ----> ADS1115 GND, BSS138 GND (all grounds), 12V PSU GND
```

### DATAQ Pigtail Wire Colors

| Pin | Wire Color | Function           | Connects To              |
|-----|------------|--------------------|--------------------------|
| 1   | Red        | +Excitation        | 12V power supply (+)     |
| 2   | Black      | -Excitation        | 12V power supply (-)     |
| 3   | White      | +Signal (output)   | ADS1115 A0               |
| 4   | Green      | -Signal (ground)   | ADS1115 GND              |
| 5   | Bare wire  | Shield (optional)  | Leave unconnected or GND |
| 6   | None       | Not used           | Not connected            |

---

## Physical Installation

### Pneumatic System Integration

**Air Flow Path:**
```
Air Pump
   |
   ├─ Relay 1 (pump power control)
   |
   v
[DATAQ Pressure Sensor] <--- Inline in air line
   |
   v
Solenoid Valve
   |
   ├─ Relay 2 (valve control)
   |
   v
Balloon
```

**Mounting:**
1. Install 1/8"F × 1/4"M brass bushing into NPT tee junction
2. Thread DATAQ sensor into bushing (hand-tight + 1/4 turn with wrench)
3. Connect pigtail cable to sensor's Molex connector
4. Mount ADS1115 and BSS138 on breadboard or custom PCB near Raspberry Pi
5. Route sensor cable to ADC (10 ft length allows flexibility)

**Pneumatic Assembly (Professional Installation):**

**Hardware:** ✅ 90-degree brass elbows (6×), hose clamps (multiple) - arrived 2026-02-08

**Air Line Routing:**
1. Use 90-degree brass elbows for clean corners (prevents kinking, improves flow)
2. Typical routing:
   ```
   Air Pump → Elbow → Horizontal run → Elbow → DATAQ Sensor (via NPT tee) →
   Elbow → Vertical drop → Solenoid Valve → Elbow → Balloon
   ```
3. Secure all connections with appropriately-sized hose clamps
4. Tighten clamps firmly but not excessively (avoid crushing hose)

**Hose Clamp Best Practices:**
- Use two clamps per critical connection (pump, valve, sensor tee)
- Position clamps 1/4" from barb end
- Ensure hose is fully seated on barb before clamping
- Test for leaks: pump air, spray soapy water on connections, look for bubbles

**Benefits of Brass Elbows:**
- Professional appearance for expo demonstrations
- Reduced air flow turbulence (better than kinked hoses)
- Easier to route hoses in tight spaces
- Prevents hose fatigue from sharp bends

**Pressure Test Point:**
Ideally install sensor AFTER the pump but BEFORE the solenoid valve. This allows:
- Monitoring pressure even when valve is closed
- Detecting pump operation
- Measuring system pressure without balloon interference

---

## Power Supply Requirements

### DATAQ Sensor Excitation

**Required:** 8-30 VDC, ~10mA

**Options:**
1. **12V Wall Adapter** (recommended for bench testing)
   - Separate 12V power supply
   - Shared ground with Raspberry Pi
   - Cleanest power, no Pi load

2. **12V from Relay HAT or External Source**
   - Sequent 8-RELAYS HAT may provide 12V terminal
   - Check HAT documentation

3. **Voltage Regulator from Pi 5V**
   - Boost 5V to 12V using DC-DC converter (e.g., Pololu U3V12F12)
   - Not ideal - adds complexity and noise

**Recommendation:** Use dedicated 12V wall adapter for each DATAQ sensor (clean, simple, reliable)

---

## Software Implementation

### Python Library: Adafruit CircuitPython ADS1x15

**Installation:**
```bash
sudo pip3 install adafruit-circuitpython-ads1x15
```

### Sample Code: Reading Pressure

```python
#!/usr/bin/env python3
"""
Test script for DATAQ inline pressure sensor via ADS1115 ADC
"""

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create ADS1115 object (I2C address 0x48)
ads = ADS.ADS1115(i2c)

# Create analog input on channel 0 (A0)
chan = AnalogIn(ads, ADS.P0)

# Conversion constants for DATAQ 2000361-30H
VOLTAGE_MIN = 0.5  # 0 PSI
VOLTAGE_MAX = 4.5  # 30 PSI
PRESSURE_MAX = 30.0  # PSI

def voltage_to_psi(voltage):
    """Convert DATAQ sensor voltage to PSI"""
    if voltage < VOLTAGE_MIN:
        return 0.0  # Below minimum = no pressure
    if voltage > VOLTAGE_MAX:
        return PRESSURE_MAX  # Above maximum = saturated

    # Linear conversion: PSI = (V - 0.5) / 4.0 * 30.0
    psi = (voltage - VOLTAGE_MIN) / (VOLTAGE_MAX - VOLTAGE_MIN) * PRESSURE_MAX
    return psi

try:
    print("DATAQ Pressure Sensor Test")
    print("Press Ctrl+C to exit\n")

    while True:
        # Read voltage from ADC
        voltage = chan.voltage

        # Convert to PSI
        pressure = voltage_to_psi(voltage)

        # Display
        print(f"Voltage: {voltage:.3f}V  |  Pressure: {pressure:.2f} PSI")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nExiting...")
```

### Integration into Existing Scripts

**Files to Update:**
1. `sensor_publisher.py` (Pi #7) - Replace BMP388 code with ADS1115 code
2. `balloon_control_secure.py` (Pi #6) - Replace BMP388 code with ADS1115 code
3. Create new `test_pressure_sensor.py` (both Pis)

**Code Changes:**

**OLD (BMP388):**
```python
import board
import adafruit_bmp3xx

i2c = board.I2C()
sensor = adafruit_bmp3xx.BMP3XX_I2C(i2c)

pressure = sensor.pressure  # Returns pressure in hPa
```

**NEW (ADS1115 + DATAQ):**
```python
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0)

voltage = chan.voltage
pressure_psi = (voltage - 0.5) / 4.0 * 30.0 if voltage >= 0.5 else 0.0
```

**Conversion:**
- BMP388 returned pressure in hectopascals (hPa)
- DATAQ returns PSI
- If existing code expects hPa: `pressure_hpa = pressure_psi * 68.9476`
- Recommend switching entire codebase to PSI (more intuitive for balloons)

---

## Calibration & Testing

### Initial Testing (When Hardware Arrives)

**1. Verify I²C Detection:**
```bash
i2cdetect -y 1
```
Should show:
- `0x48` - ADS1115 ADC
- `0x20` - Sequent 8-RELAYS HAT (when installed)

**2. Test Sensor with No Pressure:**
```bash
python3 test_pressure_sensor.py
```
Expected output:
```
Voltage: 0.500V  |  Pressure: 0.00 PSI
```

**3. Test Sensor with Air Pressure:**
- Connect sensor to air pump
- Run pump briefly
- Observe voltage rise from 0.5V toward 4.5V
- Observe pressure rise from 0 PSI toward 30 PSI

**4. Calibration (Optional):**
If you have a known-good pressure gauge:
1. Connect DATAQ sensor and reference gauge to same air source
2. Record DATAQ voltage at 0, 5, 10, 15, 20, 25, 30 PSI
3. Verify linear relationship
4. Adjust conversion formula if needed (should be within ±0.5%)

### Safety Limits

**Balloon Over-Pressure Protection:**
- Set software limit at 2-3 PSI for balloons
- DATAQ sensor rated to 30 PSI (10× safety margin)
- Emergency shutoff if pressure exceeds safe threshold

**Example in Code:**
```python
MAX_SAFE_PRESSURE = 3.0  # PSI
EMERGENCY_PRESSURE = 5.0  # PSI

if pressure > EMERGENCY_PRESSURE:
    # EMERGENCY: Shut off pump, open valve, sound alarm
    print("EMERGENCY: Over-pressure detected!")
    relay.set(PUMP_RELAY, False)  # Pump OFF
    relay.set(VALVE_RELAY, True)   # Valve OPEN (release)
    buzzer.on()
elif pressure > MAX_SAFE_PRESSURE:
    # Warning: Stop pumping, maintain current pressure
    relay.set(PUMP_RELAY, False)  # Pump OFF
    print("WARNING: Maximum safe pressure reached")
```

---

## Troubleshooting

### ADC Not Detected (No 0x48 in i2cdetect)

**Check:**
1. I²C enabled: `sudo raspi-config` → Interface Options → I2C → Enable
2. Wiring connections (SDA, SCL, GND, VDD)
3. Level shifter orientation (LV to Pi, HV to ADC)
4. ADDR pin on ADC (should be connected to GND for 0x48)

**Test:**
```bash
sudo i2cdetect -y 1
```

### Reading 0.0V or 5.0V Constantly

**Cause:** DATAQ sensor not powered or not connected

**Check:**
1. Red wire (+Excitation) connected to 12V
2. Black wire (-Excitation) connected to GND
3. Molex connector fully seated
4. 12V power supply turned on
5. Multimeter test: Measure voltage between red and black wires (should be 8-30V)

### Reading Fluctuating/Noisy Values

**Cause:** Electrical noise, poor grounding, or loose connections

**Solutions:**
1. Ensure all grounds connected (Pi, ADC, 12V PSU)
2. Twist signal wires together (white + green)
3. Connect shield wire (bare) to GND
4. Keep sensor cable away from power lines and motors
5. Add 0.1µF capacitor between +Signal and -Signal at ADC input
6. Enable ADC averaging in software:
   ```python
   # Average 10 readings
   readings = [chan.voltage for _ in range(10)]
   voltage = sum(readings) / len(readings)
   ```

### Pressure Reading Doesn't Change

**Cause:** Wrong ADC channel or air leak

**Check:**
1. White wire (+Signal) connected to A0 (not A1, A2, or A3)
2. Code specifies `ADS.P0` (not P1, P2, P3)
3. NPT fittings tight (no air leaks)
4. Pump actually running (check relay operation)
5. Valve closed when inflating

---

## Parts List Summary

| Item | Qty | Status | Purpose |
|------|-----|--------|---------|
| DATAQ 2000361-30H (0-30 PSI) | 2 | Ordered | Pressure transducer |
| DATAQ 2006030 Pigtail Cable | 2 | Ordered | Sensor wiring |
| Adafruit ADS1115 16-Bit ADC | 2 | Ordered | Analog-to-digital converter |
| Adafruit BSS138 Level Shifter | 2 | ✅ Arrived | 3.3V ↔ 5V I²C translation |
| 1/8"F × 1/4"M NPT Brass Bushing | 2 | Ordered | Fitting adapter |
| 90-degree Brass Elbows | 6 | ✅ Arrived | Clean air line routing |
| Hose Clamps (proper sizes) | Multiple | ✅ Arrived | Secure hose connections |
| 12V DC Power Supply | 2 | TBD | DATAQ excitation voltage |

**Total Cost (Pressure Sensors - Ordered 2026-02-08):** $210.70
**Total Cost (Pneumatic Hardware - Arrived 2026-02-08):** Additional components

---

## Timeline

**2026-02-08:**
- ✅ Design finalized
- ✅ Hardware ordered (DATAQ sensors + ADC)
- ✅ Level shifters arrived (3×)
- ✅ 90-degree brass elbows arrived (6×) - ready for pneumatic assembly
- ✅ Hose clamps arrived (multiple) - ready for pneumatic assembly
- ✅ 50cm GPIO extension cables arrived - for flexible component placement
- ✅ Mini-to-Micro HDMI cables arrived (2×) - for Pi displays if needed
- ✅ Sheathed 4-wire GPIO cables arrived (2×) - spare/future use
- ⏳ Python code updates pending (can write now, test when sensors arrive)

**Can Do Now (While Waiting for DATAQ Sensors):**
- [ ] Plan pneumatic system layout with brass elbows
- [ ] Pre-route air hoses with clean 90-degree turns
- [ ] Prepare hose clamp positions
- [ ] Update Python scripts for ADS1115 (ready to test when sensors arrive)

**When DATAQ Sensors + ADC Arrive:**
- [ ] Unbox and verify all components
- [ ] Wire ADS1115 + BSS138 + DATAQ sensor
- [ ] Install sensors into pneumatic system with brass elbows
- [ ] Secure all connections with hose clamps
- [ ] Test sensor readings (0 PSI baseline)
- [ ] Test with pneumatic system (pump air, read pressure)
- [ ] Check for air leaks (soapy water test)
- [ ] Calibrate if needed
- [ ] Install in both balloon systems

**Estimated Time to Install & Test:** 2-3 hours per system (pneumatic assembly + electrical wiring + software testing)

---

## References

**DATAQ 2000361-30H Datasheet:**
https://www.dataq.com/resources/pdfs/transducers/2000361-30h.pdf

**ADS1115 Datasheet:**
https://cdn-learn.adafruit.com/downloads/pdf/adafruit-4-channel-adc-breakouts.pdf

**BSS138 Level Shifter Guide:**
https://learn.adafruit.com/adafruit-4-channel-i2c-safe-bi-directional-logic-level-converter

**Adafruit ADS1x15 Python Library:**
https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15

---

**Document Created:** 2026-02-08
**Author:** Balloon Demo Team
**Status:** Ready for Implementation
