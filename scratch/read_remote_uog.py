import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

stdin, stdout, stderr = ssh.exec_command('ls -la /opt/emr/erp/bahmni-odoo-modules/uog_care/views')
print('views:', stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command('ls -la /opt/emr/erp/bahmni-odoo-modules/uog_care/models')
print('models:', stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command('cat /opt/emr/erp/bahmni-odoo-modules/uog_care/views/payment_methods_detail_view.xml')
print('xml:', stdout.read().decode()[:300])

stdin, stdout, stderr = ssh.exec_command('cat /opt/emr/erp/bahmni-odoo-modules/uog_care/models/payment_methods_detail.py')
print('py:', stdout.read().decode()[:300])

ssh.close()
