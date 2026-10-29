import subprocess

query = """
SELECT e.encounter_id, e.encounter_type, et.name as enc_type, e.encounter_datetime, e.patient_id,
       pi.identifier, pn.given_name, pn.family_name, v.visit_id, vt.name as visit_type,
       e.location_id, loc.name as location_name
FROM encounter e
JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
JOIN visit v ON e.visit_id = v.visit_id
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
JOIN patient_identifier pi ON e.patient_id = pi.patient_id
JOIN person_name pn ON e.patient_id = pn.person_id
LEFT JOIN location loc ON e.location_id = loc.location_id
WHERE e.encounter_type IN (3, 4) OR vt.name LIKE '%ward%' OR vt.name = 'IPD'
ORDER BY e.encounter_datetime DESC LIMIT 20;
"""
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print('Admitted/Discharged Encounters:')
print(res.stdout)
