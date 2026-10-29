import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

cmd = 'docker inspect bahmni-standard-bahmni-web-1 --format "{{json .Mounts}}"'
res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", cmd], capture_output=True, text=True, timeout=15)
print("Return code:", res.returncode)
print("Mounts:\n", res.stdout)
if res.stderr:
    print("Error:\n", res.stderr)
