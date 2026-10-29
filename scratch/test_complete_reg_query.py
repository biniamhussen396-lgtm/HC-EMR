import subprocess

query = """
SELECT 
    v.visit_id,
    p.uuid as patient_uuid,
    v.uuid as visit_uuid,
    pi.identifier as mrn,
    TRIM(CONCAT(pn.given_name, IF(pn.middle_name IS NOT NULL AND pn.middle_name != '', CONCAT(' ', pn.middle_name), ''), IF(pn.family_name IS NOT NULL AND pn.family_name != '', CONCAT(' ', pn.family_name), ''))) as patient_name,
    p.gender as sex,
    TIMESTAMPDIFF(YEAR, p.birthdate, v.date_started) as age,
    COALESCE(pa.city_village, pa.address1, '-') as woreda,
    COALESCE(pa.address2, pa.state_province, '-') as subcity,
    v.date_started as admission_date,
    v.date_stopped as discharge_date,
    IF(v.date_stopped IS NULL, 'Admitted', 'Discharged') as status,
    DATEDIFF(IFNULL(v.date_stopped, NOW()), v.date_started) as length_of_stay,
    vt.name as ward_name,
    IFNULL(bed_info.bed_number, '-') as bed_number,
    IFNULL(diag.admission_diag, '-') as admission_diagnosis,
    IFNULL(diag.icd11_code, '-') as icd11_code,
    IFNULL(diag.discharge_diag, IFNULL(diag.admission_diag, '-')) as discharge_diagnosis,
    IFNULL(screening.rta_obs, '-') as road_traffic_accident,
    IFNULL(screening.hiv_offered, '-') as hiv_offered,
    IFNULL(screening.hiv_performed, '-') as hiv_performed,
    '-' as hiv_target_category,
    IFNULL(screening.hiv_result, '-') as hiv_result,
    IFNULL(screening.travel_malaria, '-') as travel_malaria,
    IFNULL(screening.tb_screened, '-') as tb_screened,
    IFNULL(screening.tb_result, '-') as tb_result,
    '-' as tb_eval_type,
    IFNULL(screening.tb_result, '-') as tb_screening_result,
    IFNULL(screening.discharge_condition, IF(v.date_stopped IS NOT NULL, 'Discharged / Improved', '-')) as condition_at_discharge,
    IF(p.dead = 1, IF(TIMESTAMPDIFF(HOUR, v.date_started, IFNULL(p.death_date, v.date_stopped)) <= 24, 'Within 24 hrs', 'After 24 hrs'), '-') as death_in_ipd,
    IF(p.dead = 1, 'Yes', 'No') as death_notification,
    IFNULL(pm_attr.value, 'Free') as payment_method,
    IFNULL(ref_attr.value, '-') as voucher_no,
    '-' as remark
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
JOIN patient_identifier_type pit ON pi.identifier_type = pit.patient_identifier_type_id
JOIN global_property gp ON gp.property = 'bahmni.primaryIdentifierType' AND gp.property_value = pit.uuid
JOIN person p ON v.patient_id = p.person_id
JOIN person_name pn ON v.patient_id = pn.person_id AND pn.voided = 0
LEFT JOIN person_address pa ON v.patient_id = pa.person_id AND pa.voided = 0
LEFT JOIN (
    SELECT bp.patient_id, b.bed_number, bp.date_started, bp.date_stopped
    FROM bed_patient_assignment_map bp
    JOIN bed b ON bp.bed_id = b.bed_id
    WHERE bp.voided = 0
) bed_info ON v.patient_id = bed_info.patient_id AND (bed_info.date_stopped IS NULL OR bed_info.date_started >= v.date_started)
LEFT JOIN (
    SELECT 
        e.visit_id,
        GROUP_CONCAT(DISTINCT COALESCE(cn.name, o.value_text) SEPARATOR '; ') as admission_diag,
        GROUP_CONCAT(DISTINCT crt.code SEPARATOR '; ') as icd11_code,
        GROUP_CONCAT(DISTINCT COALESCE(cn.name, o.value_text) SEPARATOR '; ') as discharge_diag
    FROM encounter e
    JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0
        AND o.concept_id IN (SELECT concept_id FROM concept_name WHERE name IN ('Coded Diagnosis', 'Visit Diagnoses', 'Diagnosis') AND voided = 0)
    LEFT JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
    LEFT JOIN concept_reference_map crm ON o.value_coded = crm.concept_id
    LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
    GROUP BY e.visit_id
) diag ON v.visit_id = diag.visit_id
LEFT JOIN (
    SELECT
        e.visit_id,
        MAX(CASE WHEN cn.name LIKE '%HIV%Offer%' OR cn.name LIKE '%HIV%Test%' THEN IF(o.value_coded IS NOT NULL, 'Yes', o.value_text) END) as hiv_offered,
        MAX(CASE WHEN cn.name LIKE '%HIV%Perform%' THEN IF(o.value_coded IS NOT NULL, 'Yes', o.value_text) END) as hiv_performed,
        MAX(CASE WHEN cn.name LIKE '%HIV%Result%' OR cn.name = 'HIV Status' THEN COALESCE(val_cn.name, o.value_text) END) as hiv_result,
        MAX(CASE WHEN cn.name LIKE '%Malaria%' OR cn.name LIKE '%Travel%' THEN IF(o.value_coded IS NOT NULL, 'Yes', o.value_text) END) as travel_malaria,
        MAX(CASE WHEN cn.name LIKE '%TB%' OR cn.name LIKE '%Tuberculosis%' THEN COALESCE(val_cn.name, IF(o.value_coded IS NOT NULL, 'Yes', o.value_text)) END) as tb_screened,
        MAX(CASE WHEN cn.name LIKE '%TB%Result%' THEN COALESCE(val_cn.name, o.value_text) END) as tb_result,
        MAX(CASE WHEN cn.name LIKE '%Traffic%' OR cn.name LIKE '%Accident%' THEN COALESCE(val_cn.name, o.value_text) END) as rta_obs,
        MAX(CASE WHEN cn.name LIKE '%Discharge Condition%' OR cn.name LIKE '%Condition at Discharge%' THEN COALESCE(val_cn.name, o.value_text) END) as discharge_condition
    FROM encounter e
    JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0
    JOIN concept_name cn ON o.concept_id = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
    LEFT JOIN concept_name val_cn ON o.value_coded = val_cn.concept_id AND val_cn.concept_name_type = 'FULLY_SPECIFIED' AND val_cn.locale = 'en'
    GROUP BY e.visit_id
) screening ON v.visit_id = screening.visit_id
LEFT JOIN person_attribute pm_attr ON v.patient_id = pm_attr.person_id AND pm_attr.person_attribute_type_id = 17 AND pm_attr.voided = 0
LEFT JOIN person_attribute ref_attr ON v.patient_id = ref_attr.person_id AND ref_attr.person_attribute_type_id = 15 AND ref_attr.voided = 0
WHERE v.voided = 0 AND (
    vt.name IN ('Emergency OPD', 'Delivery Room', 'IPD')
    OR vt.name LIKE '%ward%'
    OR v.visit_id IN (SELECT visit_id FROM encounter WHERE encounter_type IN (3, 4))
    OR v.patient_id IN (SELECT patient_id FROM bed_patient_assignment_map WHERE voided = 0)
)
GROUP BY v.visit_id
ORDER BY v.date_started DESC
LIMIT 10;
"""

cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print('Complete register columns test:')
print(res.stdout)
