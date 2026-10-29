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
SELECT count(distinct e.encounter_id), count(distinct e.visit_id)
FROM encounter e 
JOIN location l ON e.location_id = l.location_id 
WHERE (l.name LIKE '%ICU%' OR l.name LIKE '%HDU%') AND e.voided = 0;
"""
print(run(f"docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"{script}\""))
