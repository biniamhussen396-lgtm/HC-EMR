import ssl
import json
import base64
import urllib.request

HOST = "196.189.94.149"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
auth_header = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")

# 1. Read the SQL from local file
with open(r"C:\Users\COMPUTER\Documents\emr\config\masterdata\configuration\sql\emrapi.sqlSearch.opdRegister.sql", "r", encoding="utf-8") as f:
    sql_text = f.read().strip()

uuid = "5b9475fe-d30f-11f1-8679-6e595c258e3e"
url = f"https://{HOST}/openmrs/ws/rest/v1/systemsetting/{uuid}"

payload = json.dumps({
    "value": sql_text
}).encode('utf-8')

req = urllib.request.Request(url, data=payload, headers={
    'Authorization': auth_header,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}, method='POST')

resp = urllib.request.urlopen(req, context=ctx, timeout=15)
print("Updated system setting via OpenMRS REST API! HTTP", resp.status)

# 2. Test bahmnicore/sql now!
test_url = f"https://{HOST}/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"
req2 = urllib.request.Request(test_url, headers={'Authorization': auth_header, 'Accept': 'application/json'})
resp2 = urllib.request.urlopen(req2, context=ctx, timeout=30)
data = json.loads(resp2.read().decode('utf-8'))
print(f"Now bahmnicore/sql returns {len(data)} rows!")
if data:
    print(f"First row: visit_id={data[0].get('visit_id')}, loc={data[0].get('visit_location')}, date={data[0].get('service_date')}")
