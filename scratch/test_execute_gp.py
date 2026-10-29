import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

cmd = '''docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "
SET @sql = (SELECT property_value FROM global_property WHERE property = 'emrapi.sqlSearch.opdRegister');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
"'''

res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=15)
print("Returncode:", res.returncode)
print("STDOUT lines:", len(res.stdout.splitlines()))
print("STDOUT preview:\n", res.stdout[:400])
print("STDERR:\n", res.stderr)
