-- Ensure Emergency keep concept exists with uuid '2d622905-5e79-4c3d-920a-a34ee19173c6'
INSERT INTO concept (retired, datatype_id, class_id, is_set, creator, date_created, uuid)
SELECT 0, 4, 11, 0, 1, NOW(), '2d622905-5e79-4c3d-920a-a34ee19173c6'
WHERE NOT EXISTS (
    SELECT 1 FROM concept WHERE uuid = '2d622905-5e79-4c3d-920a-a34ee19173c6'
) AND NOT EXISTS (
    SELECT 1 FROM concept_name WHERE name = 'Emergency keep' AND voided = 0
);

-- If concept exists by name, ensure it has the expected UUID
UPDATE concept c
JOIN concept_name cn ON c.concept_id = cn.concept_id
SET c.uuid = '2d622905-5e79-4c3d-920a-a34ee19173c6'
WHERE cn.name = 'Emergency keep' AND cn.voided = 0;

-- Ensure FULLY_SPECIFIED name exists
INSERT INTO concept_name (concept_id, name, locale, locale_preferred, creator, date_created, concept_name_type, voided, uuid)
SELECT c.concept_id, 'Emergency keep', 'en', 1, 1, NOW(), 'FULLY_SPECIFIED', 0, UUID()
FROM concept c
WHERE c.uuid = '2d622905-5e79-4c3d-920a-a34ee19173c6'
AND NOT EXISTS (
    SELECT 1 FROM concept_name WHERE concept_id = c.concept_id AND name = 'Emergency keep' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0
);

-- Ensure SHORT name exists
INSERT INTO concept_name (concept_id, name, locale, locale_preferred, creator, date_created, concept_name_type, voided, uuid)
SELECT c.concept_id, 'Emergency keep', 'en', 0, 1, NOW(), 'SHORT', 0, UUID()
FROM concept c
WHERE c.uuid = '2d622905-5e79-4c3d-920a-a34ee19173c6'
AND NOT EXISTS (
    SELECT 1 FROM concept_name WHERE concept_id = c.concept_id AND name = 'Emergency keep' AND concept_name_type = 'SHORT' AND voided = 0
);

-- 1. Get the emrapi concept source ID
SET @emrapi_source_id = (SELECT concept_source_id FROM concept_reference_source 
    WHERE name = 'org.openmrs.module.emrapi' LIMIT 1);

-- 2. Create reference term EMERGENCY_KEEP if not exists
INSERT INTO concept_reference_term (concept_source_id, code, name, creator, date_created, uuid, retired)
SELECT @emrapi_source_id, 'EMERGENCY_KEEP', NULL, 1, NOW(), UUID(), 0
WHERE NOT EXISTS (
    SELECT 1 FROM concept_reference_term 
    WHERE concept_source_id = @emrapi_source_id AND code = 'EMERGENCY_KEEP'
);
UPDATE concept_reference_term SET name = NULL WHERE code = 'EMERGENCY_KEEP';

-- 3. Get the reference term ID
SET @emergency_term_id = (SELECT concept_reference_term_id FROM concept_reference_term 
    WHERE concept_source_id = @emrapi_source_id AND code = 'EMERGENCY_KEEP' LIMIT 1);

-- 4. Get the Emergency keep concept ID dynamically
SET @emergency_concept_id = (SELECT concept_id FROM concept WHERE uuid = '2d622905-5e79-4c3d-920a-a34ee19173c6' LIMIT 1);

-- 5. Map concept to reference term (if not already mapped)
INSERT INTO concept_reference_map (concept_reference_term_id, concept_id, creator, date_created, uuid)
SELECT @emergency_term_id, @emergency_concept_id, 1, NOW(), UUID()
WHERE @emergency_concept_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM concept_reference_map 
    WHERE concept_reference_term_id = @emergency_term_id 
    AND concept_id = @emergency_concept_id
);

-- 6. Add as answer to Disposition concept (finding Disposition concept by name or uuid)
SET @disposition_concept_id = (SELECT concept_id FROM concept_name
    WHERE name = 'Disposition' AND concept_name_type = 'FULLY_SPECIFIED' 
    AND locale = 'en' AND voided = 0 LIMIT 1);

INSERT INTO concept_answer (concept_id, answer_concept, creator, date_created, uuid)
SELECT @disposition_concept_id, @emergency_concept_id, 1, NOW(), UUID()
WHERE @disposition_concept_id IS NOT NULL 
AND @emergency_concept_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM concept_answer 
    WHERE concept_id = @disposition_concept_id 
    AND answer_concept = @emergency_concept_id
);

-- Verify
SELECT 'EMERGENCY_KEEP mapping created successfully' AS result;
SELECT rt.code, rs.name as source, rm.concept_id as concept_id
FROM concept_reference_map rm
JOIN concept_reference_term rt ON rm.concept_reference_term_id = rt.concept_reference_term_id
JOIN concept_reference_source rs ON rt.concept_source_id = rs.concept_source_id
WHERE rs.name = 'org.openmrs.module.emrapi' AND rt.code = 'EMERGENCY_KEEP';

