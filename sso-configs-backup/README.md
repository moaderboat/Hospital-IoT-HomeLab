# SSO Configuration Backups

**Created:** 2026-03-24
**Purpose:** Backup of SSO configuration files for Wazuh and HAPI FHIR

## Directory Structure

```
sso-configs-backup/
├── wazuh/
│   ├── config.yml                    # OpenSearch Security authentication config
│   ├── opensearch_dashboards.yml     # Wazuh Dashboard config (includes OpenID settings)
│   └── roles_mapping.yml             # User role mappings (username, username)
├── hapi-fhir/
│   ├── oauth2-proxy.cfg              # OAuth2 Proxy configuration
│   └── oauth2-proxy.service          # Systemd service definition
└── README.md                         # This file
```

## Wazuh SSO Status

**Status:** ❌ **BROKEN** (as of 2026-03-24)

**Current State:**
- OpenID config present in dashboard YAML but **removed from backend** `config.yml`
- Only `basic_internal_auth_domain` enabled in OpenSearch Security
- Must use basic authentication: `admin` / `password`

**Root Cause:**
Running `securityadmin.sh` to apply OpenID config broke SSL certificate handling between dashboard and OpenSearch backend. Unable to restore original working state without backup.

**Backed Up Files:**
- `/etc/wazuh-indexer/opensearch-security/config.yml` → `wazuh/config.yml`
- `/etc/wazuh-dashboard/opensearch_dashboards.yml` → `wazuh/opensearch_dashboards.yml`
- `/etc/wazuh-indexer/opensearch-security/roles_mapping.yml` → `wazuh/roles_mapping.yml`

**Keycloak Client:**
- Client ID: `wazuh`
- Client Secret: `client-secret`
- Realm: `hospital-homelab`
- Valid redirect URIs: `https://10.30.0.55/*`

---

## HAPI FHIR SSO Status

**Status:** ✅ **WORKING** (with caveats)

**Current State:**
- OAuth2 Proxy running successfully (after Keycloak becomes available)
- High restart count (144k+) due to boot-time race condition with Keycloak
- SSO authentication functional once service is stable
- Firewall blocks external access to port 4180 (intentional security measure)

**Issues:**
- OAuth2 Proxy attempts to start before Keycloak is ready during VM boot
- Results in crash loop until Keycloak becomes available
- Once running, service is stable for extended periods

**Backed Up Files:**
- `/etc/oauth2-proxy/oauth2-proxy.cfg` → `hapi-fhir/oauth2-proxy.cfg`
- `/etc/systemd/system/oauth2-proxy.service` → `hapi-fhir/oauth2-proxy.service`

**Keycloak Client:**
- Client ID: `hapi-fhir-oauth2`
- Client Secret: `client-secret`
- Realm: `hospital-homelab`
- Redirect URL: `http://10.30.0.56:4180/oauth2/callback`

**Access:**
- Internal (from VMs): ✅ Works
- External (from workstation): ❌ Blocked by firewall (port 4180)
- Direct HAPI FHIR access: Only via Mirth Connect (port 8080 firewall exception)

---

## Restoration Instructions

### Wazuh - Restore Basic Auth Config

If OpenID config gets accidentally re-enabled and breaks authentication:

```bash
# SSH to Wazuh VM
ssh username@10.30.0.55

# Restore config.yml (basic auth only)
sudo cp /path/to/backup/wazuh/config.yml /etc/wazuh-indexer/opensearch-security/config.yml

# DO NOT run securityadmin.sh unless you have SSL client cert working
# If dashboard is broken, restart services:
sudo systemctl restart wazuh-indexer
sudo systemctl restart wazuh-dashboard
```

### HAPI FHIR - Restore OAuth2 Proxy Config

If OAuth2 Proxy config gets corrupted:

```bash
# SSH to HAPI FHIR VM
ssh username@10.30.0.56

# Restore OAuth2 Proxy config
sudo cp /path/to/backup/hapi-fhir/oauth2-proxy.cfg /etc/oauth2-proxy/oauth2-proxy.cfg

# Restore service definition if needed
sudo cp /path/to/backup/hapi-fhir/oauth2-proxy.service /etc/systemd/system/oauth2-proxy.service
sudo systemctl daemon-reload

# Restart OAuth2 Proxy
sudo systemctl restart oauth2-proxy

# Check status
sudo systemctl status oauth2-proxy
```

---

## Related Documentation

- `TROUBLESHOOTING_HISTORY.md` - Entry "Wazuh SIEM Keycloak SSO Broken After securityadmin.sh (2026-03-24)"
- `SYSTEM_STARTUP_GUIDE.md` - Keycloak SSO Not Working section
- `CLAUDE.md` - Known troubleshooting tips (Wazuh SSO broken entry)

---

## Keycloak Server

**URL:** http://10.30.0.57:8080
**Admin Login:** `admin` / `password`
**Realm:** `hospital-homelab`

**Test Users:**
- `username` / `password`
- `username` / `password`

**OIDC Discovery URL:**
`http://10.30.0.57:8080/realms/hospital-homelab/.well-known/openid-configuration`

---

## Notes

- **DO NOT** attempt to re-enable Wazuh OpenID without first backing up current working config
- **DO NOT** run `securityadmin.sh` on Wazuh without understanding SSL implications
- HAPI FHIR high restart count is cosmetic - service functional once Keycloak available
- All secrets in these configs are internal to homelab environment (not production)
