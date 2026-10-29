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

sql = """
SELECT vl.name as visit_location, vt.name as visit_type, COUNT(*) as cnt
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
LEFT JOIN location vl ON v.location_id = vl.location_id
WHERE DATE(v.date_started) = '2026-10-28' AND v.voided = 0
GROUP BY vl.name, vt.name
ORDER BY cnt DESC;
"""
print(run_query(sql))
