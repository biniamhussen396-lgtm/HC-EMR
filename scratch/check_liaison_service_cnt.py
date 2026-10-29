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
SELECT 
    COUNT(DISTINCT v.visit_id) as total_referral_visits,
    SUM(IF(DATE(v.date_started) = '2026-10-28', 1, 0)) as today_referral_visits
FROM visit v
JOIN encounter e ON v.visit_id = e.visit_id AND e.voided = 0
LEFT JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0
WHERE v.voided = 0
  AND (
      e.location_id = 24 
      OR v.visit_type_id = 18 
      OR o.concept_id IN (61954, 67271, 60880, 67272, 67273, 69611, 69612, 69620, 68984, 68985, 21895)
      OR o.value_coded IN (SELECT concept_id FROM concept_name WHERE name IN ('Refer Patient', 'Transfer Patient') AND voided = 0)
  );
"""
print(run_query(sql))
