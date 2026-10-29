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
SELECT v.visit_id, vt.name as visit_type, vl.name as loc, count(distinct e.encounter_id) as enc_cnt, count(distinct o.obs_id) as obs_cnt
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
LEFT JOIN location vl ON v.location_id = vl.location_id
LEFT JOIN encounter e ON v.visit_id = e.visit_id AND e.voided = 0
LEFT JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0
WHERE v.voided = 0 AND (vt.name LIKE '%Liaison%' OR vl.name LIKE '%Liaison%' OR e.location_id = 24 OR o.concept_id IN (61954, 49, 11850, 11851, 11852, 11853))
  AND v.date_started >= '2026-10-28 00:00:00'
GROUP BY v.visit_id;
"""
print(run(f"docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"{script}\""))
