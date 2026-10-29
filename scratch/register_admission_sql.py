import subprocess
import os

repo = r"c:\Users\COMPUTER\Documents\emr"
sql_file = os.path.join(repo, "config", "masterdata", "configuration", "sql", "emrapi.sqlSearch.admissionRegister.sql")
with open(sql_file, "r", encoding="utf-8") as f:
    sql_text = f.read()

escaped = sql_text.replace("\\", "\\\\").replace("'", "\\'")
cmd = f"""
INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.admissionRegister', '{escaped}', 'SQL Search for Admission and Discharge Register', UUID())
ON DUPLICATE KEY UPDATE property_value = '{escaped}';
"""

res = subprocess.run(
    ["docker", "exec", "-i", "bahmni-standard-openmrsdb-1", "mysql", "-uroot", "-padminAdmin!123", "openmrs", "-e", cmd],
    capture_output=True, text=True
)
print("Updated local emrapi.sqlSearch.admissionRegister: rc=", res.returncode)
if res.stderr:
    print("Stderr:", res.stderr)
