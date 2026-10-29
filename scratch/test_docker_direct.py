import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

cmd = "docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"SELECT property FROM global_property WHERE property LIKE 'emrapi.sqlSearch.%';\""
res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", cmd], capture_output=True, text=True, timeout=15)
print("Return code:", res.returncode)
print("Output:\n", res.stdout)
if res.stderr:
    print("Stderr:\n", res.stderr)
