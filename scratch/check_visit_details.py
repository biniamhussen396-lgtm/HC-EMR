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

print("--- 1. TODAY'S VISITS BY VISIT_TYPE (2026-10-28) ---")
sql1 = """
SELECT vt.name, COUNT(*) as cnt 
FROM visit v 
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id 
WHERE DATE(v.date_started) = '2026-10-28' AND v.voided = 0 
GROUP BY vt.name ORDER BY cnt DESC;
"""
print(run_query(sql1))

print("\n--- 2. TODAY'S VISITS BY LOCATION (2026-10-28) ---")
sql2 = """
SELECT l.name, COUNT(*) as cnt 
FROM visit v 
LEFT JOIN location l ON v.location_id = l.location_id 
WHERE DATE(v.date_started) = '2026-10-28' AND v.voided = 0 
GROUP BY l.name ORDER BY cnt DESC;
"""
print(run_query(sql2))

print("\n--- 3. ALL VISIT TYPES IN DB ---")
sql3 = "SELECT visit_type_id, name, description FROM visit_type;"
print(run_query(sql3))
