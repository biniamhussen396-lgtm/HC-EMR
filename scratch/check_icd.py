import subprocess

query = "SELECT concept_source_id, name FROM concept_reference_source WHERE name LIKE '%ICD%' OR name LIKE '%ESV%';"
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
