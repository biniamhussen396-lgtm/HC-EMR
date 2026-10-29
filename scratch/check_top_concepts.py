import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "192.168.10.5"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=30)
    return res.stdout

# 1. Check most common concepts in obs in the last 60 days
print("=== TOP 50 CONCEPTS IN OBS (LAST 60 DAYS) ===")
print(run_query("""
SELECT o.concept_id, cn.name, count(*) as count
FROM obs o
JOIN concept_name cn ON o.concept_id = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
WHERE o.voided = 0 AND o.obs_datetime >= DATE_SUB(NOW(), INTERVAL 60 DAY)
GROUP BY o.concept_id, cn.name
ORDER BY count DESC
LIMIT 50;
"""))
