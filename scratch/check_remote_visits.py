import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

cmd = 'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "SELECT property_value FROM global_property WHERE property = \'emrapi.sqlSearch.opdRegister\';" > /tmp/opd_query.txt'
subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)

cmd2 = 'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "SELECT v.visit_id, v.date_started, v.location_id, l.name as visit_location, vt.name as visit_type FROM visit v JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id LEFT JOIN location l ON v.location_id = l.location_id WHERE v.voided = 0 ORDER BY v.visit_id DESC LIMIT 5;"'
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd2], capture_output=True, text=True, timeout=20)
print("Latest visits on remote:\n", res.stdout)
