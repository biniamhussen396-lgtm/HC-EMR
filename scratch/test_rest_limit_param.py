import ssl
import json
import base64
import urllib.request

HOST = "196.189.94.149"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
auth_header = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")

for test_param in ["", "&limit=500", "&limit=2000", "&limit=5000", "&v=full"]:
    url = f"https://{HOST}/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister{test_param}"
    try:
        req = urllib.request.Request(url, headers={'Authorization': auth_header, 'Accept': 'application/json'})
        resp = urllib.request.urlopen(req, context=ctx, timeout=30)
        data = json.loads(resp.read().decode('utf-8'))
        print(f"URL param '{test_param}': returned {len(data)} rows")
    except Exception as e:
        print(f"URL param '{test_param}' failed: {e}")
