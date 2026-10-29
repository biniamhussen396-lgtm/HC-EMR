import subprocess
import time
import json

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

# 1. Update the global property on remote MySQL
update_gp_sql = """
UPDATE global_property 
SET property_value = (SELECT LOAD_FILE('/tmp/optimized_opd.sql'))
WHERE property = 'emrapi.sqlSearch.opdRegister';
"""

# Or update directly via python reading the file
with open('scratch/optimized_opd.sql', 'r', encoding='utf-8') as f:
    sql_text = f.read().strip()

escaped = sql_text.replace("'", "''")
cmd = f'''docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "UPDATE global_property SET property_value = '{escaped}' WHERE property = 'emrapi.sqlSearch.opdRegister';"'''
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
print("Update GP result:", res.returncode, res.stdout, res.stderr)

# 2. Test Bahmni Core API call
t0 = time.time()
curl_cmd = 'curl -k -s -u admin:Admin123 "https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"'
res2 = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", curl_cmd], capture_output=True, text=True, timeout=60)
t1 = time.time()
print(f"API call completed in {t1-t0:.2f}s!")
print("Response length:", len(res2.stdout))
try:
    data = json.loads(res2.stdout)
    print("Parsed JSON records count:", len(data))
    if len(data) > 0:
        print("Record 1:", json.dumps(data[0], indent=2))
except Exception as e:
    print("JSON parse error:", e)
    print("First 300 chars:", res2.stdout[:300])
