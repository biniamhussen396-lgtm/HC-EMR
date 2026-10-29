import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

out, err = run_sudo('docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e "SELECT property, LENGTH(property_value) FROM global_property WHERE property LIKE \'%referral%\';"')
print("Referral properties:\n", out)

out, err = run_sudo('docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e "SELECT concept_id, uuid FROM concept_name WHERE name LIKE \'%Referral%\' LIMIT 10;"')
print("Referral concepts:\n", out)

ssh.close()
