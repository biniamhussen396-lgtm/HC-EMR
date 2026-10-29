import os
import subprocess
import time

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PSCP = r"C:\Program Files\PuTTY\pscp.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

def run_remote(cmd):
    res = subprocess.run(
        [PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd],
        capture_output=True, text=True, timeout=60
    )
    return res.returncode, res.stdout, res.stderr

def upload_file(local_path, remote_path):
    res = subprocess.run(
        [PSCP, "-batch", "-pw", PW, local_path, f"{USER}@{HOST}:{remote_path}"],
        capture_output=True, text=True, timeout=60
    )
    if res.returncode != 0:
        print(f"FAILED to upload {local_path} -> {remote_path}: {res.stderr}")
        return False
    print(f"[OK] Uploaded -> {remote_path}")
    return True

print("=== Deploying Register App Updates to Remote Server ===")

# 1. Upload modified files
files_to_upload = [
    (r"apps\ui\app\register\services\ethiopianCalendarService.js", "/opt/emr/apps/ui/app/register/services/ethiopianCalendarService.js"),
    (r"apps\ui\app\register\services\registerService.js", "/opt/emr/apps/ui/app/register/services/registerService.js"),
    (r"apps\ui\app\register\controllers\registerController.js", "/opt/emr/apps/ui/app/register/controllers/registerController.js"),
    (r"apps\ui\app\register\views\register.html", "/opt/emr/apps/ui/app/register/views/register.html"),
    (r"config\masterdata\configuration\sql\emrapi.sqlSearch.opdRegister.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.opdRegister.sql"),
]

for loc, rem in files_to_upload:
    ok = upload_file(loc, rem)
    if not ok:
        print(f"Error uploading {loc}")

# 2. Upload SQL to /tmp on remote host, then copy into container and execute UPDATE
print("\n=== Updating OpenMRS global_property emrapi.sqlSearch.opdRegister ===")
upload_file(r"config\masterdata\configuration\sql\emrapi.sqlSearch.opdRegister.sql", "/tmp/opdRegister.sql")

update_cmd = """
docker cp /tmp/opdRegister.sql bahmni-standard-openmrsdb-1:/tmp/opdRegister.sql && \
docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "
UPDATE global_property 
SET property_value = LOAD_FILE('/tmp/opdRegister.sql')
WHERE property = 'emrapi.sqlSearch.opdRegister';
"
"""
rc, out, err = run_remote(update_cmd)
print("Update DB result:", rc, out, err)

# 3. Verify query execution directly from global_property
print("\n=== Verifying query from global_property ===")
verify_cmd = """docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "
SET @sql = (SELECT property_value FROM global_property WHERE property = 'emrapi.sqlSearch.opdRegister');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
" | head -n 5"""

t0 = time.time()
rc, out, err = run_remote(verify_cmd)
t1 = time.time()
print(f"Verification completed in {t1-t0:.2f}s (RC={rc}):")
print(out)

print("=== Deployment finished! ===")
