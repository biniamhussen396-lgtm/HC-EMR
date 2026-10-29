import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

def run_cmd(cmd):
    wrapped = f"echo '{pw}' | sudo -S bash -c \"{cmd}\""
    res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", wrapped], capture_output=True, text=True, timeout=25)
    return res.stdout.strip()

check_sql = """
SELECT property, LENGTH(property_value) as len, LEFT(property_value, 60) as sample 
FROM global_property 
WHERE property IN (
    'emrapi.sqlSearch.opdRegister',
    'emrapi.sqlSearch.icuRegister',
    'emrapi.sqlSearch.liaisonRegister',
    'emrapi.sqlSearch.admissionRegister'
);
"""

escaped = check_sql.replace('"', '\\"').replace('\n', ' ')
cmd = f"docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \\\"{escaped}\\\""
print(run_cmd(cmd))
