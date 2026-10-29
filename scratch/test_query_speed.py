import subprocess
import time

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

t0 = time.time()
cmd = '''docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "
SELECT 
    v.visit_id,
    v.date_started as service_date,
    vt.name as visit_type_name
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
WHERE v.voided = 0
ORDER BY v.visit_id DESC
LIMIT 5;
"'''
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=30)
t1 = time.time()
print(f"Elapsed: {t1-t0:.2f}s")
print(res.stdout)
