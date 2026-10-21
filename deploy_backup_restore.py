#!/usr/bin/env python3
"""
Deploy Backup & Restore app and backend service to remote Bahmni servers.
Supports:
  - 192.168.1.4 (kphcs)
  - 196.189.94.149 (bmh)
"""

import os
import sys
import time
import shutil
import tempfile
import subprocess

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

FILES_TO_DEPLOY = [
    ("bahmni-docker/bahmni-standard/bahmni_backup_service.py", "/opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py"),
    ("apps/ui/app/admin/views/backupRestore.html", "/opt/emr/apps/ui/app/admin/views/backupRestore.html"),
    ("apps/ui/app/admin/controllers/backupRestoreController.js", "/opt/emr/apps/ui/app/admin/controllers/backupRestoreController.js"),
    ("apps/ui/app/admin/app.js", "/opt/emr/apps/ui/app/admin/app.js"),
    ("apps/ui/app/admin/index.html", "/opt/emr/apps/ui/app/admin/index.html"),
    ("config/openmrs/apps/admin/extension.json", "/opt/emr/config/openmrs/apps/admin/extension.json"),
]

def find_tool(names):
    for n in names:
        p = shutil.which(n)
        if p: return p
    for d in [r"C:\Program Files\PuTTY", r"C:\Program Files (x86)\PuTTY", os.path.expandvars(r"%LOCALAPPDATA%\Programs\PuTTY")]:
        for n in names:
            p = os.path.join(d, n)
            if os.path.isfile(p): return p
    return None

PLINK = find_tool(["plink", "plink.exe"])
PSCP = find_tool(["pscp", "pscp.exe"])

def run_remote(host, user, pw, cmd, timeout=60):
    res = subprocess.run(
        [PLINK, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout
    )
    return res.returncode, res.stdout, res.stderr

def run_sudo(host, user, pw, cmd, timeout=60):
    wrapped = f"echo '{pw}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    return run_remote(host, user, pw, wrapped, timeout=timeout)

def upload_file(host, user, pw, local_path, remote_temp_path):
    res = subprocess.run(
        [PSCP, "-batch", "-pw", pw, local_path, f"{user}@{host}:{remote_temp_path}"],
        capture_output=True, text=True, timeout=60
    )
    return res.returncode, res.stdout, res.stderr

def deploy_to_server(host, user, pw):
    print(f"\n==================================================")
    print(f"[*] Deploying Backup & Restore to {user}@{host} ...")
    print(f"==================================================")

    # 1. Test connectivity
    rc, out, err = run_remote(host, user, pw, "hostname && whoami")
    if rc != 0:
        print(f"[!] SSH connection failed to {host}:\n{err}")
        return False
    print(f"[OK] Connected to host: {out.strip().splitlines()[0]}")

    # Ensure remote dirs
    remote_dirs = [
        "/opt/emr/backups",
        "/opt/emr/bahmni-docker/bahmni-standard",
        "/opt/emr/apps/ui/app/admin/views",
        "/opt/emr/apps/ui/app/admin/controllers",
        "/opt/emr/config/openmrs/apps/admin",
    ]
    for d in remote_dirs:
        run_sudo(host, user, pw, f"mkdir -p {d} && chown -R {user}:{user} {d} 2>/dev/null || true")

    # 2. Upload and install files
    for local_rel, remote_dest in FILES_TO_DEPLOY:
        local_full = os.path.join(REPO_ROOT, local_rel)
        if not os.path.isfile(local_full):
            print(f"[!] Local file missing: {local_full}")
            return False

        filename = os.path.basename(local_rel)
        remote_temp = f"/tmp/{filename}"
        print(f"[*] Uploading {filename} -> {remote_dest} ...")
        rc, out, err = upload_file(host, user, pw, local_full, remote_temp)
        if rc != 0:
            print(f"[!] Failed to upload {filename}: {err}")
            return False

        run_sudo(host, user, pw, f"cp {remote_temp} {remote_dest} && rm -f {remote_temp}")

    # Make python script executable
    run_sudo(host, user, pw, "chmod +x /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py")
    print("[OK] All files deployed successfully.")

    # 3. Configure Apache Proxy inside bahmni-standard-proxy-1
    print("[*] Configuring Apache Proxy (/backup-api -> http://172.18.0.1:5055/api) ...")
    proxy_script = """python3 -c "
import subprocess
subprocess.run(['docker', 'cp', 'bahmni-standard-proxy-1:/usr/local/apache2/conf/bahmni-proxy.conf', '/tmp/bahmni-proxy.conf'], check=True)
with open('/tmp/bahmni-proxy.conf', 'r') as f:
    c = f.read()
lines = [l for l in c.splitlines() if 'backup-api' not in l and 'Bahmni Backup API' not in l]
c = '\\n'.join(lines)
block = '''# Bahmni Backup API
ProxyPass /backup-api http://172.18.0.1:5055/api connectiontimeout=300 timeout=1800
ProxyPassReverse /backup-api http://172.18.0.1:5055/api
'''
if '#Bahmni Web' in c:
    c = c.replace('#Bahmni Web', block + '\\n#Bahmni Web')
else:
    c = c + '\\n' + block
with open('/tmp/bahmni-proxy.conf', 'w') as f:
    f.write(c)
subprocess.run(['docker', 'cp', '/tmp/bahmni-proxy.conf', 'bahmni-standard-proxy-1:/usr/local/apache2/conf/bahmni-proxy.conf'], check=True)
subprocess.run(['docker', 'exec', 'bahmni-standard-proxy-1', 'httpd', '-t'], check=True)
subprocess.run(['docker', 'exec', 'bahmni-standard-proxy-1', 'httpd', '-k', 'graceful'], check=True)
print('PROXY_CONFIG_OK')
"
"""
    rc, out, err = run_sudo(host, user, pw, proxy_script)
    if rc != 0:
        print(f"[!] Warning on proxy update: {err}")
    else:
        print("[OK] Apache proxy configuration verified and reloaded.")

    # 4. Setup systemd service for the backup daemon
    print("[*] Setting up systemd service bahmni-backup.service ...")
    service_content = """[Unit]
Description=Bahmni Backup and Restore Service Daemon
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/emr/bahmni-docker/bahmni-standard
ExecStart=/usr/bin/python3 /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py --daemon
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    # 4. Setup systemd service for the backup daemon
    print("[*] Setting up systemd service bahmni-backup.service ...")
    local_service_tmp = os.path.join(tempfile.gettempdir(), "bahmni-backup.service")
    with open(local_service_tmp, "w", encoding="utf-8") as f:
        f.write(service_content)
    upload_file(host, user, pw, local_service_tmp, "/tmp/bahmni-backup.service")
    try:
        os.remove(local_service_tmp)
    except Exception:
        pass

    enable_cmd = "cp /tmp/bahmni-backup.service /etc/systemd/system/bahmni-backup.service && rm -f /tmp/bahmni-backup.service && systemctl daemon-reload && systemctl enable --now bahmni-backup.service && systemctl restart bahmni-backup.service"
    rc, out, err = run_sudo(host, user, pw, enable_cmd)
    if rc != 0:
        print(f"[!] Warning on systemd service creation: {err}")
    else:
        print("[OK] Service bahmni-backup.service enabled and started.")

    time.sleep(2)

    # 5. Verify local daemon status on host
    rc, out, err = run_sudo(host, user, pw, "systemctl is-active bahmni-backup.service")
    print(f"[*] Service active state: {out.strip()}")

    # 6. Test proxy routing to /backup-api
    print("[*] Testing proxy endpoint https://localhost/backup-api/status ...")
    rc, out, err = run_remote(host, user, pw, "curl -k -s https://localhost/backup-api/status")
    print(f"[*] Response from /backup-api/status:\n{out.strip()[:300]}")

    # 7. Test Extension JSON
    print("[*] Verifying extension.json contains backupRestore tile ...")
    rc, out, err = run_remote(host, user, pw, "curl -k -s https://localhost/bahmni_config/openmrs/apps/admin/extension.json | grep -A 10 backupRestore")
    print(f"[*] Extension check:\n{out.strip()[:300]}")

    return True

if __name__ == "__main__":
    servers = [
        ("192.168.1.4", "kphcs", " "),
        ("196.189.94.149", "bmh", "   "),
    ]

    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    for host, user, pw in servers:
        if target != "all" and target != host:
            continue
        ok = deploy_to_server(host, user, pw)
        if not ok:
            print(f"[!] Deployment failed for {host}")
        else:
            print(f"[OK] Deployment SUCCEEDED for {host}")
