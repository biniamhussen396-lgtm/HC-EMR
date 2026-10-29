import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

def run_remote(cmd):
    res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", cmd], capture_output=True, text=True, timeout=20)
    return res.returncode, res.stdout, res.stderr

rc, out, err = run_remote("grep -n -C 5 'register' /opt/emr/config/openmrs/apps/home/extension.json 2>&1")
print("Extension.json register search on remote:\n", out)

rc, out, err = run_remote("grep -n 'MODULE_LABEL_REGISTER_KEY' /opt/emr/config/openmrs/i18n/home/locale_en.json 2>&1")
print("Locale_en.json register search on remote:\n", out)
