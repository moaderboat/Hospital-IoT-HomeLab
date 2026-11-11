# Installing 40A Relay HAT Library (lib3relind)

## Hardware Setup

1. **Connect 40A HAT to Pi via GPIO ribbon cable**
   - Cannot physically stack on top of 8-RELAYS HAT (too large)
   - Use female-to-female GPIO ribbon cable or side-mount headers
   - Both HATs connect to same 40-pin GPIO header

2. **Set stack address to 0** (default)
   - DIP switches on back of 40A HAT should all be OFF for address 0
   - Same as your 8-RELAYS HAT, but they use different I2C addresses internally

3. **Wire 12V power supply**
   - Connect 12V 29A power supply to 40A HAT terminal block
   - 40A HAT provides 5V/2A to Raspberry Pi (can power Pi from HAT)
   - Connect pump to relay #1 output terminals

## Software Installation

SSH to Pi #7:
```bash
ssh username@192.168.50.100
```

Install dependencies and library:
```bash
# Update package list
sudo apt-get update

# Install Python dependencies
sudo apt-get install -y build-essential python3-pip python3-dev python3-smbus git

# Install minimalmodbus (required for RS485 support)
sudo pip3 install -U minimalmodbus

# Clone the 40A relay library
cd ~
git clone https://github.com/SequentMicrosystems/3relind-rpi.git

# Install the Python library
cd 3relind-rpi/python/3relind/
sudo python3 setup.py install
```

## Verify Installation

Test that both HATs are detected:
```bash
# Scan I2C bus (should see both HATs)
i2cdetect -y 1

# Test 40A HAT library
python3 -c "import lib3relind; print('40A HAT library OK')"

# Test 8-RELAYS HAT library
python3 -c "import lib8relind; print('8-RELAYS HAT library OK')"
```

Expected output from `i2cdetect -y 1`:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- 27 -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- 48 -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- 6c -- -- --
70: -- -- -- -- -- -- -- --
```
- `0x27` = 8-RELAYS HAT
- `0x48` = ADS1115 pressure sensor ADC
- `0x6c` = 40A relay HAT (lib3relind)

## Deploy Updated Script

Copy the modified script to Pi #7:
```bash
# From your Windows machine (WSL)
scp /mnt/c/Users/david/OneDrive/Documents/Fall\ 25\ school/Senior\ Design\ I/balloon-demo/scripts/balloon_control_api_vulnerable.py username@192.168.50.100:~/balloon-demo/scripts/
```

Restart the service:
```bash
ssh username@192.168.50.100
sudo systemctl restart balloon-control-api.service
sudo journalctl -u balloon-control-api.service -f
```

Expected startup output:
```
============================================================
VULNERABLE BALLOON CONTROL SYSTEM
============================================================
⚠️  WARNING: This system is INTENTIONALLY INSECURE!
⚠️  For demonstration purposes only
============================================================
  Target Pressure: 2.5 PSI
  Max Safe Pressure: 3.5 PSI
  8-RELAYS HAT Available: True (solenoids)
  40A Relay HAT Available: True (pump)
  MQTT Available: True
============================================================
```

## Wiring Summary

**40A HAT:**
- Relay 1: Air pump (23A load)
- 12V input: Power supply positive/negative
- 5V output: Optional - can power Pi via GPIO

**8-RELAYS HAT:**
- Relay 2: Inflate solenoid (~0.5A)
- Relay 3: Vent solenoid (~0.5A)
- Relay 4: Relief solenoid (~0.5A)
- 12V input: Power from terminal block

**Power distribution:**
- 12V 29A supply feeds both HATs via terminal blocks
- Pump gets 23A through 40A HAT relay #1
- Solenoids get ~1.5A total through 8-RELAYS HAT relays #2-4

## Testing Individual Relays

Test pump (40A HAT):
```bash
# Turn pump ON
python3 -c "import lib3relind; lib3relind.set(0, 1, 1)"

# Turn pump OFF
python3 -c "import lib3relind; lib3relind.set(0, 1, 0)"
```

Test solenoids (8-RELAYS HAT):
```bash
# Inflate solenoid ON
python3 -c "import lib8relind; lib8relind.set(0, 2, 1)"

# Vent solenoid ON
python3 -c "import lib8relind; lib8relind.set(0, 3, 1)"

# Relief solenoid ON
python3 -c "import lib8relind; lib8relind.set(0, 4, 1)"

# All OFF
python3 -c "import lib8relind; lib8relind.set_all(0, 0)"
```

## Troubleshooting

**40A HAT not detected:**
- Check GPIO ribbon cable connection
- Run `i2cdetect -y 1` - should see device at 0x6c
- Verify 12V power connected to HAT

**Library import error:**
- Reinstall: `cd ~/3relind-rpi/python/3relind && sudo python3 setup.py install`
- Check: `python3 -c "import lib3relind; print(lib3relind.__file__)"`

**Pump not switching:**
- Verify wiring: 12V+ and GND to pump terminals
- Check relay LED on 40A HAT (should light when ON)
- Measure voltage at relay output with multimeter
