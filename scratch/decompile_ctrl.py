import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=60):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# The class is at omod_extracted/org/bahmni/module/bahmnicore/web/v1_0/controller/SqlSearchController.class
# Use javap inside docker container (OpenMRS runs in Java)
print('=== Copy class into container and javap ===')
# First copy to a volume-accessible path
print(run("cp /tmp/bahmni_patch/omod_extracted/org/bahmni/module/bahmnicore/web/v1_0/controller/SqlSearchController.class /tmp/"))
print(run("docker cp /tmp/SqlSearchController.class bahmni-standard-openmrs-1:/tmp/"))
print(run("docker exec bahmni-standard-openmrs-1 javap -c /tmp/SqlSearchController.class 2>/dev/null | grep -A5 -B5 '200\\|batchSize\\|maxResult\\|limit\\|size' | head -60"))

print('=== Full javap constants ===')
print(run("docker exec bahmni-standard-openmrs-1 javap -verbose /tmp/SqlSearchController.class 2>/dev/null | grep -E '200|Utf8 [a-z]|Integer' | head -30"))
