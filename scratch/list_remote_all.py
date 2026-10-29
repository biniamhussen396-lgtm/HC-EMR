import paramiko
import os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

# 1. Download extra-addons (bahmni_manual_sync) from remote server to local
stdin, stdout, stderr = ssh.exec_command("find /opt/emr/bahmni-docker/bahmni-standard/extra-odoo-addons -type f")
remote_files = [line.strip() for line in stdout.readlines() if line.strip()]

print(f"Found {len(remote_files)} files in extra-odoo-addons:")
for rf in remote_files:
    print(" -", rf)

# 2. Check all modified files across bahmni-addons on remote
stdin, stdout, stderr = ssh.exec_command("docker exec bahmni-standard-odoo-1 find /opt/bahmni-erp/bahmni-addons -type f")
all_addons_files = [line.strip() for line in stdout.readlines() if line.strip()]
print(f"Total files in /opt/bahmni-erp/bahmni-addons: {len(all_addons_files)}")

ssh.close()
