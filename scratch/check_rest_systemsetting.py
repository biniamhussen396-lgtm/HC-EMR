import ssl
import json
import base64
import urllib.request

HOST = "196.189.94.149"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
auth_header = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")

# 1. Get the global property via REST API
url = f"https://{HOST}/openmrs/ws/rest/v1/systemsetting?q=emrapi.sqlSearch.opdRegister&v=full"
req = urllib.request.Request(url, headers={'Authorization': auth_header, 'Accept': 'application/json'})
resp = urllib.request.urlopen(req, context=ctx, timeout=15)
data = json.loads(resp.read().decode('utf-8'))
results = data.get('results', [])
print(f"Found {len(results)} system settings matching 'emrapi.sqlSearch.opdRegister'")
if results:
    setting = results[0]
    print(f"UUID: {setting.get('uuid')}")
    print(f"Value length: {len(setting.get('value', ''))}")
    print("Value snippet:", setting.get('value', '')[:120])
