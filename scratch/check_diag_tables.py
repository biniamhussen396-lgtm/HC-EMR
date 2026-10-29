import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=15)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out.strip()

print("Checking diagnosis tables and concept IDs...")
res = run_sudo("""docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e "
SHOW TABLES LIKE '%diagnosis%';
SELECT concept_id, name FROM concept_name WHERE name IN ('Coded Diagnosis', 'Visit Diagnoses') AND voided = 0;
" """)
print(res)

ssh.close()
