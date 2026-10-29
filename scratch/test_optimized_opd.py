import subprocess
import time

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

optimized_query = """
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
    COALESCE(loc.name, vt.name, 'OPD') as visit_location,
    IFNULL(diag.diagnosis_name, '-') as diagnosis_name,
    IFNULL(diag.icd11_code, '-') as icd11_code,
    IF(diag.diagnosis_occurrence = 'Repeat', 'Repeat', 'New') as patient_status,
    IF(vt.name LIKE '%ward%' OR vt.name IN ('Delivery Room', 'IPD', 'Adult MICU'), 'Admitted', '') as admitted_mark,
    screening.rta_type as rta_type,
    screening.hiv_offered as hiv_offered,
    screening.hiv_performed as hiv_performed,
    screening.hiv_target_category as hiv_target_category,
    screening.hiv_result as hiv_result,
    screening.travel_malaria as travel_malaria,
    screening.tb_screened as tb_screened,
    screening.tb_result as tb_result,
    screening.tb_eval_type as tb_eval_type,
    screening.tb_code as tb_code,
    ref.referred_to as referred_to,
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
    LIMIT 1000
) v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
JOIN patient_identifier_type pit ON pi.identifier_type = pit.patient_identifier_type_id
JOIN global_property gp ON gp.property = 'bahmni.primaryIdentifierType' AND gp.property_value = pit.uuid
JOIN person p ON v.patient_id = p.person_id
JOIN person_name pn ON v.patient_id = pn.person_id AND pn.voided = 0
LEFT JOIN person_address pa ON v.patient_id = pa.person_id AND pa.voided = 0
LEFT JOIN (
    SELECT e.visit_id, l.name
    FROM encounter e
    JOIN location l ON e.location_id = l.location_id
    WHERE e.voided = 0
    GROUP BY e.visit_id
) loc ON v.visit_id = loc.visit_id
LEFT JOIN (
    SELECT 
        e.visit_id,
        GROUP_CONCAT(DISTINCT COALESCE(cn.name, o.value_text) SEPARATOR '; ') as diagnosis_name,
        GROUP_CONCAT(DISTINCT crt.code SEPARATOR '; ') as icd11_code,
        MAX(CASE WHEN cn_occ.name IS NOT NULL THEN cn_occ.name ELSE 'New' END) as diagnosis_occurrence
    FROM encounter e
    JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0 AND o.concept_id IN (22, 11847, 11848)
    LEFT JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
    LEFT JOIN concept_reference_map crm ON o.value_coded = crm.concept_id
    LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
    LEFT JOIN obs o_occ ON e.encounter_id = o_occ.encounter_id AND o_occ.concept_id = 11849 AND o_occ.voided = 0
    LEFT JOIN concept_name cn_occ ON o_occ.value_coded = cn_occ.concept_id AND cn_occ.concept_name_type = 'FULLY_SPECIFIED'
    GROUP BY e.visit_id
) diag ON v.visit_id = diag.visit_id
LEFT JOIN (
    SELECT
        e.visit_id,
        MAX(CASE WHEN o.concept_id IN (3325, 11924) THEN COALESCE(val_cn.name, o.value_text) END) as rta_type,
        MAX(CASE WHEN o.concept_id = 63657 THEN IF(o.value_coded IS NOT NULL, 'Yes', o.value_text) END) as hiv_offered,
        MAX(CASE WHEN o.concept_id IN (22442, 63658) THEN IF(o.value_coded IS NOT NULL, 'Yes', o.value_text) END) as hiv_performed,
        MAX(CASE WHEN o.concept_id IN (32992, 47297) THEN COALESCE(val_cn.name, o.value_text) END) as hiv_result,
        MAX(CASE WHEN o.concept_id = 63659 THEN COALESCE(val_cn.name, o.value_text) END) as hiv_target_category,
        MAX(CASE WHEN o.concept_id IN (63266) THEN COALESCE(val_cn.name, IF(o.value_coded IS NOT NULL, 'Yes', o.value_text)) END) as tb_screened,
        MAX(CASE WHEN o.concept_id IN (63267) THEN COALESCE(val_cn.name, o.value_text) END) as tb_result,
        MAX(CASE WHEN o.concept_id = 63268 THEN COALESCE(val_cn.name, o.value_text) END) as tb_eval_type,
        MAX(CASE WHEN o.concept_id = 63269 THEN COALESCE(val_cn.name, o.value_text) END) as tb_code,
        MAX(CASE WHEN o.concept_id = 63270 THEN COALESCE(val_cn.name, o.value_text) END) as travel_malaria
    FROM encounter e
    JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0 AND o.concept_id IN (3325, 11924, 63657, 22442, 63658, 32992, 47297, 63659, 63266, 63267, 63268, 63269, 63270)
    LEFT JOIN concept_name val_cn ON o.value_coded = val_cn.concept_id AND val_cn.concept_name_type = 'FULLY_SPECIFIED' AND val_cn.locale = 'en'
    GROUP BY e.visit_id
) screening ON v.visit_id = screening.visit_id
LEFT JOIN (
    SELECT 
        e.visit_id,
        MAX(CASE WHEN rcn.name = 'Refers' THEN ro.value_text END) as referred_to
    FROM encounter e
    JOIN obs ro ON e.encounter_id = ro.encounter_id AND ro.voided = 0
    JOIN concept_name rcn ON ro.concept_id = rcn.concept_id AND rcn.name = 'Refers' AND rcn.concept_name_type = 'FULLY_SPECIFIED'
    GROUP BY e.visit_id
) ref ON v.visit_id = ref.visit_id
GROUP BY v.visit_id
ORDER BY v.visit_id DESC;
"""

with open('scratch/optimized_opd.sql', 'w', encoding='utf-8') as f:
    f.write(optimized_query)

# Upload and execute on remote
subprocess.run([r"C:\Program Files\PuTTY\pscp.EXE", "-batch", "-pw", PW, 'scratch/optimized_opd.sql', f"{USER}@{HOST}:/tmp/optimized_opd.sql"], check=True)

t0 = time.time()
cmd = 'docker exec -i bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs < /tmp/optimized_opd.sql'
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=60)
t1 = time.time()
print(f"Execution time: {t1 - t0:.2f}s")
lines = res.stdout.strip().splitlines()
print(f"Total rows returned: {len(lines)}")
if len(lines) > 1:
    print("Header:", lines[0])
    print("Row 1:", lines[1])
    if len(lines) > 2:
        print("Row 2:", lines[2])
