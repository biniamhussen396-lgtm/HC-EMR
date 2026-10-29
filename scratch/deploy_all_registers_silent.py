import os
import sys
import ssl
import time
import json
import base64
import urllib.request
import paramiko

HOST = "196.189.94.149"
USER = "bmh"
PW = "   "
LOCAL_ROOT = r"C:\Users\COMPUTER\Documents\emr"

def get_ssh():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PW, timeout=25)
    return client

def run_sudo(ssh, cmd):
    print(f"--> [CMD]: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(f"echo '{PW}' | sudo -S bash -c \"{cmd}\"")
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print("    STDOUT:", out[:300] + ("..." if len(out) > 300 else ""))
    if err and "[sudo] password" not in err:
        print("    STDERR:", err[:300] + ("..." if len(err) > 300 else ""))
    return out

def ensure_remote_dir(sftp, remote_path):
    parts = remote_path.replace("\\", "/").strip("/").split("/")
    cur = ""
    for part in parts:
        cur += "/" + part
        try:
            sftp.stat(cur)
        except IOError:
            try:
                sftp.mkdir(cur)
            except Exception:
                pass

def deploy():
    print("=" * 60)
    print(f"SILENT DEPLOYMENT OF BAHMNI REGISTERS TO {HOST}")
    print("=" * 60)

    ssh = get_ssh()
    sftp = ssh.open_sftp()
    print("[1] Connected via SSH & SFTP.")

    # 1. Deploy UI files
    print("\n[2] Deploying Register UI App...")
    ui_files = [
        ("apps/ui/app/register/app.js", "/opt/emr/apps/ui/app/register/app.js"),
        ("apps/ui/app/register/index.html", "/opt/emr/apps/ui/app/register/index.html"),
        ("apps/ui/app/register/controllers/registerController.js", "/opt/emr/apps/ui/app/register/controllers/registerController.js"),
        ("apps/ui/app/register/services/ethiopianCalendarService.js", "/opt/emr/apps/ui/app/register/services/ethiopianCalendarService.js"),
        ("apps/ui/app/register/services/registerService.js", "/opt/emr/apps/ui/app/register/services/registerService.js"),
        ("apps/ui/app/register/styles/register.css", "/opt/emr/apps/ui/app/register/styles/register.css"),
        ("apps/ui/app/register/views/register.html", "/opt/emr/apps/ui/app/register/views/register.html"),
    ]

    for local_rel, remote_abs in ui_files:
        local_path = os.path.join(LOCAL_ROOT, local_rel)
        remote_dir = os.path.dirname(remote_abs)
        ensure_remote_dir(sftp, remote_dir)
        sftp.put(local_path, remote_abs)
        print(f"    Uploaded {local_rel} -> {remote_abs}")

    # 2. Deploy SQL files to /opt/emr/config/masterdata/configuration/sql/
    print("\n[3] Deploying SQL search files...")
    sql_files = [
        ("config/masterdata/configuration/sql/emrapi.sqlSearch.opdRegister.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.opdRegister.sql"),
        ("config/masterdata/configuration/sql/emrapi.sqlSearch.icuRegister.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.icuRegister.sql"),
        ("config/masterdata/configuration/sql/emrapi.sqlSearch.liaisonRegister.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.liaisonRegister.sql"),
        ("config/masterdata/configuration/sql/emrapi.sqlSearch.admissionRegister.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.admissionRegister.sql"),
    ]

    for local_rel, remote_abs in sql_files:
        local_path = os.path.join(LOCAL_ROOT, local_rel)
        remote_dir = os.path.dirname(remote_abs)
        ensure_remote_dir(sftp, remote_dir)
        sftp.put(local_path, remote_abs)
        print(f"    Uploaded {local_rel} -> {remote_abs}")

    # 3. Deploy Home extension & locale
    print("\n[4] Deploying Home Extension & Localization...")
    config_files = [
        ("config/openmrs/apps/home/extension.json", "/opt/emr/config/openmrs/apps/home/extension.json"),
        ("config/openmrs/i18n/home/locale_en.json", "/opt/emr/config/openmrs/i18n/home/locale_en.json"),
    ]
    for local_rel, remote_abs in config_files:
        local_path = os.path.join(LOCAL_ROOT, local_rel)
        sftp.put(local_path, remote_abs)
        print(f"    Uploaded {local_rel} -> {remote_abs}")

    # 4. Generate SQL script to update Global Properties in OpenMRS MySQL
    print("\n[5] Updating Global Properties in OpenMRS DB...")
    
    def read_and_escape(rel_path):
        full_p = os.path.join(LOCAL_ROOT, rel_path)
        with open(full_p, "r", encoding="utf-8") as f:
            content = f.read().strip()
        # Escape backslashes first, then single quotes
        escaped = content.replace('\\', '\\\\').replace("'", "\\'")
        return escaped

    opd_sql = read_and_escape("config/masterdata/configuration/sql/emrapi.sqlSearch.opdRegister.sql")
    icu_sql = read_and_escape("config/masterdata/configuration/sql/emrapi.sqlSearch.icuRegister.sql")
    liaison_sql = read_and_escape("config/masterdata/configuration/sql/emrapi.sqlSearch.liaisonRegister.sql")
    admission_sql = read_and_escape("config/masterdata/configuration/sql/emrapi.sqlSearch.admissionRegister.sql")

    gp_sql_content = f"""
DELETE FROM global_property WHERE property = 'emrapi.sqlSearch.opdRegister';
INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.opdRegister', '{opd_sql}', 'Ethiopian MOH Standardized OPD Register Search Query', UUID());

DELETE FROM global_property WHERE property = 'emrapi.sqlSearch.icuRegister';
INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.icuRegister', '{icu_sql}', 'Ethiopian MOH Standardized ICU Register Search Query', UUID());

DELETE FROM global_property WHERE property = 'emrapi.sqlSearch.liaisonRegister';
INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.liaisonRegister', '{liaison_sql}', 'Ethiopian MOH Standardized Liaison Referral Register Search Query', UUID());

DELETE FROM global_property WHERE property = 'emrapi.sqlSearch.admissionRegister';
INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.admissionRegister', '{admission_sql}', 'Ethiopian MOH Standardized Inpatient Admission & Discharge Register Search Query', UUID());
"""
    local_tmp_sql = os.path.join(LOCAL_ROOT, "scratch/apply_all_registers_temp.sql")
    with open(local_tmp_sql, "w", encoding="utf-8") as f:
        f.write(gp_sql_content)

    sftp.put(local_tmp_sql, "/tmp/apply_all_registers.sql")
    print("    Uploaded /tmp/apply_all_registers.sql to remote.")

    run_sudo(ssh, "docker cp /tmp/apply_all_registers.sql bahmni-standard-openmrsdb-1:/tmp/apply_all_registers.sql")
    run_sudo(ssh, "docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e 'source /tmp/apply_all_registers.sql'")
    run_sudo(ssh, "docker exec bahmni-standard-openmrsdb-1 rm -f /tmp/apply_all_registers.sql")
    run_sudo(ssh, "rm -f /tmp/apply_all_registers.sql")

    # 5. Check Global Properties in MySQL
    print("\n[6] Verifying Global Properties in MySQL...")
    res = run_sudo(ssh, "docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"SELECT property, LENGTH(property_value) as val_len, uuid FROM global_property WHERE property LIKE 'emrapi.sqlSearch.%Register';\"")
    print(res)

    sftp.close()
    ssh.close()
    print("\n[+] SSH connection closed.")

    # 6. Test Bahmni Core REST APIs over WAN
    print("\n[7] Testing Bahmni Core REST API for all 4 Registers...")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    auth_header = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")

    endpoints = [
        ("OPD", "emrapi.sqlSearch.opdRegister"),
        ("ICU", "emrapi.sqlSearch.icuRegister"),
        ("LIAISON", "emrapi.sqlSearch.liaisonRegister"),
        ("IPD", "emrapi.sqlSearch.admissionRegister"),
    ]

    for name, query_name in endpoints:
        url = f"https://{HOST}/openmrs/ws/rest/v1/bahmnicore/sql?q={query_name}"
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'SilentDeployer/1.0',
                'Authorization': auth_header,
                'Accept': 'application/json'
            })
            resp = urllib.request.urlopen(req, context=ctx, timeout=30)
            elapsed = time.time() - t0
            raw_json = resp.read().decode('utf-8')
            data = json.loads(raw_json)
            print(f"  --> {name} Register: HTTP {resp.status} in {elapsed:.2f}s | {len(data)} records returned.")
            if len(data) > 0:
                sample = data[0]
                keys = list(sample.keys())[:8]
                print(f"      Columns: {', '.join(keys)}...")
                print(f"      Sample Row: MRN={sample.get('mrn')}, Name={sample.get('patient_name')}, Age={sample.get('age')}, Sex={sample.get('sex')}")
        except Exception as e:
            elapsed = time.time() - t0
            print(f"  [!] {name} Register FAILED in {elapsed:.2f}s: {e}")

    # 7. Test Web UI
    print("\n[8] Testing Web UI App...")
    ui_url = f"https://{HOST}/bahmni/register/index.html"
    try:
        req = urllib.request.Request(ui_url, headers={'User-Agent': 'SilentDeployer/1.0'})
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        print(f"  --> Register UI: HTTP {resp.status} (Length: {len(resp.read())} bytes)")
    except Exception as e:
        print(f"  [!] Register UI fetch failed: {e}")

    print("\n" + "=" * 60)
    print("ALL REGISTER DEPLOYMENTS COMPLETED SILENTLY!")
    print("=" * 60)

if __name__ == "__main__":
    deploy()
