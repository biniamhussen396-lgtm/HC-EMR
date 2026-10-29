import subprocess, sys

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=60):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Find and inspect the bahmnicore omod to understand the SQL limit
# First locate the jar/class files
print('=== Find SqlSearchServiceImpl ===')
print(run("find / -name '*.omod' 2>/dev/null | head -20"))

print('=== Find bahmnicore jar ===')
print(run("find / -name 'bahmnicore*.jar' -o -name '*bahmnicore*.omod' 2>/dev/null | head -10"))

print('=== List OpenMRS modules directory ===')
print(run("ls /opt/bahmni-web/etc/openmrs/modules/ 2>/dev/null || ls ~/.OpenMRS/modules/ 2>/dev/null || find / -name 'modules' -type d 2>/dev/null | head -5"))
