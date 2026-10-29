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

print("=== BMH ICU CONCEPTS ===")
print(run_query("""
SELECT c.concept_id, cn.name
FROM concept c
JOIN concept_name cn ON c.concept_id = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
WHERE cn.name LIKE 'BMH%ICU%' OR cn.name LIKE 'BMH%Ventil%' OR cn.name LIKE '%ICU admission%' OR cn.name LIKE '%ICU discharge%'
ORDER BY cn.name;
"""))
