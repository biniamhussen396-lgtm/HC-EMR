import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Test running a simple query via bahmnicore/sql with 500 rows to see if bahmnicore/sql itself limits to 200!
print("=== Creating test GP with 500 rows ===")
print(run("docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"REPLACE INTO global_property (property, property_value, uuid) VALUES ('emrapi.sqlSearch.testLimit', 'SELECT visit_id FROM visit ORDER BY visit_id DESC LIMIT 500;', UUID());\""))

print("=== Calling bahmnicore/sql?q=emrapi.sqlSearch.testLimit ===")
print(run("curl -s -u admin:Admin123 -k 'https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.testLimit' | python3 -c \"import sys,json; data=json.load(sys.stdin); print('Returned items:', len(data))\""))
