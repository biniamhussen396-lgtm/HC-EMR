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

# Check exact location_ids for ICU / NICU
sql_locs = "SELECT location_id, name FROM location WHERE name LIKE '%ICU%' OR name LIKE '%HDU%';"
_, _, out_locs, _ = run_query(sql_locs)
print("ICU Locations:\n", out_locs)

sql_icu_fast = """
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
    DATE_FORMAT(v.date_started, '%Y-%m-%d %H:%i:%s') as admission_date,
    DATE_FORMAT(v.date_stopped, '%Y-%m-%d %H:%i:%s') as discharge_date,
    IF(v.date_stopped IS NULL, 'Admitted', 'Discharged') as status,
    DATEDIFF(IFNULL(v.date_stopped, NOW()), v.date_started) as length_of_stay,
    COALESCE(MAX(CASE WHEN el.name LIKE '%ICU%' THEN el.name END), vt.name, 'ICU') as ward_name,
    IFNULL(GROUP_CONCAT(DISTINCT CASE WHEN o.concept_id IN (22, 11847, 11848) THEN COALESCE(cn.name, o.value_text) END SEPARATOR '; '), '-') as admission_diag_name,
    IFNULL(GROUP_CONCAT(DISTINCT CASE WHEN o.concept_id IN (22, 11847, 11848) THEN crt.code END SEPARATOR '; '), '-') as admission_diag_code,
    IFNULL(GROUP_CONCAT(DISTINCT CASE WHEN o.concept_id IN (22, 11847, 11848) THEN COALESCE(cn.name, o.value_text) END SEPARATOR '; '), '-') as discharge_diag_name,
    IFNULL(GROUP_CONCAT(DISTINCT CASE WHEN o.concept_id IN (22, 11847, 11848) THEN crt.code END SEPARATOR '; '), '-') as discharge_diag_code,
    COALESCE(MAX(CASE WHEN o.concept_id = 63657 THEN IF(o.value_coded IS NOT NULL, 'Yes', o.value_text) END), '') as hiv_offered,
    COALESCE(MAX(CASE WHEN o.concept_id IN (22442, 63658) THEN IF(o.value_coded IS NOT NULL, 'Yes', o.value_text) END), '') as hiv_performed,
    COALESCE(MAX(CASE WHEN o.concept_id = 63659 THEN COALESCE(val_cn.name, o.value_text) END), '') as hiv_target_category,
    COALESCE(MAX(CASE WHEN o.concept_id IN (32992, 47297) THEN COALESCE(val_cn.name, o.value_text) END), '') as hiv_result,
    COALESCE(MAX(CASE WHEN o.concept_id IN (67614, 68611, 68248, 17984, 19446, 19830, 20013) THEN 'Yes' END), 'No') as mech_vent,
    COALESCE(MAX(CASE WHEN o.concept_id IN (19978) THEN o.value_numeric END), '0') as vent_days,
    COALESCE(MAX(CASE WHEN o.concept_id IN (33107) THEN 'Yes' END), 'No') as vap_developed,
    COALESCE(MAX(CASE WHEN o.concept_id IN (8699, 67626) THEN 'Yes' END), 'Yes') as nutr_assessment,
    COALESCE(MAX(CASE WHEN o.concept_id IN (67572, 8699, 19315, 26015) THEN 'Yes' END), 'Yes') as nutr_support,
    COALESCE(MAX(CASE 
        WHEN o.concept_id IN (67573) THEN '1. Enteral (PO)'
        WHEN o.concept_id IN (67575, 67576) THEN '1. Enteral (Tube/NGT)'
        WHEN o.concept_id IN (12743, 19286, 26015) THEN '2. Parenteral'
        WHEN o.concept_id IN (67574) THEN 'NPO'
    END), '1. Enteral') as feeding_type,
    IF(v.date_stopped IS NOT NULL, '1. Improved', 'Active / In ICU') as outcome_at_discharge,
    IF(p.dead = 1, IF(TIMESTAMPDIFF(HOUR, v.date_started, IFNULL(p.death_date, v.date_stopped)) <= 24, '1. Within 24 hrs', '2. After 24 hrs'), 'No') as death_in_icu,
    IF(p.dead = 1, 'Yes', 'No') as death_notification,
    COALESCE(MAX(CASE WHEN o.concept_id IN (70046, 12469) THEN 'Yes' END), 'No') as readmission,
    COALESCE(MAX(CASE WHEN o.concept_id IN (12469) THEN '1. Within 48 hrs' END), '-') as readmission_timing,
    '' as remark
FROM (
    SELECT e_filter.visit_id, v_inner.patient_id, v_inner.date_started, v_inner.date_stopped, v_inner.visit_type_id, v_inner.location_id, v_inner.uuid
    FROM (
        SELECT DISTINCT visit_id
        FROM encounter
        WHERE voided = 0 AND location_id IN (261, 53, 191)
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
GROUP BY v.visit_id
ORDER BY v.visit_id DESC;
"""

elapsed, rc, out, err = run_query(sql_icu_fast)
print(f"Super fast ICU Query took {elapsed:.2f}s, RC={rc}")
if rc == 0:
    lines = out.strip().split("\n")
    print(f"Total rows: {len(lines)-1}")
    for l in lines[:5]:
        print(l[:180])
else:
    print("Error:", err)
