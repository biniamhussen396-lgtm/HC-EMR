import subprocess

query = "SELECT property, LEFT(property_value, 150) FROM global_property WHERE property LIKE '%AdmissionWard%' OR property LIKE '%emrapi.getPatient%';"
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print('STDOUT:')
print(res.stdout)
if res.stderr:
    print('STDERR:')
    print(res.stderr)
