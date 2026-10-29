import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

cmd = 'curl -k -v -u admin:Admin123 "https://127.0.0.1/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"'
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
print("Returncode:", res.returncode)
print("STDOUT:\n", res.stdout[:500])
print("STDERR:\n", res.stderr[:500])
