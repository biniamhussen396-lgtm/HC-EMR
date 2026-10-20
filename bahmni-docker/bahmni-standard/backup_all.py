#!/usr/bin/env python3
import datetime
import glob
import json
import os
import subprocess
import sys

LOCAL_BACKUP_DIR = "/opt/emr/backups"
RETENTION_LIMIT = 8
CONFIG_FILE = os.path.join(LOCAL_BACKUP_DIR, "remote_config.json")
DEFAULT_CONFIG = {
    "remote_user": "kphc",
    "remote_host": "192.168.1.10",
    "remote_dir": "/home/kphc/bahmni_backups"
}
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
TARGET_DIR = os.path.join(LOCAL_BACKUP_DIR, f"bahmni_backup_{TIMESTAMP}")
SCRIPT_PATH = os.path.abspath(__file__)

def run_cmd(cmd, check=True):
    print(f"[*] Running: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if check and res.returncode != 0:
        print(f"[!] Backup error:\n{res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)
    return res.stdout.strip()

def load_or_prompt_config():
    os.makedirs(LOCAL_BACKUP_DIR, exist_ok=True)
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config.update(json.load(f))
        except Exception:
            pass

    if sys.stdin.isatty():
        print("\n--- Remote SSH Backup Configuration ---")
        u_ip = input(f"Enter Remote PC IP [{config["remote_host"]}]: ").strip()
        if u_ip: config["remote_host"] = u_ip
        u_user = input(f"Enter Remote SSH User [{config["remote_user"]}]: ").strip()
        if u_user: config["remote_user"] = u_user
        u_dir = input(f"Enter Remote Backup Dir [{config["remote_dir"]}]: ").strip()
        if u_dir: config["remote_dir"] = u_dir
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            print("[✔] Remote configuration saved.\n")
        except Exception as e:
            print(f"[!] Could not save config: {e}")
    return config

def setup_midnight_cron():
    cron_job = f"0 0 * * * /usr/bin/python3 {SCRIPT_PATH} >> {LOCAL_BACKUP_DIR}/backup.log 2>&1"
    try:
        current_cron = subprocess.run("crontab -l", shell=True, text=True, capture_output=True).stdout
        if SCRIPT_PATH not in current_cron:
            new_cron = current_cron.strip() + "\n" + cron_job + "\n"
            subprocess.run("crontab -", shell=True, text=True, input=new_cron, capture_output=True)
    except Exception:
        pass

def find_external_drives():
    external_paths = []
    for root in ["/media", "/mnt"]:
        if os.path.exists(root):
            for u in os.listdir(root):
                u_path = os.path.join(root, u)
                if os.path.isdir(u_path):
                    for m in os.listdir(u_path):
                        m_path = os.path.join(u_path, m)
                        if os.path.ismount(m_path):
                            external_paths.append(m_path)
    return external_paths

def enforce_retention(directory):
    if not os.path.exists(directory):
        return
    archives = glob.glob(os.path.join(directory, "bahmni_backup_*.tar.gz"))
    archives.sort(key=os.path.getmtime, reverse=True)
    if len(archives) > RETENTION_LIMIT:
        print(f"[*] Pruning old archives in {directory} (retention: {RETENTION_LIMIT})...")
        for old in archives[RETENTION_LIMIT:]:
            try:
                os.remove(old)
            except OSError:
                pass

def main():
    setup_midnight_cron()
    config = load_or_prompt_config()

    os.makedirs(LOCAL_BACKUP_DIR, exist_ok=True)
    os.makedirs(TARGET_DIR, exist_ok=True)
    print(f"\n[+] Backup target: {TARGET_DIR}")

    # 1. OpenMRS
    print("[*] Dumping OpenMRS DB...")
    run_cmd(f"docker exec bahmni-standard-openmrsdb-1 mysqldump -uroot -p\"adminAdmin!123\" --single-transaction --routines --triggers openmrs > {TARGET_DIR}/openmrs.sql")

    # 2. ClinLIMS / OpenELIS
    print("[*] Dumping ClinLIMS / OpenELIS DB...")
    run_cmd(f"docker exec bahmni-standard-openelisdb-1 pg_dump -U clinlims clinlims > {TARGET_DIR}/clinlims.sql", check=False)

    # 3. Odoo
    print("[*] Dumping Odoo DB...")
    run_cmd(f"docker exec bahmni-standard-odoodb-1 pg_dump -U odoo odoo > {TARGET_DIR}/odoo.sql", check=False)

    # 4. Reports
    print("[*] Dumping Reports DB...")
    run_cmd(f"docker exec bahmni-standard-reportsdb-1 mysqldump -uroot -ppassword --single-transaction bahmni_reports > {TARGET_DIR}/bahmni_reports.sql", check=False)

    # 5. Lab Result Sync tracker
    print("[*] Backing up Lab Result tracker...")
    run_cmd(f"docker cp lab-result-sync:/last_result.json {TARGET_DIR}/lab_last_result.json", check=False)

    # 6. Patient Documents Volume
    print("[*] Archiving Patient Documents...")
    run_cmd(f"tar -czf {TARGET_DIR}/document_images.tar.gz -C /var/lib/docker/volumes/bahmni-standard_bahmni-document-images/_data .", check=False)

    # 7. EMR App Configs
    if os.path.exists("/opt/emr/config"):
        print("[*] Archiving EMR Configs...")
        run_cmd(f"tar -czf {TARGET_DIR}/emr_config.tar.gz -C /opt/emr/config .", check=False)

    # 8. Web UI Patches
    print("[*] Archiving Web UI Patches...")
    web_dir = os.path.join(TARGET_DIR, "bahmni_web_patches")
    os.makedirs(web_dir, exist_ok=True)
    run_cmd(f"docker cp bahmni-standard-bahmni-web-1:/usr/local/apache2/htdocs/bahmni/registration/controllers/searchPatientController.js {web_dir}/searchPatientController.js", check=False)
    run_cmd(f"docker cp bahmni-standard-bahmni-web-1:/usr/local/apache2/htdocs/bahmni/registration/controllers/createCRTriagePatientController.js {web_dir}/createCRTriagePatientController.js", check=False)
    run_cmd(f"docker cp bahmni-standard-bahmni-web-1:/usr/local/apache2/htdocs/bahmni/common/logicAndConditionProcessors/skipLogicProcessor.js {web_dir}/skipLogicProcessor.js", check=False)

    # 9. Final tar archive
    tar_archive = f"{TARGET_DIR}.tar.gz"
    print(f"[*] Packaging into {tar_archive}...")
    run_cmd(f"tar -czf {tar_archive} -C {LOCAL_BACKUP_DIR} bahmni_backup_{TIMESTAMP}")
    run_cmd(f"rm -rf {TARGET_DIR}")

    enforce_retention(LOCAL_BACKUP_DIR)

    # 10. External drives
    for drive in find_external_drives():
        d_dir = os.path.join(drive, "bahmni_backups")
        try:
            os.makedirs(d_dir, exist_ok=True)
            print(f"[*] Copying to external drive: {d_dir}")
            run_cmd(f"cp {tar_archive} {d_dir}/")
            enforce_retention(d_dir)
        except OSError:
            pass

    # 11. Remote SCP
    print(f"[*] Sending to remote PC ({config["remote_host"]})...")
    scp = f"scp -o ConnectTimeout=5 -o BatchMode=yes {tar_archive} {config["remote_user"]}@{config["remote_host"]}:{config["remote_dir"]}/"
    res = subprocess.run(scp, shell=True, text=True, capture_output=True)
    if res.returncode == 0:
        print("[✔] Successfully transferred to Remote PC.")
    else:
        print("[!] Note: Remote PC unreachable or key-less SSH not set up (local backup is secured).")

    print(f"\n[✔] Backup process completed: {tar_archive}")

if __name__ == "__main__":
    main()
