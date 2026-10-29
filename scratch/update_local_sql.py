import subprocess
import os

repo = r"c:\Users\COMPUTER\Documents\emr"

# 1. Update emrapi.sqlSearch.referralManagement
sql_path = os.path.join(repo, "config", "masterdata", "configuration", "sql", "emrapi.sqlSearch.referralManagement.sql")
with open(sql_path, "r", encoding="utf-8") as f:
    sql_text = f.read()

# 2. Queries for doctor names with middle_name
all_doctors_sql = """SELECT provider.provider_id as id,
provider.uuid,
TRIM(CONCAT(person_name.given_name, IF(person_name.middle_name IS NOT NULL AND person_name.middle_name != '', CONCAT(' ', person_name.middle_name), ''), IF(person_name.family_name IS NOT NULL AND person_name.family_name != '', CONCAT(' ', person_name.family_name), ''))) as FullName,
users.user_id,
person.uuid as person_uuid,
user_role.role
FROM person_name
INNER JOIN users ON person_name.person_id = users.person_id
INNER JOIN user_role ON users.user_id = user_role.user_id
INNER JOIN person ON person_name.person_id = person.person_id
INNER JOIN provider ON person_name.person_id = provider.person_id
WHERE user_role.role = "Appointment Provider"
GROUP BY users.user_id ORDER BY person_name.given_name;"""

residents_sql = """SELECT TRIM(CONCAT(person_name.given_name, IF(person_name.middle_name IS NOT NULL AND person_name.middle_name != '', CONCAT(' ', person_name.middle_name), ''), IF(person_name.family_name IS NOT NULL AND person_name.family_name != '', CONCAT(' ', person_name.family_name), ''))) as FullName,
users.user_id
FROM person_name
INNER JOIN users ON person_name.person_id = users.person_id
INNER JOIN user_role ON users.user_id = user_role.user_id
WHERE user_role.role = "Resident";"""

specialists_sql = """SELECT TRIM(CONCAT(person_name.given_name, IF(person_name.middle_name IS NOT NULL AND person_name.middle_name != '', CONCAT(' ', person_name.middle_name), ''), IF(person_name.family_name IS NOT NULL AND person_name.family_name != '', CONCAT(' ', person_name.family_name), ''))) as FullName,
users.user_id
FROM person_name
INNER JOIN users ON person_name.person_id = users.person_id
INNER JOIN user_role ON users.user_id = user_role.user_id
WHERE user_role.role = "Specialist";"""

statements = [
    ("emrapi.sqlSearch.referralManagement", sql_text),
    ("bahmni.sqlGet.allLevelOfDoctors", all_doctors_sql),
    ("bahmni.sqlGet.residents", residents_sql),
    ("bahmni.sqlGet.specialists", specialists_sql),
]

for prop, val in statements:
    escaped = val.replace("\\", "\\\\").replace("'", "\\'")
    cmd = f"UPDATE global_property SET property_value = '{escaped}' WHERE property = '{prop}';"
    res = subprocess.run(
        ["docker", "exec", "-i", "bahmni-standard-openmrsdb-1", "mysql", "-uroot", "-padminAdmin!123", "openmrs", "-e", cmd],
        capture_output=True, text=True
    )
    print(f"Updated {prop}: rc={res.returncode}")
    if res.returncode != 0:
        print("Error:", res.stderr)
