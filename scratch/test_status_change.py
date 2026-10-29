import urllib.request
import json
import base64
import subprocess

# Set status to Missed
subprocess.run(['docker', 'exec', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', "UPDATE patient_appointment SET status='Missed' WHERE patient_appointment_id=2;"])

auth = base64.b64encode(b'admin:Admin123').decode()
url = 'http://localhost:8186/openmrs/ws/rest/v1/appointments/04eab431-6e8d-40d5-b2b3-e96268ce689a/status-change'

# 1. Test change to Scheduled
data = json.dumps({'toStatus': 'Scheduled'}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Basic {auth}'})
try:
    with urllib.request.urlopen(req) as resp:
        print('Change to Scheduled: SUCCESS', resp.status, resp.read().decode())
except urllib.error.HTTPError as e:
    err_text = e.read().decode()
    try:
        err_json = json.loads(err_text)
        print('Change to Scheduled: ERROR', e.code, err_json.get('error', {}).get('message', err_text[:300]))
    except:
        print('Change to Scheduled: ERROR', e.code, err_text[:300])

# 2. Test direct Missed -> CheckedIn
subprocess.run(['docker', 'exec', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', "UPDATE patient_appointment SET status='Missed' WHERE patient_appointment_id=2;"])
data = json.dumps({'toStatus': 'CheckedIn'}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Basic {auth}'})
try:
    with urllib.request.urlopen(req) as resp:
        print('Direct Missed -> CheckedIn: SUCCESS', resp.status)
except urllib.error.HTTPError as e:
    print('Direct Missed -> CheckedIn ERROR:', e.code, e.read().decode()[:300])

# 3. Test direct Missed -> Cancelled
subprocess.run(['docker', 'exec', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', "UPDATE patient_appointment SET status='Missed' WHERE patient_appointment_id=2;"])
data = json.dumps({'toStatus': 'Cancelled'}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Basic {auth}'})
try:
    with urllib.request.urlopen(req) as resp:
        print('Direct Missed -> Cancelled: SUCCESS', resp.status)
except urllib.error.HTTPError as e:
    print('Direct Missed -> Cancelled ERROR:', e.code, e.read().decode()[:300])

# Reset back to Scheduled
data = json.dumps({'toStatus': 'Scheduled'}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Basic {auth}'})
try:
    with urllib.request.urlopen(req) as resp:
        print('Reset to Scheduled: SUCCESS', resp.status)
except urllib.error.HTTPError as e:
    print('Reset to Scheduled ERROR:', e.code, e.read().decode()[:300])
