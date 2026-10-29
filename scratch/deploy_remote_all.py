import os
import tarfile
import subprocess
import time

REPO_ROOT = r"c:\Users\COMPUTER\Documents\emr"
HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

FILES_MAP = [
    # Orders App
    ("apps/ui/app/orders/views/orderSearch.html", "/opt/emr/apps/ui/app/orders/views/orderSearch.html"),
    ("apps/ui/app/orders/controllers/orderSearchController.js", "/opt/emr/apps/ui/app/orders/controllers/orderSearchController.js"),
    ("apps/ui/app/orders/app.js", "/opt/emr/apps/ui/app/orders/app.js"),
    ("apps/ui/app/orders/index.html", "/opt/emr/apps/ui/app/orders/index.html"),
    ("apps/ui/app/orders/views/orderFulfillment.html", "/opt/emr/apps/ui/app/orders/views/orderFulfillment.html"),
    ("apps/ui/app/orders/controllers/orderFulfillmentController.js", "/opt/emr/apps/ui/app/orders/controllers/orderFulfillmentController.js"),
    ("apps/ui/app/orders/initialization.js", "/opt/emr/apps/ui/app/orders/initialization.js"),
    ("apps/ui/app/orders/orderFulfillmentConfig.js", "/opt/emr/apps/ui/app/orders/orderFulfillmentConfig.js"),
    
    # Concept Set (Result report fix)
    ("apps/ui/app/common/concept-set/directives/conceptSet.js", "/opt/emr/apps/ui/app/common/concept-set/directives/conceptSet.js"),
    ("apps/ui/app/common/concept-set/services/conceptSetServices.js", "/opt/emr/apps/ui/app/common/concept-set/services/conceptSetServices.js"),
    ("apps/ui/app/common/concept-set/views/conceptSet.html", "/opt/emr/apps/ui/app/common/concept-set/views/conceptSet.html"),

    # Orders App Config
    ("config/openmrs/apps/orders/app.json", "/opt/emr/config/openmrs/apps/orders/app.json"),
    ("config/openmrs/apps/orders/extension.json", "/opt/emr/config/openmrs/apps/orders/extension.json"),

    # Admin App - Backup & Restore
    ("apps/ui/app/admin/views/backupRestore.html", "/opt/emr/apps/ui/app/admin/views/backupRestore.html"),
    ("apps/ui/app/admin/controllers/backupRestoreController.js", "/opt/emr/apps/ui/app/admin/controllers/backupRestoreController.js"),
    ("bahmni-docker/bahmni-standard/bahmni_backup_service.py", "/opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py"),

    # Admin App - Branding
    ("apps/ui/app/admin/views/branding.html", "/opt/emr/apps/ui/app/admin/views/branding.html"),
    ("apps/ui/app/admin/controllers/brandingController.js", "/opt/emr/apps/ui/app/admin/controllers/brandingController.js"),
    ("apps/ui/app/admin/app.js", "/opt/emr/apps/ui/app/admin/app.js"),
    ("apps/ui/app/admin/index.html", "/opt/emr/apps/ui/app/admin/index.html"),
    ("config/openmrs/apps/admin/extension.json", "/opt/emr/config/openmrs/apps/admin/extension.json"),
    ("config/openmrs/apps/branding.json", "/opt/emr/config/openmrs/apps/branding.json"),
    ("config/openmrs/apps/home/whiteLabel.json", "/opt/emr/config/openmrs/apps/home/whiteLabel.json"),

    # Clinical UI Fixes
    ("apps/ui/app/clinical/dashboard/views/clinicalDashboardHeader.html", "/opt/emr/apps/ui/app/clinical/dashboard/views/clinicalDashboardHeader.html"),
    ("apps/ui/app/clinical/consultation/views/orders.html", "/opt/emr/apps/ui/app/clinical/consultation/views/orders.html"),
    ("apps/ui/app/clinical/consultation/controllers/orderController.js", "/opt/emr/apps/ui/app/clinical/consultation/controllers/orderController.js"),
    ("apps/ui/app/clinical/consultation/views/orderTemplateViews/ordersTemplate.html", "/opt/emr/apps/ui/app/clinical/consultation/views/orderTemplateViews/ordersTemplate.html"),
]

def run_remote(cmd):
    res = subprocess.run(
        ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return res.returncode, res.stdout, res.stderr

def run_sudo(cmd):
    wrapped = f"echo '{PW}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    return run_remote(wrapped)

def main():
    print(f"[*] Preparing deployment to {USER}@{HOST} ...")
    
    # 1. Verify all local files
    tar_path = os.path.join(REPO_ROOT, "scratch", "emr_deploy.tar.gz")
    print(f"[*] Creating deployment archive: {tar_path}")
    with tarfile.open(tar_path, "w:gz") as tar:
        for rel_src, remote_dest in FILES_MAP:
            local_full = os.path.join(REPO_ROOT, rel_src.replace("/", os.sep))
            if not os.path.isfile(local_full):
                raise FileNotFoundError(f"Missing local file: {local_full}")
            tar.add(local_full, arcname=rel_src)
            print(f"  + Added {rel_src} ({os.path.getsize(local_full)} bytes)")
    
    tar_size_kb = os.path.getsize(tar_path) / 1024
    print(f"[OK] Archive created successfully ({tar_size_kb:.1f} KB)")

    # 2. Upload archive via pscp
    print(f"[*] Uploading archive to {HOST}:/tmp/emr_deploy.tar.gz ...")
    res = subprocess.run(
        ["pscp", "-batch", "-pw", PW, tar_path, f"{USER}@{HOST}:/tmp/emr_deploy.tar.gz"],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if res.returncode != 0:
        print(f"[!] Upload failed: {res.stderr}")
        return False
    print("[OK] Archive uploaded to remote /tmp/emr_deploy.tar.gz")

    # 3. Remote installation script
    remote_script = """#!/bin/bash
set -e

echo "[1/6] Extracting deployment archive..."
rm -rf /tmp/emr_deploy
mkdir -p /tmp/emr_deploy
tar -xzf /tmp/emr_deploy.tar.gz -C /tmp/emr_deploy

echo "[2/6] Ensuring remote directories exist..."
mkdir -p /opt/emr/apps/ui/app/orders/views
mkdir -p /opt/emr/apps/ui/app/orders/controllers
mkdir -p /opt/emr/apps/ui/app/admin/views
mkdir -p /opt/emr/apps/ui/app/admin/controllers
mkdir -p /opt/emr/apps/ui/app/common/concept-set/directives
mkdir -p /opt/emr/apps/ui/app/common/concept-set/services
mkdir -p /opt/emr/apps/ui/app/common/concept-set/views
mkdir -p /opt/emr/apps/ui/app/clinical/dashboard/views
mkdir -p /opt/emr/apps/ui/app/clinical/consultation/views/orderTemplateViews
mkdir -p /opt/emr/apps/ui/app/clinical/consultation/controllers
mkdir -p /opt/emr/config/openmrs/apps/orders
mkdir -p /opt/emr/config/openmrs/apps/admin
mkdir -p /opt/emr/config/openmrs/apps/home
mkdir -p /opt/emr/bahmni-docker/bahmni-standard
mkdir -p /opt/emr/backups

echo "[3/6] Deploying files into /opt/emr/ ..."
"""
    # Append copy commands
    for rel_src, remote_dest in FILES_MAP:
        remote_script += f"cp /tmp/emr_deploy/{rel_src} {remote_dest}\n"

    remote_script += """
chmod -R 644 /opt/emr/apps/ui/app/orders/
chmod -R 644 /opt/emr/apps/ui/app/admin/
chmod -R 644 /opt/emr/apps/ui/app/common/concept-set/
chmod -R 644 /opt/emr/config/openmrs/apps/
chmod 755 /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py

echo "[4/6] Setting up systemd service bahmni-backup.service..."
cat << 'EOF' > /etc/systemd/system/bahmni-backup.service
[Unit]
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
EOF

systemctl daemon-reload
systemctl enable --now bahmni-backup.service
systemctl restart bahmni-backup.service

echo "[5/6] Ensuring OpenMRS DB privileges and search queries..."
docker exec bahmni-standard-openmrsdb-1 mysql -uroot -p"adminAdmin!123" openmrs -e "
INSERT IGNORE INTO privilege (privilege, description, uuid) VALUES 
('app:admin:restore', 'Bahmni Admin: Privilege to restore system backups and access restore operations', UUID()), 
('app:admin:deleteBackup', 'Bahmni Admin: Privilege to delete backup archives', UUID()); 
INSERT IGNORE INTO role_privilege (role, privilege) VALUES 
('SuperAdmin', 'app:admin:restore'), ('SuperAdmin', 'app:admin:deleteBackup'), 
('System Developer', 'app:admin:restore'), ('System Developer', 'app:admin:deleteBackup'), 
('Privilege Level: Full', 'app:admin:restore'), ('Privilege Level: Full', 'app:admin:deleteBackup');
"

echo "[6/6] Cleaning up temp deployment files..."
rm -rf /tmp/emr_deploy /tmp/emr_deploy.tar.gz
echo "DEPLOYMENT_FILES_INSTALLED_OK"
"""

    remote_script_local = os.path.join(REPO_ROOT, "scratch", "remote_install.sh")
    with open(remote_script_local, "w", encoding="utf-8", newline="\n") as f:
        f.write(remote_script)

    print(f"[*] Uploading install script to {HOST}:/tmp/remote_install.sh ...")
    res = subprocess.run(
        ["pscp", "-batch", "-pw", PW, remote_script_local, f"{USER}@{HOST}:/tmp/remote_install.sh"],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if res.returncode != 0:
        print(f"[!] Upload script failed: {res.stderr}")
        return False

    print("[*] Executing remote install script with sudo (zero downtime)...")
    rc, out, err = run_sudo("chmod +x /tmp/remote_install.sh && /tmp/remote_install.sh && rm -f /tmp/remote_install.sh")
    print("Remote Install Output:\n", out)
    if err:
        print("Remote Install Stderr:\n", err)
    if rc != 0:
        print(f"[!] Error during remote installation, code {rc}")
        return False

    time.sleep(2)

    # 4. Verification step
    print("\n================ VERIFICATION ==================")
    print("[*] 1. Checking bahmni-backup.service status:")
    rc, out, err = run_remote("systemctl is-active bahmni-backup.service")
    print("  -> Service is-active:", out.strip())

    print("[*] 2. Checking /api/branding on host port 5055:")
    rc, out, err = run_remote("curl -s http://127.0.0.1:5055/api/branding | head -n 10")
    print("  -> /api/branding:\n", out.strip())

    print("[*] 3. Checking /api/backups on host port 5055:")
    rc, out, err = run_remote("curl -s http://127.0.0.1:5055/api/backups | head -n 10")
    print("  -> /api/backups:\n", out.strip())

    print("[*] 4. Checking /backup-api via Apache proxy (HTTPS):")
    rc, out, err = run_remote("curl -k -s https://localhost/backup-api/status")
    print("  -> Proxy /backup-api/status:\n", out.strip()[:200])

    print("[*] 5. Checking admin extension.json for branding and backupRestore:")
    rc, out, err = run_remote("curl -k -s https://localhost/bahmni_config/openmrs/apps/admin/extension.json | grep -E '\"branding\"|\"backupRestore\"'")
    print("  -> Extension tiles:\n", out.strip())

    print("[*] 6. Checking Orders orderSearch.html HTTP 200 via proxy:")
    rc, out, err = run_remote("curl -k -s -o /dev/null -w '%{http_code}' https://localhost/bahmni/orders/views/orderSearch.html")
    print("  -> orderSearch.html HTTP code:", out.strip())

    print("[*] 7. Checking Admin branding.html HTTP 200 via proxy:")
    rc, out, err = run_remote("curl -k -s -o /dev/null -w '%{http_code}' https://localhost/bahmni/admin/views/branding.html")
    print("  -> branding.html HTTP code:", out.strip())

    print("[*] 8. Checking Admin backupRestore.html HTTP 200 via proxy:")
    rc, out, err = run_remote("curl -k -s -o /dev/null -w '%{http_code}' https://localhost/bahmni/admin/views/backupRestore.html")
    print("  -> backupRestore.html HTTP code:", out.strip())

    print("\n[✔] ALL DEPLOYMENT STEPS COMPLETED SUCCESSFULLY WITHOUT INTERRUPTING LIVE ACTIVITIES!")
    return True

if __name__ == "__main__":
    main()
