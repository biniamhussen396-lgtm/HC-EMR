import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=15)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out.strip()

print("Count obs with concept_id = 22...")
res = run_sudo("""docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e "
SELECT count(*) FROM obs WHERE concept_id = 22 AND voided = 0;
" """)
print(res)

ssh.close()
