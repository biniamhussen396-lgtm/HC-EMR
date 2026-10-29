import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"').replace('\n', ' ')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=30)
    return res.stdout.strip()

print("Global properties containing 'opdRegister':")
print(run_query("SELECT property, LENGTH(property_value) as len FROM global_property WHERE property LIKE '%opdRegister%';"))

print("\nGlobal properties containing 'BORUMEDA GENERAL HOSPITAL':")
print(run_query("SELECT property, LENGTH(property_value) as len FROM global_property WHERE property_value LIKE '%BORUMEDA GENERAL HOSPITAL%';"))
