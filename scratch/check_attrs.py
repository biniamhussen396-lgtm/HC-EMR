import subprocess

queries = [
    "SELECT count(*) as addr_count FROM person_address;",
    "SELECT pat.name, count(*) as count FROM person_attribute pa JOIN person_attribute_type pat ON pa.person_attribute_type_id = pat.person_attribute_type_id GROUP BY pat.name;"
]
for q in queries:
    cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', q]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
