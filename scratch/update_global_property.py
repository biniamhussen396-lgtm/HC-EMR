import subprocess

with open(r"c:\Users\COMPUTER\Documents\emr\config\masterdata\configuration\sql\emrapi.sqlSearch.referralManagement.sql", "r", encoding="utf-8") as f:
    sql_content = f.read()

# Escape single quotes for SQL string literal
sql_val = sql_content.replace("\\", "\\\\").replace("'", "\\'")

query = f"UPDATE global_property SET property_value = '{sql_val}' WHERE property = 'emrapi.sqlSearch.referralManagement';"

cmd = ["docker", "exec", "bahmni-standard-openmrsdb-1", "mysql", "-uroot", "-padminAdmin!123", "openmrs", "-e", query]
res = subprocess.run(cmd, capture_output=True, text=True)
print("LOCAL UPDATE RC:", res.returncode)
print("ERR:", res.stderr)
print("OUT:", res.stdout)
