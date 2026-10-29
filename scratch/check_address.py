import subprocess

query = "SELECT person_id, address1, city_village, state_province, county_district, subregion FROM person_address WHERE voided = 0 LIMIT 10;"
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print('person_address samples:')
print(res.stdout)
