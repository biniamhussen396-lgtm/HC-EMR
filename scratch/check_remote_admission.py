import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

def run_sudo(cmd):
    wrapped = f"echo '{pw}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", wrapped], capture_output=True, text=True, timeout=15)
    return res.returncode, res.stdout, res.stderr

cmd = 'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "SELECT property_value FROM global_property WHERE property = \'emrapi.sqlSearch.admissionRegister\';"'
rc, out, err = run_sudo(cmd)
print("admissionRegister query length on remote:", len(out))
print(out[:500])
