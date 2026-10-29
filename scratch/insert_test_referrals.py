import subprocess

sql = """
-- 1. Get or create primary identifier type
SET @pit_id = (SELECT pit.patient_identifier_type_id FROM patient_identifier_type pit JOIN global_property gp ON gp.property = 'bahmni.primaryIdentifierType' AND gp.property_value = pit.uuid LIMIT 1);
SET @loc_id = (SELECT location_id FROM location WHERE name = 'Emergency OPD' LIMIT 1);
DELETE FROM obs WHERE person_id IN (SELECT person_id FROM person WHERE uuid IN ('11111111-2222-3333-4444-555555555501', '11111111-2222-3333-4444-555555555502'));
DELETE FROM encounter WHERE patient_id IN (SELECT person_id FROM person WHERE uuid IN ('11111111-2222-3333-4444-555555555501', '11111111-2222-3333-4444-555555555502'));
DELETE FROM visit WHERE patient_id IN (SELECT person_id FROM person WHERE uuid IN ('11111111-2222-3333-4444-555555555501', '11111111-2222-3333-4444-555555555502'));
DELETE FROM patient_identifier WHERE patient_id IN (SELECT person_id FROM person WHERE uuid IN ('11111111-2222-3333-4444-555555555501', '11111111-2222-3333-4444-555555555502'));
DELETE FROM patient WHERE patient_id IN (SELECT person_id FROM person WHERE uuid IN ('11111111-2222-3333-4444-555555555501', '11111111-2222-3333-4444-555555555502'));
DELETE FROM person_address WHERE person_id IN (SELECT person_id FROM person WHERE uuid IN ('11111111-2222-3333-4444-555555555501', '11111111-2222-3333-4444-555555555502'));
DELETE FROM person_name WHERE person_id IN (SELECT person_id FROM person WHERE uuid IN ('11111111-2222-3333-4444-555555555501', '11111111-2222-3333-4444-555555555502'));
DELETE FROM person WHERE uuid IN ('11111111-2222-3333-4444-555555555501', '11111111-2222-3333-4444-555555555502');

SET @user_id = 1;
SET @provider_id = (SELECT provider_id FROM provider LIMIT 1);

-- Concepts
SET @disp_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Disposition' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @refer_coded_id = (SELECT concept_id FROM concept_name WHERE name = 'Refer Patient' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);

SET @refers_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Refers' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @dept_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Referral department' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @diag_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Non-coded Diagnosis' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @cond_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Patient condition at referral' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @reason_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Reason for referral (text)' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @clin_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Relevant clinical history' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @treat_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Treatment provided' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @cc_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Chief complaint (text)' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @hpi_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'History of present illness' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @amb_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Need ambulance' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @esc_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Need escorting professionals' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);

-- Vitals concepts
SET @sbp_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Systolic blood pressure' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @dbp_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Diastolic blood pressure' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @pr_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Pulse' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @rr_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Respiratory rate' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @temp_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Temperature' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @spo2_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Arterial blood oxygen saturation (pulse oximeter)' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @o2_concept_id = COALESCE((SELECT concept_id FROM concept_name WHERE name = 'Oxygen' AND voided = 0 LIMIT 1), 1240);
SET @lab_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Lab results (text)' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);

-- 5 Senior Physician Approval Concepts
SET @appr_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Referral Approved By' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @spec_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Referral Senior Physician Specialty' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @meth_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Referral Approval Method' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @dt_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Referral Approval DateTime' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);
SET @notes_concept_id = (SELECT concept_id FROM concept_name WHERE name = 'Referral Approval Notes' AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1);

-- Encounter type Consultation
SET @enc_type_id = (SELECT encounter_type_id FROM encounter_type WHERE name = 'Consultation' LIMIT 1);
SET @visit_type_id = COALESCE((SELECT visit_type_id FROM visit_type WHERE name = 'Emergency' LIMIT 1), (SELECT visit_type_id FROM visit_type LIMIT 1));

-- Ensure Doctor User has First + Middle + Last name
UPDATE person_name SET middle_name = 'Yimer', family_name = 'Hassen' WHERE person_id = (SELECT person_id FROM users WHERE username = 'admin' LIMIT 1) AND (middle_name IS NULL OR middle_name = '');

-- PATIENT 1: ENDRIS ABEGAZ KEBEDE (Approved)
INSERT INTO person (gender, birthdate, birthdate_estimated, dead, creator, date_created, voided, uuid)
VALUES ('M', '1971-04-10', 0, 0, @user_id, NOW(), 0, '11111111-2222-3333-4444-555555555501');
SET @p1_id = LAST_INSERT_ID();

INSERT INTO person_name (preferred, person_id, given_name, middle_name, family_name, creator, date_created, voided, uuid)
VALUES (1, @p1_id, 'ENDRIS', 'ABEGAZ', 'KEBEDE', @user_id, NOW(), 0, UUID());

INSERT INTO person_address (preferred, person_id, state_province, county_district, city_village, address2, creator, date_created, voided, uuid)
VALUES (1, @p1_id, 'Amhara', 'South Wello', 'Kutaber', '02', @user_id, NOW(), 0, UUID());

INSERT INTO patient (patient_id, creator, date_created, voided)
VALUES (@p1_id, @user_id, NOW(), 0);

INSERT INTO patient_identifier (patient_id, identifier, identifier_type, preferred, location_id, creator, date_created, voided, uuid)
VALUES (@p1_id, '501839', @pit_id, 1, @loc_id, @user_id, NOW(), 0, UUID());

INSERT INTO visit (patient_id, visit_type_id, date_started, date_stopped, location_id, creator, date_created, voided, uuid)
VALUES (@p1_id, @visit_type_id, NOW(), NOW(), @loc_id, @user_id, NOW(), 0, '22222222-3333-4444-5555-666666666601');
SET @v1_id = LAST_INSERT_ID();

INSERT INTO encounter (encounter_type, patient_id, location_id, encounter_datetime, creator, date_created, voided, visit_id, uuid)
VALUES (@enc_type_id, @p1_id, @loc_id, NOW(), @user_id, NOW(), 0, @v1_id, '33333333-4444-5555-6666-777777777701');
SET @e1_id = LAST_INSERT_ID();

-- Obs for Patient 1
INSERT INTO obs (person_id, concept_id, encounter_id, order_id, obs_datetime, location_id, value_coded, creator, date_created, voided, uuid)
VALUES (@p1_id, @disp_concept_id, @e1_id, NULL, NOW(), @loc_id, @refer_coded_id, @user_id, NOW(), 0, UUID());

INSERT INTO obs (person_id, concept_id, encounter_id, obs_datetime, location_id, value_text, creator, date_created, voided, uuid) VALUES
(@p1_id, @refers_concept_id, @e1_id, NOW(), @loc_id, 'DCSH', @user_id, NOW(), 0, UUID()),
(@p1_id, @dept_concept_id, @e1_id, NOW(), @loc_id, 'Emergency/Urology', @user_id, NOW(), 0, UUID()),
(@p1_id, @cond_concept_id, @e1_id, NOW(), @loc_id, 'Emergency', @user_id, NOW(), 0, UUID()),
(@p1_id, @cc_concept_id, @e1_id, NOW(), @loc_id, 'cough and SOB aof 3 days', @user_id, NOW(), 0, UUID()),
(@p1_id, @hpi_concept_id, @e1_id, NOW(), @loc_id, 'This is a 55yrs old male pt who presented with history of SOB and cough associated with blood-tinged sputum and chest pain of 3 week duration. He also has left leg swelling of 1 month.', @user_id, NOW(), 0, UUID()),
(@p1_id, @sbp_concept_id, @e1_id, NOW(), @loc_id, '130.0', @user_id, NOW(), 0, UUID()),
(@p1_id, @dbp_concept_id, @e1_id, NOW(), @loc_id, '80.0', @user_id, NOW(), 0, UUID()),
(@p1_id, @pr_concept_id, @e1_id, NOW(), @loc_id, '89.0', @user_id, NOW(), 0, UUID()),
(@p1_id, @rr_concept_id, @e1_id, NOW(), @loc_id, '15.0', @user_id, NOW(), 0, UUID()),
(@p1_id, @temp_concept_id, @e1_id, NOW(), @loc_id, '37.0', @user_id, NOW(), 0, UUID()),
(@p1_id, @spo2_concept_id, @e1_id, NOW(), @loc_id, '97.0', @user_id, NOW(), 0, UUID()),
(@p1_id, @o2_concept_id, @e1_id, NOW(), @loc_id, 'True', @user_id, NOW(), 0, UUID()),
(@p1_id, @lab_concept_id, @e1_id, NOW(), @loc_id, 'cr= 1st=0.37 2nd = 3.49, bun/urea 1st=33 2nd=147 AST=60/23 ALT=54/28,K=5.64,Na=143 wbc=3-9 with gran=71.4 % hgb=8.8 then wbc=5.28 with gran 89.7% esr=147 Abd U/S- right echogenic kedney left severe hydrouretronephrosis + proximal yretric stine bilateral minimal pleural effusion Rt small renal cyst', @user_id, NOW(), 0, UUID()),
(@p1_id, @diag_concept_id, @e1_id, NOW(), @loc_id, 'P1=PTB + superimposed multifocal pneumonia P2- AKI 2 to ?septic ATN P3- Left side severe hydrourethronephrosis 2 to renal stone P-Chronic left lower extremity DVT', @user_id, NOW(), 0, UUID()),
(@p1_id, @treat_concept_id, @e1_id, NOW(), @loc_id, 'InO2 cetepime 1gm iv BID vancomycin 1gm iv every 72 hrs -dexamethasone 6mg iv qid -Omeprazole 40 mg iv bid -UFH 5000IU iu SC BID -Anti TB with alternating RHZE(4x/wk) and RH(3x/wk)', @user_id, NOW(), 0, UUID()),
(@p1_id, @reason_concept_id, @e1_id, NOW(), @loc_id, 'for left nephrostomy tube', @user_id, NOW(), 0, UUID()),
(@p1_id, @amb_concept_id, @e1_id, NOW(), @loc_id, 'Yes', @user_id, NOW(), 0, UUID()),
(@p1_id, @esc_concept_id, @e1_id, NOW(), @loc_id, 'Yes', @user_id, NOW(), 0, UUID()),
-- Senior Physician Approval
(@p1_id, @appr_concept_id, @e1_id, NOW(), @loc_id, 'Dr Zerubabel Amare Haile', @user_id, NOW(), 0, UUID()),
(@p1_id, @spec_concept_id, @e1_id, NOW(), @loc_id, 'Consultant General Surgeon', @user_id, NOW(), 0, UUID()),
(@p1_id, @meth_concept_id, @e1_id, NOW(), @loc_id, 'Telephone Consultation', @user_id, NOW(), 0, UUID()),
(@p1_id, @dt_concept_id, @e1_id, NOW(), @loc_id, '25/10/2026 14:15', @user_id, NOW(), 0, UUID()),
(@p1_id, @notes_concept_id, @e1_id, NOW(), @loc_id, 'Approved for urgent left nephrostomy tube placement at DCSH.', @user_id, NOW(), 0, UUID());


-- PATIENT 2: TESLIM KEDIR AHMED (Pending Approval)
INSERT INTO person (gender, birthdate, birthdate_estimated, dead, creator, date_created, voided, uuid)
VALUES ('F', '2026-10-01', 0, 0, @user_id, NOW(), 0, '11111111-2222-3333-4444-555555555502');
SET @p2_id = LAST_INSERT_ID();

INSERT INTO person_name (preferred, person_id, given_name, middle_name, family_name, creator, date_created, voided, uuid)
VALUES (1, @p2_id, 'Teslim', 'Kedir', 'Ahmed', @user_id, NOW(), 0, UUID());

INSERT INTO person_address (preferred, person_id, state_province, county_district, city_village, address2, creator, date_created, voided, uuid)
VALUES (1, @p2_id, 'Amhara', 'Dessie Town', 'Dessie Town', '012', @user_id, NOW(), 0, UUID());

INSERT INTO patient (patient_id, creator, date_created, voided)
VALUES (@p2_id, @user_id, NOW(), 0);

INSERT INTO patient_identifier (patient_id, identifier, identifier_type, preferred, location_id, creator, date_created, voided, uuid)
VALUES (@p2_id, '502292', @pit_id, 1, @loc_id, @user_id, NOW(), 0, UUID());

INSERT INTO visit (patient_id, visit_type_id, date_started, date_stopped, location_id, creator, date_created, voided, uuid)
VALUES (@p2_id, @visit_type_id, NOW(), NULL, @loc_id, @user_id, NOW(), 0, '22222222-3333-4444-5555-666666666602');
SET @v2_id = LAST_INSERT_ID();

INSERT INTO encounter (encounter_type, patient_id, location_id, encounter_datetime, creator, date_created, voided, visit_id, uuid)
VALUES (@enc_type_id, @p2_id, @loc_id, NOW(), @user_id, NOW(), 0, @v2_id, '33333333-4444-5555-6666-777777777702');
SET @e2_id = LAST_INSERT_ID();

INSERT INTO obs (person_id, concept_id, encounter_id, order_id, obs_datetime, location_id, value_coded, creator, date_created, voided, uuid)
VALUES (@p2_id, @disp_concept_id, @e2_id, NULL, NOW(), @loc_id, @refer_coded_id, @user_id, NOW(), 0, UUID());

INSERT INTO obs (person_id, concept_id, encounter_id, obs_datetime, location_id, value_text, creator, date_created, voided, uuid) VALUES
(@p2_id, @refers_concept_id, @e2_id, NOW(), @loc_id, 'DCSH', @user_id, NOW(), 0, UUID()),
(@p2_id, @dept_concept_id, @e2_id, NOW(), @loc_id, 'NICU', @user_id, NOW(), 0, UUID()),
(@p2_id, @cond_concept_id, @e2_id, NOW(), @loc_id, 'Emergency', @user_id, NOW(), 0, UUID()),
(@p2_id, @diag_concept_id, @e2_id, NOW(), @loc_id, 'Moderate Preterm (32 wks by Ballard) + VLBW(1200gm) + SGA + ?RDS + ?EONS', @user_id, NOW(), 0, UUID()),
(@p2_id, @reason_concept_id, @e2_id, NOW(), @loc_id, 'For better preterm setup', @user_id, NOW(), 0, UUID()),
(@p2_id, @amb_concept_id, @e2_id, NOW(), @loc_id, 'Yes', @user_id, NOW(), 0, UUID()),
(@p2_id, @esc_concept_id, @e2_id, NOW(), @loc_id, 'Yes', @user_id, NOW(), 0, UUID());
-- No senior physician approval obs inserted for Patient 2 -> Will be Pending!

SELECT 'Successfully created test referrals!' AS result;
"""

res = subprocess.run(
    ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs'],
    input=sql.encode('utf-8'),
    capture_output=True
)
print("STDOUT:", res.stdout.decode('utf-8', errors='ignore'))
if res.stderr:
    print("STDERR:", res.stderr.decode('utf-8', errors='ignore'))
