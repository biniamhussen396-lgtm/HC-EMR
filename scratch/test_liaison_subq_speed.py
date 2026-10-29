import subprocess
import time

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"').replace('\n', ' ')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    t0 = time.time()
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=30)
    t1 = time.time()
    return t1 - t0, res.returncode, res.stdout, res.stderr

sql_test = """
SELECT COUNT(DISTINCT visit_id) FROM (
    (SELECT visit_id FROM encounter WHERE location_id = 24 AND voided = 0 ORDER BY encounter_id DESC LIMIT 300)
    UNION
    (SELECT visit_id FROM encounter WHERE encounter_type IN (3, 4, 5) AND voided = 0 ORDER BY encounter_id DESC LIMIT 300)
) t;
"""
t, rc, out, err = run_query(sql_test)
print(f"Time: {t:.2f}s, Out: {out.strip()}")
