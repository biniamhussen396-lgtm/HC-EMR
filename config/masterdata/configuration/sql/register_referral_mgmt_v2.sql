DELETE FROM global_property WHERE property = 'emrapi.sqlSearch.referralManagement';

INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.referralManagement', 'SELECT DISTINCT
    TRIM(CONCAT(pn.given_name, IF(pn.middle_name IS NOT NULL AND pn.middle_name != '''', CONCAT('' '', pn.middle_name), ''''), IF(pn.family_name IS NOT NULL AND pn.family_name != '''', CONCAT('' '', pn.family_name), ''''))) AS name,
    pi.identifier AS identifier,
    concat('''', p.uuid) AS patientUuid,
    concat('''', v.uuid) AS visitUuid,
    TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) AS age,
    IF(p.gender = ''M'', ''Male'', IF(p.gender = ''F'', ''Female'', ''Other'')) AS sex,
    IFNULL(pa.state_province, '''') AS region,
    IFNULL(pa.county_district, '''') AS subcity,
    IFNULL(pa.city_village, '''') AS woreda,
    IFNULL(pa.address2, '''') AS kebele,
    v.date_created AS referDate,
    v.date_stopped AS closedDate,
    IF(v.date_stopped IS NULL, ''Open'', ''Closed'') AS status,
    IFNULL(refers.value_text, '''') AS referredTo,
    IFNULL(dept.value_text, '''') AS department,
    IFNULL(diag.value_text, '''') AS diagnosis,
    IFNULL(cond.value_text, '''') AS patientCondition,
    IFNULL(reason.value_text, '''') AS reasonForReferral,
    IFNULL(ambulance.value_text, '''') AS needAmbulance,
    IFNULL(escort.value_text, '''') AS needEscorting,
    IF(loc.uuid = ${location_uuid}, ''Out'', ''In'') AS referralDirection,
    IFNULL(MAX(eloc.name), '''') AS location,
    COALESCE(
        NULLIF(TRIM(MAX(CONCAT(cu_pn.given_name, IF(cu_pn.middle_name IS NOT NULL AND cu_pn.middle_name != '''', CONCAT('' '', cu_pn.middle_name), ''''), IF(cu_pn.family_name IS NOT NULL AND cu_pn.family_name != '''', CONCAT('' '', cu_pn.family_name), '''')))), ''''),
        NULLIF(TRIM(MAX(CONCAT(prv_pn.given_name, IF(prv_pn.middle_name IS NOT NULL AND prv_pn.middle_name != '''', CONCAT('' '', prv_pn.middle_name), ''''), IF(prv_pn.family_name IS NOT NULL AND prv_pn.family_name != '''', CONCAT('' '', prv_pn.family_name), '''')))), ''''),
        MAX(cu.username),
        ''''
    ) AS physicianName,
    IFNULL(MAX(ref_appr.value_text), '''') AS approvedBy,
    IFNULL(MAX(ref_spec.value_text), '''') AS approvedSpecialty,
    IFNULL(MAX(ref_method.value_text), '''') AS approvalMethod,
    IFNULL(MAX(ref_dt.value_text), '''') AS approvalDateTime,
    IFNULL(MAX(ref_notes.value_text), '''') AS approvalNotes
FROM visit v
INNER JOIN person_name pn ON v.patient_id = pn.person_id AND pn.voided = 0
INNER JOIN patient_identifier pi ON v.patient_id = pi.patient_id
INNER JOIN patient_identifier_type pit ON pi.identifier_type = pit.patient_identifier_type_id
INNER JOIN global_property gp ON gp.property = ''bahmni.primaryIdentifierType'' AND gp.property_value = pit.uuid
INNER JOIN person p ON v.patient_id = p.person_id
LEFT JOIN person_address pa ON p.person_id = pa.person_id AND pa.preferred = 1
INNER JOIN encounter e ON v.visit_id = e.visit_id
INNER JOIN obs disp_o ON e.encounter_id = disp_o.encounter_id AND disp_o.voided = 0
INNER JOIN concept_name disp_cn ON disp_o.value_coded = disp_cn.concept_id AND disp_cn.concept_name_type = ''FULLY_SPECIFIED'' AND disp_cn.voided = 0
INNER JOIN location loc ON v.location_id = loc.location_id
LEFT JOIN location eloc ON e.location_id = eloc.location_id
LEFT JOIN users cu ON e.creator = cu.user_id
LEFT JOIN person_name cu_pn ON cu.person_id = cu_pn.person_id AND cu_pn.voided = 0
LEFT JOIN encounter_provider ep ON e.encounter_id = ep.encounter_id AND ep.voided = 0
LEFT JOIN provider prv ON ep.provider_id = prv.provider_id
LEFT JOIN person_name prv_pn ON prv.person_id = prv_pn.person_id AND prv_pn.voided = 0
LEFT JOIN obs refers ON e.encounter_id = refers.encounter_id AND refers.voided = 0 AND refers.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Refers'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
LEFT JOIN obs dept ON e.encounter_id = dept.encounter_id AND dept.voided = 0 AND dept.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Referral department'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
LEFT JOIN obs diag ON e.encounter_id = diag.encounter_id AND diag.voided = 0 AND diag.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Non-coded Diagnosis'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
LEFT JOIN obs cond ON e.encounter_id = cond.encounter_id AND cond.voided = 0 AND cond.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Patient condition at referral'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
LEFT JOIN obs reason ON e.encounter_id = reason.encounter_id AND reason.voided = 0 AND reason.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Reason for referral (text)'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
LEFT JOIN obs ambulance ON e.encounter_id = ambulance.encounter_id AND ambulance.voided = 0 AND ambulance.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Need ambulance'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
LEFT JOIN obs escort ON e.encounter_id = escort.encounter_id AND escort.voided = 0 AND escort.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Need escorting professionals'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
LEFT JOIN obs ref_appr ON e.encounter_id = ref_appr.encounter_id AND ref_appr.voided = 0 AND ref_appr.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Referral Approved By'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
LEFT JOIN obs ref_spec ON e.encounter_id = ref_spec.encounter_id AND ref_spec.voided = 0 AND ref_spec.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Referral Senior Physician Specialty'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
LEFT JOIN obs ref_method ON e.encounter_id = ref_method.encounter_id AND ref_method.voided = 0 AND ref_method.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Referral Approval Method'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
LEFT JOIN obs ref_dt ON e.encounter_id = ref_dt.encounter_id AND ref_dt.voided = 0 AND ref_dt.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Referral Approval DateTime'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
LEFT JOIN obs ref_notes ON e.encounter_id = ref_notes.encounter_id AND ref_notes.voided = 0 AND ref_notes.concept_id = (SELECT concept_id FROM concept_name WHERE name = ''Referral Approval Notes'' AND concept_name_type = ''FULLY_SPECIFIED'' AND voided = 0 LIMIT 1)
WHERE v.voided = 0
AND disp_cn.name = ''Refer Patient''
AND EXISTS (
    SELECT 1 FROM location_tag_map ltm
    JOIN location_tag lt ON ltm.location_tag_id = lt.location_tag_id
    JOIN location l ON ltm.location_id = l.location_id
    WHERE l.uuid = ${location_uuid} AND lt.name = ''Refer''
)
GROUP BY v.visit_id, pn.given_name, pn.middle_name, pn.family_name, pi.identifier, p.birthdate, p.gender, pa.state_province, pa.county_district, pa.city_village, pa.address2, p.uuid, v.uuid, v.date_created, v.date_stopped, loc.uuid
ORDER BY v.date_created DESC', 'Referral Management SQL search handler', 'a1b2c3d4-e5f6-7890-abcd-100000000020');
