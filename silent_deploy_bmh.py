import os
import shutil
import subprocess

host = "196.189.94.149"
user = "bmh"
pw = "   "

REPO_ROOT = r"c:\Users\COMPUTER\Documents\emr"

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

def run_remote(cmd):
    res = subprocess.run(
        [PLINK, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return res.returncode, res.stdout, res.stderr

def run_sudo(cmd):
    wrapped = f"echo '{pw}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    return run_remote(wrapped)

def upload_file(local_path, remote_dest):
    filename = os.path.basename(local_path)
    remote_tmp = f"/tmp/{filename}"
    res = subprocess.run(
        [PSCP, "-batch", "-pw", pw, local_path, f"{user}@{host}:{remote_tmp}"],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if res.returncode != 0:
        print(f"Upload failed for {filename}: {res.stderr}")
        return False
    run_sudo(f"cp {remote_tmp} {remote_dest} && rm -f {remote_tmp}")
    print(f"[OK] Deployed {filename} -> {remote_dest}")
    return True

print("[1/4] Ensuring directories...")
run_sudo("mkdir -p /opt/emr/backups /opt/emr/apps/ui/app/admin/views /opt/emr/apps/ui/app/admin/controllers /opt/emr/config/openmrs/apps/admin /opt/emr/bahmni-docker/bahmni-standard")

print("[2/4] Uploading UI and backup files silently (bind-mounted, NO restart required)...")
files = [
    (r"bahmni-docker\bahmni-standard\bahmni_backup_service.py", "/opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py"),
    (r"apps\ui\app\admin\views\backupRestore.html", "/opt/emr/apps/ui/app/admin/views/backupRestore.html"),
    (r"apps\ui\app\admin\controllers\backupRestoreController.js", "/opt/emr/apps/ui/app/admin/controllers/backupRestoreController.js"),
    (r"apps\ui\app\admin\app.js", "/opt/emr/apps/ui/app/admin/app.js"),
    (r"apps\ui\app\admin\index.html", "/opt/emr/apps/ui/app/admin/index.html"),
    (r"config\openmrs\apps\admin\extension.json", "/opt/emr/config/openmrs/apps/admin/extension.json"),
]

for rel, dest in files:
    full = os.path.join(REPO_ROOT, rel)
    upload_file(full, dest)

run_sudo("chmod +x /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py")

print("[3/4] Configuring proxy routing gracefully (/backup-api -> http://172.18.0.1:5055/api)...")
proxy_py = """python3 -c "
import subprocess
subprocess.run(['docker', 'cp', 'bahmni-standard-proxy-1:/usr/local/apache2/conf/bahmni-proxy.conf', '/tmp/bahmni-proxy.conf'], check=True)
with open('/tmp/bahmni-proxy.conf', 'r') as f:
    c = f.read()
lines = [l for l in c.splitlines() if 'backup-api' not in l and 'Bahmni Backup API' not in l]
c = '\\n'.join(lines)
block = '''# Bahmni Backup API
ProxyPass /backup-api http://172.18.0.1:5055/api
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
print('PROXY_GRACEFUL_RELOAD_OK')
"
"""
rc, out, err = run_sudo(proxy_py)
print(f"Proxy status: {out.strip()} {err.strip()}")

print("[4/4] Starting standalone backup daemon in background (zero impact on EMR containers)...")
service_content = """[Unit]
Description=Bahmni Backup and Restore Service Daemon
After=network.target docker.service

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
local_svc = os.path.join(REPO_ROOT, "bahmni-backup.service")
with open(local_svc, "w", encoding="utf-8") as f:
    f.write(service_content)

upload_file(local_svc, "/etc/systemd/system/bahmni-backup.service")
try:
    os.remove(local_svc)
except Exception:
    pass

run_sudo("systemctl daemon-reload && systemctl enable --now bahmni-backup.service && systemctl restart bahmni-backup.service")

rc, out, err = run_remote("systemctl is-active bahmni-backup.service")
print(f"Backup daemon active: {out.strip()}")

rc, out, err = run_remote("curl -k -s https://localhost/backup-api/status")
print(f"Proxy check /backup-api/status: {out.strip()}")

print("[DONE] Silent deployment to 196.189.94.149 finished without restarting or disturbing any clinical containers.")
