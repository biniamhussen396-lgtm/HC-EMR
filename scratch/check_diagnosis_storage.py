import subprocess

queries = [
    "SHOW TABLES LIKE '%diag%';",
    "SELECT * FROM patient_diagnosis LIMIT 5;",
    "SELECT cn.name, o.obs_datetime, o.person_id FROM obs o JOIN concept_name cn ON o.concept_id = cn.concept_id WHERE cn.name LIKE '%diagnosis%' LIMIT 5;"
]

for q in queries:
    cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', q]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
