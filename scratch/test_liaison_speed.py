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
SELECT count(distinct visit_id) FROM (
    (SELECT visit_id FROM encounter WHERE location_id = 24 AND voided = 0 ORDER BY encounter_id DESC LIMIT 500)
    UNION
    (SELECT visit_id FROM encounter WHERE encounter_type IN (3, 4, 5) AND voided = 0 ORDER BY encounter_id DESC LIMIT 500)
    UNION
    (SELECT visit_id FROM visit WHERE visit_type_id = 18 AND voided = 0 ORDER BY visit_id DESC LIMIT 200)
    UNION
    (SELECT e.visit_id FROM obs o JOIN encounter e ON o.encounter_id = e.encounter_id WHERE o.concept_id IN (61954, 49) AND o.voided = 0 ORDER BY o.obs_id DESC LIMIT 500)
) u;
"""
print(run(f"docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"{script}\""))
