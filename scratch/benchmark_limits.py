import subprocess, time

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=60):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

for limit in [10000, 25000, 35000, 50000]:
    t0 = time.time()
    query = f"""
    SELECT COUNT(*) FROM (
        SELECT v_inner.visit_id
        FROM visit v_inner
        JOIN visit_type vt_inner ON v_inner.visit_type_id = vt_inner.visit_type_id
        LEFT JOIN location vl_inner ON v_inner.location_id = vl_inner.location_id
        WHERE v_inner.voided = 0
          AND vt_inner.name NOT LIKE '%Ward%'
          AND vt_inner.name NOT IN ('ICU', 'Adult MICU', 'Pedi HDU', 'PNC A', 'PNC B', 'SAM', 'preterm ward', 'IPD', 'Labor Ward', 'Delivery Room', 'Eye Ward', 'Medical Ward', 'Surgical Ward', 'NICU Ward')
          AND (vl_inner.name IS NULL OR (vl_inner.name NOT LIKE '%Ward%' AND vl_inner.name NOT IN ('ICU', 'Adult MICU', 'Pedi HDU', 'PNC A', 'PNC B', 'SAM', 'preterm ward', 'IPD', 'Labor Ward', 'Delivery Room', 'Eye Ward', 'Medical Ward', 'Surgical Ward', 'NICU Ward')))
        ORDER BY v_inner.visit_id DESC
        LIMIT {limit}
    ) v;
    """
    res = run(f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{query}"')
    dt = time.time() - t0
    print(f"LIMIT {limit}: took {dt:.2f}s, result: {res.strip()}")
