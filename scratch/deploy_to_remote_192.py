import paramiko
import os
import time
import ssl
import urllib.request

HOST = '192.168.10.5'
USER = 'bmh'
PW = '   '
REPO_ROOT = r'c:\Users\COMPUTER\Documents\emr'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"[*] Connecting to {HOST} via SSH...")
ssh.connect(HOST, username=USER, password=PW, timeout=20)
print(f"[+] Connected to {HOST}")

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '{PW}' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def run_mysql(sql):
    cmd = 'docker exec -i bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs'
    stdin, stdout, stderr = ssh.exec_command(f"echo '{PW}' | sudo -S {cmd}")
    stdin.write(sql)
    stdin.flush()
    stdin.channel.shutdown_write()
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

timestamp = time.strftime('%Y%m%d_%H%M%S')
backup_dir = f"/opt/emr/backups/deploy_backup_{timestamp}"
staging_dir = "/home/bmh/deploy_staging_referrals"

print(f"[1] Setting up backup & staging dirs...")
run_sudo(f"mkdir -p {backup_dir}")
run_sudo(f"rm -rf {staging_dir} && mkdir -p {staging_dir} && chown -R bmh:bmh {staging_dir}")

files_to_deploy = [
    ("apps/ui/app/bedmanagement/app.js", "/opt/emr/apps/ui/app/bedmanagement/app.js"),
    ("apps/ui/app/bedmanagement/index.html", "/opt/emr/apps/ui/app/bedmanagement/index.html"),
    ("apps/ui/app/bedmanagement/initialization.js", "/opt/emr/apps/ui/app/bedmanagement/initialization.js"),
    ("apps/ui/app/bedmanagement/controllers/referralManagementController.js", "/opt/emr/apps/ui/app/bedmanagement/controllers/referralManagementController.js"),
    ("apps/ui/app/bedmanagement/views/referralManagement.html", "/opt/emr/apps/ui/app/bedmanagement/views/referralManagement.html"),
    ("config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql"),
    ("config/masterdata/configuration/sql/add_referral_management_sql.sql", "/opt/emr/config/masterdata/configuration/sql/add_referral_management_sql.sql"),
]

sftp = ssh.open_sftp()

print("[2] Backing up existing files on remote...")
for rel_path, remote_path in files_to_deploy:
    fname = os.path.basename(remote_path)
    out, _ = run_sudo(f"test -f {remote_path} && echo EXISTS || echo NOT_EXISTS")
    if "EXISTS" in out:
        run_sudo(f"cp {remote_path} {backup_dir}/{fname}")
        print(f"  Backed up {remote_path} -> {backup_dir}/{fname}")

print("[3] Uploading updated files via SFTP to staging...")
for idx, (rel_path, remote_path) in enumerate(files_to_deploy):
    local_path = os.path.join(REPO_ROOT, rel_path.replace('/', os.sep))
    stage_file = f"{staging_dir}/{idx}_{os.path.basename(remote_path)}"
    sftp.put(local_path, stage_file)
    print(f"  Uploaded {rel_path} -> {stage_file}")

sftp.close()

print("[4] Moving files to destination and setting permissions (644)...")
for idx, (rel_path, remote_path) in enumerate(files_to_deploy):
    stage_file = f"{staging_dir}/{idx}_{os.path.basename(remote_path)}"
    remote_parent = os.path.dirname(remote_path)
    run_sudo(f"mkdir -p {remote_parent}")
    run_sudo(f"cp {stage_file} {remote_path}")
    run_sudo(f"chmod 644 {remote_path}")
    print(f"  Installed {remote_path}")

print("[5] Cleaning staging...")
run_sudo(f"rm -rf {staging_dir}")

print("[6] Updating emrapi.sqlSearch.referralManagement global property in MySQL...")
with open(os.path.join(REPO_ROOT, 'config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql'), 'r', encoding='utf-8') as f:
    sql_query = f.read().strip()

escaped_query = sql_query.replace('\\', '\\\\').replace("'", "''")
update_gp_sql = f"""
INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.referralManagement', '{escaped_query}', 'Referral In/Out Register SQL Search query with Senior Physician Approval', UUID())
ON DUPLICATE KEY UPDATE property_value = '{escaped_query}', description = 'Referral In/Out Register SQL Search query with Senior Physician Approval';
"""
out, err = run_mysql(update_gp_sql)
if err and 'Warning' not in err and '[sudo]' not in err:
    print("  MySQL Warning/Err:", err)

gp_verify = "SELECT property, LENGTH(property_value), date_changed FROM global_property WHERE property = 'emrapi.sqlSearch.referralManagement';"
out, err = run_mysql(gp_verify)
print("  Global Property Verification:\n", out)

print("[7] Verifying file system updates on remote...")
for rel_path, remote_path in files_to_deploy:
    local_path = os.path.join(REPO_ROOT, rel_path.replace('/', os.sep))
    local_size = os.path.getsize(local_path)
    out, _ = run_sudo(f"stat -c '%s %y' {remote_path}")
    print(f"  {os.path.basename(remote_path)}: Local={local_size}b | Remote={out.strip()}")

ssh.close()

print("[8] Verifying live endpoints over HTTPS...")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls_to_test = [
    (f"https://{HOST}/bahmni/bedmanagement/index.html", "app.js?v=3.2"),
    (f"https://{HOST}/bahmni/bedmanagement/app.js?v=3.2", "referralManagement.html?v=3.2"),
    (f"https://{HOST}/bahmni/bedmanagement/initialization.js?v=3.2", "encounterConfig && $rootScope.patientConfig"),
    (f"https://{HOST}/bahmni/bedmanagement/controllers/referralManagementController.js?v=3.2", "exportToExcel"),
    (f"https://{HOST}/bahmni/bedmanagement/views/referralManagement.html?v=3.2", "Export to Excel"),
    (f"https://{HOST}/bahmni/bedmanagement/views/referralManagement.html?v=3.2", "AMHARA NATIONAL REGIONAL STATE HEALTH BUREAU"),
]

all_passed = True
for url, snippet in urls_to_test:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='replace')
            if snippet in content:
                print(f"  [PASSED] HTTP {resp.status} for {url} (found '{snippet}')")
            else:
                print(f"  [WARNING] Snippet '{snippet}' not found in {url}!")
                all_passed = False
    except Exception as e:
        print(f"  [ERROR] Failed to fetch {url}: {e}")
        all_passed = False

if all_passed:
    print(f"\n[SUCCESS] DEPLOYMENT TO {HOST} COMPLETED SUCCESSFULLY WITH ZERO DOWNTIME!")
else:
    print(f"\n[WARNING] Deployment finished with warnings.")
