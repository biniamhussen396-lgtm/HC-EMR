import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

stdin, stdout, stderr = ssh.exec_command("grep -E 'ODOO|ADDONS|CONNECT' /opt/emr/bahmni-docker/bahmni-standard/.env")
print(stdout.read().decode())

ssh.close()
