import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=60):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Check what format service_date comes as from bahmnicore/sql API
# Check first 3 rows including visit_date field
test_cmd = (
    "curl -s -u admin:Admin123 -k "
    "'https://localhost/openmrs/ws/rest/v1/bahmnicore/sql"
    "?q=emrapi.sqlSearch.opdRegister' "
    "| python3 -c \""
    "import sys,json; data=json.load(sys.stdin); "
    "[print(r.get('service_date'), '|', r.get('visit_date'), '|', r.get('patient_name','?')) for r in data[:5]]"
    "\""
)
print('=== service_date format check ===')
print(run(test_cmd, timeout=90))

# Also check what row count comes back now that batchSize=2500
count_cmd = (
    "curl -s -u admin:Admin123 -k "
    "'https://localhost/openmrs/ws/rest/v1/bahmnicore/sql"
    "?q=emrapi.sqlSearch.opdRegister' "
    "| python3 -c \"import sys,json; data=json.load(sys.stdin); print('Total rows:', len(data))\""
)
print('=== Row count after batchSize=2500 ===')
print(run(count_cmd, timeout=90))
