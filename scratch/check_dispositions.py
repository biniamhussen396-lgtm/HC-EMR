import subprocess

query = """
SELECT cn.name, count(*) 
FROM obs o 
JOIN concept_name cn ON o.value_coded = cn.concept_id 
WHERE o.concept_id IN (SELECT concept_id FROM concept_name WHERE name IN ('Disposition', 'Discharge Disposition', 'Condition at Discharge'))
GROUP BY cn.name;
"""
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
