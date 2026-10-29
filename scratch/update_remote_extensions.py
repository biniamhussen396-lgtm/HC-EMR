import subprocess

remote_script = """
import json, shutil

# 1. Update /opt/emr/config/openmrs/apps/home/extension.json
home_file = '/opt/emr/config/openmrs/apps/home/extension.json'
shutil.copyfile(home_file, home_file + '.bak')
with open(home_file, 'r') as f:
    home_data = json.load(f)

if 'appointmentScheduling' in home_data:
    home_data['appointmentScheduling']['url'] = '/appointments'
if 'liaisonScheduling' in home_data:
    home_data['liaisonScheduling']['url'] = '/appointments/#/liaisonHome/manage/appointments/waitingList'

with open(home_file, 'w') as f:
    json.dump(home_data, f, indent=2)
print('Updated home/extension.json')

# 2. Update /opt/emr/config/openmrs/apps/adt/extension.json
adt_file = '/opt/emr/config/openmrs/apps/adt/extension.json'
shutil.copyfile(adt_file, adt_file + '.bak')
with open(adt_file, 'r') as f:
    adt_data = json.load(f)

if 'bahmniAdtPatientsSearchPatientsToAppoint' in adt_data:
    adt_data['bahmniAdtPatientsSearchPatientsToAppoint']['extensionParams']['forwardUrl'] = '/appointments/#/home/manage/appointments/list/#/patient/{{patientUuid}}'

with open(adt_file, 'w') as f:
    json.dump(adt_data, f, indent=2)
print('Updated adt/extension.json')

# 3. Update /opt/emr/config/openmrs/apps/ipd/extension.json
ipd_file = '/opt/emr/config/openmrs/apps/ipd/extension.json'
shutil.copyfile(ipd_file, ipd_file + '.bak')
with open(ipd_file, 'r') as f:
    ipd_data = json.load(f)

if 'bahmniAdtPatientsSearchPatientsToAppoint' in ipd_data:
    ipd_data['bahmniAdtPatientsSearchPatientsToAppoint']['extensionParams']['forwardUrl'] = '/appointments/#/home/manage/appointments/list/#/patient/{{patientUuid}}'

with open(ipd_file, 'w') as f:
    json.dump(ipd_data, f, indent=2)
print('Updated ipd/extension.json')
"""

cmd = ['plink', '-batch', '-ssh', '-pw', '   ', 'bmh@192.168.10.5', 'python3 -c "' + remote_script.replace('"', '\\"') + '"']
p = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", p.stdout)
print("STDERR:", p.stderr)
