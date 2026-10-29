import os
import tarfile
import subprocess
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

print("=== STEP 1: PREPARE APPOINTMENTS FRONTEND TARBALL WITH BRAND FAVICON ===")
app_dir = os.path.join(REPO_ROOT, "scratch", "local_appointments_app")
tar_path = os.path.join(REPO_ROOT, "scratch", "appointments_frontend_deploy.tar.gz")

if os.path.exists(tar_path):
    os.remove(tar_path)

with tarfile.open(tar_path, "w:gz") as tar:
    for root, dirs, files in os.walk(app_dir):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, app_dir).replace("\\", "/")
            tar.add(full_path, arcname=rel_path)

print(f"Created frontend tarball: {tar_path} ({os.path.getsize(tar_path)} bytes)")

print("\n=== STEP 2: UPLOAD FRONTEND TARBALL AND OPENMRS MODULE ===")
# Upload frontend tarball
res = subprocess.run(
    ["pscp", "-batch", "-pw", PW, tar_path, f"{USER}@{HOST}:/tmp/appointments_frontend_deploy.tar.gz"],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
if res.returncode != 0:
    print("Failed to upload frontend tarball:", res.stderr)
    exit(1)
print("Uploaded frontend tarball to /tmp/appointments_frontend_deploy.tar.gz")

# Upload appointments-2.1.0.omod
omod_path = os.path.join(REPO_ROOT, "scratch", "appointments-2.1.0.omod")
res = subprocess.run(
    ["pscp", "-batch", "-pw", PW, omod_path, f"{USER}@{HOST}:/tmp/appointments-2.1.0.omod"],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
if res.returncode != 0:
    print("Failed to upload appointments-2.1.0.omod:", res.stderr)
    exit(1)
print("Uploaded appointments-2.1.0.omod to /tmp/appointments-2.1.0.omod")

# Upload brand favicon.ico
fav_path = os.path.join(REPO_ROOT, "apps", "ui", "app", "favicon.ico")
res = subprocess.run(
    ["pscp", "-batch", "-pw", PW, fav_path, f"{USER}@{HOST}:/tmp/brand_favicon.ico"],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
if res.returncode != 0:
    print("Failed to upload favicon.ico:", res.stderr)
    exit(1)
print("Uploaded brand favicon to /tmp/brand_favicon.ico")

print("\n=== STEP 3: DEPLOY FRONTEND APP INTO APPOINTMENTS CONTAINER ===")
deploy_frontend_cmd = """
set -e
mkdir -p /tmp/appointments_extract
tar -xzf /tmp/appointments_frontend_deploy.tar.gz -C /tmp/appointments_extract

# Copy into appointments container
docker exec bahmni-standard-appointments-1 mkdir -p /usr/local/apache2/htdocs/appointments/backup_original
docker cp /tmp/appointments_extract/. bahmni-standard-appointments-1:/usr/local/apache2/htdocs/appointments/

# Copy brand favicon explicitly into appointments root and htdocs root
docker cp /tmp/brand_favicon.ico bahmni-standard-appointments-1:/usr/local/apache2/htdocs/appointments/favicon.ico
docker cp /tmp/brand_favicon.ico bahmni-standard-appointments-1:/usr/local/apache2/htdocs/favicon.ico

# Set permissions inside appointments container
docker exec bahmni-standard-appointments-1 chmod -R 755 /usr/local/apache2/htdocs/appointments
docker exec bahmni-standard-appointments-1 chmod 644 /usr/local/apache2/htdocs/appointments/favicon.ico

# Also ensure bahmni web has brand favicon
docker cp /tmp/brand_favicon.ico bahmni-standard-bahmni-web-1:/usr/local/apache2/htdocs/bahmni/favicon.ico 2>/dev/null || true

rm -rf /tmp/appointments_extract /tmp/appointments_frontend_deploy.tar.gz
echo "Frontend deployment complete."
"""

rc, out, err = run_sudo(deploy_frontend_cmd)
print("FRONTEND DEPLOY OUT:\n", out)
if err and "password" not in err.lower():
    print("FRONTEND DEPLOY ERR:\n", err)

print("\n=== STEP 4: DEPLOY OPENMRS MODULE APPOINTMENTS-2.1.0.OMOD ===")
deploy_module_cmd = """
set -e
# Backup old module and copy new one
docker exec bahmni-standard-openmrs-1 mkdir -p /openmrs/data/modules/backup
docker exec bahmni-standard-openmrs-1 cp /openmrs/data/modules/appointments-*.omod /openmrs/data/modules/backup/ 2>/dev/null || true
docker exec bahmni-standard-openmrs-1 rm -f /openmrs/data/modules/appointments-2.0.2.omod

# Copy new omod into modules
docker cp /tmp/appointments-2.1.0.omod bahmni-standard-openmrs-1:/openmrs/data/modules/appointments-2.1.0.omod
docker exec bahmni-standard-openmrs-1 chmod 644 /openmrs/data/modules/appointments-2.1.0.omod

# Also backup and extract into .openmrs-lib-cache/appointments
docker exec bahmni-standard-openmrs-1 rm -rf /openmrs/data/.openmrs-lib-cache/appointments/backup 2>/dev/null || true
docker exec bahmni-standard-openmrs-1 mkdir -p /openmrs/data/.openmrs-lib-cache/appointments/backup
docker exec bahmni-standard-openmrs-1 cp -r /openmrs/data/.openmrs-lib-cache/appointments/appointments.jar /openmrs/data/.openmrs-lib-cache/appointments/backup/ 2>/dev/null || true

# Extract new omod directly into /openmrs/data/.openmrs-lib-cache/appointments/
docker exec bahmni-standard-openmrs-1 unzip -o /openmrs/data/modules/appointments-2.1.0.omod -d /openmrs/data/.openmrs-lib-cache/appointments/
docker exec bahmni-standard-openmrs-1 chmod -R 755 /openmrs/data/.openmrs-lib-cache/appointments/

rm -f /tmp/appointments-2.1.0.omod /tmp/brand_favicon.ico
echo "Module file replacement complete."
"""

rc, out, err = run_sudo(deploy_module_cmd)
print("MODULE DEPLOY OUT:\n", out)
if err and "password" not in err.lower():
    print("MODULE DEPLOY ERR:\n", err)

print("\n=== STEP 5: RESTART OPENMRS CONTAINER TO INITIALIZE MODULE ===")
rc, out, err = run_sudo("docker restart bahmni-standard-openmrs-1")
print("OPENMRS RESTART OUT:\n", out)

print("\n=== STEP 6: WAIT FOR OPENMRS TO BE READY AND VERIFY ===")
for attempt in range(24): # wait up to 120s
    time.sleep(5)
    rc, out, err = run_remote("curl -k -s -o /dev/null -w '%{http_code}' https://127.0.0.1/openmrs/ws/rest/v1/session")
    code = out.strip()
    print(f"Attempt {attempt+1}: Session HTTP status = {code}")
    if code == "200":
        break

print("\n=== STEP 7: VERIFY ALL APPOINTMENT ENDPOINTS & FAVICON ===")
# 1. Check speciality/all API
rc, out, err = run_remote("curl -k -s -u admin:Admin123 https://127.0.0.1/openmrs/ws/appointmentsApi/speciality/all")
print("SPECIALITY/ALL API RESPONSE:\n", out[:400])

# 2. Check appointments module version
rc, out, err = run_remote("curl -k -s -u admin:Admin123 https://127.0.0.1/openmrs/ws/rest/v1/module/appointments?v=custom:(uuid,version,started)")
print("APPOINTMENTS MODULE VERSION:\n", out)

# 3. Check frontend index.html HTTP status
rc, out, err = run_remote("curl -k -s -o /dev/null -w '%{http_code}' https://127.0.0.1/appointments/")
print("APPOINTMENTS FRONTEND HTTP STATUS:", out.strip())

# 4. Check speciality-admin.html HTTP status
rc, out, err = run_remote("curl -k -s -o /dev/null -w '%{http_code}' https://127.0.0.1/appointments/speciality-admin.html")
print("SPECIALITY-ADMIN HTTP STATUS:", out.strip())

# 5. Check provider-admin.html HTTP status
rc, out, err = run_remote("curl -k -s -o /dev/null -w '%{http_code}' https://127.0.0.1/appointments/provider-admin.html")
print("PROVIDER-ADMIN HTTP STATUS:", out.strip())

# 6. Check favicon.ico HTTP status & size
rc, out, err = run_remote("curl -k -s -w '%{size_download}' -o /dev/null https://127.0.0.1/appointments/favicon.ico")
print("FAVICON DOWNLOAD SIZE (should be 6752):", out.strip())
