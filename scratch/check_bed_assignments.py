import subprocess

query = "SELECT * FROM bed_patient_assignment_map ORDER BY bed_patient_assignment_map_id DESC LIMIT 10;"
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print('Recent bed_patient_assignment_map rows:')
print(res.stdout)
