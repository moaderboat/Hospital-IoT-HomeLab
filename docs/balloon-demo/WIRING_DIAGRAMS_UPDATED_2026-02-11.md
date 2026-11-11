# Pi #7 Vulnerable System - Complete Wiring Diagrams
## UPDATED 2026-02-11 - DataQ Sensors + BSS138 Level Shifter

**System:** Pi #7 Vulnerable Balloon Demo (192.168.50.100, VLAN2)

---

## PNEUMATIC AIR FLOW DIAGRAM (ASCII)

```
Stage 0 → Stage 9: Descending Air Flow Order
═══════════════════════════════════════════════════════════════════

┌─────────────────┐
│  STAGE 0        │
│  Air Pump       │  12V DC, 160 LPM, Relay #1
│  HEALiNK 120W   │
└────────┬────────┘
         │ 12" tube
         ↓
┌────────────────────┐
│  STAGE 1           │
│  T-Joint #1        │  F×F×F
└────┬──────────┬────┘
     │          │
  MAIN FLOW     │ POST (tail)
     │          ↓
     │     ┌─────────────────┐
     │     │ ⚠ Ball Valve #1 │  EMERGENCY BLEED A
     │     └────────┬────────┘
     │              └─ to ATMOSPHERE
     ↓
┌────────────────────┐
│  STAGE 2           │
│  T-Joint #2        │  F×F×F
└────┬──────────┬────┘
     │          │ POST
     │          ↓
     │     ┌─────────────────┐
     │     │ DataQ Sensor #1 │  30 PSI (2000361-30H)
     │     │ HIGH RANGE      │  Signal → ADS1115 CH0
     │     └─────────────────┘
     ↓ 6" tube
┌────────────────────┐
│  STAGE 3           │
│  T-Joint #3        │  F×F×F
└────┬──────────┬────┘
     │          │ POST
     │          ↓
     │     ┌─────────────────┐
     │     │  Solenoid #3    │  12V NC, Relay #4
     │     │  HIGH-PRESSURE  │  Opens if 30 PSI > 25 PSI
     │     │  RELIEF         │
     │     └────────┬────────┘
     │              └─ to ATMOSPHERE
     ↓ 6" tube
┌─────────────────┐
│  STAGE 4        │
│  Solenoid #1    │  12V NC, Relay #2
│  MAIN INLET     │  PRIMARY PRESSURE CONTROL
└────────┬────────┘
         │ 6" tube
         ↓
┌────────────────────┐
│  STAGE 5           │
│  T-Joint #4        │  F×F×F
└────┬──────────┬────┘
     │          │ POST
     │          ↓
     │     ┌─────────────────┐
     │     │ ⚠ Ball Valve #2 │  EMERGENCY BLEED B
     │     └────────┬────────┘
     │              └─ to ATMOSPHERE
     ↓ 6" tube
┌────────────────────┐
│  STAGE 6           │
│  T-Joint #5        │  F×F×F
└────┬──────────┬────┘
     │          │ POST
     │          ↓
     │     ┌─────────────────┐
     │     │ DataQ Sensor #2 │  15 PSI (2000361-15H)
     │     │ LOW RANGE       │  Signal → ADS1115 CH1
     │     │ PRIMARY CONTROL │
     │     └─────────────────┘
     ↓ 6" tube
┌────────────────────┐
│  STAGE 7           │
│  T-Joint #6        │  F×F×F
└────┬──────────┬────┘
     │          │ POST
     │          ↓
     │     ┌─────────────────┐
     │     │  Solenoid #2    │  12V NC, Relay #3
     │     │  BALLOON        │  Opens if 15 PSI > 3.5 PSI
     │     │  DEFLATE        │
     │     └────────┬────────┘
     │              └─ to ATMOSPHERE
     ↓ 6" tube
┌────────────────────┐
│  STAGE 8           │
│  T-Joint #7        │  F×F×F
└────┬──────────┬────┘
     │          │ POST
     │          ↓
     │     ┌─────────────────┐
     │     │ Analog Gauge    │  0-15 PSI, Visual
     │     │ VISUAL CONFIRM  │
     │     └─────────────────┘
     ↓ 6" tube
┌─────────────────┐
│  STAGE 9        │
│  Quick-Connect  │  Brass barb + 6" silicone
│  + BALLOON      │  Secured with wide zip ties
└─────────────────┘
```

---

## ELECTRICAL WIRING DIAGRAM - COMPLETE SYSTEM

### Power Distribution Overview:

```
120VAC SECTION (⚡ DANGER):
═══════════════════════════════════
Wall Outlet (120VAC)
    │
    ├─→ 12V PSU Input (AC hot + neutral)
    │       ↓
    │   12V PSU Output (12V DC + GND)
    │       ↓
    │   Emergency Cutoff Switch (RED toggle)
    │       ↓
    │   Terminal Block Position 1 (12V+)
    │   Terminal Block Position 7 (GND)
    │
    └─→ Raspberry Pi USB-C Adapter (5V DC to Pi)
            ↓
        Raspberry Pi 5 (3.3V + 5V rails)


12V DC DISTRIBUTION (⚠️ CAUTION):
═══════════════════════════════════
Terminal Block Position 1 (12V+) distributes to:
    ├─→ Position 2: Relay #1 COM (Pump)
    ├─→ Position 3: Relay #2 COM (Sol #1)
    ├─→ Position 4: Relay #3 COM (Sol #2)
    ├─→ Position 5: Relay #4 COM (Sol #3)
    ├─→ 30 PSI Sensor RED wire (12V power)
    └─→ 15 PSI Sensor RED wire (12V power)

Terminal Block Position 7 (GND) distributes to:
    ├─→ Position 8: Pump GND
    ├─→ Position 9: Solenoid #1 GND
    ├─→ Position 10: Solenoid #2 GND
    ├─→ Position 11: Solenoid #3 GND
    ├─→ 30 PSI Sensor BLACK wire (GND)
    └─→ 15 PSI Sensor BLACK wire (GND)


RELAY SWITCHING (✅ SAFE - Pi controls via I2C):
═══════════════════════════════════
Relay #1: Pump Control
    COM ← 12V+ (Position 2)
    NO → Pump + (RED wire)
    Pump - → GND (Position 8)

Relay #2: Solenoid #1 (Main Inlet)
    COM ← 12V+ (Position 3)
    NO → Sol #1 + (RED wire)
    Sol #1 - → GND (Position 9)

Relay #3: Solenoid #2 (Balloon Deflate)
    COM ← 12V+ (Position 4)
    NO → Sol #2 + (RED wire)
    Sol #2 - → GND (Position 10)

Relay #4: Solenoid #3 (High-Pressure Relief)
    COM ← 12V+ (Position 5)
    NO → Sol #3 + (RED wire)
    Sol #3 - → GND (Position 11)
```

---

## SENSOR WIRING - DATAQ + ADS1115 + BSS138

### Critical Voltage Levels:

```
DataQ Sensors: 12V power, 0.5-4.5V analog output
ADS1115 ADC:   5V power (MUST be 5V to read 4.5V signal)
BSS138 Shifter: Translates 5V I2C ↔ 3.3V I2C
Raspberry Pi:  3.3V GPIO (NOT 5V tolerant)
```

### Wiring Connections:

```
DATAQ 30 PSI SENSOR (Stage 2):
═══════════════════════════════════
RED wire    → Terminal Block Position 2 (12V+)
BLACK wire  → Terminal Block Position 8 (GND)
YELLOW wire → ADS1115 A0 (analog input channel 0)


DATAQ 15 PSI SENSOR (Stage 6):
═══════════════════════════════════
RED wire    → Terminal Block Position 2 (12V+)
BLACK wire  → Terminal Block Position 8 (GND)
YELLOW wire → ADS1115 A1 (analog input channel 1)


ADS1115 ADC MODULE:
═══════════════════════════════════
Pin   Wire Color  Connects To
────  ──────────  ───────────────────────────────
VDD   ORANGE      Pi Pin 2 (5V) ⚠️ MUST BE 5V
GND   GREEN       Pi Pin 6 (GND)
SCL   WHITE       BSS138 B2 (HV2) ⚠️ NOT directly to Pi!
SDA   PURPLE      BSS138 B1 (HV1) ⚠️ NOT directly to Pi!
ADDR  GREEN       GND on board (sets I2C address to 0x48)
A0    YELLOW      30 PSI sensor signal
A1    YELLOW      15 PSI sensor signal
A2    -           Not used
A3    -           Not used


BSS138 LEVEL SHIFTER (CRITICAL FOR SAFETY):
═══════════════════════════════════
Pin   Wire Color  Connects To
────  ──────────  ───────────────────────────────
HV    ORANGE      Pi Pin 2 (5V reference)
B1    PURPLE      ADS1115 SDA (5V I2C data)
B2    WHITE       ADS1115 SCL (5V I2C clock)
LV    RED         Pi Pin 1 (3.3V reference)
A1    BLUE        Pi Pin 5 (GPIO3/SCL - 3.3V safe)
A2    YELLOW      Pi Pin 3 (GPIO2/SDA - 3.3V safe)
GND   GREEN       Pi Pin 6 (common ground)


OLED DISPLAY (Optional):
═══════════════════════════════════
VCC → Raspberry Pi Pin 1 (3.3V)
GND → Raspberry Pi Pin 6 (GND)
SCL → Raspberry Pi Pin 5 (GPIO3/SCL - shares with BSS138 A1)
SDA → Raspberry Pi Pin 3 (GPIO2/SDA - shares with BSS138 A2)
```

---

## RASPBERRY PI GPIO PINOUT REFERENCE

```
Pi 5 GPIO Header (40-pin):
═══════════════════════════════════

     3.3V [ 1] [ 2] 5V       ← BSS138 LV, OLED VCC | ADS1115 VDD, BSS138 HV
      SDA [ 3] [ 4] 5V       ← BSS138 LV2, OLED SDA
      SCL [ 5] [ 6] GND      ← BSS138 LV1, OLED SCL | Common ground
    GPIO4 [ 7] [ 8] GPIO14
      GND [ 9] [10] GPIO15
   GPIO17 [11] [12] GPIO18
   GPIO27 [13] [14] GND
   GPIO22 [15] [16] GPIO23
     3.3V [17] [18] GPIO24
   GPIO10 [19] [20] GND
    GPIO9 [21] [22] GPIO25
   GPIO11 [23] [24] GPIO8
      GND [25] [26] GPIO7
    GPIO0 [27] [28] GPIO1
    GPIO5 [29] [30] GND
    GPIO6 [31] [32] GPIO12
   GPIO13 [33] [34] GND
   GPIO19 [35] [36] GPIO16
   GPIO26 [37] [38] GPIO20
      GND [39] [40] GPIO21

Sequent 8-RELAYS HAT uses I2C (Pins 3+5) at address 0x20
```

---

## I2C DEVICE ADDRESSES

```
0x20: Sequent 8-RELAYS HAT (relay control)
0x3C: SSD1306 OLED Display (128x64, optional)
0x48: ADS1115 ADC (16-bit, 4-channel analog input)

All devices share same I2C bus (SCL/SDA on Pi Pins 5+3)
No address conflicts ✓
```

---

## SAFETY FEATURES (8 LAYERS)

```
Layer 1: Software Limit
    → 15 PSI sensor reads > 3.5 PSI
    → Python script stops pump (Relay #1 OFF)
    → Python script closes Sol #1 (Relay #2 OFF)

Layer 2: Software Alarm
    → 15 PSI sensor reads > 3.0 PSI
    → Python script triggers buzzer
    → OLED displays "WARNING: HIGH PRESSURE"

Layer 3: Emergency Bleed A (Manual)
    → Ball Valve #1 (Stage 1, upstream)
    → Operator twists handle 90° → instant vent to atmosphere

Layer 4: Emergency Bleed B (Manual)
    → Ball Valve #2 (Stage 5, downstream)
    → Operator twists handle 90° → instant vent to atmosphere

Layer 5: Automated Balloon Deflate
    → Solenoid #2 (Relay #3, Stage 7)
    → Opens if 15 PSI sensor > 3.5 PSI
    → Vents balloon pressure to atmosphere

Layer 6: Automated Upstream Relief
    → Solenoid #3 (Relay #4, Stage 3)
    → Opens if 30 PSI sensor > 25 PSI
    → Protects pump/fittings from overpressure

Layer 7: Emergency Cutoff Switch
    → RED illuminated toggle
    → Cuts ALL 12V power when flipped OFF
    → All solenoids close (NC design = fail-safe)

Layer 8: Visual Analog Gauge
    → Stage 8, always visible
    → Independent of software (mechanical)
    → Operator can see pressure even if Pi crashes
```

---

## WIRE COLOR CODING

```
POWER (12V DC):
    RED    = 12V+ (positive)
    BLACK  = GND (negative/ground)

SENSORS (DataQ pigtail):
    RED    = 12V+ power
    BLACK  = GND
    YELLOW = Analog signal (0.5-4.5V)

PCB JUMPER WIRES (ADS1115 + BSS138):
    ORANGE = 5V (VDD / HV reference)
    RED    = 3.3V (LV reference)
    GREEN  = GND
    WHITE  = SCL (clock)
    PURPLE = SDA (data)
    BLUE   = LV1 (3.3V SCL to Pi)
    YELLOW = LV2 (3.3V SDA to Pi) / analog sensor signals

RELAY LOADS:
    RED    = Positive to load
    BLACK  = Negative from load to GND
    BLUE   = Optional color for solenoid wiring
```

---

## TESTING VERIFICATION CHECKLIST

### Before Power-On:
- [ ] All 12V+ wires are RED
- [ ] All GND wires are BLACK
- [ ] No reversed polarity connections
- [ ] BSS138 wired correctly (ADS1115 SCL/SDA NOT directly to Pi)
- [ ] Emergency cutoff switch in OFF position
- [ ] All exposed wires covered with heat shrink or electrical tape
- [ ] No bare wires touching each other (shorts)
- [ ] Multimeter resistance test: 12V+ to GND = infinite resistance

### After Power-On (12V System):
- [ ] Flip emergency switch ON → Terminal block reads 11.5-12.5V DC
- [ ] No smoke, sparks, or burning smell
- [ ] PSU LED indicator lit (green)
- [ ] Emergency switch LED lit (if equipped)

### After Power-On (Raspberry Pi):
- [ ] Pi boots successfully (green LED flashing)
- [ ] HDMI shows boot screen
- [ ] Pi accessible via SSH

### I2C Device Detection:
```bash
i2cdetect -y 1
```
Expected output:
- [ ] 0x20 detected (Sequent HAT)
- [ ] 0x3C detected (OLED) - if connected
- [ ] 0x48 detected (ADS1115)

### Sensor Voltage Test:
```bash
python3 test_sensors.py
```
Expected readings at 0 PSI:
- [ ] 30 PSI sensor: ~0.5V (channel 0)
- [ ] 15 PSI sensor: ~0.5V (channel 1)

### Relay Click Test:
- [ ] Relay #1 clicks when commanded (pump)
- [ ] Relay #2 clicks when commanded (sol #1)
- [ ] Relay #3 clicks when commanded (sol #2)
- [ ] Relay #4 clicks when commanded (sol #3)

---

## SHOPPING LIST - STILL NEEDED

Based on updated design (7 tees, 3 solenoids, 2 ball valves per system):

**For ONE Complete System (Pi #7):**
- [ ] 1× Brass tee (need 7 total, have 6) - $8
- [ ] 2× Solenoid valves (need 3 total, have 4 for both systems) - NOT NEEDED
- [ ] 0× Ball valves (need 2 total, have 2) - $0
- [ ] 2× Brass barb fittings (need 20 total, have 34) - $0
- [ ] 1× Silicone tubing (6" for balloon) - $5

**Total to Order for Pi #7:** ~$13

**For BOTH Systems (Pi #6 + Pi #7):**
- [ ] 7× More brass tees (for Pi #6 second system) - $56
- [ ] 2× More solenoids (for Pi #6, need 6 total have 4) - $56
- [ ] 2× More ball valves (for Pi #6) - $16
- [ ] 10× More brass barbs (for Pi #6) - $25

**Total to Order for Both Systems:** ~$153

---

**Document Version:** 2.0 - Updated for DataQ Sensors + BSS138
**Created:** 2026-02-11
**Author:** Claude + David (Team 41)
**Status:** Ready for assembly after parts arrive
