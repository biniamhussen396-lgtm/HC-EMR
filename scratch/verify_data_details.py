import ssl
import json
import base64
import urllib.request

HOST = "196.189.94.149"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
auth_header = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")

endpoints = [
    ("OPD", "emrapi.sqlSearch.opdRegister"),
    ("ICU", "emrapi.sqlSearch.icuRegister"),
    ("LIAISON", "emrapi.sqlSearch.liaisonRegister"),
    ("IPD", "emrapi.sqlSearch.admissionRegister"),
]

for name, q in endpoints:
    url = f"https://{HOST}/openmrs/ws/rest/v1/bahmnicore/sql?q={q}"
    req = urllib.request.Request(url, headers={'Authorization': auth_header, 'Accept': 'application/json'})
    resp = urllib.request.urlopen(req, context=ctx, timeout=30)
    data = json.loads(resp.read().decode('utf-8'))
    print(f"\n==================== {name} REGISTER ({len(data)} records) ====================")
    for i, row in enumerate(data[:3]):
        print(f"--- Row {i+1} ---")
        for k, v in row.items():
            if v and v != '-' and v != 'No':
                print(f"  {k}: {v}")
