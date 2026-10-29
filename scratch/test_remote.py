import subprocess
import os

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

cmd = "hostname; uptime; docker ps --format '{{.Names}}' | head -n 10"
res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", cmd], capture_output=True, text=True, timeout=15)
print("Return code:", res.returncode)
print("Output:\n", res.stdout)
if res.stderr:
    print("Error:\n", res.stderr)
