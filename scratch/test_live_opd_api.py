import ssl
import json
import base64
import urllib.request
import time

HOST = "196.189.94.149"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
auth_header = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")

url = f"https://{HOST}/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"
t0 = time.time()
req = urllib.request.Request(url, headers={'Authorization': auth_header, 'Accept': 'application/json'})
resp = urllib.request.urlopen(req, context=ctx, timeout=60)
data = json.loads(resp.read().decode('utf-8'))
elapsed = time.time() - t0
print(f"OPD Register REST API returned {len(data)} rows in {elapsed:.2f}s!")

# Check how many from today (2026-10-28)
today_cnt = sum(1 for r in data if r.get('service_date', '').startswith('2026-10-28'))
print(f"Of which {today_cnt} visits are from today (2026-10-28)!")
