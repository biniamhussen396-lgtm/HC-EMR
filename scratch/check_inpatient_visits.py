import subprocess

query = """
SELECT v.visit_id, v.patient_id, pi.identifier, pn.given_name, pn.family_name,
       vt.name as visit_type, v.date_started, v.date_stopped,
       b.bed_number, l.name as bed_ward
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
JOIN person_name pn ON v.patient_id = pn.person_id
LEFT JOIN bed_patient_assignment_map bp ON v.patient_id = bp.patient_id AND (bp.date_stopped IS NULL OR bp.date_started >= v.date_started)
LEFT JOIN bed b ON bp.bed_id = b.bed_id
LEFT JOIN bed_location_map blm ON b.bed_id = blm.bed_id
LEFT JOIN location l ON blm.location_id = l.location_id
WHERE v.voided = 0 AND (
    vt.name IN ('Emergency OPD', 'Delivery Room', 'IPD')
    OR vt.name LIKE '%ward%'
    OR v.visit_id IN (SELECT visit_id FROM encounter WHERE encounter_type IN (3, 4))
    OR v.patient_id IN (SELECT patient_id FROM bed_patient_assignment_map)
)
ORDER BY v.date_started DESC LIMIT 20;
"""

cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print('Inpatient/Ward visits found:')
print(res.stdout)
