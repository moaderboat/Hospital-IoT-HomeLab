# ECG-style heartbeat sweep for Sense HAT (Raspberry Pi)
# Shows a static red "4" with IRREGULAR ECG trace (Atrial Fibrillation simulation)
# pip install sense-hat paho-mqtt
# Run with: python3 HeartRate4Monitor.py

import time, math, sys, random, json
from datetime import datetime
try:
    from sense_hat import SenseHat
except ImportError:
    print("This script requires the sense-hat package and hardware.")
    sys.exit(1)

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("This script requires paho-mqtt: pip3 install paho-mqtt")
    sys.exit(1)

# ---------------- Settings ----------------
BASE_BPM = 110           # Elevated heart rate (tachycardia)
BPM_VARIATION = 40       # Random variation ±40 bpm (very irregular!)
TRACE = (0, 255, 0)      # ECG trace color (bright green)
TRACE_DIM = (0, 48, 0)   # optional trailing pixel
FOUR = (255, 0, 0)       # color of the "4"
BG = (0, 0, 0)           # background

SAMPLES_PER_BEAT = 120   # more = smoother shape
SWEEP_RATE = 60          # columns/second target
SHOW_GRID = True         # faint grid background like a monitor
GRID_GAP = 2             # grid spacing in pixels

# MQTT Settings
MQTT_BROKER = "10.30.0.51"
MQTT_PORT = 1883
MQTT_TOPIC = "hospital/heartrate/pi4"
PI_ID = 4
PUBLISH_INTERVAL = 0.05  # seconds between MQTT publishes (50ms = 20 Hz)

# ------------------------------------------
sense = SenseHat()
sense.low_light = False
sense.clear()

# Setup MQTT
username = mqtt.Client(client_id=f"heartrate_pi{PI_ID}")
mqtt_connected = False

def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        print(f"[MQTT] Connected to broker at {MQTT_BROKER}")
    else:
        print(f"[MQTT] Connection failed with code {rc}")

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False
    print(f"[MQTT] Disconnected from broker")

username.on_connect = on_connect
username.on_disconnect = on_disconnect

try:
    username.connect(MQTT_BROKER, MQTT_PORT, 60)
    username.loop_start()
    print(f"[MQTT] Connecting to broker at {MQTT_BROKER}:{MQTT_PORT}...")
except Exception as e:
    print(f"[MQTT] Failed to connect: {e}")
    print("[MQTT] Continuing without MQTT...")

def base_grid():
    if not SHOW_GRID:
        return [BG for _ in range(64)]
    grid = []
    dim = (0, 32, 0)  # Green grid
    for y in range(8):
        for x in range(8):
            if x % GRID_GAP == 0 or y % GRID_GAP == 0:
                grid.append(dim)
            else:
                grid.append(BG)
    return grid

def put_point(pixels, x, y, color):
    if 0 <= x < 8 and 0 <= y < 8:
        pixels[y*8 + x] = color

def draw_digit_four(pixels, color):
    """
    Draw a simple '4' that's readable on 8x8:
      - Left vertical line from top to middle
      - Horizontal line in the middle connecting left to right
      - Right vertical line from top to bottom
    """
    # Left vertical stroke (top to middle)
    put_point(pixels, 2, 1, color)
    put_point(pixels, 2, 2, color)
    put_point(pixels, 2, 3, color)
    # Horizontal middle line
    put_point(pixels, 2, 3, color)
    put_point(pixels, 3, 3, color)
    put_point(pixels, 4, 3, color)
    put_point(pixels, 5, 3, color)
    put_point(pixels, 6, 3, color)
    # Right vertical stroke (full height)
    put_point(pixels, 6, 1, color)
    put_point(pixels, 6, 2, color)
    put_point(pixels, 6, 3, color)
    put_point(pixels, 6, 4, color)
    put_point(pixels, 6, 5, color)

# --- IRREGULAR ECG model (AFib simulation) ---
def ecg_wave_irregular(t):
    """
    Simulates atrial fibrillation:
    - No consistent P wave (atrial activity is chaotic)
    - Irregular QRS timing
    - Variable amplitude
    - Random baseline fluctuation
    """
    # Segment durations (more variable)
    qrs_dur = 0.06
    st_dur = random.uniform(0.08, 0.15)  # Variable ST segment
    t_dur = random.uniform(0.12, 0.20)   # Variable T wave

    qrs_center = qrs_dur * 0.5
    t_start = qrs_dur + st_dur
    t_center = t_start + t_dur * 0.5

    # Variable amplitudes
    qrs_amp = random.uniform(0.7, 1.0)   # QRS varies in height
    t_amp = random.uniform(0.2, 0.4)     # T wave varies
    baseline = random.uniform(-0.05, 0.08)  # Wandering baseline (AFib characteristic)

    def gauss(x, mu, sigma):
        return math.exp(-0.5 * ((x - mu) / sigma)**2)

    val = baseline  # Start with wandering baseline

    # No P wave - this is AFib! Just random fibrillation
    if 0 <= t < qrs_dur:
        # Add random fibrillation noise before QRS
        val += random.uniform(-0.1, 0.1)

    # QRS complex (sharp spike) - but irregular
    if 0 <= t < qrs_dur:
        tri_pos = t / qrs_dur
        tri = 1.0 - abs(2.0 * tri_pos - 1.0)
        val += qrs_amp * (0.75 * tri + 0.25 * gauss(t, qrs_center, qrs_dur/9.0))

    # ST segment - variable elevation/depression
    if qrs_dur <= t < t_start:
        val += random.uniform(-0.05, 0.1)

    # T wave - variable
    if t_start <= t < (t_start + t_dur):
        val += t_amp * gauss(t, t_center, t_dur/3.0)

    # Add some random noise throughout (fibrillation)
    val += random.uniform(-0.08, 0.08)

    return max(0.0, min(1.0, val))

def make_beat_table_irregular(n_samples):
    """Generate one irregular beat"""
    return [ecg_wave_irregular(i / n_samples) for i in range(n_samples)]

def amp_to_row(a):
    # Map amplitude [0..1] to row [1..6] to avoid edge clipping; invert (row 0 is top)
    min_row, max_row = 6, 1
    y = round(min_row + (max_row - min_row) * a)
    return int(max(0, min(7, y)))

# ---- Trace buffer (transparent) ----
def trace_clear():
    return [None for _ in range(64)]

def trace_shift_left(trace):
    new_trace = [None for _ in range(64)]
    for y in range(8):
        for x in range(7):
            src_idx = y*8 + (x+1)
            dst_idx = y*8 + x
            new_trace[dst_idx] = trace[src_idx]
    return new_trace

def composite_frame(base, trace):
    out = base[:]
    for i, px in enumerate(trace):
        if px is not None:
            out[i] = px
    return out

def run():
    # Build constant base layer: grid + static orange "4"
    BASE = base_grid()
    draw_digit_four(BASE, FOUR)

    col_dt = 1.0 / SWEEP_RATE

    # Trace layer starts transparent
    trace = trace_clear()

    phase = 0.0
    beat = make_beat_table_irregular(SAMPLES_PER_BEAT)

    # Irregular timing - use gradual BPM changes with momentum
    current_bpm = BASE_BPM + random.uniform(-BPM_VARIATION, BPM_VARIATION)
    target_bpm = current_bpm
    bpm_velocity = 0.0  # Rate of change (BPM per second)
    period = 60.0 / current_bpm

    t_prev = time.perf_counter()
    last_publish = time.perf_counter()
    last_bpm_change = time.perf_counter()

    try:
        while True:
            now = time.perf_counter()
            dt = now - t_prev
            if dt < col_dt:
                time.sleep(col_dt - dt)
                now = time.perf_counter()
                dt = now - t_prev
            t_prev = now

            # Smooth BPM transitions with heavy damping (critically damped for smooth AFib)
            bpm_error = target_bpm - current_bpm
            # Accelerate toward target with heavy damping (no overshoot, smooth curves)
            acceleration = bpm_error * 0.3 - bpm_velocity * 0.7  # Critically damped system
            bpm_velocity += acceleration * dt
            # Limit maximum rate of change (slower = smoother)
            max_velocity = 10.0  # BPM per second (reduced from 20)
            bpm_velocity = max(-max_velocity, min(max_velocity, bpm_velocity))
            current_bpm += bpm_velocity * dt
            # Soft limits with margin - stay away from boundaries
            current_bpm = max(75, min(145, current_bpm))
            period = 60.0 / current_bpm

            # Change target BPM every 2-5 seconds
            if (now - last_bpm_change) > random.uniform(2.0, 5.0):
                target_bpm = BASE_BPM + random.uniform(-BPM_VARIATION, BPM_VARIATION)
                target_bpm = max(70, min(150, target_bpm))
                last_bpm_change = now

            # Advance ECG phase
            phase = (phase + dt / period) % 1.0

            # Regenerate beat pattern occasionally for variety
            if phase < 0.1 and random.random() < 0.02:
                beat = make_beat_table_irregular(SAMPLES_PER_BEAT)

            idx = int(phase * SAMPLES_PER_BEAT) % SAMPLES_PER_BEAT
            a = beat[idx]
            row = amp_to_row(a)

            # Shift only the TRACE layer left
            trace = trace_shift_left(trace)

            # Draw new ECG column at x=7 on trace layer
            put_point(trace, 7, row, TRACE)
            if row + 1 <= 7:
                put_point(trace, 7, row + 1, TRACE_DIM)

            # Composite: base (with orange "4") + trace (on top)
            frame = composite_frame(BASE, trace)
            sense.set_pixels(frame)

            # Publish MQTT message periodically
            if mqtt_connected and (now - last_publish) >= PUBLISH_INTERVAL:
                payload = {
                    "timestamp": datetime.now().isoformat(),
                    "pi_id": PI_ID,
                    "bpm": int(current_bpm),
                    "status": "anomaly",
                    "anomaly_type": "afib"
                }
                username.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
                last_publish = now

    except KeyboardInterrupt:
        sense.clear()
        username.loop_stop()
        username.disconnect()
        print("\nStopped.")

if __name__ == "__main__":
    print(f"Starting IRREGULAR ECG sweep (AFib simulation) at {BASE_BPM}±{BPM_VARIATION} bpm. Press Ctrl+C to stop.")
    run()
