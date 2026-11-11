#!/usr/bin/env python3
"""
Vulnerable System - Balloon Control API
Flask web server that controls balloon inflation based on sensor data

⚠️ CRITICAL VULNERABILITIES (Intentional for Demo):
  1. NO AUTHENTICATION on /sensor endpoint
  2. TRUSTS all incoming sensor data without validation
  3. NO SOURCE VERIFICATION (can't tell real sensor from attacker)
  4. NO RATE LIMITING on sensor updates
  5. NO LOGGING of sensor data sources

This allows an attacker to spoof sensor readings and bypass safety limits!

Pi #7 (Vulnerable System) - 192.168.50.100 (VLAN2)
Port: 5000
"""

import time
import threading
import json
import signal
import sys
from datetime import datetime
from flask import Flask, request, jsonify

try:
    import lib8relind
    RELAY8_AVAILABLE = True
except ImportError:
    print("⚠ Warning: lib8relind not installed - 8-relay HAT control disabled (testing mode)")
    RELAY8_AVAILABLE = False

try:
    import lib3relind
    RELAY40A_AVAILABLE = True
except ImportError:
    print("⚠ Warning: lib3relind not installed - 40A relay HAT control disabled (testing mode)")
    RELAY40A_AVAILABLE = False

RELAYS_AVAILABLE = RELAY8_AVAILABLE or RELAY40A_AVAILABLE

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    print("⚠ Warning: paho-mqtt not installed - MQTT publishing disabled")
    MQTT_AVAILABLE = False

app = Flask(__name__)

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "balloon/vulnerable"
username = None

def init_mqtt():
    """Initialize MQTT client for publishing status updates"""
    global username
    if not MQTT_AVAILABLE:
        return

    try:
        username = mqtt.Client(client_id="balloon_vulnerable_control")
        username.connect(MQTT_BROKER, MQTT_PORT, 60)
        username.loop_start()
        print(f"✓ Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        print(f"✗ MQTT connection failed: {e}")
        username = None

def publish_mqtt(topic, payload):
    """Publish data to MQTT topic"""
    if not MQTT_AVAILABLE or username is None:
        return

    try:
        full_topic = f"{MQTT_TOPIC_PREFIX}/{topic}"
        username.publish(full_topic, json.dumps(payload), qos=0, retain=False)
    except Exception as e:
        # Silently ignore publish errors to avoid spamming logs
        pass

# Configuration
STACK_8RELAY = 0    # 8-RELAYS HAT stack level (solenoids)
STACK_40A = 0       # 40A relay HAT stack level (pump)

# Relay assignments
# Physical flow: Pump → UPSTREAM (R4) → INFLATE (R2) → DOWNSTREAM (R3) → Bottle
# Solenoids are NC (normally closed): relay OFF = closed, relay ON = open
# 40A HAT (high-current pump)
RELAY_PUMP = 3      # Air pump (23A) - on 40A HAT relay 3

# 8-RELAYS HAT (solenoids)
RELAY_INFLATE    = 2   # Main line control solenoid - on 8-relay HAT
RELAY_DOWNSTREAM = 3   # Closest to bottle (vent/deflate) - on 8-relay HAT
RELAY_UPSTREAM   = 4   # Closer to pump (high-pressure relief) - on 8-relay HAT

# Pressure thresholds (PSI)
TARGET_PRESSURE_MIN = 25.0   # Start pumping when below this
TARGET_PRESSURE_MAX = 30.0   # Stop pumping when reaching this
MAX_SAFE_PRESSURE = 35.0     # Emergency shutoff (open vents)

# System state
current_pressure = 0.0  # PSI (downstream, primary control)
current_pressure_upstream = 0.0  # PSI (upstream monitoring)
current_temperature = 25.0  # Celsius
last_sensor_update = None
pump_running = False
inflate_valve_open = False
downstream_valve_open = False
upstream_valve_open = False
emergency_stop = False
shutting_down = False  # Flag to stop control loop during shutdown

# Safety: low pressure detection (leak/sensor failure detection)
low_pressure_start_time = None  # Track when both sensors dropped below 10 PSI
LOW_PRESSURE_THRESHOLD = 10.0   # PSI
LOW_PRESSURE_DURATION = 3.0     # seconds

# Statistics
sensor_update_count = 0
last_sensor_source = "none"

def set_relay(relay_num, state):
    """Safely set relay state (with or without hardware)"""
    relay_names = {
        RELAY_PUMP: "PUMP",
        RELAY_INFLATE: "INFLATE",
        RELAY_DOWNSTREAM: "DOWNSTREAM",
        RELAY_UPSTREAM: "UPSTREAM"
    }
    relay_name = relay_names.get(relay_num, f"RELAY{relay_num}")
    state_str = "ON" if state else "OFF"

    # CRITICAL SAFETY: Never turn pump ON if shutting down
    if relay_num == RELAY_PUMP and state == True and shutting_down:
        print(f"⚠ SAFETY: Blocked pump ON command during shutdown")
        return

    if RELAYS_AVAILABLE:
        try:
            # Route pump to 40A HAT, solenoids to 8-RELAYS HAT
            if relay_num == RELAY_PUMP:
                if RELAY40A_AVAILABLE:
                    lib3relind.set(STACK_40A, RELAY_PUMP, 1 if state else 0)
                else:
                    print(f"⚠ Warning: 40A HAT not available, cannot control {relay_name}")
            else:
                if RELAY8_AVAILABLE:
                    lib8relind.set(STACK_8RELAY, relay_num, 1 if state else 0)
                else:
                    print(f"⚠ Warning: 8-RELAYS HAT not available, cannot control {relay_name}")
        except Exception as e:
            print(f"✗ Relay error on {relay_name}: {e}")
    else:
        # Testing mode - just print
        hat_name = "40A HAT" if relay_num == RELAY_PUMP else "8-RELAYS HAT"
        print(f"  [{hat_name} RELAY {relay_num} {relay_name}] → {state_str}")

def emergency_hardware_stop():
    """Force all hardware OFF immediately - bypasses all state tracking"""
    print("⚠ EMERGENCY HARDWARE STOP - Forcing all relays OFF")
    set_relay(RELAY_PUMP, False)
    set_relay(RELAY_INFLATE, False)
    set_relay(RELAY_DOWNSTREAM, False)
    set_relay(RELAY_UPSTREAM, False)

def cleanup_on_exit(signum, frame):
    """Clean up relays when script exits - controlled depressurization"""
    global shutting_down, pump_running, inflate_valve_open, downstream_valve_open, upstream_valve_open

    print("\n\n⚠ SHUTDOWN SIGNAL RECEIVED")
    shutting_down = True  # Signal control loop to stop (set_relay now blocks pump ON)
    time.sleep(0.7)  # Wait for control loop to exit
    print("⚠ Starting depressurization sequence")

    # Step 1: Turn off pump
    print("  1. Pump OFF")
    set_relay(RELAY_PUMP, False)
    pump_running = False
    time.sleep(0.2)

    # Step 2: Close inflate valve (stop flow path)
    print("  2. Inflate valve CLOSED")
    set_relay(RELAY_INFLATE, False)
    inflate_valve_open = False
    time.sleep(0.2)

    # Step 3: Open downstream valve (vent bottle)
    print("  3. Downstream valve OPEN (venting)")
    set_relay(RELAY_DOWNSTREAM, True)
    downstream_valve_open = True
    time.sleep(0.2)

    # Step 4: Open upstream valve (vent upstream line)
    print("  4. Upstream valve OPEN (venting)")
    set_relay(RELAY_UPSTREAM, True)
    upstream_valve_open = True
    time.sleep(2.0)  # Wait for depressurization

    # Step 5: Close downstream valve
    print("  5. Downstream valve CLOSED")
    set_relay(RELAY_DOWNSTREAM, False)
    downstream_valve_open = False
    time.sleep(0.2)

    # Step 6: Close upstream valve
    print("  6. Upstream valve CLOSED")
    set_relay(RELAY_UPSTREAM, False)
    upstream_valve_open = False

    print("✓ Depressurization complete - all hardware OFF")
    sys.exit(0)

def control_loop():
    """Main control loop - runs in background thread"""
    global pump_running, inflate_valve_open, downstream_valve_open, emergency_stop, upstream_valve_open, shutting_down
    global low_pressure_start_time

    print("Control loop started")
    last_mqtt_publish = 0

    while True:
        # Check shutdown flag FIRST (before any sleeps)
        if shutting_down:
            print("Control loop: shutting_down flag set, exiting immediately")
            emergency_hardware_stop()
            return

        # Publish status to MQTT every 0.1 seconds (10 Hz)
        now = time.time()
        if now - last_mqtt_publish >= 0.1:
            publish_mqtt("pressure", {"value": current_pressure, "upstream": current_pressure_upstream, "unit": "PSI"})
            publish_mqtt("relays", {
                "pump": pump_running,
                "inflate": inflate_valve_open,
                "downstream": downstream_valve_open,
                "upstream": upstream_valve_open
            })
            publish_mqtt("sensor_source", {"source": last_sensor_source, "count": sensor_update_count})
            last_mqtt_publish = now

        if emergency_stop:
            # Emergency stop - shut down pump, wait 1s, close all solenoids
            if pump_running or inflate_valve_open or downstream_valve_open or upstream_valve_open:
                print("⚠ EMERGENCY STOP ACTIVE - Shutting down all systems")
                set_relay(RELAY_PUMP, False)
                pump_running = False
                time.sleep(1.0)  # Wait 1 second before closing solenoids (prevent overheating)
                set_relay(RELAY_INFLATE, False)
                set_relay(RELAY_DOWNSTREAM, False)
                set_relay(RELAY_UPSTREAM, False)
                inflate_valve_open = False
                downstream_valve_open = False
                upstream_valve_open = False
            time.sleep(0.5)
            continue

        # Check for stale sensor data - stop pump and close all solenoids
        if last_sensor_update:
            age = (datetime.now() - last_sensor_update).total_seconds()
            if age > 5.0:
                if pump_running or inflate_valve_open:
                    print(f"⚠ Sensor data stale ({age:.1f}s) - stopping pump and closing all valves")
                    set_relay(RELAY_PUMP, False)
                    pump_running = False
                    set_relay(RELAY_INFLATE, False)
                    inflate_valve_open = False
                    set_relay(RELAY_DOWNSTREAM, False)
                    downstream_valve_open = False
                    set_relay(RELAY_UPSTREAM, False)
                    upstream_valve_open = False
                time.sleep(0.5)
                continue
        else:
            # NO SENSOR DATA YET - don't start pump! Ensure ALL hardware is OFF
            if pump_running or inflate_valve_open or downstream_valve_open or upstream_valve_open:
                print("⚠ No sensor data received yet - ensuring all hardware OFF")
                set_relay(RELAY_PUMP, False)
                pump_running = False
                set_relay(RELAY_INFLATE, False)
                inflate_valve_open = False
                set_relay(RELAY_DOWNSTREAM, False)
                downstream_valve_open = False
                set_relay(RELAY_UPSTREAM, False)
                upstream_valve_open = False
            time.sleep(0.5)
            continue

        # ⚠️ VULNERABILITY: Trusts current_pressure without validation
        # An attacker can send fake low pressure and keep pump running!

        if current_pressure > MAX_SAFE_PRESSURE:
            # Over-pressure: vent down to safe level
            if pump_running:
                print(f"⚠ OVERPRESSURE: {current_pressure:.2f} PSI > {MAX_SAFE_PRESSURE} PSI - Stopping pump")
                set_relay(RELAY_PUMP, False)
                pump_running = False

            # Close inflate valve
            if inflate_valve_open:
                set_relay(RELAY_INFLATE, False)
                inflate_valve_open = False

            # Open BOTH downstream AND upstream relief valves for complete venting
            # (prevents dangerous pressure buildup in upstream section during attacks)
            if not downstream_valve_open:
                print(f"⚠ VENTING: Opening downstream valve ({current_pressure:.2f} PSI)")
                set_relay(RELAY_DOWNSTREAM, True)
                downstream_valve_open = True

            if not upstream_valve_open:
                print(f"⚠ VENTING: Opening upstream valve (upstream relief)")
                set_relay(RELAY_UPSTREAM, True)
                upstream_valve_open = True

        elif current_pressure < TARGET_PRESSURE_MIN:
            # Below 25 PSI - inflate to 30 PSI
            # ⚠️ VULNERABILITY: Blindly trusts current_pressure without validation!

            # Check shutdown flag
            if shutting_down:
                emergency_hardware_stop()
                return

            # Close ALL vents immediately (we need to inflate!)
            if downstream_valve_open:
                set_relay(RELAY_DOWNSTREAM, False)
                downstream_valve_open = False
            if upstream_valve_open:
                set_relay(RELAY_UPSTREAM, False)
                upstream_valve_open = False

            # Open inflate valve
            if not inflate_valve_open:
                set_relay(RELAY_INFLATE, True)
                inflate_valve_open = True

            # Start pump
            if not pump_running:
                if shutting_down:
                    emergency_hardware_stop()
                    return
                print(f"→ Starting pump (current: {current_pressure:.2f} PSI, target: {TARGET_PRESSURE_MAX} PSI)")
                set_relay(RELAY_PUMP, True)
                pump_running = True

        elif current_pressure >= TARGET_PRESSURE_MAX:
            # At or above 30 PSI (and below 35 PSI overpressure) - stop pump and hold
            if pump_running:
                print(f"✓ Target reached: {current_pressure:.2f} PSI - Stopping pump")
                set_relay(RELAY_PUMP, False)
                pump_running = False

            # Close inflate valve
            if inflate_valve_open:
                set_relay(RELAY_INFLATE, False)
                inflate_valve_open = False

            # Close vents (we're in safe zone)
            if downstream_valve_open:
                set_relay(RELAY_DOWNSTREAM, False)
                downstream_valve_open = False
            if upstream_valve_open:
                set_relay(RELAY_UPSTREAM, False)
                upstream_valve_open = False

        else:
            # Between 25-30 PSI - continue pumping if pump is running
            # (hysteresis band - don't start/stop pump in this zone)
            pass

        time.sleep(0.1)  # 10 Hz control loop

# Control thread will be started after MQTT initialization in main

# ============== API ENDPOINTS ==============

@app.route('/')
def index():
    """System info"""
    return jsonify({
        "system": "Vulnerable Balloon Control System",
        "pi": "Pi #7 (192.168.50.100)",
        "vlan": "VLAN2 (Vulnerable Network)",
        "security": "DISABLED - No authentication, no validation",
        "warning": "This system is intentionally vulnerable for demonstration purposes",
        "status": get_status()
    })

@app.route('/status')
def status():
    """Get current system status"""
    return jsonify(get_status())

def get_status():
    """Helper to build status dict"""
    return {
        "system": "Vulnerable Balloon Control System",
        "pi": "Pi #7 (192.168.50.100)",
        "vlan": "VLAN2 (Vulnerable Network)",
        "pressure_psi": round(current_pressure, 4),
        "pressure_upstream_psi": round(current_pressure_upstream, 4),
        "pump_running": pump_running,
        "inflate_valve_open": inflate_valve_open,
        "downstream_valve_open": downstream_valve_open,
        "upstream_valve_open": upstream_valve_open,
        "emergency_stop": emergency_stop,
        "attack_detected": last_sensor_source == "attacker",
        "sensor_read_count": sensor_update_count,
        "anomaly_count": 0,  # Vulnerable system does no anomaly detection
        "emergency_stop_count": 1 if emergency_stop else 0,
        "last_sensor_source": last_sensor_source,
        "target_pressure_min": TARGET_PRESSURE_MIN,
        "target_pressure_max": TARGET_PRESSURE_MAX,
        "max_safe_pressure": MAX_SAFE_PRESSURE,
        "absolute_max_pressure": MAX_SAFE_PRESSURE,
        "timestamp": datetime.now().isoformat()
    }

@app.route('/sensor', methods=['POST'])
def update_sensor():
    """
    ⚠️ CRITICAL VULNERABILITY: Accept sensor data from ANYONE

    No authentication required!
    No source validation!
    No rate limiting!

    An attacker can send fake pressure readings and the system
    will blindly trust them, leading to balloon over-inflation!
    """
    global current_pressure, current_pressure_upstream, current_temperature, last_sensor_update
    global sensor_update_count, last_sensor_source

    data = request.json

    # ⚠️ VULNERABILITY: No validation of data source!
    # ⚠️ VULNERABILITY: No validation of data sanity!

    current_pressure = data.get('pressure', current_pressure)
    current_pressure_upstream = data.get('pressure_upstream', current_pressure_upstream)
    current_temperature = data.get('temperature', current_temperature)
    last_sensor_update = datetime.now()
    last_sensor_source = data.get('source', 'unknown')
    sensor_update_count += 1

    return jsonify({
        "status": "accepted",
        "pressure": current_pressure,
        "pressure_upstream": current_pressure_upstream,
        "source": last_sensor_source
    })

@app.route('/control', methods=['POST'])
def manual_control():
    """Manual control (for testing)"""
    global pump_running, inflate_valve_open, downstream_valve_open, upstream_valve_open
    data = request.json

    if 'pump' in data:
        pump_state = data['pump']
        set_relay(RELAY_PUMP, pump_state)
        pump_running = pump_state
        return jsonify({"status": "ok", "pump": pump_state})

    if 'inflate' in data:
        inflate_state = data['inflate']
        set_relay(RELAY_INFLATE, inflate_state)
        inflate_valve_open = inflate_state
        return jsonify({"status": "ok", "inflate": inflate_state})

    if 'downstream' in data:
        downstream_state = data['downstream']
        set_relay(RELAY_DOWNSTREAM, downstream_state)
        downstream_valve_open = downstream_state
        return jsonify({"status": "ok", "downstream": downstream_state})

    if 'upstream' in data:
        upstream_state = data['upstream']
        set_relay(RELAY_UPSTREAM, upstream_state)
        upstream_valve_open = upstream_state
        return jsonify({"status": "ok", "upstream": upstream_state})

    return jsonify({"error": "No valid command"}), 400

@app.route('/emergency_stop', methods=['POST'])
def emergency_stop_api():
    """Emergency stop - shut down everything immediately"""
    global emergency_stop, pump_running, inflate_valve_open, downstream_valve_open, upstream_valve_open
    emergency_stop = True

    # Immediate hardware shutoff
    set_relay(RELAY_PUMP, False)
    pump_running = False

    set_relay(RELAY_INFLATE, False)
    inflate_valve_open = False

    set_relay(RELAY_DOWNSTREAM, False)
    downstream_valve_open = False

    set_relay(RELAY_UPSTREAM, False)
    upstream_valve_open = False

    return jsonify({"status": "emergency_stop_activated"})

@app.route('/reset', methods=['POST'])
def reset():
    """Reset emergency stop"""
    global emergency_stop
    emergency_stop = False
    return jsonify({"status": "reset_complete"})

if __name__ == "__main__":
    print("=" * 60)
    print("VULNERABLE BALLOON CONTROL SYSTEM")
    print("=" * 60)
    print("⚠️  WARNING: This system is INTENTIONALLY INSECURE!")
    print("⚠️  For demonstration purposes only")
    print("=" * 60)
    print(f"  Target Pressure Range: {TARGET_PRESSURE_MIN}-{TARGET_PRESSURE_MAX} PSI")
    print(f"  Max Safe Pressure: {MAX_SAFE_PRESSURE} PSI")
    print(f"  8-RELAYS HAT Available: {RELAY8_AVAILABLE} (solenoids)")
    print(f"  40A Relay HAT Available: {RELAY40A_AVAILABLE} (pump)")
    print(f"  MQTT Available: {MQTT_AVAILABLE}")
    print("=" * 60)
    print("\nVULNERABILITIES:")
    print("  ✗ No authentication on /sensor endpoint")
    print("  ✗ No source validation")
    print("  ✗ No input sanitization")
    print("  ✗ No rate limiting")
    print("  ✗ Trusts all sensor data blindly")
    print("=" * 60)
    print("\nAPI Endpoints:")
    print("  GET  /          - System info")
    print("  GET  /status    - Current status")
    print("  POST /sensor    - Update sensor data (VULNERABLE!)")
    print("  POST /control   - Manual control")
    print("  POST /emergency_stop - Emergency stop")
    print("  POST /reset     - Reset emergency stop")
    print("=" * 60)
    if MQTT_AVAILABLE:
        print("\nMQTT Topics:")
        print(f"  {MQTT_TOPIC_PREFIX}/pressure  - Pressure readings")
        print(f"  {MQTT_TOPIC_PREFIX}/relays    - Relay states")
        print(f"  {MQTT_TOPIC_PREFIX}/sensor_source - Sensor metadata")
        print("=" * 60)
    print("\nInitializing MQTT connection...")
    init_mqtt()

    # Register cleanup handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup_on_exit)
    signal.signal(signal.SIGTERM, cleanup_on_exit)

    print("\nInitializing relays (all OFF)...")
    set_relay(RELAY_PUMP, False)
    set_relay(RELAY_INFLATE, False)
    set_relay(RELAY_DOWNSTREAM, False)
    set_relay(RELAY_UPSTREAM, False)
    pump_running = False
    inflate_valve_open = False
    downstream_valve_open = False
    upstream_valve_open = False
    print("✓ All relays initialized to OFF")
    time.sleep(0.5)  # Let hardware settle before starting control loop

    print("\nStarting control loop...")
    print("⚠ Control loop will wait for sensor data before starting pump")
    # Control loop enabled for EXPO demo
    control_thread = threading.Thread(target=control_loop, daemon=True)
    control_thread.start()

    print("\nStarting Flask server on port 5000...")
    print("(Ctrl+C to stop)\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
