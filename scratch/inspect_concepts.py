import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=25)
    return res.stdout

print("=== ICU CONCEPTS IN OPENMRS ===")
print(run_query("""
SELECT c.concept_id, cn.name
FROM concept c
JOIN concept_name cn ON c.concept_id = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
WHERE cn.name LIKE '%ICU%' OR cn.name LIKE '%ventilat%' OR cn.name LIKE '%VAP%'
ORDER BY cn.name;
"""))

print("=== LIAISON / REFERRAL CONCEPTS IN OPENMRS ===")
print(run_query("""
SELECT c.concept_id, cn.name
FROM concept c
JOIN concept_name cn ON c.concept_id = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
WHERE cn.name LIKE '%Refer%' OR cn.name LIKE '%Liaison%'
ORDER BY cn.name;
"""))
