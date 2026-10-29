import subprocess
import time

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

t0 = time.time()
curl_cmd = 'curl -k -s -u admin:Admin123 "https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"'
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", curl_cmd], capture_output=True, text=True, timeout=60)
t1 = time.time()
print(f"Elapsed: {t1-t0:.2f}s")
print("RC:", res.returncode)
print("Output length:", len(res.stdout))
print("First 500 chars:")
print(res.stdout[:500])
