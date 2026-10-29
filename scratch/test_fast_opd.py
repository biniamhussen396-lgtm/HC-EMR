import subprocess
import time

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

# Direct indexed join for encounter location
fast_sql = """
SELECT 
    v.visit_id,
    p.uuid as patient_uuid,
    v.uuid as visit_uuid,
    pi.identifier as mrn,
    TRIM(CONCAT(pn.given_name, IF(pn.middle_name IS NOT NULL AND pn.middle_name != '', CONCAT(' ', pn.middle_name), ''), IF(pn.family_name IS NOT NULL AND pn.family_name != '', CONCAT(' ', pn.family_name), ''))) as patient_name,
    p.gender as sex,
    TIMESTAMPDIFF(YEAR, p.birthdate, v.date_started) as age,
    COALESCE(pa.city_village, pa.address1, '') as woreda,
    COALESCE(pa.address2, pa.county_district, '') as kebele,
    COALESCE(pa.state_province, 'Amhara') as region,
    DATE_FORMAT(v.date_started, '%Y-%m-%d %H:%i:%s') as service_date,
    vt.name as visit_type_name,
    COALESCE(MAX(el.name), vl.name, vt.name, 'OPD') as visit_location,
    IFNULL(GROUP_CONCAT(DISTINCT IF(o.concept_id IN (22, 11847, 11848), COALESCE(cn.name, o.value_text), NULL) SEPARATOR '; '), '-') as diagnosis_name,
    IFNULL(GROUP_CONCAT(DISTINCT IF(o.concept_id IN (22, 11847, 11848), crt.code, NULL) SEPARATOR '; '), '-') as icd11_code,
    IF(MAX(CASE WHEN o.concept_id = 11849 AND cn_val.name = 'Repeat' THEN 1 ELSE 0 END) = 1, 'Repeat', 'New') as patient_status,
    IF(vt.name LIKE '%ward%' OR vt.name IN ('Delivery Room', 'IPD', 'Adult MICU'), 'Admitted', '') as admitted_mark,
    MAX(CASE WHEN o.concept_id IN (3325, 11924) THEN COALESCE(cn_val.name, o.value_text) END) as rta_type,
    MAX(CASE WHEN o.concept_id = 63657 THEN IF(o.value_coded IS NOT NULL, 'Yes', o.value_text) END) as hiv_offered,
    MAX(CASE WHEN o.concept_id IN (22442, 63658) THEN IF(o.value_coded IS NOT NULL, 'Yes', o.value_text) END) as hiv_performed,
    MAX(CASE WHEN o.concept_id = 63659 THEN COALESCE(cn_val.name, o.value_text) END) as hiv_target_category,
    MAX(CASE WHEN o.concept_id IN (32992, 47297) THEN COALESCE(cn_val.name, o.value_text) END) as hiv_result,
    MAX(CASE WHEN o.concept_id = 63270 THEN COALESCE(cn_val.name, o.value_text) END) as travel_malaria,
    MAX(CASE WHEN o.concept_id = 63266 THEN COALESCE(cn_val.name, IF(o.value_coded IS NOT NULL, 'Yes', o.value_text)) END) as tb_screened,
    MAX(CASE WHEN o.concept_id = 63267 THEN COALESCE(cn_val.name, o.value_text) END) as tb_result,
    MAX(CASE WHEN o.concept_id = 63268 THEN COALESCE(cn_val.name, o.value_text) END) as tb_eval_type,
    MAX(CASE WHEN o.concept_id = 63269 THEN COALESCE(cn_val.name, o.value_text) END) as tb_code,
    MAX(CASE WHEN rcn.name = 'Refers' THEN o.value_text END) as referred_to,
    IF(p.dead = 1, 'Yes', 'No') as died,
    IF(p.dead = 1, 'Yes', 'No') as death_notified,
    '' as remark
FROM (
    SELECT v_inner.visit_id, v_inner.patient_id, v_inner.date_started, v_inner.visit_type_id, v_inner.location_id, v_inner.uuid
    FROM visit v_inner
    JOIN visit_type vt_inner ON v_inner.visit_type_id = vt_inner.visit_type_id
    WHERE v_inner.voided = 0
      AND (
          vt_inner.name LIKE '%OPD%' 
          OR vt_inner.name LIKE '%ER%' 
          OR vt_inner.name LIKE '%Triage%' 
          OR vt_inner.name LIKE '%Clinic%' 
          OR vt_inner.name LIKE '%ANC%'
          OR vt_inner.name LIKE '%Dental%'
          OR vt_inner.name LIKE '%MRU%'
          OR vt_inner.name IN ('OPD', 'Adult ER', 'Central Triage 11', 'Liaison', 'Physiotherapy OPD')
      )
      AND vt_inner.name NOT LIKE '%Ward%'
      AND vt_inner.name NOT IN ('ICU', 'IPD', 'Labor Ward', 'PNC A', 'PNC B', 'Pedi HDU', 'SAM', 'preterm ward')
    ORDER BY v_inner.visit_id DESC
    LIMIT 500
) v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
JOIN patient_identifier_type pit ON pi.identifier_type = pit.patient_identifier_type_id
JOIN global_property gp ON gp.property = 'bahmni.primaryIdentifierType' AND gp.property_value = pit.uuid
JOIN person p ON v.patient_id = p.person_id
JOIN person_name pn ON v.patient_id = pn.person_id AND pn.voided = 0
LEFT JOIN person_address pa ON v.patient_id = pa.person_id AND pa.voided = 0
LEFT JOIN location vl ON v.location_id = vl.location_id
LEFT JOIN encounter e ON v.visit_id = e.visit_id AND e.voided = 0
LEFT JOIN location el ON e.location_id = el.location_id AND el.name != 'BORUMEDA GENERAL HOSPITAL'
LEFT JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0 AND o.concept_id IN (22, 11847, 11848, 11849, 3325, 11924, 63657, 22442, 63658, 32992, 47297, 63659, 63266, 63267, 63268, 63269, 63270)
LEFT JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
LEFT JOIN concept_name cn_val ON o.value_coded = cn_val.concept_id AND cn_val.concept_name_type = 'FULLY_SPECIFIED'
LEFT JOIN concept_reference_map crm ON o.value_coded = crm.concept_id
LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
LEFT JOIN concept_name rcn ON o.concept_id = rcn.concept_id AND rcn.name = 'Refers' AND rcn.concept_name_type = 'FULLY_SPECIFIED'
GROUP BY v.visit_id
ORDER BY v.visit_id DESC;
"""

with open('scratch/fast_opd.sql', 'w', encoding='utf-8') as f:
    f.write(fast_sql)

subprocess.run([r"C:\Program Files\PuTTY\pscp.EXE", "-batch", "-pw", PW, 'scratch/fast_opd.sql', f"{USER}@{HOST}:/tmp/fast_opd.sql"], check=True)

t0 = time.time()
cmd = 'docker exec -i bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs < /tmp/fast_opd.sql'
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=30)
t1 = time.time()
print(f"Fast execution time: {t1 - t0:.2f}s")
lines = res.stdout.strip().splitlines()
print(f"Total rows: {len(lines)}")
if len(lines) > 1:
    print("Row 1:\n", lines[1])
