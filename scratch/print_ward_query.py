import subprocess

query = "SELECT property_value FROM global_property WHERE property = 'emrapi.getPatientAdmissionWard';"
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-s', '-N', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print('Query:')
print(res.stdout)
