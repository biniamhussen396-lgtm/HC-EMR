import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=90):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

print(run("curl -s -u admin:Admin123 -k 'https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister' | python3 -c \"import sys,json; data=json.load(sys.stdin); print('opd count:', len(data))\""))
print(run("curl -s -u admin:Admin123 -k 'https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.icuRegister' | python3 -c \"import sys,json; data=json.load(sys.stdin); print('icu count:', len(data))\""))
print(run("curl -s -u admin:Admin123 -k 'https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.liaisonRegister' | python3 -c \"import sys,json; data=json.load(sys.stdin); print('liaison count:', len(data))\""))
