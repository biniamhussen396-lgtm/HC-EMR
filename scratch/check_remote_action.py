import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

stdin, stdout, stderr = ssh.exec_command('grep -rn "action_fetch_payment_info" /home/bmh/ /mnt/ /opt/ 2>/dev/null')
print('host grep:', stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command('docker exec bahmni-standard-odoo-1 grep -rn "action_fetch_payment_info" /opt/ /mnt/ 2>/dev/null')
print('container grep:', stdout.read().decode())

ssh.close()
