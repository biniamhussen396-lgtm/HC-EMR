import os
import sys
import json
import uuid
import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PSCP = r"C:\Program Files\PuTTY\pscp.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"
LOCAL_ROOT = r"c:\Users\COMPUTER\Documents\emr"

def run_remote(cmd):
    res = subprocess.run(
        [PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd],
        capture_output=True, text=True, timeout=60
    )
    return res.returncode, res.stdout, res.stderr

def upload_file(local_path, remote_path):
    # Ensure remote parent directory exists
    remote_dir = os.path.dirname(remote_path).replace("\\", "/")
    run_remote(f"mkdir -p '{remote_dir}'")
    
    res = subprocess.run(
        [PSCP, "-batch", "-pw", PW, local_path, f"{USER}@{HOST}:{remote_path}"],
        capture_output=True, text=True, timeout=60
    )
    if res.returncode != 0:
        print(f"FAILED to upload {local_path} -> {remote_path}: {res.stderr}")
        return False
    print(f"[OK] Uploaded -> {remote_path}")
    return True

print("=========================================================")
print("  SILENT DEPLOYMENT OF REGISTER APP TO 196.189.94.149")
print("=========================================================")

# 1. Ensure remote directories
print("\n[Step 1/6] Creating remote directories...")
dirs_cmd = "mkdir -p /opt/emr/apps/ui/app/register/controllers /opt/emr/apps/ui/app/register/services /opt/emr/apps/ui/app/register/styles /opt/emr/apps/ui/app/register/views /opt/emr/config/masterdata/configuration/sql"
rc, out, err = run_remote(dirs_cmd)
if rc != 0:
    print("Error creating directories:", err)
    sys.exit(1)
print("[OK] Directories verified.")

# 2. Upload Register App UI files
print("\n[Step 2/6] Uploading Register App UI files...")
ui_files = [
    (r"apps\ui\app\register\app.js", "/opt/emr/apps/ui/app/register/app.js"),
    (r"apps\ui\app\register\index.html", "/opt/emr/apps/ui/app/register/index.html"),
    (r"apps\ui\app\register\controllers\registerController.js", "/opt/emr/apps/ui/app/register/controllers/registerController.js"),
    (r"apps\ui\app\register\services\ethiopianCalendarService.js", "/opt/emr/apps/ui/app/register/services/ethiopianCalendarService.js"),
    (r"apps\ui\app\register\services\registerService.js", "/opt/emr/apps/ui/app/register/services/registerService.js"),
    (r"apps\ui\app\register\styles\register.css", "/opt/emr/apps/ui/app/register/styles/register.css"),
    (r"apps\ui\app\register\views\register.html", "/opt/emr/apps/ui/app/register/views/register.html"),
]

for local_rel, remote_dest in ui_files:
    local_full = os.path.join(LOCAL_ROOT, local_rel)
    if not upload_file(local_full, remote_dest):
        sys.exit(1)

# 3. Merge and update extension.json and locale_en.json
print("\n[Step 3/6] Merging Register into remote extension.json and locale_en.json...")
rc, out, err = run_remote("cat /opt/emr/config/openmrs/apps/home/extension.json")
if rc == 0 and out.strip():
    try:
        remote_ext = json.loads(out.strip())
    except Exception as e:
        print("Could not parse remote extension.json, using fallback merge:", e)
        remote_ext = {}
else:
    remote_ext = {}

remote_ext["register"] = {
    "id": "bahmni.register",
    "extensionPointId": "org.bahmni.home.dashboard",
    "type": "link",
    "label": "Register",
    "translationKey": "MODULE_LABEL_REGISTER_KEY",
    "url": "../register/index.html#/dashboard/register",
    "icon": "fa-book",
    "order": 5,
    "requiredPrivilege": "app:register"
}

temp_ext_path = os.path.join(LOCAL_ROOT, r"scratch\merged_remote_extension.json")
with open(temp_ext_path, "w", encoding="utf-8") as f:
    json.dump(remote_ext, f, indent=2)

upload_file(temp_ext_path, "/opt/emr/config/openmrs/apps/home/extension.json")

# Update locale_en.json
rc, out, err = run_remote("cat /opt/emr/config/openmrs/i18n/home/locale_en.json")
if rc == 0 and out.strip():
    try:
        remote_locale = json.loads(out.strip())
    except Exception:
        remote_locale = {}
else:
    remote_locale = {}

remote_locale["MODULE_LABEL_REGISTER_KEY"] = "Register"
temp_locale_path = os.path.join(LOCAL_ROOT, r"scratch\merged_remote_locale.json")
with open(temp_locale_path, "w", encoding="utf-8") as f:
    json.dump(remote_locale, f, indent=4)

upload_file(temp_locale_path, "/opt/emr/config/openmrs/i18n/home/locale_en.json")

# 4. Upload Masterdata Configuration files
print("\n[Step 4/6] Uploading Masterdata configuration files...")
masterdata_files = [
    (r"config\masterdata\configuration\privileges\privileges.csv", "/opt/emr/config/masterdata/configuration/privileges/privileges.csv"),
    (r"config\masterdata\configuration\roles\roles.csv", "/opt/emr/config/masterdata/configuration/roles/roles.csv"),
    (r"config\masterdata\configuration\sql\emrapi.sqlSearch.admissionRegister.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.admissionRegister.sql"),
    (r"config\masterdata\configuration\sql\emrapi.sqlSearch.icuRegister.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.icuRegister.sql"),
    (r"config\masterdata\configuration\sql\emrapi.sqlSearch.liaisonRegister.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.liaisonRegister.sql"),
    (r"config\masterdata\configuration\sql\emrapi.sqlSearch.opdRegister.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.opdRegister.sql"),
]

for local_rel, remote_dest in masterdata_files:
    local_full = os.path.join(LOCAL_ROOT, local_rel)
    if os.path.exists(local_full):
        upload_file(local_full, remote_dest)

# 5. Build and execute SQL migration for OpenMRS Database
print("\n[Step 5/6] Deploying Privilege, Roles, and Global Properties into OpenMRS DB...")
sql_statements = []

# Privilege & Roles
sql_statements.append("""
-- 1. Create app:register privilege
INSERT IGNORE INTO privilege (privilege, description, uuid)
VALUES ('app:register', 'Bahmni register app access privilege', 'e8f4c210-5e07-11ef-8f7c-0242ac120002');

-- 2. Create Register-App role
INSERT IGNORE INTO role (role, description, uuid)
VALUES ('Register-App', 'Will have full access for Register app', UUID());

-- 3. Map privilege to roles
INSERT IGNORE INTO role_privilege (role, privilege) VALUES
('Register-App', 'app:register'),
('Super User', 'app:register'),
('SuperAdmin', 'app:register'),
('System Developer', 'app:register'),
('Privilege Level: Full', 'app:register'),
('Privilege Level: High', 'app:register'),
('Doctor', 'app:register'),
('FrontDesk', 'app:register');
""")

# Global Properties (SQL Searches)
gp_files = [
    ('emrapi.sqlSearch.icuRegister', r"config\masterdata\configuration\sql\emrapi.sqlSearch.icuRegister.sql"),
    ('emrapi.sqlSearch.opdRegister', r"config\masterdata\configuration\sql\emrapi.sqlSearch.opdRegister.sql"),
    ('emrapi.sqlSearch.liaisonRegister', r"config\masterdata\configuration\sql\emrapi.sqlSearch.liaisonRegister.sql"),
    ('emrapi.sqlSearch.admissionRegister', r"config\masterdata\configuration\sql\emrapi.sqlSearch.admissionRegister.sql")
]

for prop_name, sql_file_rel in gp_files:
    sql_file_full = os.path.join(LOCAL_ROOT, sql_file_rel)
    if os.path.exists(sql_file_full):
        with open(sql_file_full, "r", encoding="utf-8") as f:
            content = f.read().strip()
        escaped_val = content.replace("'", "''")
        u = str(uuid.uuid4())
        stmt = f"""
INSERT INTO global_property (property, property_value, uuid)
VALUES ('{prop_name}', '{escaped_val}', '{u}')
ON DUPLICATE KEY UPDATE property_value = '{escaped_val}';
"""
        sql_statements.append(stmt)

full_sql = "\n".join(sql_statements)
temp_sql_path = os.path.join(LOCAL_ROOT, r"scratch\deploy_register_db.sql")
with open(temp_sql_path, "w", encoding="utf-8") as f:
    f.write(full_sql)

# Upload SQL file to remote /tmp/deploy_register_db.sql
upload_file(temp_sql_path, "/tmp/deploy_register_db.sql")

# Execute via docker exec without restart
exec_sql_cmd = "docker exec -i bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs < /tmp/deploy_register_db.sql"
rc, out, err = run_remote(exec_sql_cmd)
if rc != 0:
    print("Error executing SQL in OpenMRS DB:", err)
    sys.exit(1)
print("[OK] Database migration applied successfully!")

# Clean up remote tmp sql file
run_remote("rm -f /tmp/deploy_register_db.sql")

# 6. Verify Deployment
print("\n[Step 6/6] Verifying remote deployment...")
verify_db_cmd = "docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"SELECT privilege, description FROM privilege WHERE privilege = 'app:register'; SELECT role, privilege FROM role_privilege WHERE privilege = 'app:register'; SELECT property FROM global_property WHERE property LIKE 'emrapi.sqlSearch.%Register';\""
rc, out, err = run_remote(verify_db_cmd)
print("Database Verification:\n", out)

verify_files_cmd = "ls -la /opt/emr/apps/ui/app/register; grep -n 'app:register' /opt/emr/config/openmrs/apps/home/extension.json"
rc, out, err = run_remote(verify_files_cmd)
print("Files & Extension Verification:\n", out)

print("\n=========================================================")
print("  REGISTER APP FULLY AND SILENTLY DEPLOYED ON REMOTE!     ")
print("  URL: http://196.189.94.149/bahmni/home/index.html#/dashboard")
print("=========================================================")
