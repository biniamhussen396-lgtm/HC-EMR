import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "192.168.10.5"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
    return res.stdout

print("=== 1. ICU VISITS & ENCOUNTERS ===")
print(run_query("""
SELECT v.visit_id, v.date_started, vt.name as visit_type, e.encounter_id, et.name as enc_type, l.name as loc_name
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
LEFT JOIN encounter e ON v.visit_id = e.visit_id AND e.voided = 0
LEFT JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
LEFT JOIN location l ON e.location_id = l.location_id
WHERE v.voided = 0 AND (vt.name LIKE '%ICU%' OR vt.name LIKE '%HDU%')
ORDER BY v.visit_id DESC
LIMIT 10;
"""))

print("=== 2. LIAISON VISITS & ENCOUNTERS ===")
print(run_query("""
SELECT v.visit_id, v.date_started, vt.name as visit_type, e.encounter_id, et.name as enc_type, l.name as loc_name
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
LEFT JOIN encounter e ON v.visit_id = e.visit_id AND e.voided = 0
LEFT JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
LEFT JOIN location l ON e.location_id = l.location_id
WHERE v.voided = 0 AND vt.name = 'Liaison'
ORDER BY v.visit_id DESC
LIMIT 10;
"""))

print("=== 3. IPD / ADMISSION / DISCHARGE ENCOUNTERS ===")
print(run_query("""
SELECT e.encounter_id, e.encounter_datetime, et.name as enc_type, vt.name as visit_type, l.name as loc_name
FROM encounter e
JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
JOIN visit v ON e.visit_id = v.visit_id
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
LEFT JOIN location l ON e.location_id = l.location_id
WHERE e.voided = 0 AND et.name IN ('ADMISSION', 'DISCHARGE', 'TRANSFER')
ORDER BY e.encounter_id DESC
LIMIT 10;
"""))
