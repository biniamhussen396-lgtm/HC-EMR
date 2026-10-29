import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

cmd = '''docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "
SELECT e.encounter_id, e.visit_id, vt.name as visit_type, el.name as encounter_location, vl.name as visit_location 
FROM encounter e 
JOIN visit v ON e.visit_id = v.visit_id 
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
LEFT JOIN location el ON e.location_id = el.location_id
LEFT JOIN location vl ON v.location_id = vl.location_id
WHERE v.voided = 0 AND e.voided = 0
ORDER BY e.encounter_id DESC LIMIT 10;
"'''
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
print("Latest encounter locations:\n", res.stdout)
