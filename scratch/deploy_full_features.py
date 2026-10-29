import paramiko
import os
import json
import time

HOST = "196.189.94.149"
USER = "bmh"
PASS = "   "

print("Connecting to remote server via SSH/SFTP...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=30)
sftp = ssh.open_sftp()
print("Connected.")

# 1. Upload SQL files
sql_dir = r"C:\Users\COMPUTER\Documents\emr\config\masterdata\configuration\sql"
sql_files = {
    "opdRegister.sql": "emrapi.sqlSearch.opdRegister.sql",
    "icuRegister.sql": "emrapi.sqlSearch.icuRegister.sql",
    "liaisonRegister.sql": "emrapi.sqlSearch.liaisonRegister.sql",
    "admissionRegister.sql": "emrapi.sqlSearch.admissionRegister.sql",
}

for dest_name, src_file in sql_files.items():
    src_path = os.path.join(sql_dir, src_file)
    sftp.put(src_path, f"/tmp/{dest_name}")
    sftp.put(src_path, f"/opt/emr/config/masterdata/configuration/sql/{src_file}")
    print(f"Uploaded & Synced {src_file}")

# 2. Upload UI files to /opt/emr/apps/ui/app/register/
ui_root = r"C:\Users\COMPUTER\Documents\emr\apps\ui\app\register"
ui_files = [
    (r"controllers\registerController.js", "/opt/emr/apps/ui/app/register/controllers/registerController.js"),
    (r"services\registerService.js", "/opt/emr/apps/ui/app/register/services/registerService.js"),
    (r"services\ethiopianCalendarService.js", "/opt/emr/apps/ui/app/register/services/ethiopianCalendarService.js"),
    (r"views\register.html", "/opt/emr/apps/ui/app/register/views/register.html"),
    (r"styles\register.css", "/opt/emr/apps/ui/app/register/styles/register.css"),
    (r"app.js", "/opt/emr/apps/ui/app/register/app.js"),
    (r"index.html", "/opt/emr/apps/ui/app/register/index.html"),
]

for src_rel, dest_path in ui_files:
    src_full = os.path.join(ui_root, src_rel)
    sftp.put(src_full, dest_path)
    print(f"Uploaded UI: {src_rel} -> {dest_path}")

# 3. Create updater on remote to update OpenMRS Global Properties
remote_updater = """
import urllib.request, json, base64, ssl, os

files = {
    'emrapi.sqlSearch.opdRegisterV2': '/tmp/opdRegister.sql',
    'emrapi.sqlSearch.opdRegister': '/tmp/opdRegister.sql',
    'emrapi.sqlSearch.icuRegisterV2': '/tmp/icuRegister.sql',
    'emrapi.sqlSearch.icuRegister': '/tmp/icuRegister.sql',
    'emrapi.sqlSearch.liaisonRegisterV2': '/tmp/liaisonRegister.sql',
    'emrapi.sqlSearch.liaisonRegister': '/tmp/liaisonRegister.sql',
    'emrapi.sqlSearch.admissionRegisterV2': '/tmp/admissionRegister.sql',
    'emrapi.sqlSearch.admissionRegister': '/tmp/admissionRegister.sql',
}

auth = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Get existing system settings
req = urllib.request.Request("https://localhost/openmrs/ws/rest/v1/systemsetting?v=custom:(uuid,property)", headers={"Authorization": auth})
with urllib.request.urlopen(req, context=ctx) as resp:
    existing = json.load(resp).get("results", [])
prop_uuid = {item["property"]: item["uuid"] for item in existing if "property" in item and "uuid" in item}

for prop_name, file_path in files.items():
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    if prop_name in prop_uuid:
        uuid = prop_uuid[prop_name]
        url = f"https://localhost/openmrs/ws/rest/v1/systemsetting/{uuid}"
        payload = json.dumps({"value": sql}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "Authorization": auth})
        try:
            with urllib.request.urlopen(req, context=ctx) as r:
                print(f"Updated {prop_name} ({uuid}): {r.status}")
        except Exception as e:
            print(f"Update error {prop_name}: {e}")
    else:
        url = "https://localhost/openmrs/ws/rest/v1/systemsetting"
        payload = json.dumps({"property": prop_name, "value": sql}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "Authorization": auth})
        try:
            with urllib.request.urlopen(req, context=ctx) as r:
                print(f"Created {prop_name}: {r.status}")
        except Exception as e:
            print(f"Create error {prop_name}: {e}")
"""

with sftp.open("/tmp/run_update.py", "w") as f:
    f.write(remote_updater)
print("Uploaded /tmp/run_update.py")
sftp.close()

# 4. Execute updater on remote
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/run_update.py")
print("=== GP Update Output ===")
print(stdout.read().decode())
print(stderr.read().decode())

# 5. Quick verification of endpoints
verify_script = """
import urllib.request, json, base64, ssl

auth = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for q in ['emrapi.sqlSearch.opdRegisterV2', 'emrapi.sqlSearch.admissionRegisterV2']:
    url = f"https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q={q}"
    req = urllib.request.Request(url, headers={"Authorization": auth})
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            data = json.load(r)
            print(f"{q}: {len(data)} rows loaded!")
    except Exception as e:
        print(f"Error {q}: {e}")
"""

with ssh.open_sftp() as s:
    with s.open("/tmp/verify_quick.py", "w") as f:
        f.write(verify_script)

stdin, stdout, stderr = ssh.exec_command("python3 /tmp/verify_quick.py")
print("=== Verification Output ===")
print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()
print("Deployment completed successfully.")
