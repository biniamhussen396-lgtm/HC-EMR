import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

out, err = run_sudo('docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -s -N -e "SELECT property_value FROM global_property WHERE property = \'emrapi.sqlSearch.referralManagement\';"')
with open('scratch/remote_referralManagement.sql', 'w', encoding='utf-8') as f:
    f.write(out)

print("Saved remote SQL query to scratch/remote_referralManagement.sql. Length:", len(out))
ssh.close()
