import subprocess

for tbl in ['bed_patient_assignment_map', 'bed', 'bed_location_map']:
    query = f"DESCRIBE {tbl};"
    cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"--- {tbl} ---")
    print(res.stdout)
