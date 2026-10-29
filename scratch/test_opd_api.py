import subprocess
import json

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

cmd = '''curl -k -s -u admin:Admin123 "https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"'''
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=25)
print("STDOUT length:", len(res.stdout))
try:
    data = json.loads(res.stdout)
    print("Row count:", len(data))
    if len(data) > 0:
        print("First row keys:", list(data[0].keys()))
        print("First row sample:", json.dumps(data[0], indent=2))
except Exception as e:
    print("JSON parse error:", e)
    print("First 500 chars:", res.stdout[:500])
