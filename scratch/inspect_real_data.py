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

print("=== 1. REAL ICU ENCOUNTERS (location_id=261 or name LIKE '%ICU%') ===")
print(run_query("""
SELECT e.encounter_id, e.encounter_datetime, et.name as enc_type, l.name as loc_name, v.visit_id, vt.name as visit_type, pi.identifier as mrn
FROM encounter e
JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
JOIN location l ON e.location_id = l.location_id
JOIN visit v ON e.visit_id = v.visit_id
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
WHERE e.voided = 0 AND (l.name LIKE '%ICU%' OR vt.name LIKE '%ICU%')
ORDER BY e.encounter_id DESC
LIMIT 10;
"""))

print("=== 2. REAL LIAISON ENCOUNTERS (location_id=24 or vt.name='Liaison' or with referral obs) ===")
print(run_query("""
SELECT e.encounter_id, e.encounter_datetime, et.name as enc_type, l.name as loc_name, v.visit_id, vt.name as visit_type, pi.identifier as mrn
FROM encounter e
JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
JOIN location l ON e.location_id = l.location_id
JOIN visit v ON e.visit_id = v.visit_id
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
WHERE e.voided = 0 AND (l.name = 'Liaison' OR vt.name = 'Liaison')
ORDER BY e.encounter_id DESC
LIMIT 10;
"""))

print("=== 3. REAL IPD / WARD ENCOUNTERS ===")
print(run_query("""
SELECT e.encounter_id, e.encounter_datetime, et.name as enc_type, l.name as loc_name, v.visit_id, vt.name as visit_type, pi.identifier as mrn
FROM encounter e
JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
JOIN location l ON e.location_id = l.location_id
JOIN visit v ON e.visit_id = v.visit_id
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
WHERE e.voided = 0 AND (et.name IN ('ADMISSION', 'DISCHARGE', 'TRANSFER') OR l.name LIKE '%Ward%')
ORDER BY e.encounter_id DESC
LIMIT 10;
"""))
