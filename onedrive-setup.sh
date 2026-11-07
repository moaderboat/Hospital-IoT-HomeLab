#!/usr/bin/env bash
set -euo pipefail
SOURCE_PI="${1:-SOURCE_PI}"

# 1) Install latest rclone
curl -fsSL https://rclone.org/install.sh | sudo bash

# 2) Pull known-good rclone.conf from your source Pi
mkdir -p ~/.config/rclone
scp -o StrictHostKeyChecking=no "${USER}@${SOURCE_PI}:~/.config/rclone/rclone.conf" ~/.config/rclone/rclone.conf

# 3) Clear any stale root id and sanity check
rclone config update One_Drive_Personal root_folder_id= || true
rclone about One_Drive_Personal: && rclone lsd One_Drive_Personal:

# 4) Create persistent systemd user service (mounts Documents → ~/OneDrive_Personal)
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/rclone-onedrive.service <<'UNIT'
[Unit]
Description=Rclone OneDrive Mount
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/rclone mount One_Drive_Personal:Documents %h/OneDrive_Personal --vfs-cache-mode full --dir-cache-time 12h --buffer-size 16M --poll-interval 10s --exclude *.lnk --exclude ea38fc*.json
ExecStop=/bin/fusermount -u %h/OneDrive_Personal
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
UNIT

# 5) Enable + start cleanly
systemctl --user daemon-reload
systemctl --user enable --now rclone-onedrive.service
systemctl --user stop rclone-onedrive.service || true
pkill -f "rclone mount One_Drive_Personal:" 2>/dev/null || true
fusermount -u -z ~/OneDrive_Personal 2>/dev/null || true
systemctl --user start rclone-onedrive.service

# 6) Start at boot before login
sudo loginctl enable-linger "$USER"

# 7) Show status
systemctl --user status rclone-onedrive.service --no-pager
