import subprocess
import time

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

def run_query(sql):
    escaped = sql.replace('"', '\\"')
    cmd = f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{escaped}"'
    t0 = time.time()
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
    t1 = time.time()
    return t1 - t0, res.returncode, res.stdout, res.stderr

sql_ipd_fast = """
SELECT 
    v.visit_id,
    p.uuid as patient_uuid,
    v.uuid as visit_uuid,
    pi.identifier as mrn,
    TRIM(CONCAT(pn.given_name, IF(pn.middle_name IS NOT NULL AND pn.middle_name != '', CONCAT(' ', pn.middle_name), ''), IF(pn.family_name IS NOT NULL AND pn.family_name != '', CONCAT(' ', pn.family_name), ''))) as patient_name,
    p.gender as sex,
    TIMESTAMPDIFF(YEAR, p.birthdate, v.date_started) as age,
    COALESCE(pa.city_village, pa.address1, '') as woreda,
    COALESCE(pa.address2, pa.county_district, '') as subcity,
    DATE_FORMAT(v.date_started, '%Y-%m-%d %H:%i:%s') as admission_date,
    DATE_FORMAT(v.date_stopped, '%Y-%m-%d %H:%i:%s') as discharge_date,
    IF(v.date_stopped IS NULL, 'Admitted', 'Discharged') as status,
    DATEDIFF(IFNULL(v.date_stopped, NOW()), v.date_started) as length_of_stay,
    COALESCE(MAX(CASE WHEN el.name LIKE '%Ward%' OR el.name LIKE '%ICU%' THEN el.name END), vt.name, 'IPD') as ward_name,
    '-' as bed_number,
    IFNULL(GROUP_CONCAT(DISTINCT CASE WHEN o.concept_id IN (22, 11847, 11848) THEN COALESCE(cn.name, o.value_text) END SEPARATOR '; '), '-') as admission_diagnosis,
    IFNULL(GROUP_CONCAT(DISTINCT CASE WHEN o.concept_id IN (22, 11847, 11848) THEN crt.code END SEPARATOR '; '), '-') as icd11_code,
    IFNULL(GROUP_CONCAT(DISTINCT CASE WHEN o.concept_id IN (22, 11847, 11848) THEN COALESCE(cn.name, o.value_text) END SEPARATOR '; '), '-') as discharge_diagnosis,
    COALESCE(MAX(CASE WHEN o.concept_id IN (3325, 11924) THEN COALESCE(val_cn.name, o.value_text) END), '') as road_traffic_accident,
    COALESCE(MAX(CASE WHEN o.concept_id = 63657 THEN IF(o.value_coded IS NOT NULL, 'Yes', o.value_text) END), '') as hiv_offered,
    COALESCE(MAX(CASE WHEN o.concept_id IN (22442, 63658) THEN IF(o.value_coded IS NOT NULL, 'Yes', o.value_text) END), '') as hiv_performed,
    COALESCE(MAX(CASE WHEN o.concept_id = 63659 THEN COALESCE(val_cn.name, o.value_text) END), '') as hiv_target_category,
    COALESCE(MAX(CASE WHEN o.concept_id IN (32992, 47297) THEN COALESCE(val_cn.name, o.value_text) END), '') as hiv_result,
    COALESCE(MAX(CASE WHEN o.concept_id = 63270 THEN COALESCE(val_cn.name, o.value_text) END), '') as travel_malaria,
    COALESCE(MAX(CASE WHEN o.concept_id IN (63266) THEN COALESCE(val_cn.name, IF(o.value_coded IS NOT NULL, 'Yes', o.value_text)) END), '') as tb_screened,
    COALESCE(MAX(CASE WHEN o.concept_id IN (63267) THEN COALESCE(val_cn.name, o.value_text) END), '') as tb_result,
    '-' as tb_eval_type,
    COALESCE(MAX(CASE WHEN o.concept_id IN (63267) THEN COALESCE(val_cn.name, o.value_text) END), '') as tb_screening_result,
    IF(v.date_stopped IS NOT NULL, 'Discharged / Improved', 'Admitted') as condition_at_discharge,
    IF(p.dead = 1, IF(TIMESTAMPDIFF(HOUR, v.date_started, IFNULL(p.death_date, v.date_stopped)) <= 24, 'Within 24 hrs', 'After 24 hrs'), '-') as death_in_ipd,
    IF(p.dead = 1, 'Yes', 'No') as death_notification,
    COALESCE(MAX(pm_attr.value), 'CBHI') as payment_method,
    '-' as voucher_no,
    '' as remark
FROM (
    SELECT e_filter.visit_id, v_inner.patient_id, v_inner.date_started, v_inner.date_stopped, v_inner.visit_type_id, v_inner.location_id, v_inner.uuid
    FROM (
        SELECT DISTINCT visit_id
        FROM encounter
        WHERE voided = 0 AND (
            location_id IN (267, 117, 130, 170, 77, 53, 157, 246, 67, 261, 211)
            OR encounter_type IN (3, 4, 5)
        )
        ORDER BY encounter_id DESC
        LIMIT 100
    ) e_filter
    JOIN visit v_inner ON e_filter.visit_id = v_inner.visit_id
    WHERE v_inner.voided = 0
    ORDER BY v_inner.visit_id DESC
) v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
JOIN patient_identifier_type pit ON pi.identifier_type = pit.patient_identifier_type_id
JOIN global_property gp ON gp.property = 'bahmni.primaryIdentifierType' AND gp.property_value = pit.uuid
JOIN person p ON v.patient_id = p.person_id
JOIN person_name pn ON v.patient_id = pn.person_id AND pn.voided = 0
LEFT JOIN person_address pa ON v.patient_id = pa.person_id AND pa.voided = 0
LEFT JOIN encounter e ON v.visit_id = e.visit_id AND e.voided = 0
LEFT JOIN location el ON e.location_id = el.location_id
LEFT JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0
LEFT JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
LEFT JOIN concept_reference_map crm ON o.value_coded = crm.concept_id
LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
LEFT JOIN concept_name val_cn ON o.value_coded = val_cn.concept_id AND val_cn.concept_name_type = 'FULLY_SPECIFIED' AND val_cn.locale = 'en'
LEFT JOIN person_attribute pm_attr ON v.patient_id = pm_attr.person_id AND pm_attr.person_attribute_type_id = 17 AND pm_attr.voided = 0
GROUP BY v.visit_id
ORDER BY v.visit_id DESC;
"""

elapsed, rc, out, err = run_query(sql_ipd_fast)
print(f"IPD Query took {elapsed:.2f}s, RC={rc}")
if rc == 0:
    lines = out.strip().split("\n")
    print(f"Total rows: {len(lines)-1}")
    for l in lines[:5]:
        print(l[:180])
else:
    print("Error:", err)
