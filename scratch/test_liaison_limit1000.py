import subprocess
import time

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"').replace('\n', ' ')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    t0 = time.time()
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=60)
    t1 = time.time()
    return t1 - t0, res.returncode, res.stdout, res.stderr

sql_liaison_test = """
SELECT
    v.visit_id,
    p.uuid as patient_uuid,
    v.uuid as visit_uuid,
    pi.identifier AS mrn,
    TRIM(CONCAT(pn.given_name, IF(pn.middle_name IS NOT NULL AND pn.middle_name != '', CONCAT(' ', pn.middle_name), ''), IF(pn.family_name IS NOT NULL AND pn.family_name != '', CONCAT(' ', pn.family_name), ''))) AS patient_name,
    TIMESTAMPDIFF(YEAR, p.birthdate, v.date_started) AS age,
    p.gender AS sex,
    COALESCE(pa.state_province, 'Amhara') AS region,
    COALESCE(pa.county_district, '-') AS subcity_zone,
    COALESCE(pa.city_village, pa.address1, '-') AS woreda_kebele,
    DATE_FORMAT(v.date_started, '%Y-%m-%d %H:%i:%s') AS service_date,
    IF(MAX(CASE WHEN o.concept_id IN (49, 69611, 69612, 69620, 21895, 57417, 28891) OR o.value_coded IN (SELECT concept_id FROM concept_name WHERE name IN ('Refer Patient', 'Transfer Patient') AND voided = 0) OR et.name = 'DISCHARGE' THEN 1 END) = 1, 'Out', 'In') AS referral_type,
    COALESCE(MAX(CASE WHEN o.concept_id IN (67271, 68984, 57417, 28891) THEN COALESCE(val_cn.name, o.value_text) END), 'Dessie Comprehensive Specialized Hospital') AS facility_name,
    IF(vt.name LIKE '%Emergency%' OR MAX(CASE WHEN o.concept_id = 69611 AND o.value_text LIKE '%Emerg%' THEN 1 END) = 1, 'Emergency', 'Cold / Elective') AS case_type,
    IFNULL(GROUP_CONCAT(DISTINCT CASE WHEN o.concept_id IN (22, 11847, 67272) THEN COALESCE(cn.name, o.value_text) END SEPARATOR '; '), 'Medical Evaluation') AS diagnosis,
    COALESCE(MAX(CASE WHEN o.concept_id = 69612 THEN o.value_text END), MAX(CASE WHEN el.name != 'BORUMEDA GENERAL HOSPITAL' THEN el.name END), vt.name, 'Liaison') AS department,
    COALESCE(MAX(CASE WHEN o.concept_id IN (21895, 67273, 11084) THEN o.value_text END), 'Specialized Investigation / Management') AS reason_for_referral,
    COALESCE(MAX(CASE WHEN o.concept_id IN (69611) AND o.value_text LIKE '%Ambulance%' THEN 'Yes' END), IF(vt.name LIKE '%Emergency%', 'Yes', 'No')) AS ambulance_dispatched,
    'Yes' AS communication_done,
    COALESCE(MAX(pm_attr.value), 'CBHI') AS payment_type,
    'Yes' AS feedback_sent_received,
    COALESCE(MAX(CASE WHEN o.concept_id = 69621 THEN o.value_text END), '') AS remark
FROM (
    SELECT DISTINCT v_inner.visit_id, v_inner.patient_id, v_inner.date_started, v_inner.visit_type_id, v_inner.location_id, v_inner.uuid
    FROM visit v_inner
    JOIN encounter e_inner ON v_inner.visit_id = e_inner.visit_id AND e_inner.voided = 0
    LEFT JOIN obs o_inner ON e_inner.encounter_id = o_inner.encounter_id AND o_inner.voided = 0
      AND (
          o_inner.concept_id IN (61954, 67271, 60880, 67272, 67273, 69611, 69612, 69620, 68984, 68985, 21895, 49, 57417, 28891)
          OR o_inner.value_coded IN (SELECT concept_id FROM concept_name WHERE name IN ('Refer Patient', 'Transfer Patient') AND voided = 0)
      )
    WHERE v_inner.voided = 0
      AND (
          e_inner.location_id = 24 
          OR v_inner.visit_type_id = 18 
          OR o_inner.obs_id IS NOT NULL
      )
    ORDER BY v_inner.visit_id DESC
    LIMIT 1000
) v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
JOIN patient_identifier_type pit ON pi.identifier_type = pit.patient_identifier_type_id
JOIN global_property gp ON gp.property = 'bahmni.primaryIdentifierType' AND gp.property_value = pit.uuid
JOIN person p ON v.patient_id = p.person_id
JOIN person_name pn ON v.patient_id = pn.person_id AND pn.voided = 0
LEFT JOIN person_address pa ON v.patient_id = pa.person_id AND pa.voided = 0
LEFT JOIN encounter e ON v.visit_id = e.visit_id AND e.voided = 0
LEFT JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
LEFT JOIN location el ON e.location_id = el.location_id
LEFT JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0
  AND (
      o.concept_id IN (22, 11847, 67272, 61954, 67271, 60880, 67273, 69611, 69612, 69620, 68984, 68985, 21895, 49, 57417, 28891, 69621)
      OR o.value_coded IN (SELECT concept_id FROM concept_name WHERE name IN ('Refer Patient', 'Transfer Patient') AND voided = 0)
  )
LEFT JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
LEFT JOIN concept_name val_cn ON o.value_coded = val_cn.concept_id AND val_cn.concept_name_type = 'FULLY_SPECIFIED' AND val_cn.locale = 'en'
LEFT JOIN person_attribute pm_attr ON v.patient_id = pm_attr.person_id AND pm_attr.person_attribute_type_id = 17 AND pm_attr.voided = 0
GROUP BY v.visit_id
ORDER BY v.visit_id DESC;
"""

elapsed, rc, out, err = run_query(sql_liaison_test)
print(f"Liaison Query with LIMIT 1000 took: {elapsed:.2f}s, RC={rc}")
if rc == 0:
    lines = out.strip().split("\n")
    print(f"Total rows: {len(lines)-1}")
