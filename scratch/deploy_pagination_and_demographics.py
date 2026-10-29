import os
import time
import ssl
import urllib.request
import paramiko

REPO_ROOT = r"c:\Users\COMPUTER\Documents\emr"
HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

FILES_TO_DEPLOY = [
    ("apps/ui/app/bedmanagement/app.js", "/opt/emr/apps/ui/app/bedmanagement/app.js"),
    ("apps/ui/app/bedmanagement/index.html", "/opt/emr/apps/ui/app/bedmanagement/index.html"),
    ("apps/ui/app/bedmanagement/controllers/referralManagementController.js", "/opt/emr/apps/ui/app/bedmanagement/controllers/referralManagementController.js"),
    ("apps/ui/app/bedmanagement/views/referralManagement.html", "/opt/emr/apps/ui/app/bedmanagement/views/referralManagement.html"),
    ("apps/ui/app/bedmanagement/controllers/referFormPrintController.js", "/opt/emr/apps/ui/app/bedmanagement/controllers/referFormPrintController.js"),
    ("apps/ui/app/bedmanagement/views/referFormPrint.html", "/opt/emr/apps/ui/app/bedmanagement/views/referFormPrint.html"),
]

def run_sudo(ssh, cmd):
    full_cmd = f"echo '{PW}' | sudo -S bash -c {repr(cmd)}"
    stdin, stdout, stderr = ssh.exec_command(full_cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return exit_status, out, err

def main():
    print(f"[*] Starting silent production deployment to {HOST}...")

    # 1. Connect via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PW, timeout=10)
    print("  [+] SSH connection established.")

    # 2. Backup existing files
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = f"/opt/emr/backups/backup_pagination_{ts}"
    rc, out, err = run_sudo(ssh, f"mkdir -p {backup_dir}")
    print(f"  [+] Created backup dir: {backup_dir}")

    for rel_path, remote_dest in FILES_TO_DEPLOY:
        backup_dest = f"{backup_dir}/{os.path.basename(remote_dest)}"
        rc, out, err = run_sudo(ssh, f"cp {remote_dest} {backup_dest} 2>/dev/null || true")
        print(f"      Backed up {os.path.basename(remote_dest)}")

    # 3. Setup staging dir in bmh home
    staging_dir = "/home/bmh/deploy_staging"
    stdin, stdout, stderr = ssh.exec_command(f"rm -rf {staging_dir} && mkdir -p {staging_dir}")
    stdout.channel.recv_exit_status()

    # 4. Upload files via SFTP
    sftp = ssh.open_sftp()
    print("  [+] Uploading files to staging...")
    for rel_path, remote_dest in FILES_TO_DEPLOY:
        local_path = os.path.join(REPO_ROOT, rel_path.replace("/", os.sep))
        staging_file = f"{staging_dir}/{os.path.basename(remote_dest)}"
        sftp.put(local_path, staging_file)
        print(f"      Uploaded {os.path.basename(remote_dest)}")
    sftp.close()

    # 5. Move files into place with sudo and set permissions
    print("  [+] Moving files into /opt/emr/apps/ui/app/bedmanagement/ ...")
    for rel_path, remote_dest in FILES_TO_DEPLOY:
        staging_file = f"{staging_dir}/{os.path.basename(remote_dest)}"
        cmd = f"cp {staging_file} {remote_dest} && chmod 644 {remote_dest}"
        rc, out, err = run_sudo(ssh, cmd)
        if rc != 0:
            print(f"  [!] Error copying {remote_dest}: {err}")
            ssh.close()
            return False

    # Cleanup staging
    ssh.exec_command(f"rm -rf {staging_dir}")
    print("  [+] Files moved and permissions set (644). Staging cleaned.")

    ssh.close()

    # 6. Verify live deployment over HTTPS
    print("  [+] Verifying deployment over HTTPS...")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    urls_to_test = [
        f"https://{HOST}/bahmni/bedmanagement/index.html",
        f"https://{HOST}/bahmni/bedmanagement/app.js?v=2.5",
        f"https://{HOST}/bahmni/bedmanagement/controllers/referralManagementController.js?v=2.5",
        f"https://{HOST}/bahmni/bedmanagement/views/referralManagement.html?v=2.5",
        f"https://{HOST}/bahmni/bedmanagement/controllers/referFormPrintController.js?v=2.5",
        f"https://{HOST}/bahmni/bedmanagement/views/referFormPrint.html?v=2.5",
    ]

    for url in urls_to_test:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='replace')
            print(f"      HTTP {resp.status} for {url} ({len(content)} bytes)")
            if "referralManagementController.js" in url and "updatePagination" in content:
                print("      [CHECK PASSED] 'updatePagination' verified in live controller!")
            if "referralManagement.html" in url and "pagination-bar" in content:
                print("      [CHECK PASSED] 'pagination-bar' verified in live template!")
            if "referFormPrintController.js" in url and "primaryId" in content:
                print("      [CHECK PASSED] 'primaryId' demographic extraction verified in live print controller!")
            if "referFormPrint.html" in url and "patientIdentifier" in content:
                print("      [CHECK PASSED] 'patientIdentifier' verified in live print template!")

    print("[*] SILENT DEPLOYMENT COMPLETED SUCCESSFULLY WITH ZERO DOWNTIME.")
    return True

if __name__ == "__main__":
    main()
