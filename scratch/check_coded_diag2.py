import subprocess

query = """
SELECT o.encounter_id, e.visit_id, cn.name as diagnosis_name, crt.code as icd_code
FROM obs o
JOIN encounter e ON o.encounter_id = e.encounter_id
JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
LEFT JOIN concept_reference_map crm ON o.value_coded = crm.concept_id
LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
WHERE o.concept_id = 22 AND o.voided = 0
LIMIT 10;
"""
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
