import subprocess
import time
import json

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

# Read fast_opd.sql and update global property
with open('scratch/fast_opd.sql', 'r', encoding='utf-8') as f:
    sql_text = f.read().strip()

escaped = sql_text.replace("'", "''")
cmd = f'''docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "UPDATE global_property SET property_value = '{escaped}' WHERE property = 'emrapi.sqlSearch.opdRegister';"'''
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
print("Update GP:", res.returncode)

t0 = time.time()
curl_cmd = 'curl -k -s -u admin:Admin123 "https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"'
res2 = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", curl_cmd], capture_output=True, text=True, timeout=30)
t1 = time.time()
print(f"Bahmnicore API returned in {t1 - t0:.2f}s!")
print("Response size:", len(res2.stdout))
data = json.loads(res2.stdout)
print("JSON row count:", len(data))
if len(data) > 0:
    print("Record 0:", json.dumps(data[0], indent=2))
