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
SELECT v.visit_id, pi.identifier as mrn, vt.name as visit_type, vl.name as visit_loc,
       GROUP_CONCAT(DISTINCT el.name) as enc_locs
FROM visit v
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
LEFT JOIN location vl ON v.location_id = vl.location_id
LEFT JOIN encounter e ON v.visit_id = e.visit_id
LEFT JOIN location el ON e.location_id = el.location_id
WHERE pi.identifier IN ('499170', '501558', '223620', '356533')
GROUP BY v.visit_id;
"""
print(run_query(sql))
