import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

commands = [
    "docker exec bahmni-standard-odoo-1 ls -la /opt/bahmni-erp/ 2>/dev/null || true",
    "docker exec bahmni-standard-odoo-1 ls -la /opt/bahmni-erp/bahmni-addons/ 2>/dev/null || true",
    "docker exec bahmni-standard-odoo-1 ls -la /mnt/extra-addons/ 2>/dev/null || true",
    "docker exec bahmni-standard-odoo-1 cat /etc/odoo/odoo.conf 2>/dev/null || true",
    "ls -la /opt/emr/bahmni-docker/bahmni-standard/ 2>/dev/null || true",
    "ls -la /opt/emr/bahmni-docker/bahmni-standard/extra-odoo-addons 2>/dev/null || true",
    "ls -la /home/bmh/Documents/emr/ 2>/dev/null || true",
    "ls -la /home/bmh/Documents/emr/erp/ 2>/dev/null || true"
]

for cmd in commands:
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())

ssh.close()
