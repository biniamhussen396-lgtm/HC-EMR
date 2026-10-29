import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

with open(r'C:\Users\COMPUTER\Documents\emr\config\masterdata\configuration\sql\emrapi.sqlSearch.opdRegister.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

script = f'''
import urllib.request, json, base64, ssl

sql_content = {repr(sql)}

url = "https://localhost/openmrs/ws/rest/v1/systemsetting"
payload = json.dumps({{"property": "emrapi.sqlSearch.testOpdNew", "value": sql_content}}).encode("utf-8")

req = urllib.request.Request(url, data=payload, headers={{
    "Content-Type": "application/json",
    "Authorization": "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")
}})

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with urllib.request.urlopen(req, context=ctx) as resp:
    print("Created:", resp.status)
'''

print(run(f"cat << 'EOF' > /tmp/create_test_opd.py\n{script}\nEOF"))
print(run("python3 /tmp/create_test_opd.py"))

print("=== Calling bahmnicore/sql?q=emrapi.sqlSearch.testOpdNew ===")
print(run("curl -s -u admin:Admin123 -k 'https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.testOpdNew' | python3 -c \"import sys,json; data=json.load(sys.stdin); print('Returned items:', len(data))\""))
