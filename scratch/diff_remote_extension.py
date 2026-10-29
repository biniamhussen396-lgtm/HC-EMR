import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

def run_remote(cmd):
    res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", cmd], capture_output=True, text=True, timeout=20)
    return res.returncode, res.stdout, res.stderr

rc, out, err = run_remote("wc -l /opt/emr/config/openmrs/apps/home/extension.json; md5sum /opt/emr/config/openmrs/apps/home/extension.json")
print("Remote extension.json:\n", out)
