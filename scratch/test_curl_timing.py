import subprocess
import time
import json

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

t0 = time.time()
curl_cmd = 'curl -k -s -u admin:Admin123 "https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"'
res2 = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", curl_cmd], capture_output=True, text=True, timeout=60)
t1 = time.time()
print(f"Curl completed in {t1-t0:.2f}s, RC={res2.returncode}")
print(f"Stdout length: {len(res2.stdout)}")
try:
    data = json.loads(res2.stdout)
    print(f"Record count: {len(data)}")
    if len(data) > 0:
        print("Sample keys:", list(data[0].keys()))
        print("Visit location of row 0:", data[0].get('visit_location'))
        print("Service date of row 0:", data[0].get('service_date'))
        print("TB screened of row 0:", data[0].get('tb_screened'))
        print("HIV offered of row 0:", data[0].get('hiv_offered'))
except Exception as e:
    print("JSON parse error:", e)
    print("Output preview:", res2.stdout[:300])
