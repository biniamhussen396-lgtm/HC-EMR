import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

script = """
import json, urllib.request

req = urllib.request.Request('https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister')
import base64
auth = base64.b64encode(b'admin:Admin123').decode('ascii')
req.add_header('Authorization', f'Basic {auth}')
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with urllib.request.urlopen(req, context=ctx) as resp:
    data = json.load(resp)
    print("Len:", len(data))
    dates = [r.get('service_date', '')[:10] for r in data]
    from collections import Counter
    print("Dates breakdown:", Counter(dates))
"""
print(run(f"python3 -c \"{script}\""))
