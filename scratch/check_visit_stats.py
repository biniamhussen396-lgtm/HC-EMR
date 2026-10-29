import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

query = """
SELECT 
    COUNT(*) as total_visits,
    COUNT(CASE WHEN date_started >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as last_30_days,
    COUNT(CASE WHEN date_started >= DATE_SUB(NOW(), INTERVAL 90 DAY) THEN 1 END) as last_90_days,
    COUNT(CASE WHEN date_started >= DATE_SUB(NOW(), INTERVAL 180 DAY) THEN 1 END) as last_180_days
FROM visit WHERE voided = 0;
"""
print(run(f'docker exec bahmni-standard-openmrsdb-1 mysql -u openmrs-user -pulDHfskBAYSFkOPBGkkjCPbv openmrs -e "{query}"'))
