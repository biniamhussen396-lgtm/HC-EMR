import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

commands = [
    "cat /opt/emr/bahmni-docker/bahmni-standard/extra-odoo-addons/bahmni_manual_sync/models/bahmni_sync.py",
    "cat /opt/emr/bahmni-docker/bahmni-standard/extra-odoo-addons/bahmni_manual_sync/__manifest__.py",
]

for cmd in commands:
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())

ssh.close()
