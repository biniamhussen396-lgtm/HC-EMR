import subprocess, sys

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=30)
    return result.stdout + result.stderr

# Check current searchWidget.batchSize and related global properties
mysql_cmd = (
    "docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user "
    "-pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "
    "\"SELECT property, property_value FROM global_property "
    "WHERE property IN ('searchWidget.batchSize','webservices.rest.maxResultsDefault',"
    "'webservices.rest.maxResultsAbsolute','bahmni.sqlSearch.maxResultsDefault') "
    "ORDER BY property;\""
)
print('=== Global Properties ===')
print(run(mysql_cmd))

# Now increase batch size to 2500
update_cmd = (
    "docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user "
    "-pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "
    "\"UPDATE global_property SET property_value='2500' "
    "WHERE property='searchWidget.batchSize'; "
    "SELECT ROW_COUNT() as rows_updated;\""
)
print('=== Update searchWidget.batchSize to 2500 ===')
print(run(update_cmd))

# Also update maxResultsDefault if it exists
update2_cmd = (
    "docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user "
    "-pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "
    "\"UPDATE global_property SET property_value='2500' "
    "WHERE property='webservices.rest.maxResultsDefault'; "
    "SELECT ROW_COUNT() as rows_updated;\""
)
print('=== Update webservices.rest.maxResultsDefault to 2500 ===')
print(run(update2_cmd))

# Verify
print('=== Verify ===')
print(run(mysql_cmd))
