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

print("Checking row counts...")
counts = run_sudo("docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"SELECT (SELECT COUNT(*) FROM visit) as visits, (SELECT COUNT(*) FROM encounter) as encounters, (SELECT COUNT(*) FROM obs) as obs_count;\"")
print(counts)

print("\nChecking query execution time...")
t0 = time.time()
res = run_sudo("docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"SELECT property_value FROM global_property WHERE property = 'emrapi.sqlSearch.admissionRegister'\"")
sql_query = res.split("property_value\n", 1)[-1]

# Run with LIMIT 20 to test
t0 = time.time()
res_run = run_sudo("docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"SET @q = (SELECT property_value FROM global_property WHERE property = 'emrapi.sqlSearch.admissionRegister'); PREPARE stmt FROM @q; EXECUTE stmt; DEALLOCATE PREPARE stmt;\"")
t1 = time.time()
print(f"Full query execution time: {t1 - t0:.2f}s")
print(f"Output lines: {len(res_run.splitlines())}")
if len(res_run.splitlines()) > 1:
    print("First 2 lines:\n", "\n".join(res_run.splitlines()[:2]))

ssh.close()
