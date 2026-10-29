import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

stdin, stdout, stderr = ssh.exec_command('ls -la /opt/emr/erp/bahmni-odoo-modules')
print('remote modules:', stdout.read().decode())

ssh.close()
