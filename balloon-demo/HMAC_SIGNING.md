# HMAC Signing for the Secure Pi `/sensor` Endpoint

Added 2026-11-10. Applies only to the **Secure Pi** (`balloon-secure`, 10.30.0.25).
The Vulnerable Pi and `attack_spoof.py` are unchanged.

## What it does

The sensor publisher signs every reading with a shared secret key:

```
X-Timestamp: <unix time, 6 decimals>
X-Signature: hex(HMAC-SHA256(key, "<timestamp>." + request body))
```

The control script checks the signature **before** any other validation. A reading is
rejected (HTTP 401, logged to Wazuh as `[hmac_rejected] ATTACK: ...`) if the signature is
missing, wrong, made with a different key, the body was altered, the timestamp is more
than `MAX_SKEW` seconds old, or the exact request is replayed.

Readings that pass go on to the existing checks (range, I2C cross-check, 2 Hz rate limit,
rate of change). So even with a stolen key, a spoofed value is still caught by the I2C
cross-check: two independent layers.

## Configuration

`/etc/balloon-demo/hmac.conf` on the Pi (owner `username`, mode 600, **not in git**):

```
MODE=off | monitor | enforce
KEY=<64 hex characters>
MAX_SKEW=5
```

| MODE | Behaviour |
|---|---|
| `off` (or no file) | Exactly the pre-HMAC behaviour. Publisher sends unsigned. |
| `monitor` | Publisher signs. Controller checks and logs every signature but rejects nothing for it. |
| `enforce` | Unsigned or invalid readings are rejected. With no key set, everything is rejected (fail closed) and control falls back to the I2C sensor. |

The mode and counters appear in `/status` and in the `balloon/secure/status` MQTT payload
as `hmac_mode`, `hmac_valid_count`, `hmac_failed_count`.

## Files

| File | Where it goes on the Pi |
|---|---|
| `scripts/deployed_to_pi6/balloon_control_secure.py` | `~/balloon-demo/scripts/` |
| `scripts/deployed_to_pi6/sensor_publisher_secure.py` | `~/balloon-demo/scripts/` |
| `scripts/deployed_to_pi6/setup_hmac.sh` | `~/balloon-demo/scripts/` (run once with sudo) |

No systemd unit changes are needed.

## Deploy

⚠️ Restarting the balloon services moves hardware if the 12 V supply is connected.
Do this with 12 V unplugged, or with the bottles fitted, the area clear and the kill switch in reach.

```bash
# from the admin PC
scp balloon_control_secure.py sensor_publisher_secure.py setup_hmac.sh username@10.30.0.25:~/balloon-demo/scripts/

# on the Pi
cd ~/balloon-demo/scripts
sudo bash setup_hmac.sh monitor
sudo systemctl restart balloon-control-secure balloon-sensor-publisher-secure
journalctl -u balloon-control-secure -n 30 | grep -i hmac        # "HMAC mode: monitor ... key set"
journalctl -u balloon-sensor-publisher-secure -n 10              # "HMAC signing: ON", readings OK
curl -s localhost:5000/status | python3 -m json.tool | grep hmac # hmac_valid_count climbing
```

When monitor mode shows the publisher's readings as valid, switch to enforce:

```bash
sudo bash setup_hmac.sh enforce
sudo systemctl restart balloon-control-secure balloon-sensor-publisher-secure
```

## Rollback

1. **Fastest:** `sudo bash setup_hmac.sh off` and restart both services.
2. **Restore the old files:** the pre-HMAC copies are on the Pi as
   `*.known-good-2026-11-10`:
   ```bash
   cd ~/balloon-demo/scripts
   cp balloon_control_secure.py.known-good-2026-11-10 balloon_control_secure.py
   cp sensor_publisher_secure.py.known-good-2026-11-10 sensor_publisher_secure.py
   sudo systemctl restart balloon-control-secure balloon-sensor-publisher-secure
   ```
3. **Git:** tag `secure-known-good-2026-11-10` holds the exact pre-HMAC files
   (credentials scrubbed in the published repo).
