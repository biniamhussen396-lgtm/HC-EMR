import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

stdin, stdout, stderr = ssh.exec_command('docker inspect bahmni-standard-odoo-1')
out = stdout.read().decode()
data = json.loads(out)
mounts = data[0]['Mounts']
for m in mounts:
    print(m['Source'], '->', m['Destination'])

ssh.close()
