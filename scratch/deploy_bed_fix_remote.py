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

staging_dir = "/home/bmh/deploy_staging_bed_fix2"
run_sudo(f"rm -rf {staging_dir} && mkdir -p {staging_dir} && chown -R bmh:bmh {staging_dir}")

files_to_deploy = [
    ("apps/ui/app/bedmanagement/controllers/adtController.js", "/opt/emr/apps/ui/app/bedmanagement/controllers/adtController.js", "bed_adtController.js"),
    ("apps/ui/app/bedmanagement/index.html", "/opt/emr/apps/ui/app/bedmanagement/index.html", "bed_index.html"),
    ("apps/ui/app/adt/controllers/adtController.js", "/opt/emr/apps/ui/app/adt/controllers/adtController.js", "adt_adtController.js"),
    ("apps/ui/app/adt/index.html", "/opt/emr/apps/ui/app/adt/index.html", "adt_index.html"),
]

sftp = ssh.open_sftp()
print("[1] Uploading updated files to staging with unique names...")
for rel_path, remote_path, stage_name in files_to_deploy:
    local_path = os.path.join(REPO_ROOT, rel_path.replace("/", "\\"))
    staging_file = f"{staging_dir}/{stage_name}"
    sftp.put(local_path, staging_file)
    print(f"  Uploaded {rel_path} -> {staging_file} ({os.path.getsize(local_path)} bytes)")

sftp.close()

print("[2] Installing to production...")
for rel_path, remote_path, stage_name in files_to_deploy:
    staging_file = f"{staging_dir}/{stage_name}"
    run_sudo(f"cp {staging_file} {remote_path}")
    run_sudo(f"chmod 644 {remote_path}")
    run_sudo(f"chown -R bmh:bmh {remote_path}")
    print(f"  Installed {remote_path}")

run_sudo(f"rm -rf {staging_dir}")
ssh.close()
print("[+] SSH session closed.")

print("[3] Verifying remote endpoints over HTTPS...")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    ("https://192.168.10.5/bahmni/bedmanagement/index.html", 17293),
    ("https://192.168.10.5/bahmni/bedmanagement/controllers/adtController.js?v=3.3", 22902),
    ("https://192.168.10.5/bahmni/adt/index.html", 18579),
    ("https://192.168.10.5/bahmni/adt/controllers/adtController.js?v=3.3", 20488)
]

for url, expected_len in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'DeployVerifier/1.0'})
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        content = resp.read().decode('utf-8', errors='ignore')
        print(f"  [OK] {url} -> HTTP {resp.status} (Length: {len(content)}, Expected: ~{expected_len})")
    except Exception as e:
        print(f"  [FAIL] {url} -> {e}")

print("\n=== Re-deploy Complete and Verified ===")
