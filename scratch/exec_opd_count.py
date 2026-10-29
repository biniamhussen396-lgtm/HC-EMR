import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=90):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Run the query in opdRegister global property and count the rows
query_runner = """
docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "
SET @q = (SELECT property_value FROM global_property WHERE property = 'emrapi.sqlSearch.opdRegister');
PREPARE stmt FROM @q;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
" > /tmp/exec_opd.txt
"""
print(run(query_runner))
print(run("wc -l /tmp/exec_opd.txt"))
