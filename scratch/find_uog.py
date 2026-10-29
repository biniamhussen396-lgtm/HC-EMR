import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

stdin, stdout, stderr = ssh.exec_command('find /home/bmh -name "payment_methods_detail*"')
print('find:', stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command('docker exec bahmni-standard-odoo-1 find / -name "payment_methods_detail*" 2>/dev/null')
print('container find:', stdout.read().decode())

ssh.close()
