import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

remote_py = '''
import json, urllib.request, base64, ssl
from collections import Counter

req = urllib.request.Request("https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister")
auth = base64.b64encode(b"admin:Admin123").decode("ascii")
req.add_header("Authorization", "Basic " + auth)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with urllib.request.urlopen(req, context=ctx) as resp:
    data = json.load(resp)
    print("Total records returned by API:", len(data))
    dates = [r.get("service_date", "")[:10] for r in data]
    print("Dates breakdown:", Counter(dates))
'''

# Write to remote /tmp/check_api.py and run
import tempfile
print(run(f"cat << 'EOF' > /tmp/check_api.py\n{remote_py}\nEOF"))
print(run("python3 /tmp/check_api.py"))
