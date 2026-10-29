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

print("--- 1. SEARCH FOR 'Referral Service' IN CONCEPTS ---")
sql_ref = """
SELECT c.concept_id, cn.name, cn.concept_name_type, c.datatype_id 
FROM concept c 
JOIN concept_name cn ON c.concept_id = cn.concept_id 
WHERE cn.name LIKE '%Referral%' OR cn.name LIKE '%Refer%' 
  AND cn.voided = 0 
LIMIT 30;
"""
print(run_query(sql_ref))

print("\n--- 2. CHECK OBS WITH REFERRAL CONCEPTS TODAY AND ALL TIME ---")
sql_obs = """
SELECT c.concept_id, cn.name, COUNT(*) as cnt
FROM obs o
JOIN concept c ON o.concept_id = c.concept_id
JOIN concept_name cn ON c.concept_id = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
WHERE (cn.name LIKE '%Refer%' OR cn.name LIKE '%refer%') AND o.voided = 0
GROUP BY c.concept_id, cn.name
ORDER BY cnt DESC
LIMIT 20;
"""
print(run_query(sql_obs))

print("\n--- 3. CHECK ICU VISITS & ADMISSIONS ---")
sql_icu = """
SELECT vt.name, COUNT(*) as all_time_cnt, SUM(IF(DATE(v.date_started) = '2026-10-28', 1, 0)) as today_cnt
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
WHERE (vt.name LIKE '%ICU%' OR vt.name LIKE '%HDU%' OR vt.name LIKE '%NICU%')
  AND v.voided = 0
GROUP BY vt.name;
"""
print(run_query(sql_icu))
