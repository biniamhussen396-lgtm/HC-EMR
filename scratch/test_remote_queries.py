import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

def run_sudo(cmd):
    wrapped = f"echo '{pw}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", wrapped], capture_output=True, text=True, timeout=30)
    return res.returncode, res.stdout, res.stderr

queries = [
    ("ICU", "config/masterdata/configuration/sql/emrapi.sqlSearch.icuRegister.sql"),
    ("OPD", "config/masterdata/configuration/sql/emrapi.sqlSearch.opdRegister.sql"),
    ("LIAISON", "config/masterdata/configuration/sql/emrapi.sqlSearch.liaisonRegister.sql"),
    ("IPD", "config/masterdata/configuration/sql/emrapi.sqlSearch.admissionRegister.sql"),
]

for name, path in queries:
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read().strip()
    # Replace LIMIT with LIMIT 2 for test
    sql_test = sql.replace("LIMIT 1000;", "LIMIT 2;").replace("LIMIT 500;", "LIMIT 2;")
    escaped = sql_test.replace('"', '\\"')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    rc, out, err = run_sudo(cmd)
    if rc == 0:
        print(f"[{name}] Query SUCCESS! Output rows:\n{out[:200]}...")
    else:
        print(f"[{name}] Query FAILED! Error:\n{err}\n{out}")
