# Firewall Setup Session Notes - 2026-02-05

## Current Status

### What We've Accomplished
- ✅ Confirmed vulnerable Pi is at **192.168.50.100** on **VLAN2**
- ✅ Confirmed inter-VLAN routing works (can ping 192.168.50.1 gateway from 10.30.0.20)
- ✅ Confirmed ping works from username (10.30.0.20) to vulnerable Pi (192.168.50.100)
- ✅ Removed all firewall rules to verify connectivity
- ✅ Identified correct username: **vulnerable** (not vulnerable_balloon_admin)

### Current Issue - SSH Access
- ❌ Cannot SSH to vulnerable@192.168.50.100 from username
- Connection reaches the server (asks for password)
- Password is being rejected even after reset
- **Need to fix before proceeding with firewall rule testing**

---

## Network Configuration Summary

### Vulnerable Pi Details
- **IP Address**: 192.168.50.100
- **VLAN**: VLAN2 (192.168.50.0/24)
- **Switch Port**: Port 15
- **Username**: vulnerable
- **Hostname**: balloon-vulnerable
- **Gateway**: 192.168.50.1

### Testing Pi Details
- **Device**: username
- **IP Address**: 10.30.0.20
- **VLAN**: VLAN30 (10.30.0.0/24)

---

## Firewall Rules to Create (NOT YET DONE)

### Goal
1. ✅ Allow VLAN30 → VLAN2 (so you can manage the vulnerable Pi)
2. ❌ Block VLAN2 → VLAN30 (prevent lateral movement if compromised)

### Rule 1: ALLOW VLAN30 → VLAN2 (Create FIRST)
```
Name: ALLOW_VLAN30_TO_VLAN2
Type: LAN In
Action: Accept

Source:
  Type: Network
  Network: VLAN30 (10.30.0.0/24)

Destination:
  Type: Network
  Network: VLAN2 (192.168.50.0/24)

Protocol: All
Logging: Disable
```

### Rule 2: BLOCK VLAN2 → VLAN30 (Create SECOND)
```
Name: BLOCK_VLAN2_TO_VLAN30
Type: LAN In
Action: Drop

Source:
  Type: Network
  Network: VLAN2 (192.168.50.0/24)

Destination:
  Type: Network
  Network: VLAN30 (10.30.0.0/24)

Protocol: All
Logging: ✅ Enable Logging
```

**CRITICAL**: Rule order matters! ALLOW must come before BLOCK.

---

## Next Steps When You Return

### 1. Fix SSH Access to Vulnerable Pi

**Option A: Fix Password Authentication**

On vulnerable Pi (physical access):
```bash
# Verify user exists
cat /etc/passwd | grep vulnerable

# Reset password with simple password
sudo passwd vulnerable

# Check SSH config allows passwords
sudo grep "PasswordAuthentication" /etc/ssh/sshd_config
# Should say: PasswordAuthentication yes

# If not, edit it:
sudo nano /etc/ssh/sshd_config
# Change to: PasswordAuthentication yes

# Restart SSH
sudo systemctl restart ssh
```

From username:
```bash
ssh vulnerable@192.168.50.100
# Enter the password
```

**Option B: Use SSH Keys (Recommended)**

On username:
```bash
# Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""

# Show public key (copy this)
cat ~/.ssh/id_ed25519.pub
```

On vulnerable Pi (physical access):
```bash
# Switch to vulnerable user
su - vulnerable

# Create SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add username's public key
nano ~/.ssh/authorized_keys
# Paste the public key, save

# Fix permissions
chmod 600 ~/.ssh/authorized_keys
```

From username:
```bash
# Should work without password now
ssh vulnerable@192.168.50.100
```

### 2. Create Firewall Rules

Once SSH works:

1. Go to UDM-SE: **Settings** → **Security** → **Traffic & Security** → **Firewall Rules**
2. Create **ALLOW_VLAN30_TO_VLAN2** first (Rule 1 above)
3. Create **BLOCK_VLAN2_TO_VLAN30** second (Rule 2 above)
4. Verify rule order (ALLOW first, BLOCK second)

### 3. Test Firewall Rules

**Test 1: Admin access still works (VLAN30 → VLAN2) ✅**
```bash
# From username
ping 192.168.50.100
ssh vulnerable@192.168.50.100
```

**Test 2: Lateral movement blocked (VLAN2 → VLAN30) ❌**
```bash
# SSH to vulnerable Pi first
ssh vulnerable@192.168.50.100

# Then from vulnerable Pi, try to reach VLAN30
ping 10.30.0.1        # Should timeout
ping 10.30.0.20       # Should timeout
telnet 10.30.0.51 1883  # Should timeout
```

**Test 3: Check UDM-SE firewall logs**
- Go to **Settings** → **System** → **Logs** → **Firewall**
- Filter by Source: 192.168.50.0/24
- Should see DROP events for blocked attempts

---

## Quick Reference

**Ping works**: ✅ username (10.30.0.20) → vulnerable Pi (192.168.50.100)
**SSH works**: ❌ Need to fix
**Firewall rules**: ❌ Not created yet

**Current firewall state**: All rules removed, all traffic allowed between VLANs

---

**Document Created**: 2026-02-05
**Status**: Paused - SSH troubleshooting needed before firewall testing
