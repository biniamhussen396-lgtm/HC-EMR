import subprocess

query = """
SELECT v.visit_id, e.encounter_id, o.obs_id, cn.name as diag_name, crt.code as icd_code
FROM visit v
JOIN encounter e ON v.visit_id = e.visit_id
JOIN obs o ON e.encounter_id = o.encounter_id
JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
LEFT JOIN concept_reference_map crm ON o.value_coded = crm.concept_id
LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
WHERE v.visit_id IN (382, 351, 333, 228, 209, 61, 48, 46, 44, 42, 41, 39, 37, 33, 31, 10);
"""
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
