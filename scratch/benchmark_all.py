import subprocess
import time

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    t0 = time.time()
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=30)
    t1 = time.time()
    return t1 - t0, res.returncode, res.stdout, res.stderr

queries = [
    ("OPD", "scratch/test_fast_query.py"),
    ("ICU", "scratch/test_icu_super_fast.py"),
    ("LIAISON", "scratch/test_liaison_fast.py"),
    ("IPD", "scratch/test_ipd_fast.py"),
]

for name, script in queries:
    t0 = time.time()
    res = subprocess.run(["python", script], capture_output=True, text=True)
    t1 = time.time()
    print(f"=== {name} REGISTER ===")
    print(f"Overall time: {t1-t0:.2f}s")
    lines = res.stdout.strip().split("\n")
    print(lines[0] if len(lines) > 0 else "No output")
    print(lines[1] if len(lines) > 1 else "")
    print(lines[2] if len(lines) > 2 else "")
    print()
