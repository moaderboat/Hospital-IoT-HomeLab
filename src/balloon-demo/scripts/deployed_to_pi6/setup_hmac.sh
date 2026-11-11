#!/bin/bash
# Configure HMAC signing for the Secure Pi (balloon-secure, 10.30.0.25).
#
# Usage:  sudo bash setup_hmac.sh [off|monitor|enforce]     (default: monitor)
#
# - First run: creates /etc/balloon-demo/hmac.conf with a new random 256-bit key.
# - Later runs: only change MODE; the key is kept.
# - The key never leaves the Pi and is never committed to git.
#
# This script does NOT restart anything. Restarting the balloon services
# MOVES HARDWARE (pump and solenoids) if the 12 V supply is connected.
set -euo pipefail

MODE="${1:-monitor}"
case "$MODE" in
  off|monitor|enforce) ;;
  *) echo "Usage: sudo bash $0 [off|monitor|enforce]"; exit 1 ;;
esac

SVC_USER=username
CONF_DIR=/etc/balloon-demo
CONF=$CONF_DIR/hmac.conf

install -d -m 750 -o "$SVC_USER" -g "$SVC_USER" "$CONF_DIR"

if [ ! -f "$CONF" ]; then
  KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
  umask 077
  printf '# HMAC key for Secure Pi /sensor signing. Never commit this file.\nMODE=%s\nKEY=%s\nMAX_SKEW=5\n' \
    "$MODE" "$KEY" > "$CONF"
  echo "Created $CONF with a new key"
else
  sed -i "s/^MODE=.*/MODE=$MODE/" "$CONF"
  echo "Set MODE=$MODE in $CONF (key unchanged)"
fi

chown "$SVC_USER:$SVC_USER" "$CONF"
chmod 600 "$CONF"

ls -l "$CONF"
grep '^MODE=' "$CONF"
echo
echo "To apply (MOVES HARDWARE if 12 V is connected):"
echo "  sudo systemctl restart balloon-control-secure balloon-sensor-publisher-secure"
