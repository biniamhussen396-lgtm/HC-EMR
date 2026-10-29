import ssl
import json
import base64
import urllib.request

HOST = "196.189.94.149"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
auth_header = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")

url = f"https://{HOST}/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"
req = urllib.request.Request(url, headers={'Authorization': auth_header, 'Accept': 'application/json'})
resp = urllib.request.urlopen(req, context=ctx, timeout=30)
data = json.loads(resp.read().decode('utf-8'))
print(f"Total rows returned by REST API: {len(data)}")
if data:
    print(f"First row: visit_id={data[0].get('visit_id')}, loc={data[0].get('visit_location')}, date={data[0].get('service_date')}")
    print(f"Last row: visit_id={data[-1].get('visit_id')}, loc={data[-1].get('visit_location')}, date={data[-1].get('service_date')}")
