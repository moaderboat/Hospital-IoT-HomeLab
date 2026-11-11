# Read-only config backup of Grafana, Mirth Connect and Keycloak via their admin APIs.
# Run from a computer that can reach VLAN 30 (the desktop at home, or the admin laptop):
#   powershell -ExecutionPolicy Bypass -File .\con_backup.ps1
# Output: .\backups\<yyyy-MM-dd_HHmm>\{grafana,mirth,keycloak}\...  (OneDrive syncs it)
# Node-RED is NOT covered: its API only accepts a Keycloak browser login. Back it up over SSH
# (see CON_FIELD_GUIDE.md section 1A).
# SENSITIVE: the Mirth server configuration can contain connector passwords in plain text.

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
[Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }   # lab services use self-signed certs

$pw   = 'password'
$root = Join-Path $PSScriptRoot ("backups\" + (Get-Date -Format 'yyyy-MM-dd_HHmm'))
$summary = New-Object System.Collections.Generic.List[string]

function Basic([string]$user, [string]$pass) { 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${user}:${pass}")) }
function Save-Url([string]$url, [hashtable]$headers, [string]$path, [string]$method = 'GET', [string]$body = $null) {
    New-Item -ItemType Directory -Force (Split-Path $path) | Out-Null
    $p = @{ Uri = $url; Headers = $headers; Method = $method; UseBasicParsing = $true; TimeoutSec = 120 }
    if ($body) { $p.Body = $body; $p.ContentType = 'application/json' }
    $r = Invoke-WebRequest @p
    $ms = New-Object IO.MemoryStream; $r.RawContentStream.CopyTo($ms)
    [IO.File]::WriteAllBytes($path, $ms.ToArray())                         # raw bytes: keeps UTF-8 intact
    return [Text.Encoding]::UTF8.GetString($ms.ToArray())
}
function Safe([string]$s) { ($s -replace '[^\w\-\. ]', '_').Trim() }

# ---------------- Grafana ----------------
try {
    $g = 'http://10.30.0.53:3000'; $h = @{ Authorization = (Basic 'admin' $pw) }
    $dir = Join-Path $root 'grafana'
    $list = (Save-Url "$g/api/search?type=dash-db&limit=5000" $h "$dir\dashboard_list.json") | ConvertFrom-Json
    foreach ($d in $list) { [void](Save-Url "$g/api/dashboards/uid/$($d.uid)" $h ("$dir\dashboards\" + (Safe $d.title) + "_$($d.uid).json")) }
    [void](Save-Url "$g/api/folders" $h "$dir\folders.json")
    [void](Save-Url "$g/api/datasources" $h "$dir\datasources.json")       # no secrets: passwords are write-only in Grafana
    foreach ($x in @('alert-rules', 'contact-points', 'policies')) {
        try { [void](Save-Url "$g/api/v1/provisioning/$x/export?format=json" $h "$dir\alerting_$x.json") } catch { $summary.Add("Grafana alerting $x export skipped: $($_.Exception.Message)") }
    }
    $summary.Add("Grafana: $(@($list).Count) dashboards + folders, datasources, alerting")
} catch { $summary.Add("Grafana FAILED: $($_.Exception.Message)") }

# ---------------- Mirth Connect ----------------
# Mirth only accepts TLS 1.3, which Windows PowerShell 5.1's web cmdlets can't do, so this uses Windows' curl.exe.
try {
    $m = 'https://10.30.0.54:8443/api'; $dir = Join-Path $root 'mirth'
    New-Item -ItemType Directory -Force $dir | Out-Null
    function Mirth([string]$path, [string]$accept, [string]$file) {
        & curl.exe -sSkf --tlsv1.3 --max-time 120 -u "admin:$pw" -H 'X-Requested-With: OpenAPI' -H "Accept: $accept" -o $file "$m/$path"
        if ($LASTEXITCODE -ne 0) { throw "curl exit $LASTEXITCODE on $path" }
    }
    Mirth 'server/version' 'text/plain' "$dir\server_version.txt"
    Mirth 'server/configuration' 'application/xml' "$dir\server_configuration_FULL_BACKUP.xml"   # = Administrator "Backup Config" (restorable)
    Mirth 'channels' 'application/xml' "$dir\all_channels.xml"
    $ch = [IO.File]::ReadAllText("$dir\all_channels.xml", [Text.Encoding]::UTF8)
    $names = ([regex]::Matches($ch, '<channel version="[^"]*">\s*<id>[^<]*</id>\s*<nextMetaDataId>[^<]*</nextMetaDataId>\s*<name>([^<]*)</name>') | ForEach-Object { $_.Groups[1].Value })
    $summary.Add("Mirth: full server configuration + $(@($names).Count) channel(s): $($names -join ', ')")
} catch { $summary.Add("Mirth FAILED: $($_.Exception.Message)") }

# ---------------- Keycloak ----------------
try {
    $k = 'http://10.30.0.57:8080'; $dir = Join-Path $root 'keycloak'
    $tok = Invoke-RestMethod "$k/realms/master/protocol/openid-connect/token" -Method Post -TimeoutSec 30 `
        -Body @{ grant_type = 'password'; client_id = 'admin-cli'; username = 'admin'; password = $pw }
    $h = @{ Authorization = "Bearer $($tok.access_token)" }
    $realms = (Save-Url "$k/admin/realms" $h "$dir\realms_list.json") | ConvertFrom-Json
    foreach ($r in $realms) {
        $n = $r.realm
        # partial-export is a POST but only reads; client secrets come out masked
        [void](Save-Url "$k/admin/realms/$n/partial-export?exportClients=true&exportGroupsAndRoles=true" $h "$dir\realm_${n}_partial_export.json" 'POST' '{}')
        [void](Save-Url "$k/admin/realms/$n/users?max=1000" $h "$dir\realm_${n}_users.json")   # no passwords
    }
    $summary.Add("Keycloak: realms $(($realms | ForEach-Object realm) -join ', ') (clients, roles, groups, users list)")
} catch { $summary.Add("Keycloak FAILED: $($_.Exception.Message)") }

Write-Host "`nBackup folder: $root" -ForegroundColor Cyan
$summary | ForEach-Object { Write-Host "  $_" -ForegroundColor $(if ($_ -match 'FAILED|skipped') { 'Yellow' } else { 'Green' }) }
Get-ChildItem $root -Recurse -File | Measure-Object Length -Sum | ForEach-Object { Write-Host ("  {0} files, {1:N0} KB" -f $_.Count, ($_.Sum / 1KB)) }
