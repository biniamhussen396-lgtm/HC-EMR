import pymysql

conn = pymysql.connect(
    host='127.0.0.1',
    port=3206,
    user='root',
    password='adminAdmin!123',
    database='openmrs',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cursor:
    # Test OPD Query
    opd_query = """
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
        v.date_started as service_date,
        vt.name as visit_type_name,
        IFNULL(diag.diagnosis_name, '-') as diagnosis_name,
        IFNULL(diag.icd11_code, '-') as icd11_code,
        IF(diag.diagnosis_occurrence = 'Repeat', 'Repeat', 'New') as patient_status,
        IF(vt.name LIKE '%ward%' OR vt.name IN ('Delivery Room', 'IPD', 'Adult MICU'), 'Admitted', '') as admitted_mark,
        IFNULL(screening.rta_type, '') as rta_type,
        IFNULL(screening.hiv_offered, 'Yes') as hiv_offered,
        IFNULL(screening.hiv_performed, 'Yes') as hiv_performed,
        IFNULL(screening.hiv_target_category, 'General population') as hiv_target_category,
        IFNULL(screening.hiv_result, 'Negative') as hiv_result,
        IFNULL(screening.travel_malaria, 'No') as travel_malaria,
        IFNULL(screening.tb_screened, 'Yes') as tb_screened,
        IFNULL(screening.tb_result, 'Negative') as tb_result,
        IFNULL(screening.tb_eval_type, 'Sputum smear microscopy') as tb_eval_type,
        IFNULL(screening.tb_code, 'No TB') as tb_code,
        IFNULL(ref.referred_to, '') as referred_to,
        IF(p.dead = 1, 'Yes', 'No') as died,
        IF(p.dead = 1, 'Yes', 'No') as death_notified,
        '' as remark
    FROM visit v
    JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
    JOIN patient_identifier pi ON v.patient_id = pi.patient_id
    JOIN patient_identifier_type pit ON pi.identifier_type = pit.patient_identifier_type_id
    JOIN global_property gp ON gp.property = 'bahmni.primaryIdentifierType' AND gp.property_value = pit.uuid
    JOIN person p ON v.patient_id = p.person_id
    JOIN person_name pn ON v.patient_id = pn.person_id AND pn.voided = 0
    LEFT JOIN person_address pa ON v.patient_id = pa.person_id AND pa.voided = 0
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
        JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0
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
    WHERE v.voided = 0
    GROUP BY v.visit_id
    ORDER BY v.visit_id DESC
    LIMIT 20;
    """
    cursor.execute(opd_query)
    rows = cursor.fetchall()
    print("OPD query rows returned:", len(rows))
    if rows:
        print("First row:", rows[0])
