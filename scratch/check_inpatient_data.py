import subprocess

queries = [
    # Check concept for diagnosis, discharge, admission
    "SELECT concept_id, datatype_id, class_id FROM concept WHERE concept_id IN (SELECT concept_id FROM concept_name WHERE name IN ('Coded Diagnosis', 'Visit Diagnoses', 'Diagnosis', 'Condition at Discharge', 'Discharge Note', 'Discharge Disposition', 'TB Screening', 'HIV Status'));",
    # Check concept names
    "SELECT concept_id, name, concept_name_type FROM concept_name WHERE name IN ('Condition at Discharge', 'Discharge Disposition', 'Length of stay', 'HIV Status', 'Screened for TB', 'TBRx Status') LIMIT 10;",
    # Check bed_patient_assignment_map joined with patient
    "SELECT b.bed_number, l.name as ward, p.patient_id, pi.identifier, pn.given_name, pn.family_name, bp.date_started, bp.date_stopped FROM bed_patient_assignment_map bp JOIN bed b ON bp.bed_id = b.bed_id LEFT JOIN bed_location_map blm ON b.bed_id = blm.bed_id LEFT JOIN location l ON blm.location_id = l.location_id JOIN patient p ON bp.patient_id = p.patient_id JOIN patient_identifier pi ON p.patient_id = pi.patient_id JOIN person_name pn ON p.patient_id = pn.person_id LIMIT 10;"
]

for idx, q in enumerate(queries):
    cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', q]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Query {idx+1} result:")
    print(res.stdout)
