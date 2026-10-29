import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=25)
    return res.stdout

print("=== 1. VISITS COUNT BY VISIT TYPE (ALL TIME) ===")
print(run_query("""
SELECT vt.visit_type_id, vt.name, count(*) as count
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
WHERE v.voided = 0
GROUP BY vt.visit_type_id, vt.name
ORDER BY count DESC
LIMIT 40;
"""))

print("=== 2. ENCOUNTER LOCATIONS (TOP 30) ===")
print(run_query("""
SELECT l.location_id, l.name, count(*) as count
FROM encounter e
JOIN location l ON e.location_id = l.location_id
WHERE e.voided = 0
GROUP BY l.location_id, l.name
ORDER BY count DESC
LIMIT 30;
"""))
