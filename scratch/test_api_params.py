import ssl
import json
import base64
import urllib.request

HOST = "196.189.94.149"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
auth_header = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")

# Test 1: Can we pass startDate / endDate to bahmnicore/sql?
# Let's check how bahmnicore/sql handles query params
url = f"https://{HOST}/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"
req = urllib.request.Request(url, headers={'Authorization': auth_header, 'Accept': 'application/json'})
resp = urllib.request.urlopen(req, context=ctx, timeout=15)
data = json.loads(resp.read().decode('utf-8'))
print(f"Base query returned {len(data)} rows.")
