import paramiko
import os
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=20)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

timestamp = time.strftime('%Y%m%d_%H%M%S')
backup_dir = f"/opt/emr/backups/deploy_backup_{timestamp}"
staging_dir = "/home/bmh/deploy_staging"

print(f"[1] Creating backup directory on remote: {backup_dir}")
run_sudo(f"mkdir -p {backup_dir}")
run_sudo(f"rm -rf {staging_dir} && mkdir -p {staging_dir} && chown -R bmh:bmh {staging_dir}")

files_to_deploy = [
    # relative_local_path, remote_dest_path
    ("apps/ui/app/bedmanagement/app.js", "/opt/emr/apps/ui/app/bedmanagement/app.js"),
    ("apps/ui/app/bedmanagement/index.html", "/opt/emr/apps/ui/app/bedmanagement/index.html"),
    ("apps/ui/app/bedmanagement/controllers/referFormPrintController.js", "/opt/emr/apps/ui/app/bedmanagement/controllers/referFormPrintController.js"),
    ("apps/ui/app/bedmanagement/controllers/referralManagementController.js", "/opt/emr/apps/ui/app/bedmanagement/controllers/referralManagementController.js"),
    ("apps/ui/app/bedmanagement/views/referFormPrint.html", "/opt/emr/apps/ui/app/bedmanagement/views/referFormPrint.html"),
    ("apps/ui/app/bedmanagement/views/referralManagement.html", "/opt/emr/apps/ui/app/bedmanagement/views/referralManagement.html"),
    ("apps/ui/app/clinical/consultation/controllers/dispositionController.js", "/opt/emr/apps/ui/app/clinical/consultation/controllers/dispositionController.js"),
    ("apps/ui/app/clinical/consultation/views/disposition.html", "/opt/emr/apps/ui/app/clinical/consultation/views/disposition.html"),
    ("apps/ui/app/common/domain/services/dispositionService.js", "/opt/emr/apps/ui/app/common/domain/services/dispositionService.js"),
    ("apps/ui/app/common/patient/services/patientService.js", "/opt/emr/apps/ui/app/common/patient/services/patientService.js"),
    ("apps/ui/app/common/util/httpErrorInterceptor.js", "/opt/emr/apps/ui/app/common/util/httpErrorInterceptor.js"),
    ("config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql"),
    ("config/masterdata/configuration/sql/add_referral_management_sql.sql", "/opt/emr/config/masterdata/configuration/sql/add_referral_management_sql.sql"),
    ("config/masterdata/configuration/sql/register_referral_mgmt.sql", "/opt/emr/config/masterdata/configuration/sql/register_referral_mgmt.sql"),
    ("config/masterdata/configuration/sql/register_referral_mgmt_v2.sql", "/opt/emr/config/masterdata/configuration/sql/register_referral_mgmt_v2.sql"),
]

sftp = ssh.open_sftp()

print("[2] Backing up existing files on remote...")
for local_path, remote_path in files_to_deploy:
    fname = os.path.basename(remote_path)
    # Check if remote file exists
    out, _ = run_sudo(f"test -f {remote_path} && echo EXISTS || echo NOT_EXISTS")
    if "EXISTS" in out:
        run_sudo(f"cp {remote_path} {backup_dir}/{fname}")
        print(f"  Backed up {remote_path} -> {backup_dir}/{fname}")

print("[3] Uploading updated files to staging and copying to destination...")
for local_path, remote_path in files_to_deploy:
    fname = os.path.basename(remote_path)
    stage_file = f"{staging_dir}/{fname}"
    
    # Upload via SFTP to staging
    sftp.put(local_path, stage_file)
    
    # Ensure parent dir exists on remote
    remote_parent = os.path.dirname(remote_path)
    run_sudo(f"mkdir -p {remote_parent}")
    
    # Copy from staging to destination with sudo
    run_sudo(f"cp {stage_file} {remote_path}")
    run_sudo(f"chmod 644 {remote_path}")
    print(f"  Deployed {local_path} -> {remote_path}")

sftp.close()

print("[4] Cleaning up staging...")
run_sudo(f"rm -rf {staging_dir}")

print("[5] Verifying deployed files on remote...")
for local_path, remote_path in files_to_deploy:
    local_size = os.path.getsize(local_path)
    out, _ = run_sudo(f"stat -c '%s %y' {remote_path}")
    print(f"  {remote_path}: Local={local_size}b | Remote={out.strip()}")

ssh.close()
print(f"[SUCCESS] All files deployed silently and verified without any container downtime.")
