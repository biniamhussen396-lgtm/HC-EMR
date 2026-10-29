import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

cmd = 'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -N -s -e "SELECT property_value FROM global_property WHERE property = \'emrapi.sqlSearch.opdRegister\';"'
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
with open("scratch/current_remote_opd_query.sql", "w", encoding="utf-8") as f:
    f.write(res.stdout)
print("Saved to scratch/current_remote_opd_query.sql")
