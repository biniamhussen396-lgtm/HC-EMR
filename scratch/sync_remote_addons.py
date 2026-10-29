import paramiko
import os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

sftp = ssh.open_sftp()

def download_dir(remote_dir, local_dir):
    os.makedirs(local_dir, exist_ok=True)
    for entry in sftp.listdir_attr(remote_dir):
        rpath = remote_dir + "/" + entry.filename
        lpath = os.path.join(local_dir, entry.filename)
        if entry.st_mode & 0o040000:
            download_dir(rpath, lpath)
        else:
            sftp.get(rpath, lpath)
            print(f"Downloaded {rpath} -> {lpath}")

print("Downloading bahmni_manual_sync...")
download_dir("/opt/emr/bahmni-docker/bahmni-standard/extra-odoo-addons/bahmni_manual_sync", "bahmni-docker/bahmni-standard/extra-odoo-addons/bahmni_manual_sync")

# Also copy uog_care updated models
print("Updating uog_care models from remote...")
for mod in ["payment_methods_detail.py", "sale_report.py"]:
    rpath = f"/opt/bahmni-erp/bahmni-addons/uog_care/models/{mod}"
    lpath = f"erp/bahmni-odoo-modules/uog_care/models/{mod}"
    stdin, stdout, stderr = ssh.exec_command(f"docker exec bahmni-standard-odoo-1 cat {rpath}")
    content = stdout.read()
    if content:
        with open(lpath, "wb") as f:
            f.write(content)
        print(f"Updated {lpath} ({len(content)} bytes)")

sftp.close()
ssh.close()
print("All addons synced successfully!")
