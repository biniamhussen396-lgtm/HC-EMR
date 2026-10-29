import subprocess

concepts_to_find = [
    'Road Traffic Accident', 'Trauma', 'Accident',
    'HIV', 'PITC',
    'Malaria', 'Malarious',
    'TB', 'Tuberculosis',
    'Condition at Discharge', 'Discharge Condition', 'Discharge Disposition',
    'Death', 'Cause of Death',
    'Payment', 'Voucher', 'Amount', 'Fee'
]

conditions = " OR ".join([f"name LIKE '%{term}%'" for term in concepts_to_find])
query = f"SELECT concept_id, name, concept_name_type FROM concept_name WHERE ({conditions}) AND concept_name_type = 'FULLY_SPECIFIED' AND locale = 'en' LIMIT 30;"
cmd = ['docker', 'exec', '-i', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', query]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
