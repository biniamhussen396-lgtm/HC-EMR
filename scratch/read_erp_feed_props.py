import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

commands = [
    "docker exec bahmni-standard-odoo-connect-1 cat /var/run/bahmni-erp-connect/bahmni-erp-connect/WEB-INF/classes/erp-atomfeed.properties",
    "docker exec bahmni-standard-odoo-connect-1 cat /var/run/bahmni-erp-connect/bahmni-erp-connect/WEB-INF/classes/jobs-context.xml",
]

for cmd in commands:
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())

ssh.close()
