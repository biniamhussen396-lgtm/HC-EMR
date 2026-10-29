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

print("=== 1. ICU REGISTER TARGET VISITS ===")
print(run_query("""
SELECT count(DISTINCT e.visit_id) as total_icu_visits
FROM encounter e
JOIN location l ON e.location_id = l.location_id
JOIN visit v ON e.visit_id = v.visit_id
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
WHERE e.voided = 0 AND (l.name LIKE '%ICU%' OR vt.name LIKE '%ICU%');
"""))

print("=== 2. LIAISON REGISTER TARGET VISITS ===")
print(run_query("""
SELECT count(DISTINCT e.visit_id) as total_liaison_visits
FROM encounter e
JOIN location l ON e.location_id = l.location_id
JOIN visit v ON e.visit_id = v.visit_id
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
WHERE e.voided = 0 AND (l.name = 'Liaison' OR vt.name = 'Liaison');
"""))

print("=== 3. IPD REGISTER TARGET VISITS ===")
print(run_query("""
SELECT count(DISTINCT e.visit_id) as total_ipd_visits
FROM encounter e
JOIN location l ON e.location_id = l.location_id
JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
JOIN visit v ON e.visit_id = v.visit_id
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
WHERE e.voided = 0 AND (l.name LIKE '%Ward%' OR vt.name LIKE '%Ward%' OR et.name IN ('ADMISSION', 'DISCHARGE', 'TRANSFER'));
"""))

print("=== 4. OPD REGISTER TARGET VISITS ===")
print(run_query("""
SELECT count(DISTINCT e.visit_id) as total_opd_visits
FROM encounter e
JOIN location l ON e.location_id = l.location_id
JOIN visit v ON e.visit_id = v.visit_id
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
WHERE e.voided = 0 AND (l.name LIKE '%OPD%' OR l.name LIKE '%ER%' OR l.name LIKE '%Triage%' OR vt.name LIKE '%OPD%' OR vt.name LIKE '%ER%')
  AND l.name NOT LIKE '%Ward%' AND vt.name NOT LIKE '%Ward%';
"""))
