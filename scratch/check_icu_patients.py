import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

script = """
SELECT v.visit_id, vt.name as visit_type, vl.name as visit_loc, v.date_started, pi.identifier, pn.given_name
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
LEFT JOIN location vl ON v.location_id = vl.location_id
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
JOIN person_name pn ON v.patient_id = pn.person_id AND pn.voided = 0
WHERE v.voided = 0 
  AND (vt.name LIKE '%ICU%' OR vt.name LIKE '%HDU%' OR vl.name LIKE '%ICU%' OR vl.name LIKE '%HDU%')
ORDER BY v.visit_id DESC LIMIT 15;
"""
print(run(f"docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"{script}\""))
