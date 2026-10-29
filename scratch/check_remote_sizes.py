import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

commands = [
    "docker exec bahmni-standard-odoo-1 du -sh /var/lib/odoo/filestore 2>/dev/null || true",
    "docker exec bahmni-standard-odoodb-1 du -sh /var/lib/postgresql/data 2>/dev/null || true"
]

for cmd in commands:
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())

ssh.close()
