import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

stdin, stdout, stderr = ssh.exec_command("sed -n '/odoo:/,/^[a-zA-Z]/p' /opt/emr/bahmni-docker/bahmni-standard/docker-compose.yml")
print(stdout.read().decode())

ssh.close()
