import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

print(run("unzip -o /tmp/bahmni_patch/omod_extracted/lib/bahmnicore-api-1.2.0.jar 'org/bahmni/module/bahmnicore/util/SqlQueryHelper*' -d /tmp/"))
print(run("docker cp /tmp/org/bahmni/module/bahmnicore/util/SqlQueryHelper.class bahmni-standard-openmrs-1:/tmp/"))
print(run("docker exec bahmni-standard-openmrs-1 javap -p -c /tmp/SqlQueryHelper.class"))
