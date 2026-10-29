import subprocess

query = """
SELECT o.obs_id, o.person_id, o.encounter_id, o.concept_id, o.value_coded, o.value_text,
       cn.name as coded_concept_name, crt.code as icd10_code
FROM obs o
JOIN concept_name cn_type ON o.concept_id = cn_type.concept_id AND cn_type.name = 'Coded Diagnosis'
LEFT JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED'
LEFT JOIN concept_reference_map crm ON o.value_coded = crm.concept_id
LEFT JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
ORDER BY o.obs_id DESC LIMIT 10;
"""

cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
