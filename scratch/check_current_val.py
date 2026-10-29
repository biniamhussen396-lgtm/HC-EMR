import ssl
import json
import base64
import urllib.request

HOST = "196.189.94.149"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
auth_header = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")

url = f"https://{HOST}/openmrs/ws/rest/v1/systemsetting?q=emrapi.sqlSearch.opdRegister&v=full"
req = urllib.request.Request(url, headers={'Authorization': auth_header, 'Accept': 'application/json'})
resp = urllib.request.urlopen(req, context=ctx, timeout=15)
data = json.loads(resp.read().decode('utf-8'))
val = data['results'][0]['value']
print("Length of value:", len(val))
print("Contains LIMIT 2500?", "LIMIT 2500" in val)
print("Contains LIMIT 200?", "LIMIT 200" in val)
print("Contains NICU Ward in SELECT?", "NICU" in val)
print("Contains CASE WHEN vl.name?", "CASE \n        WHEN vl.name IS NOT NULL" in val)
