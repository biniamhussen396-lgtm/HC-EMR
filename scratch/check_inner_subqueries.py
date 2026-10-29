import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

def run_cmd(sql):
    escaped = sql.replace('"', '\\"').replace('\n', ' ')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", cmd], capture_output=True, text=True, timeout=25)
    return res.stdout.strip()

for prop in ['emrapi.sqlSearch.icuRegister', 'emrapi.sqlSearch.liaisonRegister', 'emrapi.sqlSearch.admissionRegister']:
    print(f"=== {prop} ===")
    sql = f"SELECT SUBSTRING(property_value, LOCATE('FROM (', property_value), 300) as inner_subq FROM global_property WHERE property = '{prop}';"
    print(run_cmd(sql))
