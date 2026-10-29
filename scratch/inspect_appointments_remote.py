import subprocess
import json

HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

def run_remote(cmd):
    res = subprocess.run(
        ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return res.returncode, res.stdout, res.stderr

print("=== CHECK OPENMRS MOUNTS ON REMOTE ===")
rc, out, err = run_remote("docker inspect bahmni-standard-openmrs-1 --format '{{json .Mounts}}'")
try:
    mounts = json.loads(out)
    for m in mounts:
        print(f"Type: {m.get('Type')}, Source: {m.get('Source')}, Destination: {m.get('Destination')}")
except Exception as e:
    print("Raw output:", out)
    print("Error:", e)

print("\n=== CHECK APPOINTMENTS CONTAINER MOUNTS ON REMOTE ===")
rc, out, err = run_remote("docker inspect bahmni-standard-appointments-1 --format '{{json .Mounts}}'")
try:
    mounts = json.loads(out)
    for m in mounts:
        print(f"Type: {m.get('Type')}, Source: {m.get('Source')}, Destination: {m.get('Destination')}")
except Exception as e:
    print("Raw output:", out)
    print("Error:", e)

print("\n=== CHECK OPENMRS MODULES ON REMOTE ===")
rc, out, err = run_remote("docker exec bahmni-standard-openmrs-1 ls -la /openmrs/data/modules/ | grep appointments")
print("Remote omod:", out)

print("\n=== CHECK OPENMRS SESSION HTTP STATUS ===")
rc, out, err = run_remote("curl -k -s -o /dev/null -w '%{http_code}' https://127.0.0.1/openmrs/ws/rest/v1/session")
print("Session HTTPS 127.0.0.1 status:", out.strip())
rc, out, err = run_remote("curl -k -s -o /dev/null -w '%{http_code}' https://192.168.10.5/openmrs/ws/rest/v1/session")
print("Session HTTPS 192.168.10.5 status:", out.strip())







