# Balloon Demo - Indicator LED and Buzzer Wiring

**Last Updated:** 2026-03-07
**Purpose:** GPIO wiring for visual/audio pressure indicators on Pi #7 (vulnerable system)

---

## Components Needed

- **1× Yellow/Orange LED** (5mm, 20mA)
- **1× Red LED** (5mm, 20mA)
- **1× Active Buzzer** (3-5V, piezo or magnetic)
- **2× 220Ω Resistors** (for LEDs)
- **Jumper wires** (male-to-female or male-to-male depending on connections)
- **Breadboard** (optional, for prototyping)

---

## GPIO Pin Assignments (Pi #7)

| Component | GPIO Pin (BCM) | Physical Pin | Description |
|-----------|----------------|--------------|-------------|
| Warning LED (Yellow/Orange) | GPIO 17 | Pin 11 | Activates at 30 PSI (WARNING_PRESSURE) |
| Danger LED (Red) | GPIO 27 | Pin 13 | Activates at 35 PSI (MAX_SAFE_PRESSURE) |
| Buzzer | GPIO 22 | Pin 15 | Activates at 35 PSI (MAX_SAFE_PRESSURE) |
| Ground | GND | Pin 6, 9, 14, 20, 25, 30, 34, or 39 | Common ground |

---

## Wiring Diagram

```
Raspberry Pi 5 (Pi #7)
┌─────────────────────────────┐
│ Pin 11 (GPIO17) ─────┐      │
│ Pin 13 (GPIO27) ───┐ │      │
│ Pin 15 (GPIO22) ─┐ │ │      │
│ Pin 14 (GND) ──┐ │ │ │      │
└────────────────┼─┼─┼─┼──────┘
                 │ │ │ │
                 │ │ │ └─────► Yellow LED (+) → 220Ω resistor → LED (-) → GND
                 │ │ └───────► Red LED (+) → 220Ω resistor → LED (-) → GND
                 │ └─────────► Buzzer (+) → Buzzer (-) → GND
                 └───────────► Common Ground Rail
```

---

## Step-by-Step Wiring

### Warning LED (Yellow/Orange)
1. Connect **GPIO 17 (Pin 11)** to the **anode (+, longer leg)** of the yellow LED
2. Connect the yellow LED **anode (+)** to a **220Ω resistor**
3. Connect the other end of the resistor to the **cathode (-, shorter leg)** of the LED
4. Connect the LED **cathode (-)** to **GND (Pin 14)**

### Danger LED (Red)
1. Connect **GPIO 27 (Pin 13)** to the **anode (+, longer leg)** of the red LED
2. Connect the red LED **anode (+)** to a **220Ω resistor**
3. Connect the other end of the resistor to the **cathode (-, shorter leg)** of the LED
4. Connect the LED **cathode (-)** to **GND (Pin 14)**

### Buzzer (Active Buzzer)
1. Identify buzzer polarity:
   - **Positive (+)**: Usually marked with a "+" symbol or red wire
   - **Negative (-)**: Usually marked with a "-" symbol or black wire
2. Connect **GPIO 22 (Pin 15)** to **Buzzer (+)**
3. Connect **Buzzer (-)** to **GND (Pin 14)**

**Note:** If using a **passive buzzer**, the wiring is the same, but it will produce a constant tone (no PWM implemented).

---

## Raspberry Pi 5 Pinout Reference

```
         3V3  (1) (2)  5V
   I2C1 SDA  (3) (4)  5V
   I2C1 SCL  (5) (6)  GND
      GPIO4  (7) (8)  GPIO14
        GND  (9) (10) GPIO15
  →  GPIO17 (11) (12) GPIO18
  →  GPIO27 (13) (14) GND   ← Ground for all indicators
  →  GPIO22 (15) (16) GPIO23
         3V3 (17) (18) GPIO24
     GPIO10 (19) (20) GND
      GPIO9 (21) (22) GPIO25
     GPIO11 (23) (24) GPIO8
        GND (25) (26) GPIO7
     GPIO0  (27) (28) GPIO1
      GPIO5 (29) (30) GND
      GPIO6 (31) (32) GPIO12
     GPIO13 (33) (34) GND
     GPIO19 (35) (36) GPIO16
     GPIO26 (37) (38) GPIO20
        GND (39) (40) GPIO21

→ = Used for indicators
I2C pins (3,5) reserved for ADS1115 sensor
```

---

## Behavior

### Normal Operation (< 30 PSI)
- **Yellow LED**: OFF
- **Red LED**: OFF
- **Buzzer**: OFF

### Warning Zone (30-34 PSI)
- **Yellow LED**: ON (solid)
- **Red LED**: OFF
- **Buzzer**: OFF

### Danger Zone (≥ 35 PSI)
- **Yellow LED**: ON
- **Red LED**: ON (solid)
- **Buzzer**: ON (continuous tone)

---

## Testing the Indicators

### Before wiring to Pi:

**Test LEDs with 3.3V:**
```bash
# SSH to Pi #7
ssh username@192.168.50.100

# Test yellow LED
gpio -g mode 17 out
gpio -g write 17 1  # LED should turn ON
gpio -g write 17 0  # LED should turn OFF

# Test red LED
gpio -g mode 27 out
gpio -g write 27 1  # LED should turn ON
gpio -g write 27 0  # LED should turn OFF

# Test buzzer
gpio -g mode 22 out
gpio -g write 22 1  # Buzzer should sound
gpio -g write 22 0  # Buzzer should stop
```

### After deploying updated script:

```bash
# Deploy updated script
scp balloon_control_api_vulnerable.py username@192.168.50.100:~/balloon-demo/scripts/

# Restart service
sudo systemctl restart balloon-control-api.service

# Watch logs to verify GPIO initialization
sudo journalctl -u balloon-control-api.service -f
```

You should see:
```
✓ GPIO initialized - Warning LED (GPIO17), Danger LED (GPIO27), Buzzer (GPIO22)
```

---

## Troubleshooting

**LEDs don't light up:**
- Check polarity (long leg = +, short leg = -)
- Verify resistor is 220Ω (not 220kΩ)
- Test with multimeter: GPIO pin should read 3.3V when HIGH

**Buzzer doesn't sound:**
- Verify it's an **active buzzer** (has internal oscillator)
- Check polarity (+ to GPIO, - to GND)
- Test with 3.3V directly from Pin 1 (3V3) to buzzer

**GPIO errors in logs:**
- Check for GPIO conflicts with relay HATs
- Verify pins 11, 13, 15 are not used by HAT stacking

**Indicators stuck ON:**
- Script may have crashed without cleanup
- Manually reset: `gpio -g write 17 0 && gpio -g write 27 0 && gpio -g write 22 0`

---

## Integration with Demo

During expo demo:

1. **Baseline (0-25 PSI)**: System inflates to target, all indicators OFF
2. **Attack starts**: Pressure begins climbing past 25 PSI
3. **30 PSI reached**: Yellow LED turns ON (visible warning)
4. **35 PSI reached**: Red LED + Buzzer activate (audible + visual alarm)
5. **Continued climb**: Indicators stay ON until burst (39-71 PSI)

This provides dramatic visual/audio feedback as the attack progresses!

---

**See also:**
- `balloon_control_api_vulnerable.py` - Updated script with GPIO control
- `CURRENT_STATUS_2026-03-04.md` - Hardware assembly status
- `WIRING_DIAGRAM_VULNERABLE.md` - Complete pneumatic system wiring
