import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

cmd = "ls -ld /opt/emr/apps/ui/app /opt/emr/config"
res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", cmd], capture_output=True, text=True, timeout=15)
print("Return code:", res.returncode)
print("Output:\n", res.stdout)
