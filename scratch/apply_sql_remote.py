import paramiko
import os
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
ssh.connect(HOST, username=USER, password=PW, timeout=15)
print(f"[+] Connected to {HOST}")

def run_sudo(cmd):
    print(f"--> [CMD]: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(f"echo '{PW}' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out:
        print("STDOUT:\n" + out.strip())
    if err and "[sudo] password" not in err:
        print("STDERR:\n" + err.strip())
    return out.strip()

# 1. Upload SQL
local_tmp = os.path.join(REPO_ROOT, "scratch/apply_gp_clean.sql")
sftp = ssh.open_sftp()
sftp.put(local_tmp, "/tmp/apply_gp_clean.sql")
sftp.close()
print("[1] Uploaded /tmp/apply_gp_clean.sql to remote.")

# 2. Copy into openmrsdb container
run_sudo("docker cp /tmp/apply_gp_clean.sql bahmni-standard-openmrsdb-1:/tmp/apply_gp_clean.sql")

# 3. Execute inside container
run_sudo("docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e 'source /tmp/apply_gp_clean.sql'")

# 4. Check
res = run_sudo("docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"SELECT property, LENGTH(property_value) as val_len, uuid FROM global_property WHERE property = 'emrapi.sqlSearch.admissionRegister'\"")

# 5. Clean up
run_sudo("rm -f /tmp/apply_gp_clean.sql")
run_sudo("docker exec bahmni-standard-openmrsdb-1 rm -f /tmp/apply_gp_clean.sql")

ssh.close()
print("[+] SSH closed.")

# 6. Test REST API on remote
print("\n[6] Testing REST API on remote...")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

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
    print(f"  [OK] Remote SQL REST API returned {len(data)} inpatient records!")
    if len(data) > 0:
        first = data[0]
        print(f"  Sample Patient: ID={first.get('patient_identifier')}, Name={first.get('patient_name')}, Ward={first.get('ward_name')}, Status={first.get('admission_status')}")
except Exception as e:
    print(f"  [FAIL] Remote REST API test -> {e}")
