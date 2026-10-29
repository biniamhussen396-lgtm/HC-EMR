import subprocess

queries = [
    "SELECT COUNT(*) as total_bed_assignments FROM bed_patient_assignment_map;",
    "SELECT encounter_type_id, name FROM encounter_type WHERE name LIKE '%admit%' OR name LIKE '%admission%' OR name LIKE '%discharge%' OR name LIKE '%ipd%';",
    "SELECT visit_type_id, name FROM visit_type WHERE name LIKE '%ipd%' OR name LIKE '%admit%' OR name LIKE '%inpatient%' OR name LIKE '%ward%';",
    "SELECT COUNT(*) as active_visits FROM visit WHERE date_stopped IS NULL AND voided = 0;"
]

for q in queries:
    cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', q]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
