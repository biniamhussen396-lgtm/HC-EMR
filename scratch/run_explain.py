import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

cmd = 'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "EXPLAIN " < scratch/optimized_opd.sql'
# We will prepend EXPLAIN to scratch/optimized_opd.sql
with open('scratch/optimized_opd.sql', 'r') as f:
    sql = f.read()

with open('scratch/explain_opd.sql', 'w') as f:
    f.write('EXPLAIN ' + sql)

subprocess.run([r"C:\Program Files\PuTTY\pscp.EXE", "-batch", "-pw", PW, 'scratch/explain_opd.sql', f"{USER}@{HOST}:/tmp/explain_opd.sql"], check=True)
cmd = 'docker exec -i bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs < /tmp/explain_opd.sql'
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=20)
print(res.stdout)
