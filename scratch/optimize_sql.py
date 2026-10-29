import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=15)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out.strip()

print("Querying visit types breakdown...")
q1 = """
SELECT vt.name, count(*) as total, sum(v.date_stopped is null) as active
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
WHERE vt.name IN ('Emergency OPD', 'Delivery Room', 'IPD') OR vt.name LIKE '%ward%'
GROUP BY vt.name;
"""
res = run_sudo(f"docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"{q1}\"")
print(res)

ssh.close()
