import subprocess
import json

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

cmd = "cat /opt/emr/config/openmrs/apps/home/extension.json"
res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", cmd], capture_output=True, text=True, timeout=20)
print("STDOUT len:", len(res.stdout))
print("STDERR:", res.stderr)
with open('scratch/remote_raw.txt', 'w', encoding='utf-8') as f:
    f.write(res.stdout)
remote_json = json.loads(res.stdout.strip())
print("Remote extension keys:", list(remote_json.keys()))
with open('scratch/remote_extension.json', 'w', encoding='utf-8') as f:
    json.dump(remote_json, f, indent=2)
print("Saved remote extension.json to scratch/remote_extension.json")
