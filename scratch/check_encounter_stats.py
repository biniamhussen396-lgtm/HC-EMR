import subprocess

queries = [
    "SELECT e.encounter_type, et.name, count(*) as count FROM encounter e JOIN encounter_type et ON e.encounter_type = et.encounter_type_id GROUP BY e.encounter_type;",
    "SELECT v.visit_type_id, vt.name, count(*) as count FROM visit v JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id GROUP BY v.visit_type_id;"
]

for q in queries:
    cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', q]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
