import subprocess

query = "SELECT property_value FROM global_property WHERE property = 'emrapi.sqlSearch.admittedPatients';"
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-s', '-N', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print('admittedPatients query:')
print(res.stdout)
