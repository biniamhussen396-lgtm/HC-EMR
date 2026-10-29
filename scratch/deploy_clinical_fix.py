import os
import tarfile
import subprocess
import time

REPO_ROOT = r"c:\Users\COMPUTER\Documents\emr"
HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

FILES_MAP = [
    ("apps/ui/app/common/util/httpErrorInterceptor.js", "/opt/emr/apps/ui/app/common/util/httpErrorInterceptor.js"),
    ("apps/ui/app/clinical/app.js", "/opt/emr/apps/ui/app/clinical/app.js"),
    ("apps/ui/app/clinical/index.html", "/opt/emr/apps/ui/app/clinical/index.html"),
    ("apps/ui/app/clinical/consultation/views/orders.html", "/opt/emr/apps/ui/app/clinical/consultation/views/orders.html"),
    ("apps/ui/app/clinical/consultation/controllers/orderController.js", "/opt/emr/apps/ui/app/clinical/consultation/controllers/orderController.js"),
    ("apps/ui/app/clinical/consultation/controllers/investigationController.js", "/opt/emr/apps/ui/app/clinical/consultation/controllers/investigationController.js"),
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
    print(f"[*] Packaging files for deployment to {HOST}...")
    tar_path = os.path.join(REPO_ROOT, "scratch", "clinical_fix_deploy.tar.gz")
    with tarfile.open(tar_path, "w:gz") as tar:
        for rel_src, remote_dest in FILES_MAP:
            local_full = os.path.join(REPO_ROOT, rel_src.replace("/", os.sep))
            if not os.path.isfile(local_full):
                raise FileNotFoundError(f"Missing local file: {local_full}")
            tar.add(local_full, arcname=rel_src)
            print(f"  + Added {rel_src} ({os.path.getsize(local_full)} bytes)")

    print(f"[*] Uploading archive to {HOST}:/tmp/clinical_fix_deploy.tar.gz ...")
    res = subprocess.run(
        ["pscp", "-batch", "-pw", PW, tar_path, f"{USER}@{HOST}:/tmp/clinical_fix_deploy.tar.gz"],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if res.returncode != 0:
        print(f"[!] Upload failed: {res.stderr}")
        return False
    print("[OK] Upload successful")

    remote_script = """#!/bin/bash
set -e
echo "[1/4] Extracting archive..."
rm -rf /tmp/clinical_fix_deploy
mkdir -p /tmp/clinical_fix_deploy
tar -xzf /tmp/clinical_fix_deploy.tar.gz -C /tmp/clinical_fix_deploy

echo "[2/4] Deploying files to /opt/emr/..."
cp /tmp/clinical_fix_deploy/apps/ui/app/common/util/httpErrorInterceptor.js /opt/emr/apps/ui/app/common/util/httpErrorInterceptor.js
cp /tmp/clinical_fix_deploy/apps/ui/app/clinical/app.js /opt/emr/apps/ui/app/clinical/app.js
cp /tmp/clinical_fix_deploy/apps/ui/app/clinical/index.html /opt/emr/apps/ui/app/clinical/index.html
cp /tmp/clinical_fix_deploy/apps/ui/app/clinical/consultation/views/orders.html /opt/emr/apps/ui/app/clinical/consultation/views/orders.html
cp /tmp/clinical_fix_deploy/apps/ui/app/clinical/consultation/controllers/orderController.js /opt/emr/apps/ui/app/clinical/consultation/controllers/orderController.js
cp /tmp/clinical_fix_deploy/apps/ui/app/clinical/consultation/controllers/investigationController.js /opt/emr/apps/ui/app/clinical/consultation/controllers/investigationController.js

echo "[3/4] Setting permissions..."
chmod 644 /opt/emr/apps/ui/app/common/util/httpErrorInterceptor.js
chmod 644 /opt/emr/apps/ui/app/clinical/app.js
chmod 644 /opt/emr/apps/ui/app/clinical/index.html
chmod 644 /opt/emr/apps/ui/app/clinical/consultation/views/orders.html
chmod 644 /opt/emr/apps/ui/app/clinical/consultation/controllers/orderController.js
chmod 644 /opt/emr/apps/ui/app/clinical/consultation/controllers/investigationController.js

echo "[4/4] Verifying content in bahmni-web container..."
docker exec bahmni-standard-bahmni-web-1 grep -n "openelis" /usr/local/apache2/htdocs/bahmni/common/util/httpErrorInterceptor.js
docker exec bahmni-standard-bahmni-web-1 grep -n "ignoreErrors" /usr/local/apache2/htdocs/bahmni/clinical/consultation/controllers/orderController.js
echo "DEPLOYMENT COMPLETE!"
"""

    script_path = os.path.join(REPO_ROOT, "scratch", "remote_clinical_install.sh")
    with open(script_path, "w", newline="\n", encoding="utf-8") as f:
        f.write(remote_script)

    print(f"[*] Uploading install script...")
    res = subprocess.run(
        ["pscp", "-batch", "-pw", PW, script_path, f"{USER}@{HOST}:/tmp/remote_clinical_install.sh"],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if res.returncode != 0:
        print(f"[!] Upload of script failed: {res.stderr}")
        return False

    print(f"[*] Executing install script with sudo...")
    rc, stdout, stderr = run_sudo("chmod +x /tmp/remote_clinical_install.sh && /tmp/remote_clinical_install.sh")
    print("STDOUT:\n", stdout)
    if rc != 0:
        print("STDERR:\n", stderr)
        return False

    print("[SUCCESS] Files deployed and active!")
    return True

if __name__ == "__main__":
    main()
