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

print("OPD REGISTER GP:")
print(run_cmd("SELECT property, property_value IS NULL as is_null, LENGTH(property_value) as val_len FROM global_property WHERE property = 'emrapi.sqlSearch.opdRegister';"))

print("\nICU REGISTER GP (first 250 chars):")
print(run_cmd("SELECT property, SUBSTRING(property_value, 1, 250) as snippet FROM global_property WHERE property = 'emrapi.sqlSearch.icuRegister';"))

print("\nLIAISON REGISTER GP (first 250 chars):")
print(run_cmd("SELECT property, SUBSTRING(property_value, 1, 250) as snippet FROM global_property WHERE property = 'emrapi.sqlSearch.liaisonRegister';"))

print("\nIPD REGISTER GP (first 250 chars):")
print(run_cmd("SELECT property, SUBSTRING(property_value, 1, 250) as snippet FROM global_property WHERE property = 'emrapi.sqlSearch.admissionRegister';"))
