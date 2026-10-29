import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"').replace('\n', ' ')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=30)
    return res.stdout.strip()

sql = """
SELECT cn.name, COUNT(*) as cnt
FROM obs o
JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
WHERE o.concept_id = 32 AND o.voided = 0
GROUP BY cn.name;
"""
print(run_query(sql))
