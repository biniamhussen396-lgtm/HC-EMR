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
SELECT vt.name as visit_type, vl.name as location, count(*) as cnt
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
LEFT JOIN location vl ON v.location_id = vl.location_id
WHERE v.voided = 0 AND v.date_started >= '2026-10-28 00:00:00'
GROUP BY vt.name, vl.name
ORDER BY cnt DESC;
"""
print(run(f"docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"{script}\""))
