import os
import tarfile
import subprocess
import json
import time

REPO_ROOT = r"c:\Users\COMPUTER\Documents\emr"
HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

def run_remote(cmd):
    res = subprocess.run(
        ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return res.returncode, res.stdout, res.stderr

def run_sudo(cmd):
    wrapped = f"echo '{PW}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    return run_remote(wrapped)

print("=== STEP 1: PREPARE REMOTE DASHBOARD.JSON WITHOUT PACS ===")
with open(os.path.join(REPO_ROOT, "scratch", "remote_dashboard.json"), "r", encoding="utf-8") as f:
    rem_data = json.load(f)

if "pacs" in rem_data.get("general", {}).get("sections", {}):
    del rem_data["general"]["sections"]["pacs"]
    print("SUCCESS: 'pacs' removed from general sections in remote dashboard data.")
else:
    print("NOTE: 'pacs' was not present in general sections.")

clean_dashboard_path = os.path.join(REPO_ROOT, "scratch", "clean_remote_dashboard.json")
with open(clean_dashboard_path, "w", encoding="utf-8") as f:
    json.dump(rem_data, f, indent=4)
print(f"Saved cleaned dashboard.json to {clean_dashboard_path}")

print("\n=== STEP 2: BUILD TARBALL FOR DEPLOYMENT ===")
tar_path = os.path.join(REPO_ROOT, "scratch", "remote_deploy_pacs_ref.tar.gz")
if os.path.exists(tar_path):
    os.remove(tar_path)

with tarfile.open(tar_path, "w:gz") as tar:
    # 1. Clean dashboard.json
    tar.add(clean_dashboard_path, arcname="dashboard.json")
    
    # 2. Header views (AI Assistant removed)
    tar.add(
        os.path.join(REPO_ROOT, "apps", "ui", "app", "clinical", "dashboard", "views", "clinicalDashboardHeader.html"),
        arcname="clinicalDashboardHeader.html"
    )
    tar.add(
        os.path.join(REPO_ROOT, "apps", "ui", "app", "common", "ui-helper", "header.html"),
        arcname="header.html"
    )
    
    # 3. Clinical Reference App
    cr_dir = os.path.join(REPO_ROOT, "apps", "ui", "app", "clinical-reference")
    for root, dirs, files in os.walk(cr_dir):
        for file in files:
            full_f = os.path.join(root, file)
            rel_f = os.path.relpath(full_f, cr_dir)
            arc_name = os.path.join("clinical-reference", rel_f).replace("\\", "/")
            tar.add(full_f, arcname=arc_name)

print(f"Tarball created successfully: {os.path.getsize(tar_path)} bytes")

print("\n=== STEP 3: UPLOAD TARBALL TO REMOTE SERVER ===")
res = subprocess.run(
    ["pscp", "-batch", "-pw", PW, tar_path, f"{USER}@{HOST}:/tmp/remote_deploy_pacs_ref.tar.gz"],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
if res.returncode != 0:
    print(f"ERROR uploading tarball: {res.stderr}")
    exit(1)
print("Uploaded tarball to /tmp/remote_deploy_pacs_ref.tar.gz")

print("\n=== STEP 4: EXTRACT AND INSTALL ON REMOTE HOST ===")
install_cmd = """
set -e
mkdir -p /tmp/deploy_extract
tar -xzf /tmp/remote_deploy_pacs_ref.tar.gz -C /tmp/deploy_extract

# Backup dashboard.json
cp /opt/emr/config/openmrs/apps/clinical/dashboard.json /opt/emr/config/openmrs/apps/clinical/dashboard.json.bak_pacs
# Copy clean dashboard.json
cp /tmp/deploy_extract/dashboard.json /opt/emr/config/openmrs/apps/clinical/dashboard.json
chmod 644 /opt/emr/config/openmrs/apps/clinical/dashboard.json
chown 1000:1000 /opt/emr/config/openmrs/apps/clinical/dashboard.json 2>/dev/null || true

# Backup and copy headers
cp /opt/emr/apps/ui/app/clinical/dashboard/views/clinicalDashboardHeader.html /opt/emr/apps/ui/app/clinical/dashboard/views/clinicalDashboardHeader.html.bak_ai
cp /tmp/deploy_extract/clinicalDashboardHeader.html /opt/emr/apps/ui/app/clinical/dashboard/views/clinicalDashboardHeader.html
chmod 644 /opt/emr/apps/ui/app/clinical/dashboard/views/clinicalDashboardHeader.html
chown 1000:1000 /opt/emr/apps/ui/app/clinical/dashboard/views/clinicalDashboardHeader.html 2>/dev/null || true

cp /opt/emr/apps/ui/app/common/ui-helper/header.html /opt/emr/apps/ui/app/common/ui-helper/header.html.bak_ai
cp /tmp/deploy_extract/header.html /opt/emr/apps/ui/app/common/ui-helper/header.html
chmod 644 /opt/emr/apps/ui/app/common/ui-helper/header.html
chown 1000:1000 /opt/emr/apps/ui/app/common/ui-helper/header.html 2>/dev/null || true

# Deploy clinical-reference folder
mkdir -p /opt/emr/apps/ui/app/clinical-reference
cp -r /tmp/deploy_extract/clinical-reference/* /opt/emr/apps/ui/app/clinical-reference/
chmod -R 755 /opt/emr/apps/ui/app/clinical-reference
chown -R 1000:1000 /opt/emr/apps/ui/app/clinical-reference 2>/dev/null || true

rm -rf /tmp/deploy_extract /tmp/remote_deploy_pacs_ref.tar.gz
"""

rc, out, err = run_sudo(install_cmd)
print("INSTALL RC:", rc)
print("INSTALL OUT:\n", out)
if err and "password" not in err.lower():
    print("INSTALL ERR:\n", err)

print("\n=== STEP 5: VERIFY DEPLOYMENT ON REMOTE SERVER ===")
# 1. Verify pacs is gone
rc, out, err = run_remote('grep -n "pacs" /opt/emr/config/openmrs/apps/clinical/dashboard.json || true')
print("PACS IN DASHBOARD.JSON (should be empty):", out.strip())

# 2. Verify AI Assistant is gone
rc, out, err = run_remote('grep -n "AI Assistant" /opt/emr/apps/ui/app/clinical/dashboard/views/clinicalDashboardHeader.html /opt/emr/apps/ui/app/common/ui-helper/header.html 2>/dev/null || true')
print("AI ASSISTANT IN HEADERS (should be empty):", out.strip())

# 3. Verify clinical-reference files exist
rc, out, err = run_remote('ls -la /opt/emr/apps/ui/app/clinical-reference')
print("CLINICAL-REFERENCE DIRECTORY:\n", out)

# 4. Verify HTTP access via curl on remote server
rc, out, err = run_remote('curl -k -s -o /dev/null -w "%{http_code}" https://127.0.0.1/bahmni/clinical-reference/index.html')
print("HTTP STATUS FOR clinical-reference/index.html:", out.strip())
