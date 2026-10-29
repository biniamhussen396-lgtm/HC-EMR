import subprocess
import paramiko
import os
import ssl
import urllib.request
import base64
import json
import time

REPO_ROOT = r'c:\Users\COMPUTER\Documents\emr'
sql_file = os.path.join(REPO_ROOT, "config/masterdata/configuration/sql/emrapi.sqlSearch.admissionRegister.sql")
with open(sql_file, "r", encoding="utf-8") as f:
    sql_text = f.read().strip()

escaped_sql = sql_text.replace("\\", "\\\\").replace("'", "\\'")

apply_sql = f"""
DELETE FROM global_property WHERE property = 'emrapi.sqlSearch.admissionRegister';
INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.admissionRegister', '{escaped_sql}', 'Ethiopian MOH Inpatient Admission and Discharge Register Search Query', UUID());
"""

# 1. Update LOCAL MySQL
print("[1] Updating local MySQL...")
tmp_local_sql = os.path.join(REPO_ROOT, "scratch/apply_local_temp.sql")
with open(tmp_local_sql, "w", encoding="utf-8") as f:
    f.write(apply_sql)

p = subprocess.run([
    "docker", "exec", "-i", "bahmni-standard-openmrsdb-1",
    "mysql", "-uroot", "-padminAdmin!123", "openmrs"
], input=apply_sql, text=True, capture_output=True, encoding="utf-8")
print("Local MySQL result:", p.returncode, p.stderr)

# 2. Update REMOTE MySQL via SSH
print("[2] Updating remote MySQL on 192.168.10.5...")
HOST = '192.168.10.5'
USER = 'bmh'
PW = '   '

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PW, timeout=20)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '{PW}' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out.strip()

sftp = ssh.open_sftp()
sftp.put(tmp_local_sql, "/tmp/apply_remote_temp.sql")
sftp.close()

run_sudo("docker cp /tmp/apply_remote_temp.sql bahmni-standard-openmrsdb-1:/tmp/apply_remote_temp.sql")
out_sql = run_sudo("docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e 'source /tmp/apply_remote_temp.sql'")
print("Remote MySQL exec:", out_sql)

out_len = run_sudo("docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"SELECT property, LENGTH(property_value) as val_len FROM global_property WHERE property = 'emrapi.sqlSearch.admissionRegister';\"")
print("Remote DB property check:\n", out_len)

run_sudo("rm -f /tmp/apply_remote_temp.sql")
run_sudo("docker exec bahmni-standard-openmrsdb-1 rm -f /tmp/apply_remote_temp.sql")
ssh.close()
print("[+] SSH closed.")

# 3. Test Local REST API
print("\n[3] Testing Local REST API (http://localhost:8186)...")
local_api = "http://localhost:8186/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.admissionRegister"
auth = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")
try:
    req = urllib.request.Request(local_api, headers={'Authorization': auth})
    t0 = time.time()
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode('utf-8'))
    t1 = time.time()
    print(f"  [OK] Local REST API returned {len(data)} records in {t1-t0:.2f}s!")
except Exception as e:
    print(f"  [FAIL] Local REST API -> {e}")

# 4. Test Remote REST API
print("\n[4] Testing Remote REST API (https://192.168.10.5)...")
remote_api = "https://192.168.10.5/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.admissionRegister"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    req = urllib.request.Request(remote_api, headers={'Authorization': auth})
    t0 = time.time()
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    data = json.loads(resp.read().decode('utf-8'))
    t1 = time.time()
    print(f"  [OK] Remote REST API returned {len(data)} records in {t1-t0:.2f}s!")
    if len(data) > 0:
        first = data[0]
        print(f"  Sample record: ID={first.get('mrn')}, Name={first.get('patient_name')}, Ward={first.get('ward_name')}, Status={first.get('status')}")
except Exception as e:
    print(f"  [FAIL] Remote REST API -> {e}")

print("\n=== Verification Complete ===")
