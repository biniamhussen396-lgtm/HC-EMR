import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

cmd = '''docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "
SELECT vt.visit_type_id, vt.name, count(v.visit_id) as visit_count 
FROM visit_type vt 
LEFT JOIN visit v ON vt.visit_type_id = v.visit_type_id 
GROUP BY vt.visit_type_id, vt.name 
ORDER BY visit_count DESC;
"'''
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
print(res.stdout)
