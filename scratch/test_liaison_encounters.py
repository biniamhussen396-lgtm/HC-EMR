import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
    return res.stdout

print("=== LIAISON ENCOUNTER TYPES & LOCATIONS ===")
print(run_query("""
SELECT e.encounter_id, e.encounter_datetime, et.name as enc_type, l.name as loc_name, vt.name as visit_type, pi.identifier as mrn
FROM encounter e
JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
JOIN location l ON e.location_id = l.location_id
JOIN visit v ON e.visit_id = v.visit_id
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
WHERE e.voided = 0 AND (l.location_id = 24 OR vt.visit_type_id = 18)
ORDER BY e.encounter_id DESC
LIMIT 15;
"""))

print("=== OBSERVATIONS IN LIAISON ENCOUNTERS ===")
print(run_query("""
SELECT cn.name, count(*) as count
FROM obs o
JOIN encounter e ON o.encounter_id = e.encounter_id
JOIN concept_name cn ON o.concept_id = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
WHERE o.voided = 0 AND e.location_id = 24
GROUP BY cn.name
ORDER BY count DESC
LIMIT 20;
"""))
