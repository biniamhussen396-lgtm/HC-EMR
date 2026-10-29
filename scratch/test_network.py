import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

cmd = 'curl -k --connect-timeout 3 -m 5 -I https://localhost/bahmni/home/ ; curl -k --connect-timeout 3 -m 5 -I https://196.189.94.149/bahmni/home/ ; docker exec bahmni-standard-openmrs-1 curl -s -I http://localhost:8080/openmrs/'
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
print("Returncode:", res.returncode)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
