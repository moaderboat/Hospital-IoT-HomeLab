# Balloon Demo - Pneumatic System Assembly Guide

**Last Updated:** 2026-02-09

---

## System Overview

Two identical pneumatic systems (one per Pi) with inflate/vent control and inline pressure sensing.

---

## Components Per System (x2 Total)

### Valves & Sensors
- 1× Air pump (12V DC)
- 1× US Solid USS-NSV00001 inflate valve (1/4" NPT, 12V DC, Normally Closed)
- 1× US Solid USS-NSV00001 vent valve (1/4" NPT, 12V DC, Normally Closed)
- 1× DATAQ 2000361-30H inline pressure sensor (1/8" NPT male, 0-30 PSI, 0.5-4.5V)

### Fittings
- 1× Main T-fitting (1/4" NPT female, 3 ports)
- 1× Sensor T-fitting (1/4" NPT female, 3 ports)
- 1× Reducer bushing (1/4" NPT female → 1/8" NPT female)
- 4-5× 1/4" NPT close nipples or hose barbs (for hose connections)
- 1/4" pneumatic hose (cut to length)
- Hose clamps (for barb connections)

### Electronics
- 1× Sequent 8-RELAYS HAT (shared between both systems)
- 1× ADS1115 16-bit ADC (I²C, for reading DATAQ sensor)
- 1× BSS138 level shifter (3.3V ↔ 5V for ADC)

### Balloon
- 1× Latex balloon (appropriate size for demo)

---

## Pneumatic Flow Diagram

```
                    ┌─────────────┐
                    │  Air Pump   │
                    │ (Relay 1/4) │
                    └──────┬──────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Inflate Valve  │
                  │ USS-NSV00001   │
                  │  (Relay 2/5)   │
                  └────────┬───────┘
                           │
                      [1/4" Hose]
                           │
                           ▼
                      ┌─────────┐
                      │T-Fitting│ (1/4" NPT all ports)
                      │ (Main)  │
                      └─┬────┬──┘
                        │    │
        ┌───────────────┘    └───────────────┐
        │                                    │
   [1/4" Hose]                          [1/4" Hose]
        │                                    │
        ▼                                    ▼
  ┌──────────────┐                    ┌─────────┐
  │  Vent Valve  │                    │T-Fitting│
  │ USS-NSV00001 │                    │(Sensor) │
  │  (Relay 3/6) │                    └─┬────┬──┘
  └──────┬───────┘                      │    │
         │                     [1/4" Hose]  [1/4" to 1/8"]
         ▼                               │       │
   [ Atmosphere ]                        │       └──────► [DATAQ Sensor]
                                         │                (1/8" NPT port)
                                         │                (0-30 PSI)
                                         ▼
                                    ┌─────────┐
                                    │ Balloon │
                                    └─────────┘
```

---

## Assembly Steps

### Step 1: Prepare T-Fittings

**Main T-Fitting:**
1. Apply thread tape to nipple/hose barb threads (2-3 wraps, clockwise)
2. Port 1: Install nipple for hose from inflate valve
3. Port 2: Install nipple for hose to vent valve
4. Port 3: Install nipple for hose to sensor T-fitting

**Sensor T-Fitting:**
1. Port 1: Install nipple for hose from main T-fitting
2. Port 2: Install nipple for hose to balloon
3. Port 3: Install reducer bushing (1/4" → 1/8")

### Step 2: Install DATAQ Sensor

1. Apply thread tape to DATAQ sensor threads (1/8" NPT male)
2. Thread sensor into reducer bushing on sensor T-fitting
3. Tighten snugly (don't over-torque - brass is soft)
4. Sensor should be mounted perpendicular to flow path

### Step 3: Connect Valves

**Inflate Valve (USS-NSV00001):**
1. Input port: Connect hose from air pump
2. Output port: Connect hose to main T-fitting port 1

**Vent Valve (USS-NSV00001):**
1. Input port: Connect hose from main T-fitting port 2
2. Output port: **Leave open to atmosphere** (no connection)

### Step 4: Connect Hoses

Using 1/4" pneumatic hose:
1. Pump → Inflate valve input
2. Inflate valve output → Main T port 1
3. Main T port 2 → Vent valve input
4. Main T port 3 → Sensor T port 1
5. Sensor T port 2 → Balloon

**Secure all hose connections with hose clamps**

### Step 5: Leak Test

1. Close vent valve (relay off)
2. Open inflate valve (relay on)
3. Run pump briefly to pressurize to ~5 PSI
4. Spray soapy water on all fittings
5. Look for bubbles (indicates leak)
6. Re-tighten or re-tape leaking fittings
7. Vent system before proceeding

---

## Relay Wiring (Sequent 8-RELAYS HAT)

### Pi #6 (Secure System - 10.30.0.25)

| Relay | Device | Voltage | Notes |
|-------|--------|---------|-------|
| 1 | Air Pump | 12V DC | Powers air pump |
| 2 | Inflate Valve | 12V DC | USS-NSV00001 (NC) |
| 3 | Vent Valve | 12V DC | USS-NSV00001 (NC) |
| 4-8 | Available | - | Future use (LEDs, buzzer, etc.) |

### Pi #7 (Vulnerable System - 192.168.50.100)

| Relay | Device | Voltage | Notes |
|-------|--------|---------|-------|
| 1-3 | Available | - | Reserved for Pi #6 |
| 4 | Air Pump | 12V DC | Powers air pump |
| 5 | Inflate Valve | 12V DC | USS-NSV00001 (NC) |
| 6 | Vent Valve | 12V DC | USS-NSV00001 (NC) |
| 7-8 | Available | - | Future use |

**Power Supply:** 12V DC power supply (adequate amperage for pump + 2 valves)

---

## ADS1115 ADC Wiring (for DATAQ Sensor)

### Connections (Both Pis)

**ADS1115 to Raspberry Pi:**
- VDD → 5V (Pin 2 or 4) via BSS138 level shifter
- GND → GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
- SCL → GPIO 3 (Pin 5) via BSS138 level shifter
- SDA → GPIO 2 (Pin 3) via BSS138 level shifter
- ADDR → GND (sets I²C address to 0x48)

**DATAQ Sensor to ADS1115:**
- Red wire (+12V excitation) → 12V power supply positive
- Black wire (GND) → 12V power supply ground (common with Pi ground)
- White wire (Signal+) → ADS1115 A0 (channel 0 input)
- Green wire (Signal-) → ADS1115 GND

**BSS138 Level Shifter:**
- LV (Low Voltage) side: 3.3V (Pi GPIO)
- HV (High Voltage) side: 5V (ADS1115)
- Converts I²C signals between 3.3V and 5V levels

---

## Operating Modes

### 1. Inflate Mode
- Relay 1/4 (Pump): **ON**
- Relay 2/5 (Inflate): **ON**
- Relay 3/6 (Vent): **OFF**
- Air flows: Pump → Inflate → Main T → Sensor T → Balloon

### 2. Hold Mode
- Relay 1/4 (Pump): **OFF**
- Relay 2/5 (Inflate): **OFF**
- Relay 3/6 (Vent): **OFF**
- Pressure trapped in system

### 3. Deflate Mode
- Relay 1/4 (Pump): **OFF**
- Relay 2/5 (Inflate): **OFF**
- Relay 3/6 (Vent): **ON**
- Air flows: Balloon → Sensor T → Main T → Vent → Atmosphere

### 4. Emergency Mode
- Relay 1/4 (Pump): **OFF**
- Relay 2/5 (Inflate): **OFF**
- Relay 3/6 (Vent): **ON** (rapid deflation)

---

## Safety Features

✅ **Normally Closed Valves:** Safe default - valves closed when unpowered
✅ **Mutual Exclusion:** Software prevents inflate + vent from opening simultaneously
✅ **Emergency Deflation:** Emergency stop opens vent valve automatically
✅ **Pressure Monitoring:** DATAQ sensor reads 0-30 PSI continuously
✅ **Overpressure Protection:** Software stops pump at MAX_SAFE_PRESSURE (3.5 PSI)
✅ **Stale Data Detection:** System stops if sensor data >5 seconds old

---

## Testing Procedure

### Phase 1: Electrical Testing (No Pressure)

1. Install relay HAT on Pi
2. Wire valves to relays (no air pump yet)
3. Run Python scripts in test mode
4. Verify relay clicks when valves commanded
5. Use multimeter to verify 12V across valve terminals when commanded

### Phase 2: Pneumatic Testing (Low Pressure)

1. Connect air pump to inflate valve
2. Attach balloon to sensor T-fitting
3. Run scripts with TARGET_PRESSURE = 1.0 PSI (very low)
4. Verify:
   - ✓ Pump starts when pressure < target
   - ✓ Pump stops when pressure ≥ target
   - ✓ Pressure sensor reads correctly
   - ✓ Vent valve deflates balloon
   - ✓ No leaks detected

### Phase 3: Full System Testing

1. Increase TARGET_PRESSURE to 2.5 PSI
2. Run full inflate/hold/deflate cycle
3. Test emergency stop (should vent immediately)
4. Verify Wazuh logging (Pi #6 only)
5. Verify Suricata IDS detection

### Phase 4: Attack Demo Testing

1. Run sensor_publisher.py on one Pi
2. Send spoofed pressure data via HTTP
3. Verify:
   - ✓ Vulnerable system (Pi #7) accepts spoofed data
   - ✓ Secure system (Pi #6) rejects spoofed data
   - ✓ Suricata logs attack traffic
   - ✓ Wazuh logs validation failures (Pi #6)

---

## Troubleshooting

### Pump Won't Start
- Check relay wiring (relay 1 or 4)
- Verify 12V power supply connected
- Check Python script RELAY_PUMP constant

### Pressure Not Reading
- Check ADS1115 I²C connection: `i2cdetect -y 1` (should show 0x48)
- Verify DATAQ sensor wiring (signal+ to A0, signal- to GND)
- Check 12V excitation voltage to DATAQ sensor
- Run test_pressure_sensor.py to diagnose

### Leaks Detected
- Re-tighten all NPT fittings
- Add more thread tape (2-3 wraps)
- Check hose clamps are tight
- Replace damaged hose

### Balloon Won't Deflate
- Check vent valve wiring (relay 3 or 6)
- Verify relay clicks when vent commanded
- Check vent valve output is open to atmosphere
- Manually test vent valve with 12V

### Valves Not Operating
- Verify USS-NSV00001 is 12V DC (not 24V or AC)
- Check polarity (solenoids are polarity-sensitive)
- Test with multimeter: should read ~100-150Ω coil resistance
- Verify relay HAT is powered

---

## Next Steps After Assembly

1. **Deploy Updated Scripts:**
   - Copy updated Python scripts to both Pis
   - Test in software mode first (RELAYS_AVAILABLE = False)
   - Enable hardware mode when ready

2. **Calibrate Sensors:**
   - Run test_pressure_sensor.py
   - Verify 0 PSI reads ~0.5V
   - Verify atmospheric pressure reads correctly
   - Document any offset/calibration needed

3. **Integration Testing:**
   - Test full inflate/deflate cycles
   - Verify all safety interlocks work
   - Test emergency stop scenarios
   - Document any issues

4. **Demo Preparation:**
   - Practice attack demonstration
   - Prepare expo talking points
   - Test LED indicators (when installed)
   - Create visual aids for audience

---

**Document Created:** 2026-02-09
**Hardware Status:**
- ✅ Inflate valves: On hand
- ⏳ Vent valves: Arriving tomorrow/Wednesday
- ✅ DATAQ sensors: Ordered, in transit
- ✅ Relay HAT: Ordered (ETA Feb 10-12)
- ⏳ T-fittings, reducer bushings: Need to order
- ✅ Python scripts: Updated with vent control logic

**Related Documents:**
- balloon-demo/scripts/balloon_control_secure.py - Secure system control
- balloon-demo/scripts/balloon_control_api.py - Vulnerable system API
- balloon-demo/scripts/test_pressure_sensor.py - Sensor diagnostic tool
