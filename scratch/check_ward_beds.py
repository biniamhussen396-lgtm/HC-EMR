import urllib.request, base64, json

auth = base64.b64encode(b'admin:Admin123').decode()
req = urllib.request.Request(
    'http://localhost:8186/openmrs/ws/rest/v1/admissionLocation',
    headers={'Authorization': f'Basic {auth}'}
)
r = urllib.request.urlopen(req)
data = json.loads(r.read().decode())
for res in data['results']:
    ward = res['ward']
    w_uuid = ward['uuid']
    w_name = ward['name']
    req2 = urllib.request.Request(
        f'http://localhost:8186/openmrs/ws/rest/v1/admissionLocation/{w_uuid}?v=full',
        headers={'Authorization': f'Basic {auth}'}
    )
    r2 = urllib.request.urlopen(req2)
    d2 = json.loads(r2.read().decode())
    print(w_name, 'bedLayouts count:', len(d2.get('bedLayouts', [])))
    if d2.get('bedLayouts'):
        sample = d2['bedLayouts'][0]
        print('  Sample bed:', sample.get('bedNumber'), 'status:', sample.get('status'), 'patients:', sample.get('patients'))
