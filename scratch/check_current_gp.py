import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

cmd = 'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -N -s -e "SELECT property_value FROM global_property WHERE property = \'emrapi.sqlSearch.opdRegister\';"'
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
val = res.stdout.strip()
print("Total length:", len(val))
print("Contains 'v_inner':", "v_inner" in val)
print("Contains 'IFNULL(screening.tb_screened, ''Yes'')':", "IFNULL(screening.tb_screened, 'Yes')" in val)
print("Contains 'visit_location':", "visit_location" in val)
