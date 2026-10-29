import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=45):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Find the bahmnicore omod inside the OpenMRS container
print('=== Find modules in OpenMRS container ===')
print(run("docker exec bahmni-standard-openmrs-1 find /root/.OpenMRS/modules /usr/share/tomcat9 /opt -name 'bahmnicore*.omod' 2>/dev/null | head -10"))

print('=== Also check /opt/bahmni for omods ===')
print(run("find /opt -name '*.omod' 2>/dev/null | head -20"))
