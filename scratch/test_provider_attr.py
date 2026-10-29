import subprocess, json

payload = json.dumps({'attributeType': 'e2aaac17-5e07-11ef-8f7c-0242ac120002', 'value': True})
remote_cmd = f"curl -k -s -u admin:Admin123 -X POST -H 'Content-Type: application/json' -d '{payload}' 'https://127.0.0.1/openmrs/ws/rest/v1/provider/784d88ef-6562-4a5a-a938-d3bb9c78249c/attribute'"
cmd = ['plink', '-batch', '-ssh', '-pw', '   ', 'bmh@192.168.10.5', remote_cmd]
res = subprocess.run(cmd, capture_output=True, text=True)
print("Response:", res.stdout[:500])
