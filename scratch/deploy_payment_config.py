import os
import tarfile
import subprocess
import time

REPO_ROOT = r"c:\Users\COMPUTER\Documents\emr"
HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

FILES_MAP = [
    ("apps/ui/app/admin/views/paymentConfig.html", "/opt/emr/apps/ui/app/admin/views/paymentConfig.html"),
    ("apps/ui/app/admin/controllers/paymentConfigController.js", "/opt/emr/apps/ui/app/admin/controllers/paymentConfigController.js"),
    ("apps/ui/app/admin/app.js", "/opt/emr/apps/ui/app/admin/app.js"),
    ("apps/ui/app/admin/index.html", "/opt/emr/apps/ui/app/admin/index.html"),
    ("config/openmrs/apps/admin/extension.json", "/opt/emr/config/openmrs/apps/admin/extension.json"),
    ("bahmni-docker/bahmni-standard/bahmni_backup_service.py", "/opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py"),
    ("apps/ui/app/orders/controllers/orderFulfillmentController.js", "/opt/emr/apps/ui/app/orders/controllers/orderFulfillmentController.js"),
    ("apps/ui/app/orders/views/orderFulfillment.html", "/opt/emr/apps/ui/app/orders/views/orderFulfillment.html"),
    ("apps/ui/app/clinical/index.html", "/opt/emr/apps/ui/app/clinical/index.html"),
    ("apps/ui/app/clinical/dashboard/controllers/patientDashboardController.js", "/opt/emr/apps/ui/app/clinical/dashboard/controllers/patientDashboardController.js"),
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
    print(f"[*] Deploying Payment Configuration to {USER}@{HOST} ...")
    
    tar_path = os.path.join(REPO_ROOT, "scratch", "payment_deploy.tar.gz")
    with tarfile.open(tar_path, "w:gz") as tar:
        for rel_src, remote_dest in FILES_MAP:
            local_full = os.path.join(REPO_ROOT, rel_src.replace("/", os.sep))
            if not os.path.isfile(local_full):
                raise FileNotFoundError(f"Missing local file: {local_full}")
            tar.add(local_full, arcname=rel_src)
            print(f"  + Added {rel_src}")

    print("[*] Uploading package via pscp...")
    res = subprocess.run(
        ["pscp", "-batch", "-pw", PW, tar_path, f"{USER}@{HOST}:/tmp/payment_deploy.tar.gz"],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if res.returncode != 0:
        print(f"[!] Upload failed: {res.stderr}")
        return False

    remote_cmds = """
set -e
mkdir -p /tmp/payment_deploy
tar -xzf /tmp/payment_deploy.tar.gz -C /tmp/payment_deploy
"""
    for rel_src, remote_dest in FILES_MAP:
        remote_cmds += f"cp /tmp/payment_deploy/{rel_src} {remote_dest}\n"

    remote_cmds += """
find /opt/emr/apps/ui/app/admin -type d -exec chmod 755 {} +
find /opt/emr/apps/ui/app/admin -type f -exec chmod 644 {} +
find /opt/emr/apps/ui/app/orders -type d -exec chmod 755 {} +
find /opt/emr/apps/ui/app/orders -type f -exec chmod 644 {} +
find /opt/emr/apps/ui/app/clinical -type d -exec chmod 755 {} +
find /opt/emr/apps/ui/app/clinical -type f -exec chmod 644 {} +
find /opt/emr/config/openmrs/apps/admin -type f -exec chmod 644 {} +
chmod 755 /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py

systemctl daemon-reload
systemctl restart bahmni-backup.service

rm -rf /tmp/payment_deploy /tmp/payment_deploy.tar.gz
echo "PAYMENT_DEPLOY_SUCCESS"
"""
    script_local = os.path.join(REPO_ROOT, "scratch", "remote_payment_install.sh")
    with open(script_local, "w", encoding="utf-8", newline="\n") as f:
        f.write(remote_cmds)

    subprocess.run(["pscp", "-batch", "-pw", PW, script_local, f"{USER}@{HOST}:/tmp/remote_payment_install.sh"], check=True)
    rc, out, err = run_sudo("chmod +x /tmp/remote_payment_install.sh && /tmp/remote_payment_install.sh && rm -f /tmp/remote_payment_install.sh")
    print("Remote Install Output:\n", out)
    if err:
        print("Remote Install Stderr:\n", err)
    if rc != 0:
        return False

    time.sleep(2)
    print("\n=== VERIFICATION ===")
    rc, out, err = run_remote("curl -s http://127.0.0.1:5055/api/payment-config")
    print("Direct 5055 /api/payment-config:\n", out[:400])

    rc, out, err = run_remote("curl -k -s https://localhost/backup-api/payment-config")
    print("Proxy /backup-api/payment-config:\n", out[:400])

    rc, out, err = run_remote("curl -k -s -o /dev/null -w '%{http_code}' https://localhost/bahmni/admin/views/paymentConfig.html")
    print("paymentConfig.html HTTP code:", out.strip())

    rc, out, err = run_remote("curl -k -s https://localhost/bahmni_config/openmrs/apps/admin/extension.json | grep -A 8 '\"paymentConfig\"'")
    print("extension.json paymentConfig tile:\n", out.strip())

    return True

if __name__ == "__main__":
    main()
