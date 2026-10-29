import subprocess, time

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=90):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

for limit in [10000, 20000]:
    t0 = time.time()
    query = f"""
    SELECT COUNT(*) FROM (
        SELECT v.visit_id
        FROM (
            SELECT v_inner.visit_id, v_inner.patient_id, v_inner.date_started, v_inner.visit_type_id, v_inner.location_id, v_inner.uuid
            FROM visit v_inner
            JOIN visit_type vt_inner ON v_inner.visit_type_id = vt_inner.visit_type_id
            LEFT JOIN location vl_inner ON v_inner.location_id = vl_inner.location_id
            WHERE v_inner.voided = 0
              AND vt_inner.name NOT LIKE '%Ward%'
              AND vt_inner.name NOT IN ('ICU', 'Adult MICU', 'Pedi HDU', 'PNC A', 'PNC B', 'SAM', 'preterm ward', 'IPD', 'Labor Ward', 'Delivery Room', 'Eye Ward', 'Medical Ward', 'Surgical Ward', 'NICU Ward')
              AND (vl_inner.name IS NULL OR (vl_inner.name NOT LIKE '%Ward%' AND vl_inner.name NOT IN ('ICU', 'Adult MICU', 'Pedi HDU', 'PNC A', 'PNC B', 'SAM', 'preterm ward', 'IPD', 'Labor Ward', 'Delivery Room', 'Eye Ward', 'Medical Ward', 'Surgical Ward', 'NICU Ward')))
            ORDER BY v_inner.visit_id DESC
            LIMIT {limit}
        ) v
        JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
        LEFT JOIN location vl ON v.location_id = vl.location_id
        JOIN patient_identifier pi ON v.patient_id = pi.patient_id
        JOIN patient_identifier_type pit ON pi.identifier_type = pit.patient_identifier_type_id
        JOIN global_property gp ON gp.property = 'bahmni.primaryIdentifierType' AND gp.property_value = pit.uuid
        JOIN person p ON v.patient_id = p.person_id
        JOIN person_name pn ON v.patient_id = pn.person_id AND pn.voided = 0
        LEFT JOIN person_address pa ON v.patient_id = pa.person_id AND pa.voided = 0
        LEFT JOIN encounter e ON v.visit_id = e.visit_id AND e.voided = 0
        LEFT JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0 
          AND o.concept_id IN (22, 11847, 11848, 11849, 3325, 11924, 63657, 22442, 63658, 32992, 47297, 63659, 63266, 63267, 63268, 63269, 63270, 49)
        GROUP BY v.visit_id
    ) total;
    """
    res = run(f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{query}"')
    dt = time.time() - t0
    print(f"Full query with limit {limit}: took {dt:.2f}s, result: {res.strip()}")
