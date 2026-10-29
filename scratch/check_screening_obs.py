import subprocess

query = """
SELECT cn.name, o.value_text, o.value_numeric, o.value_coded, val_cn.name as coded_val_name, count(*) as cnt
FROM obs o
JOIN concept_name cn ON o.concept_id = cn.concept_id AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.locale = 'en'
LEFT JOIN concept_name val_cn ON o.value_coded = val_cn.concept_id AND val_cn.concept_name_type = 'FULLY_SPECIFIED' AND val_cn.locale = 'en'
WHERE cn.name LIKE '%HIV%' OR cn.name LIKE '%TB%' OR cn.name LIKE '%Tuberculosis%' OR cn.name LIKE '%Malaria%' OR cn.name LIKE '%Discharge%'
GROUP BY cn.name, o.value_text, o.value_numeric, o.value_coded, val_cn.name
LIMIT 30;
"""
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
