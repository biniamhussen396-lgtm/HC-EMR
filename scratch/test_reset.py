import urllib.request
import json
import base64
import subprocess

auth = base64.b64encode(b'admin:Admin123').decode()
url = 'http://localhost:8186/openmrs/ws/rest/v1/appointments/04eab431-6e8d-40d5-b2b3-e96268ce689a/status-change'

for st in ['CheckedIn', 'Completed', 'Cancelled', 'Missed']:
    subprocess.run(['docker', 'exec', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', f"UPDATE patient_appointment SET status='{st}' WHERE patient_appointment_id=2;"], capture_output=True)
    data = json.dumps({'toStatus': 'Scheduled'}).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Basic {auth}'})
    try:
        with urllib.request.urlopen(req) as resp:
            print(f'Reset from {st} -> Scheduled: SUCCESS', resp.status)
    except urllib.error.HTTPError as e:
        print(f'Reset from {st} -> Scheduled ERROR:', e.code)

# Restore to Scheduled
subprocess.run(['docker', 'exec', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', "UPDATE patient_appointment SET status='Scheduled' WHERE patient_appointment_id=2;"], capture_output=True)
