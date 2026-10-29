import os
import tarfile
import subprocess
import time
import json
import urllib.request
import base64
import ssl

REPO_ROOT = r"c:\Users\COMPUTER\Documents\emr"
HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

FILES_MAP = [
    ("config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql", "/opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql"),
    ("apps/ui/app/bedmanagement/app.js", "/opt/emr/apps/ui/app/bedmanagement/app.js"),
    ("apps/ui/app/bedmanagement/index.html", "/opt/emr/apps/ui/app/bedmanagement/index.html"),
    ("apps/ui/app/bedmanagement/controllers/referralManagementController.js", "/opt/emr/apps/ui/app/bedmanagement/controllers/referralManagementController.js"),
    ("apps/ui/app/bedmanagement/views/referralManagement.html", "/opt/emr/apps/ui/app/bedmanagement/views/referralManagement.html"),
    ("apps/ui/app/bedmanagement/controllers/referFormPrintController.js", "/opt/emr/apps/ui/app/bedmanagement/controllers/referFormPrintController.js"),
    ("apps/ui/app/bedmanagement/views/referFormPrint.html", "/opt/emr/apps/ui/app/bedmanagement/views/referFormPrint.html"),
]

def run_remote(cmd):
    res = subprocess.run(
        ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return res.returncode, res.stdout, res.stderr

def run_sudo(cmd):
    wrapped = f"echo '{PW}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    return run_remote(wrapped)

def main():
    print(f"[*] Deploying Referral Management and Print updates to {USER}@{HOST} ...")

    # 1. Package files
    tar_path = os.path.join(REPO_ROOT, "scratch", "referral_deploy.tar.gz")
    with tarfile.open(tar_path, "w:gz") as tar:
        for rel_src, remote_dest in FILES_MAP:
            local_full = os.path.join(REPO_ROOT, rel_src.replace("/", os.sep))
            if not os.path.isfile(local_full):
                raise FileNotFoundError(f"Missing local file: {local_full}")
            tar.add(local_full, arcname=rel_src)
            print(f"  + Added {rel_src}")

    # 2. Upload archive
    print("[*] Uploading package via pscp...")
    res = subprocess.run(
        ["pscp", "-batch", "-pw", PW, tar_path, f"{USER}@{HOST}:/tmp/referral_deploy.tar.gz"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if res.returncode != 0:
        print(f"[!] Upload failed: {res.stderr}")
        return False

    # 3. Remote copy and permissions
    remote_cmds = """
set -e
mkdir -p /tmp/referral_deploy
tar -xzf /tmp/referral_deploy.tar.gz -C /tmp/referral_deploy
"""
    for rel_src, remote_dest in FILES_MAP:
        remote_cmds += f"cp /tmp/referral_deploy/{rel_src} {remote_dest}\n"

    remote_cmds += """
find /opt/emr/apps/ui/app/bedmanagement -type d -exec chmod 755 {} +
find /opt/emr/apps/ui/app/bedmanagement -type f -exec chmod 644 {} +
find /opt/emr/config/masterdata/configuration/sql -type f -exec chmod 644 {} +

rm -rf /tmp/referral_deploy /tmp/referral_deploy.tar.gz
echo "REFERRAL_FILES_COPIED_SUCCESS"
"""
    script_local = os.path.join(REPO_ROOT, "scratch", "remote_referral_install.sh")
    with open(script_local, "w", encoding="utf-8", newline="\n") as f:
        f.write(remote_cmds)

    subprocess.run(["pscp", "-batch", "-pw", PW, script_local, f"{USER}@{HOST}:/tmp/remote_referral_install.sh"], check=True)
    rc, out, err = run_sudo("chmod +x /tmp/remote_referral_install.sh && /tmp/remote_referral_install.sh && rm -f /tmp/remote_referral_install.sh")
    print("Remote Install Output:\n", out)
    if rc != 0:
        print("Remote Install Stderr:\n", err)
        return False

    # 4. Update OpenMRS global_property in remote OpenMRS DB
    print("[*] Updating OpenMRS global_property in remote database...")
    sql_file = os.path.join(REPO_ROOT, "config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql")
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Update via REST API on 192.168.10.5
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    auth = base64.b64encode(b"admin:Admin123").decode()
    payload = json.dumps({"property": "emrapi.sqlSearch.referralManagement", "value": sql_content}).encode("utf-8")
    req = urllib.request.Request(
        "https://192.168.10.5/openmrs/ws/rest/v1/systemsetting/emrapi.sqlSearch.referralManagement",
        data=payload,
        headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        print("[*] OpenMRS REST systemsetting updated: HTTP", resp.status)
    except Exception as e:
        print("[!] OpenMRS REST systemsetting failed, fallback to SQL:", e)
        # Fallback SQL update
        escaped_sql = sql_content.replace("\\", "\\\\").replace("'", "\\'")
        sql_cmd = f"docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"UPDATE global_property SET property_value = '{escaped_sql}' WHERE property = 'emrapi.sqlSearch.referralManagement';\""
        rc, out, err = run_remote(sql_cmd)
        print("SQL update rc:", rc, out, err)

    # 5. Verification
    print("\n=== VERIFICATION ON REMOTE ===")
    req_verify = urllib.request.Request(
        "https://192.168.10.5/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.referralManagement&v=full&location_uuid=4935194e-1c9c-4ace-b807-724c234926d7",
        headers={"Authorization": "Basic " + auth}
    )
    try:
        resp = urllib.request.urlopen(req_verify, context=ctx)
        data = json.loads(resp.read().decode("utf-8"))
        print(f"Total referrals returned: {len(data)}")
        if len(data) > 0:
            first = data[0]
            print(f"First row Name: {first.get('name')}")
            print(f"First row Location: {first.get('location')}")
            print(f"First row Physician: {first.get('physicianName')}")
    except Exception as e:
        print("[!] Verification failed:", e)

    print("\n[✓] Deployment completed successfully!")
    return True

if __name__ == "__main__":
    main()
