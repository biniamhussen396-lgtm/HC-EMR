import subprocess

safe_sql = """SELECT
    ob.value_text AS ward
FROM
    obs ob
    INNER JOIN person p ON ob.person_id = p.person_id
    AND p.uuid = '${uuid}'
WHERE
    ob.concept_id = 60729
ORDER BY ob.obs_id DESC
LIMIT 1;"""

escaped = safe_sql.replace("\\", "\\\\").replace("'", "\\'")
cmd = f"UPDATE global_property SET property_value = '{escaped}' WHERE property = 'emrapi.getPatientAdmissionWard';"

res = subprocess.run(
    ["docker", "exec", "-i", "bahmni-standard-openmrsdb-1", "mysql", "-uroot", "-padminAdmin!123", "openmrs", "-e", cmd],
    capture_output=True, text=True
)
print("Updated local emrapi.getPatientAdmissionWard:", res.returncode)
if res.stderr:
    print("Stderr:", res.stderr)
