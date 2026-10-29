import subprocess

query = "SELECT person_id, city_village, address1, address2, address3, address4, address5, state_province FROM person_address WHERE voided = 0 AND (city_village IS NOT NULL OR address1 IS NOT NULL) LIMIT 5;"
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
