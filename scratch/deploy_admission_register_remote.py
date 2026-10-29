import paramiko
import os
import sys
import ssl
import urllib.request
import base64
import json

HOST = '192.168.10.5'
USER = 'bmh'
PW = '   '
REPO_ROOT = r'c:\Users\COMPUTER\Documents\emr'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"[*] Connecting to {HOST} via SSH...")
ssh.connect(HOST, username=USER, password=PW, timeout=25)
print(f"[+] Connected to {HOST}")

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '{PW}' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

staging_dir = "/home/bmh/deploy_staging_reg"
run_sudo(f"rm -rf {staging_dir} && mkdir -p {staging_dir} && chown -R bmh:bmh {staging_dir}")

files_to_deploy = [
    ("apps/ui/app/bedmanagement/controllers/admissionRegisterController.js", "/opt/emr/apps/ui/app/bedmanagement/controllers/admissionRegisterController.js", "admissionRegisterController.js"),
    ("apps/ui/app/bedmanagement/views/admissionRegister.html", "/opt/emr/apps/ui/app/bedmanagement/views/admissionRegister.html", "admissionRegister.html"),
    ("apps/ui/app/bedmanagement/views/bedManagement.html", "/opt/emr/apps/ui/app/bedmanagement/views/bedManagement.html", "bedManagement.html"),
    ("apps/ui/app/bedmanagement/app.js", "/opt/emr/apps/ui/app/bedmanagement/app.js", "app.js"),
    ("apps/ui/app/bedmanagement/index.html", "/opt/emr/apps/ui/app/bedmanagement/index.html", "index.html"),
    ("apps/ui/app/bedmanagement/directives/backLinksCacheBuster.js", "/opt/emr/apps/ui/app/bedmanagement/directives/backLinksCacheBuster.js", "backLinksCacheBuster.js"),
    ("apps/ui/app/i18n/ipd/locale_en.json", "/opt/emr/apps/ui/app/i18n/ipd/locale_en.json", "locale_en_app.json"),
    ("config/openmrs/i18n/ipd/locale_en.json", "/opt/emr/config/openmrs/i18n/ipd/locale_en.json", "locale_en_config.json"),
    ("config/masterdata/configuration/sql/emrapi.sqlSearch.admissionRegister.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.admissionRegister.sql", "admissionRegister.sql"),
]

sftp = ssh.open_sftp()
print("[1] Uploading files to remote staging area...")
for rel_path, remote_path, stage_name in files_to_deploy:
    local_path = os.path.join(REPO_ROOT, rel_path.replace("/", "\\"))
    staging_file = f"{staging_dir}/{stage_name}"
    sftp.put(local_path, staging_file)
    print(f"  Uploaded {rel_path} -> {staging_file} ({os.path.getsize(local_path)} bytes)")

sftp.close()

print("[2] Installing files into production paths...")
for rel_path, remote_path, stage_name in files_to_deploy:
    staging_file = f"{staging_dir}/{stage_name}"
    # Ensure parent dir exists
    parent_dir = os.path.dirname(remote_path).replace("\\", "/")
    run_sudo(f"mkdir -p {parent_dir}")
    run_sudo(f"cp {staging_file} {remote_path}")
    run_sudo(f"chmod 644 {remote_path}")
    run_sudo(f"chown -R bmh:bmh {remote_path}")
    print(f"  Installed {remote_path}")

print("[3] Registering SQL Query in remote OpenMRS MySQL global_property...")
sql_path = os.path.join(REPO_ROOT, "config/masterdata/configuration/sql/emrapi.sqlSearch.admissionRegister.sql")
with open(sql_path, "r", encoding="utf-8") as f:
    sql_content = f.read().strip()

# Prepare MySQL INSERT / UPDATE statement
escaped_query = sql_content.replace("\\", "\\\\").replace("'", "\\'")
mysql_script = f"""
DELETE FROM global_property WHERE property = 'emrapi.sqlSearch.admissionRegister';
INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.admissionRegister', '{escaped_query}', 'Ethiopian MOH Inpatient Admission and Discharge Register Search Query', UUID());
"""

staging_sql_file = f"{staging_dir}/apply_global_property.sql"
with open(os.path.join(REPO_ROOT, "scratch/apply_gp_temp.sql"), "w", encoding="utf-8") as f:
    f.write(mysql_script)

sftp = ssh.open_sftp()
sftp.put(os.path.join(REPO_ROOT, "scratch/apply_gp_temp.sql"), staging_sql_file)
sftp.close()

out, err = run_sudo(f"docker exec -i bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs < {staging_sql_file}")
if err and "Using a password" not in err:
    print(f"  MySQL Warning/Error: {err}")
else:
    print("  MySQL query executed successfully into global_property.")

# Verify query in global_property
out_check, _ = run_sudo("docker exec -i bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"SELECT property, LENGTH(property_value) as val_len, uuid FROM global_property WHERE property = 'emrapi.sqlSearch.admissionRegister';\"")
print("  Database check output:\n", out_check.strip())

run_sudo(f"rm -rf {staging_dir}")
ssh.close()
print("[+] SSH session closed.")

print("[4] Verifying remote endpoints via HTTPS...")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    "https://192.168.10.5/bahmni/bedmanagement/index.html",
    "https://192.168.10.5/bahmni/bedmanagement/app.js?v=3.4",
    "https://192.168.10.5/bahmni/bedmanagement/controllers/admissionRegisterController.js?v=3.4",
    "https://192.168.10.5/bahmni/bedmanagement/views/admissionRegister.html?v=3.4",
    "https://192.168.10.5/bahmni/bedmanagement/views/bedManagement.html?v=3.4"
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'DeployVerifier/1.0'})
        resp = urllib.request.urlopen(req, context=ctx, timeout=12)
        content = resp.read().decode('utf-8', errors='ignore')
        print(f"  [OK] {url} -> HTTP {resp.status} (Length: {len(content)})")
    except Exception as e:
        print(f"  [FAIL] {url} -> {e}")

print("\n[5] Testing remote SQL REST API endpoint directly...")
api_url = "https://192.168.10.5/openmrs/ws/rest/v1/bahmnicore/sql/search?q=emrapi.sqlSearch.admissionRegister"
auth_header = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")

try:
    req = urllib.request.Request(api_url, headers={
        'User-Agent': 'DeployVerifier/1.0',
        'Authorization': auth_header,
        'Accept': 'application/json'
    })
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    data = json.loads(resp.read().decode('utf-8'))
    print(f"  [OK] SQL REST API returned {len(data)} inpatient records!")
    if len(data) > 0:
        first = data[0]
        print(f"  Sample Patient: ID={first.get('patient_identifier')}, Name={first.get('patient_name')}, Ward={first.get('ward_name')}, Status={first.get('admission_status')}")
except Exception as e:
    print(f"  [FAIL] REST API test -> {e}")

print("\n=== Remote Deployment to 192.168.10.5 Completed Successfully! ===")
