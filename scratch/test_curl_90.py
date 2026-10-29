import subprocess
import time

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

# Update GP with test_limit.sql
with open('scratch/test_limit.sql', 'r', encoding='utf-8') as f:
    sql_text = f.read().strip()

escaped = sql_text.replace("'", "''")
cmd = f'''docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "UPDATE global_property SET property_value = '{escaped}' WHERE property = 'emrapi.sqlSearch.opdRegister';"'''
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
print("Updated GP:", res.returncode)

t0 = time.time()
curl_cmd = 'curl -k -s -u admin:Admin123 "https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"'
res2 = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", curl_cmd], capture_output=True, text=True, timeout=90)
t1 = time.time()
print(f"API time: {t1-t0:.2f}s, length: {len(res2.stdout)}")
if len(res2.stdout) > 0:
    print(res2.stdout[:300])
