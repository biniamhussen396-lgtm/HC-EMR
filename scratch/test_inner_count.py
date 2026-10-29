import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Run the query as SQL in mysql and count the rows
print(run("docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"SELECT COUNT(*) FROM (SELECT property_value FROM global_property WHERE property = 'emrapi.sqlSearch.opdRegister') gp;\""))

# Let's see how many rows the inner subquery of opdRegister produces:
check_inner = """
SELECT COUNT(*) 
FROM visit v_inner
JOIN visit_type vt_inner ON v_inner.visit_type_id = vt_inner.visit_type_id
LEFT JOIN location vl_inner ON v_inner.location_id = vl_inner.location_id
WHERE v_inner.voided = 0
  AND vt_inner.name NOT LIKE '%Ward%'
  AND vt_inner.name NOT IN ('ICU', 'Adult MICU', 'Pedi HDU', 'PNC A', 'PNC B', 'SAM', 'preterm ward', 'IPD', 'Labor Ward', 'Delivery Room')
  AND (vl_inner.name IS NULL OR (vl_inner.name NOT LIKE '%Ward%' AND vl_inner.name NOT IN ('ICU', 'Adult MICU', 'Pedi HDU', 'PNC A', 'PNC B', 'SAM', 'preterm ward', 'IPD', 'Labor Ward', 'Delivery Room')))
  AND v_inner.date_started >= '2026-10-28 00:00:00';
"""
print("=== Inner query count for TODAY (2026-10-28) ===")
print(run(f"docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e \"{check_inner}\""))
