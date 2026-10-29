import requests
import time

requests.packages.urllib3.disable_warnings()

url = "https://196.189.94.149/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister"
t0 = time.time()
res = requests.get(url, auth=("admin", "Admin123"), verify=False, timeout=30)
t1 = time.time()
print(f"Request took {t1-t0:.2f}s, status: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    print(f"Returned {len(data)} records!")
    if len(data) > 0:
        first = data[0]
        print("First record:")
        for k in ['mrn', 'patient_name', 'service_date', 'visit_location', 'tb_screened', 'hiv_offered']:
            print(f"  {k}: {first.get(k)}")
else:
    print("Response text:", res.text[:300])
