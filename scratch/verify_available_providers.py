import subprocess, json

cmd = ['plink', '-batch', '-ssh', '-pw', '   ', 'bmh@192.168.10.5', "curl -k -s -u admin:Admin123 'https://127.0.0.1/openmrs/ws/rest/v1/provider?limit=1000&v=custom:(display,person,uuid,identifier,retired,attributes:(uuid,attributeType:(uuid,display),value,voided))'"]
out = subprocess.run(cmd, capture_output=True, text=True).stdout
data = json.loads(out)
results = data.get('results', [])
available = []
for p in results:
    if p.get('retired'): continue
    for a in p.get('attributes', []):
        if not a.get('voided') and a.get('attributeType', {}).get('display') == 'Available for appointments' and str(a.get('value')).lower() == 'true':
            available.append((p.get('uuid'), (p.get('person') or {}).get('display') or p.get('display')))
print(f'Total active providers: {len(results)}')
print(f'Total currently available for appointments: {len(available)}')
for uuid, name in available:
    print(' -', name, f'({uuid})')
