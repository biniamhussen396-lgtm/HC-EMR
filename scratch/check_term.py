import subprocess

query = """
SELECT crt.code, crt.name, crs.name as source_name
FROM concept_reference_map crm
JOIN concept_reference_term crt ON crm.concept_reference_term_id = crt.concept_reference_term_id
JOIN concept_reference_source crs ON crt.concept_source_id = crs.concept_source_id
WHERE crm.concept_id = 42794;
"""
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
