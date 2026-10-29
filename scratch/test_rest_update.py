import subprocess, json

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Test updating via REST API
# Let's read the local emrapi.sqlSearch.opdRegister.sql
with open(r'C:\Users\COMPUTER\Documents\emr\config\masterdata\configuration\sql\emrapi.sqlSearch.opdRegister.sql', 'r', encoding='utf-8') as f:
    opd_sql = f.read()

print("Local opd_sql length:", len(opd_sql))

# Write to remote /tmp/update_opd.py
updater_code = f'''
import urllib.request, json, base64, ssl

sql_content = {repr(opd_sql)}

url = "https://localhost/openmrs/ws/rest/v1/systemsetting/5b9475fe-d30f-11f1-8679-6e595c258e3e"
payload = json.dumps({{"value": sql_content}}).encode("utf-8")

req = urllib.request.Request(url, data=payload, headers={{
    "Content-Type": "application/json",
    "Authorization": "Basic " + base64.b64encode(b"admin:Admin123").decode("ascii")
}})

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        print("Update status:", resp.status)
        res = json.load(resp)
        print("Updated property:", res.get("property"), "len:", len(res.get("value", "")))
except Exception as e:
    print("Error:", e)
    if hasattr(e, "read"):
        print(e.read().decode("utf-8"))
'''

print(run(f"cat << 'EOF' > /tmp/update_opd.py\n{updater_code}\nEOF"))
print(run("python3 /tmp/update_opd.py"))

# Now verify what bahmnicore/sql returns!
print("=== Check bahmnicore/sql row count for opdRegister ===")
print(run("curl -s -u admin:Admin123 -k 'https://localhost/openmrs/ws/rest/v1/bahmnicore/sql?q=emrapi.sqlSearch.opdRegister' | python3 -c \"import sys,json; data=json.load(sys.stdin); print('API returned count:', len(data))\""))
