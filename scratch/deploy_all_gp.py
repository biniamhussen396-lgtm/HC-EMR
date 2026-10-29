import subprocess, json, sys

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=60):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Read local SQL files
with open(r'C:\Users\COMPUTER\Documents\emr\config\masterdata\configuration\sql\emrapi.sqlSearch.opdRegister.sql', 'r', encoding='utf-8') as f:
    opd_sql = f.read()

with open(r'C:\Users\COMPUTER\Documents\emr\config\masterdata\configuration\sql\emrapi.sqlSearch.icuRegister.sql', 'r', encoding='utf-8') as f:
    icu_sql = f.read()

with open(r'C:\Users\COMPUTER\Documents\emr\config\masterdata\configuration\sql\emrapi.sqlSearch.liaisonRegister.sql', 'r', encoding='utf-8') as f:
    liaison_sql = f.read()

with open(r'C:\Users\COMPUTER\Documents\emr\config\masterdata\configuration\sql\emrapi.sqlSearch.admissionRegister.sql', 'r', encoding='utf-8') as f:
    ipd_sql = f.read()

print("Read all 4 SQL files successfully.")

# Prepare Python script to execute on the remote host to update OpenMRS Global Properties via REST API
# We create/update both original and V2 property names!
props = {
    'emrapi.sqlSearch.opdRegisterV2': opd_sql,
    'emrapi.sqlSearch.opdRegister': opd_sql,
    'emrapi.sqlSearch.icuRegisterV2': icu_sql,
    'emrapi.sqlSearch.icuRegister': icu_sql,
    'emrapi.sqlSearch.liaisonRegisterV2': liaison_sql,
    'emrapi.sqlSearch.liaisonRegister': liaison_sql,
    'emrapi.sqlSearch.admissionRegisterV2': ipd_sql,
    'emrapi.sqlSearch.admissionRegister': ipd_sql
}

remote_script = f'''
import urllib.request, json, base64, ssl

props = {repr(props)}
auth = "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 1. Fetch existing settings to know UUIDs
req = urllib.request.Request("https://localhost/openmrs/ws/rest/v1/systemsetting?v=custom:(uuid,property)", headers={{"Authorization": auth}})
with urllib.request.urlopen(req, context=ctx) as resp:
    existing = json.load(resp).get("results", [])
prop_uuid = {{item["property"]: item["uuid"] for item in existing if "property" in item and "uuid" in item}}

for prop_name, prop_val in props.items():
    if prop_name in prop_uuid:
        # Update existing
        uuid = prop_uuid[prop_name]
        url = f"https://localhost/openmrs/ws/rest/v1/systemsetting/{{uuid}}"
        payload = json.dumps({{"value": prop_val}}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={{"Content-Type": "application/json", "Authorization": auth}})
        try:
            with urllib.request.urlopen(req, context=ctx) as r:
                print(f"Updated {{prop_name}} via UUID {{uuid}}: status {{r.status}}")
        except Exception as e:
            print(f"Error updating {{prop_name}}: {{e}}")
    else:
        # Create new
        url = "https://localhost/openmrs/ws/rest/v1/systemsetting"
        payload = json.dumps({{"property": prop_name, "value": prop_val}}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={{"Content-Type": "application/json", "Authorization": auth}})
        try:
            with urllib.request.urlopen(req, context=ctx) as r:
                print(f"Created {{prop_name}}: status {{r.status}}")
        except Exception as e:
            print(f"Error creating {{prop_name}}: {{e}}")
'''

print(run(f"cat << 'EOF' > /tmp/deploy_all_gp.py\n{remote_script}\nEOF"))
print(run("python3 /tmp/deploy_all_gp.py"))
