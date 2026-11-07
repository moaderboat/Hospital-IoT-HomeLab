# LED Indicator System Design - Balloon Security Demo

**Last Updated:** 2026-02-10
**Status:** Design Complete - Ready for Assembly

---

## Overview

Visual indicator system using 8× 22mm panel-mount LEDs housed in junction boxes with silicone gaskets. Provides real-time status feedback for both secure and vulnerable balloon control systems during expo demonstration.

---

## Hardware Components

**LED Indicators:**
- 8× 22mm panel-mount LEDs with built-in resistors (12V DC)
- 4× Red LEDs (critical alerts)
- 4× Yellow/Amber LEDs (warnings)
- 4× Green LEDs (operational status)
- 4× Blue LEDs (inflation active)

**Housing:**
- Junction box with 12 pre-drilled holes for 22mm indicators
- Silicone gaskets matching LED profile (waterproof seal)
- Using 8 of 12 available mounting positions

**Control:**
- 2× Sequent Microsystems 8-RELAYS HAT (arrived 2026-02-10)
- 8 relay channels used (4 per Pi)
- 8 relay channels reserved for future expansion

---

## Physical Layout

### Junction Box Arrangement

**Traffic Light Section (Side/Back of Box):**
```
┌─────────────┐
│             │
│    [RED]    │  ← Critical Alert
│             │
│  [YELLOW]   │  ← Warning State
│             │
│   [GREEN]   │  ← System Healthy
│             │
└─────────────┘
```

**Activity Indicator (Front of Box):**
```
┌─────────────┐
│             │
│    [BLUE]   │  ← Inflation in Progress
│             │
└─────────────┘
```

**Rationale:**
- Traffic light metaphor (red/yellow/green) is universally recognized
- Vertical arrangement mirrors traditional traffic signals
- Blue isolated on front for high visibility during active inflation
- Clear separation: Status lights vs. Activity light

---

## LED State Logic

### Both Pis Use IDENTICAL Logic

```python
# Same control code runs on both Pi #6 (secure) and Pi #7 (vulnerable)

# Status LEDs (mutually exclusive - only one on at a time)
if pressure < 70%:
    green_led.on()      # System healthy - safe pressure
    yellow_led.off()
    red_led.off()

elif 70% <= pressure < 90%:
    green_led.off()
    yellow_led.on()     # Warning - approaching limit
    red_led.off()

else:  # pressure >= 90%
    green_led.off()
    yellow_led.off()
    red_led.on()        # CRITICAL - stop inflation immediately
    STOP_INFLATION()

# Activity LED (independent of status)
if inflating:
    blue_led.on()       # Pump running
else:
    blue_led.off()      # Pump idle
```

**Key Point:** Both systems run the EXACT SAME code. The difference is the data they receive.

---

## Attack Demonstration Behavior

### Secure Pi #6 (Shows REAL State)

**Normal Operation:**
1. Green ON → Blue ON (start inflation)
2. Yellow ON → Blue ON (pressure rising, still inflating)
3. Red ON → Blue OFF (STOP! pressure limit reached)
4. Balloon safely inflated, system stops

**LED Progression:**
```
Green → Yellow → Red → STOP
 ✓       ✓       ✓    (safe)
```

### Vulnerable Pi #7 (Shows SPOOFED State)

**Under Attack:**
1. Green ON → Blue ON (start inflation)
2. **Green STAYS ON** → Blue ON (attacker spoofs low pressure readings)
3. **Green STAYS ON** → Blue ON (balloon actually critical, but Pi doesn't know)
4. **Green STAYS ON** → Blue ON → 💥 BALLOON POPS

**LED State:**
```
Green → Green → Green → POP!
 ✓       ✓       ✓    (danger!)
```

**CRITICAL:** Vulnerable Pi #7 NEVER shows Yellow or Red LEDs, even during catastrophic failure. The Pi genuinely believes everything is safe because the attacker is feeding it false sensor data.

---

## Visual Impact for Expo

### Side-by-Side Comparison

**What Attendees Will See:**

**Secure System (Left Box):**
```
Time: 0s    10s    20s    30s
Red:   ○  →  ○  →  ○  →  ●  (STOP)
Yellow:○  →  ○  →  ●  →  ○
Green: ●  →  ●  →  ○  →  ○
Blue:  ●  →  ●  →  ●  →  ○
Result: ✓ Safe inflation, controlled stop
```

**Vulnerable System (Right Box):**
```
Time: 0s    10s    20s    30s    40s
Red:   ○  →  ○  →  ○  →  ○  →  ○
Yellow:○  →  ○  →  ○  →  ○  →  ○
Green: ●  →  ●  →  ●  →  ●  →  ● (FALSE!)
Blue:  ●  →  ●  →  ●  →  ●  →  ● (still going!)
Result: ✗ Balloon over-inflates and POPS
```

**The Contrast:**
- Left box: Green → Yellow → Red → SAFE
- Right box: Green → Green → Green → 💥 POP!

This visual tells the entire security story without words.

---

## Relay Channel Assignments

### Secure Pi #6 (Relay HAT #1)

| Relay | Function | LED Color | State Logic |
|-------|----------|-----------|-------------|
| 1 | Status: Healthy | Green | ON when pressure < 70% |
| 2 | Status: Warning | Yellow | ON when 70% ≤ pressure < 90% |
| 3 | Status: Critical | Red | ON when pressure ≥ 90% |
| 4 | Activity: Inflating | Blue | ON when pump running |
| 5-8 | Reserved | - | Future expansion |

### Vulnerable Pi #7 (Relay HAT #2)

| Relay | Function | LED Color | State Logic |
|-------|----------|-----------|-------------|
| 1 | Status: Healthy | Green | ON when (spoofed) pressure < 70% |
| 2 | Status: Warning | Yellow | NEVER USED (attack prevents) |
| 3 | Status: Critical | Red | NEVER USED (attack prevents) |
| 4 | Activity: Inflating | Blue | ON when pump running |
| 5-8 | Reserved | - | Future expansion |

**Note:** Vulnerable Pi relays for Yellow/Red are wired but never activated due to spoofed sensor data.

---

## Wiring Details

### Power Distribution

**12V DC Power Bus:**
- All 8 LEDs powered from same 12V supply
- Common positive (+12V) bus bar in junction box
- Individual relay-switched ground for each LED

**Wiring per LED:**
```
+12V ──────────────────┬──[LED]──┬
                       │         │
                       │         │
                    [Other LEDs] │
                                 │
                                 ↓
                            Relay NO ──→ GND
                            (Pi GPIO controlled)
```

### Relay Connections

**Each LED Circuit:**
- LED positive (+) → 12V bus (always powered)
- LED negative (-) → Relay Normally Open (NO) terminal
- Relay Common (COM) → Ground
- Relay coil → Pi GPIO via relay HAT

**When Relay Activates:**
- GPIO goes HIGH → Relay energizes → NO closes → LED cathode connected to ground → LED lights

---

## Physical Assembly Notes

### Junction Box Preparation

1. **Gasket Installation:**
   - Install 8 silicone gaskets in selected mounting holes
   - 3 gaskets in vertical line (side/back): Red, Yellow, Green
   - 1 gasket on front: Blue
   - Repeat for second set (8 total)

2. **LED Mounting:**
   - Insert LEDs through gaskets from outside
   - Tighten mounting nuts from inside box
   - Verify waterproof seal compression

3. **Internal Wiring:**
   - Run +12V bus wire to all LED positive terminals
   - Run individual wires from each LED negative to relay terminals
   - Label each wire with LED color and relay number
   - Secure wiring with zip ties to prevent movement

4. **Cable Management:**
   - Route relay control cables to Pi
   - Route 12V power cable to power supply
   - Use strain relief grommets for all entry points

---

## Testing Procedure

### Pre-Assembly Test (Bench)

1. **Individual LED Test:**
   ```bash
   # Test each LED with 12V power supply
   # Connect +12V to LED anode, GND to cathode
   # Verify: Bright, even illumination, no flickering
   ```

2. **Relay HAT Test:**
   ```python
   # Test each relay channel
   import lib8relind
   stack = 0  # HAT position (0 = first HAT)

   for relay in range(1, 9):
       lib8relind.set(stack, relay, 1)  # Turn on
       time.sleep(1)
       lib8relind.set(stack, relay, 0)  # Turn off
   ```

### Post-Assembly Test (Integrated)

1. **Power-On Test:**
   - Apply 12V power to bus
   - Verify no LEDs illuminated (all relays open)
   - Check for shorts or unexpected behavior

2. **Sequential Activation:**
   ```python
   # Cycle through each LED
   leds = ['green', 'yellow', 'red', 'blue']
   for led in leds:
       activate_led(led)
       input(f"{led.upper()} LED should be ON. Press Enter...")
       deactivate_led(led)
   ```

3. **State Machine Test:**
   ```python
   # Simulate pressure increase
   for pressure in range(0, 100, 10):
       update_status_leds(pressure)
       print(f"Pressure: {pressure}% - Check LED state")
       time.sleep(2)
   ```

4. **Traffic Light Sequence:**
   - Verify only ONE status LED on at a time (never multiple)
   - Verify smooth transitions: Green → Yellow → Red
   - Verify blue independent of status LEDs

---

## Integration with Control Scripts

### Code Structure

**File:** `~/balloon-demo/led_control.py`

```python
import lib8relind

class LEDController:
    def __init__(self, stack=0):
        self.stack = stack
        self.GREEN_RELAY = 1
        self.YELLOW_RELAY = 2
        self.RED_RELAY = 3
        self.BLUE_RELAY = 4

    def set_status(self, color):
        """Set status LED (green/yellow/red) - mutually exclusive"""
        # Turn off all status LEDs first
        lib8relind.set(self.stack, self.GREEN_RELAY, 0)
        lib8relind.set(self.stack, self.YELLOW_RELAY, 0)
        lib8relind.set(self.stack, self.RED_RELAY, 0)

        # Turn on requested LED
        if color == 'green':
            lib8relind.set(self.stack, self.GREEN_RELAY, 1)
        elif color == 'yellow':
            lib8relind.set(self.stack, self.YELLOW_RELAY, 1)
        elif color == 'red':
            lib8relind.set(self.stack, self.RED_RELAY, 1)

    def set_activity(self, inflating):
        """Set blue activity LED (independent)"""
        lib8relind.set(self.stack, self.BLUE_RELAY, 1 if inflating else 0)

    def update_from_pressure(self, pressure_percent):
        """Update status LEDs based on pressure reading"""
        if pressure_percent < 70:
            self.set_status('green')
        elif pressure_percent < 90:
            self.set_status('yellow')
        else:
            self.set_status('red')
```

**Usage in Main Script:**
```python
from led_control import LEDController

leds = LEDController(stack=0)

# During inflation loop
while inflating:
    pressure = read_pressure_sensor()
    leds.update_from_pressure(pressure)
    leds.set_activity(True)  # Blue ON

    if pressure >= 90:
        stop_pump()
        inflating = False

leds.set_activity(False)  # Blue OFF when done
```

---

## Safety Considerations

1. **Electrical:**
   - All 12V circuits isolated from Pi 5V logic
   - Relay HAT provides optical isolation
   - Fused power supply (inline fuse on +12V)

2. **Mechanical:**
   - LEDs securely mounted, cannot vibrate loose
   - Silicone gaskets prevent moisture ingress
   - Junction box protects internal wiring

3. **Software:**
   - Fail-safe: If Pi crashes, all relays open → all LEDs off
   - No LED state persists after power loss
   - Watchdog timer can reset system if hung

---

## Bill of Materials (LED System Only)

| Item | Quantity | Unit Price | Total | Source | Status |
|------|----------|------------|-------|--------|--------|
| 22mm Red LED (12V) | 2 | $3.50 | $7.00 | Amazon | ✅ ARRIVED |
| 22mm Yellow LED (12V) | 2 | $3.50 | $7.00 | Amazon | ✅ ARRIVED |
| 22mm Green LED (12V) | 2 | $3.50 | $7.00 | Amazon | ✅ ARRIVED |
| 22mm Blue LED (12V) | 2 | $3.50 | $7.00 | Amazon | ✅ ARRIVED |
| Junction Box (12-hole) | 2 | $15.00 | $30.00 | Hardware Store | ✅ ARRIVED |
| Silicone Gaskets (22mm) | Included | - | - | With junction box | ✅ ARRIVED |
| Sequent 8-RELAYS HAT | 2 | $45.00 | $90.00 | Sequent Microsystems | ✅ ARRIVED (2026-02-10) |
| 12V Power Supply (2A) | 2 | $7.99 | $15.98 | Amazon | ✅ ARRIVED |
| Wire (22 AWG stranded) | 50ft | - | - | Hardware Store | ✅ ARRIVED |
| Terminal blocks | 10 | - | - | Amazon | ✅ ARRIVED |

**Total LED System Cost:** ~$163.98

---

## Next Steps

1. ⏳ **Install relay HATs on Pi #6 and Pi #7**
   - Stack on GPIO header (no soldering required)
   - Verify I²C detection: `i2cdetect -y 1` (should see 0x20)
   - Install Python library: `pip3 install 8relind`

2. ⏳ **Mount LEDs in junction boxes**
   - Install gaskets, insert LEDs, tighten mounting nuts
   - Arrange traffic light layout (red/yellow/green vertical)
   - Position blue LED on front for visibility

3. ⏳ **Wire LED power circuits**
   - Create +12V bus bar inside junction box
   - Wire each LED (+) to bus, (-) to relay terminal
   - Wire relay COM terminals to ground

4. ⏳ **Write LED control code**
   - Create `led_control.py` module
   - Implement status and activity control functions
   - Integrate with main balloon control script

5. ⏳ **Test LED sequences**
   - Verify traffic light progression
   - Verify blue independence
   - Test rapid state changes

6. ⏳ **Validate attack demonstration**
   - Secure system: Green → Yellow → Red (working correctly)
   - Vulnerable system: Green only (attack successful)

---

## Documentation References

- **Relay HAT Documentation:** https://sequentmicrosystems.com/products/eight-relays-stackable-card-for-raspberry-pi
- **Python Library:** https://github.com/SequentMicrosystems/8relind-rpi
- **Wiring Diagrams:** See `WIRING_DIAGRAM_MERMAID.md` Section 4 (Relay Control)
- **Control Scripts:** See `balloon_control_secure.py` and `balloon_control_vulnerable.py`
- **Network Config:** See `BALLOON_DEMO_NETWORK_CONFIG.md`
- **Bill of Materials:** See `BALLOON_DEMO_BOM_FINAL.md`

---

**Design Status:** ✅ COMPLETE - Ready for physical assembly when relay HATs installed

**Last Reviewed:** 2026-02-10 by David

