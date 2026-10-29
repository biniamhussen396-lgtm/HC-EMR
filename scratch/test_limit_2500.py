import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

print(run("docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"REPLACE INTO global_property (property, property_value, uuid) VALUES ('emrapi.sqlSearch.testLimit2500', 'SELECT visit_id, uuid FROM visit ORDER BY visit_id DESC LIMIT 2500;', UUID());\""))
print(run("curl -s -u admin:Admin123 -k 'https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.testLimit2500' | python3 -c \"import sys,json; data=json.load(sys.stdin); print('Returned items for 2500:', len(data))\""))
