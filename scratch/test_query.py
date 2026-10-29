import subprocess

with open('config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# Replace ${location_uuid} with '266bc297-9b52-4ece-b96c-f3b31b09f838'
sql = sql.replace("${location_uuid}", "'266bc297-9b52-4ece-b96c-f3b31b09f838'")

res = subprocess.run(
    ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs'],
    input=sql.encode('utf-8'),
    capture_output=True
)

out = res.stdout.decode('utf-8', errors='ignore')
print("OUT:", out[:1000])
if res.stderr:
    print("ERR:", res.stderr.decode('utf-8', errors='ignore'))
