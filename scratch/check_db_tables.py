import subprocess

query = "SHOW TABLES LIKE '%bed%';"
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print('Bed tables:')
print(res.stdout)

query2 = "SHOW TABLES LIKE '%admission%';"
cmd2 = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query2]
res2 = subprocess.run(cmd2, capture_output=True, text=True)
print('Admission tables:')
print(res2.stdout)
