import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

commands = [
    "pwd",
    "ls -la",
    "docker inspect bahmni-standard-odoo-1 --format '{{json .Mounts}}'",
    "docker inspect bahmni-standard-odoo-connect-1 --format '{{json .Mounts}}' 2>/dev/null || true",
    "find /home/bmh -maxdepth 3 -type d -name '*odoo*' -o -name '*emr*' -o -name '*bahmni*'",
]

for cmd in commands:
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())

ssh.close()
