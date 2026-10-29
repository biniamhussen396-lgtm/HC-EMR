import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

out, err = run_sudo('docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e "SELECT MAX(concept_id) FROM concept; SELECT MAX(concept_name_id) FROM concept_name;"')
print("Max IDs on 192.168.10.5:\n", out)

out, err = run_sudo('docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e "SELECT concept_datatype_id, name FROM concept_datatype WHERE name = \'Text\'; SELECT concept_class_id, name FROM concept_class WHERE name = \'Question\';"')
print("Datatype and class IDs on 192.168.10.5:\n", out)

ssh.close()
