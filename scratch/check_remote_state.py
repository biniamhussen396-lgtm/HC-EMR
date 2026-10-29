import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

def run_sudo(cmd):
    wrapped = f"echo '{pw}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", wrapped], capture_output=True, text=True, timeout=30)
    return res.returncode, res.stdout, res.stderr

print("Checking remote /opt/emr/apps/ui/app/register...")
rc, out, err = run_sudo("ls -la /opt/emr/apps/ui/app/register 2>&1")
print(out)

print("Checking OpenMRS privilege app:register on remote...")
rc, out, err = run_sudo("docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -ppassword openmrs -e \"SELECT * FROM privilege WHERE privilege = 'app:register'; SELECT * FROM role_privilege WHERE privilege = 'app:register';\" 2>&1")
print(out)

print("Checking SQL searches in OpenMRS on remote...")
rc, out, err = run_sudo("docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -ppassword openmrs -e \"SELECT property FROM global_property WHERE property LIKE '%Register%' OR property LIKE '%register%';\" 2>&1")
print(out)
