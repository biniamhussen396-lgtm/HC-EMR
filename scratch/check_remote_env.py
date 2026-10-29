import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

def run_sudo(cmd):
    wrapped = f"echo '{pw}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", wrapped], capture_output=True, text=True, timeout=30)
    return res.returncode, res.stdout, res.stderr

print("Checking remote .env MYSQL and OPENMRS settings...")
rc, out, err = run_sudo("grep -E 'MYSQL|OPENMRS_DB' /opt/emr/bahmni-docker/bahmni-standard/.env 2>&1")
print(out)
