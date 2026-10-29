import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "192.168.10.5"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=30)
    return res.stdout

print("=== 1. VISIT TYPES ===")
print(run_query("SELECT visit_type_id, name, description FROM visit_type WHERE retired = 0;"))

print("=== 2. ENCOUNTER TYPES ===")
print(run_query("SELECT encounter_type_id, name, description FROM encounter_type WHERE retired = 0;"))

print("=== 3. RECENT ENCOUNTERS BY TYPE (LAST 30 DAYS) ===")
print(run_query("""
SELECT et.name as encounter_type, count(*) as count
FROM encounter e
JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
WHERE e.voided = 0 AND e.encounter_datetime >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY et.name
ORDER BY count DESC;
"""))

print("=== 4. RECENT VISITS BY TYPE (LAST 30 DAYS) ===")
print(run_query("""
SELECT vt.name as visit_type, count(*) as count
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
WHERE v.voided = 0 AND v.date_started >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY vt.name
ORDER BY count DESC;
"""))
