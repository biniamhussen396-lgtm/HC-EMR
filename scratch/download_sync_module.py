import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

stdin, stdout, stderr = ssh.exec_command("cat /opt/emr/bahmni-docker/bahmni-standard/extra-odoo-addons/bahmni_manual_sync/models/bahmni_sync.py")
content = stdout.read()
with open("scratch/remote_bahmni_sync.py", "wb") as f:
    f.write(content)

stdin, stdout, stderr = ssh.exec_command("cat /opt/emr/bahmni-docker/bahmni-standard/extra-odoo-addons/bahmni_manual_sync/__manifest__.py")
content = stdout.read()
with open("scratch/remote_manifest.py", "wb") as f:
    f.write(content)

print("Saved files successfully! Size:", len(content))
ssh.close()
