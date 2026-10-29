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

# Test 1: Count inpatient visits properly defined
test_q = """
SELECT count(*) 
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
WHERE v.voided = 0 
  AND (vt.name LIKE '%ward%' OR vt.name IN ('IPD', 'Delivery Room', 'Emergency OPD')
       OR EXISTS (SELECT 1 FROM encounter e WHERE e.visit_id = v.visit_id AND e.encounter_type IN (3, 4) AND e.voided = 0));
"""
print("Counting actual inpatient visits...")
t0 = time.time()
res = run_sudo(f"docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"{test_q}\"")
t1 = time.time()
print(f"Count result ({t1-t0:.2f}s):\n{res}")

ssh.close()
