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
SELECT c.concept_id, cn.name, COUNT(o.obs_id) as obs_cnt
FROM concept c
JOIN concept_name cn ON c.concept_id = cn.concept_id
LEFT JOIN obs o ON c.concept_id = o.concept_id AND o.voided = 0
WHERE cn.name LIKE '%Referral Out%' OR cn.name LIKE '%Referred Out%' OR cn.name LIKE '%Refer Out%'
GROUP BY c.concept_id, cn.name;
"""
print(run_query(sql))
