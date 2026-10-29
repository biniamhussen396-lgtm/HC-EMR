DELETE FROM global_property WHERE property = 'emrapi.sqlSearch.referralManagement';

INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.referralManagement', 'SELECT
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
    IFNULL(MAX(CASE WHEN rcn.name = ''Refers'' THEN ro.value_text END), '''') AS referredTo,
    IFNULL(MAX(CASE WHEN rcn.name = ''Referral department'' THEN ro.value_text END), '''') AS department,
    IFNULL(MAX(CASE WHEN rcn.name = ''Non-coded Diagnosis'' THEN ro.value_text END), '''') AS diagnosis,
    IFNULL(MAX(CASE WHEN rcn.name = ''Patient condition at referral'' THEN ro.value_text END), '''') AS patientCondition,
    IFNULL(MAX(CASE WHEN rcn.name = ''Reason for referral (text)'' THEN ro.value_text END), '''') AS reasonForReferral,
    IFNULL(MAX(CASE WHEN rcn.name = ''Need ambulance'' THEN ro.value_text END), '''') AS needAmbulance,
    IFNULL(MAX(CASE WHEN rcn.name = ''Need escorting professionals'' THEN ro.value_text END), '''') AS needEscorting,
    IF(loc.uuid = ${location_uuid}, ''Out'', ''In'') AS referralDirection,
    IFNULL(MAX(eloc.name), '''') AS location,
    COALESCE(
        NULLIF(TRIM(MAX(CONCAT(cu_pn.given_name, IF(cu_pn.middle_name IS NOT NULL AND cu_pn.middle_name != '''', CONCAT('' '', cu_pn.middle_name), ''''), IF(cu_pn.family_name IS NOT NULL AND cu_pn.family_name != '''', CONCAT('' '', cu_pn.family_name), '''')))), ''''),
        NULLIF(TRIM(MAX(CONCAT(prv_pn.given_name, IF(prv_pn.middle_name IS NOT NULL AND prv_pn.middle_name != '''', CONCAT('' '', prv_pn.middle_name), ''''), IF(prv_pn.family_name IS NOT NULL AND prv_pn.family_name != '''', CONCAT('' '', prv_pn.family_name), '''')))), ''''),
        MAX(cu.username),
        ''''
    ) AS physicianName,
    IFNULL(MAX(CASE WHEN rcn.name = ''Referral Approved By'' THEN ro.value_text END), '''') AS approvedBy,
    IFNULL(MAX(CASE WHEN rcn.name = ''Referral Senior Physician Specialty'' THEN ro.value_text END), '''') AS approvedSpecialty,
    IFNULL(MAX(CASE WHEN rcn.name = ''Referral Approval Method'' THEN ro.value_text END), '''') AS approvalMethod,
    IFNULL(MAX(CASE WHEN rcn.name = ''Referral Approval DateTime'' THEN ro.value_text END), '''') AS approvalDateTime,
    IFNULL(MAX(CASE WHEN rcn.name = ''Referral Approval Notes'' THEN ro.value_text END), '''') AS approvalNotes
FROM (
    SELECT DISTINCT disp_o.encounter_id
    FROM obs disp_o
    INNER JOIN concept_name disp_cn ON disp_o.value_coded = disp_cn.concept_id 
        AND disp_cn.name = ''Refer Patient'' 
        AND disp_cn.concept_name_type = ''FULLY_SPECIFIED'' 
        AND disp_cn.voided = 0
    WHERE disp_o.voided = 0
) ref_enc
INNER JOIN encounter e ON ref_enc.encounter_id = e.encounter_id AND e.voided = 0
INNER JOIN visit v ON e.visit_id = v.visit_id AND v.voided = 0
INNER JOIN person p ON v.patient_id = p.person_id AND p.voided = 0
INNER JOIN person_name pn ON p.person_id = pn.person_id AND pn.voided = 0
INNER JOIN patient_identifier pi ON p.person_id = pi.patient_id AND pi.voided = 0
INNER JOIN patient_identifier_type pit ON pi.identifier_type = pit.patient_identifier_type_id
INNER JOIN global_property gp ON gp.property = ''bahmni.primaryIdentifierType'' AND gp.property_value = pit.uuid
LEFT JOIN person_address pa ON p.person_id = pa.person_id AND pa.voided = 0 AND pa.preferred = 1
INNER JOIN location loc ON v.location_id = loc.location_id
LEFT JOIN location eloc ON e.location_id = eloc.location_id
LEFT JOIN users cu ON e.creator = cu.user_id
LEFT JOIN person_name cu_pn ON cu.person_id = cu_pn.person_id AND cu_pn.voided = 0
LEFT JOIN encounter_provider ep ON e.encounter_id = ep.encounter_id AND ep.voided = 0
LEFT JOIN provider prv ON ep.provider_id = prv.provider_id
LEFT JOIN person_name prv_pn ON prv.person_id = prv_pn.person_id AND prv_pn.voided = 0
LEFT JOIN obs ro ON e.encounter_id = ro.encounter_id AND ro.voided = 0
LEFT JOIN concept_name rcn ON ro.concept_id = rcn.concept_id 
    AND rcn.name IN (
        ''Refers'', ''Referral department'', ''Non-coded Diagnosis'', 
        ''Patient condition at referral'', ''Reason for referral (text)'', 
        ''Need ambulance'', ''Need escorting professionals'', 
        ''Referral Approved By'', ''Referral Senior Physician Specialty'', 
        ''Referral Approval Method'', ''Referral Approval DateTime'', 
        ''Referral Approval Notes''
    )
    AND rcn.concept_name_type = ''FULLY_SPECIFIED'' 
    AND rcn.voided = 0
GROUP BY v.visit_id, e.encounter_id, pn.given_name, pn.middle_name, pn.family_name, 
         pi.identifier, p.birthdate, p.gender, pa.state_province, pa.county_district, 
         pa.city_village, pa.address2, p.uuid, v.uuid, v.date_created, v.date_stopped, loc.uuid
ORDER BY v.date_created DESC', 'SQL query for Referral Management register', UUID());
