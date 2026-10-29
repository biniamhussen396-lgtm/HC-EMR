import subprocess

query = "SELECT property, LEFT(property_value, 200) FROM global_property WHERE property LIKE 'emrapi.sqlSearch.%' LIMIT 10;"
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print('STDOUT:')
print(res.stdout)
