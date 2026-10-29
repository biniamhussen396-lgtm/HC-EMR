import subprocess, sys

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=60):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Test bahmnicore/sql API row count via curl on the server
# (avoid downloading 2500 rows through our connection)
test_cmd = (
    "curl -s -u admin:Admin123 -k "
    "'https://localhost/openmrs/ws/rest/v1/bahmnicore/sql"
    "?q=emrapi.sqlSearch.opdRegister' "
    "| python3 -c \"import sys,json; data=json.load(sys.stdin); "
    "print('Row count:', len(data)); "
    "print('First visit_date:', data[0].get('visit_date','?') if data else 'EMPTY')\""
)
print('=== API Row Count Test ===')
print(run(test_cmd, timeout=120))
