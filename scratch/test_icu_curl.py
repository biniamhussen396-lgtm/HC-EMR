import subprocess
import time

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

t0 = time.time()
cmd = 'curl -k -s -u admin:Admin123 "https://127.0.0.1/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.icuRegister"'
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=30)
t1 = time.time()
print(f"ICU curl completed in {t1-t0:.2f}s, RC={res.returncode}, len={len(res.stdout)}")
