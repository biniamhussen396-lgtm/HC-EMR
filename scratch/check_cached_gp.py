import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Let's check what OpenMRS REST API returns for the global property value:
# GET /openmrs/ws/rest/v1/systemsetting?q=emrapi.sqlSearch.opdRegister
# Or GET /openmrs/ws/rest/v1/bahmnicore/sql/globalproperty?property=emrapi.sqlSearch.opdRegister
print(run("curl -s -u admin:Admin123 -k 'https://localhost/openmrs/ws/rest/v1/bahmnicore/sql/globalproperty?property=emrapi.sqlSearch.opdRegister' | grep -i 'limit'"))
