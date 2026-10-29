import paramiko
import os
import tarfile

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

# Create a tar of uog_care on remote
stdin, stdout, stderr = ssh.exec_command('tar -czf /home/bmh/uog_care.tar.gz -C /opt/emr/erp/bahmni-odoo-modules uog_care')
exit_status = stdout.channel.recv_exit_status()
print('Tar exit status:', exit_status)

# SFTP download
sftp = ssh.open_sftp()
local_tar = r'c:\Users\COMPUTER\Documents\emr\scratch\uog_care.tar.gz'
sftp.get('/home/bmh/uog_care.tar.gz', local_tar)
sftp.close()
ssh.close()

print('Downloaded uog_care.tar.gz, extracting...')
target_dir = r'c:\Users\COMPUTER\Documents\emr\erp\bahmni-odoo-modules'
with tarfile.open(local_tar, 'r:gz') as tar:
    tar.extractall(target_dir)

print('Extracted uog_care successfully!')
