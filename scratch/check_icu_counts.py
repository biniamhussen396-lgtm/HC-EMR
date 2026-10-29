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
    COUNT(DISTINCT v.visit_id) as total_icu_visits,
    SUM(IF(DATE(v.date_started) = '2026-10-28', 1, 0)) as today_icu_visits
FROM visit v
LEFT JOIN encounter e ON v.visit_id = e.visit_id AND e.voided = 0
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
WHERE v.voided = 0
  AND (
      vt.name IN ('ICU', 'NICU Ward', 'Adult MICU', 'Pedi HDU', 'RETIRED_Adult MICU', 'RETIRED_AICU Ward 179')
      OR v.location_id IN (261, 53, 191, 17, 83, 23, 100, 221, 143)
      OR e.location_id IN (261, 53, 191, 17, 83, 23, 100, 221, 143)
  );
"""
print(run_query(sql))
