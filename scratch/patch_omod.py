import subprocess, os

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=60):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Extract and examine the SqlSearchServiceImpl class from bahmnicore omod
# First, the .omod is a jar (zip), then inside there's a lib jar with the actual classes
print('=== Extract class from omod to tmp dir ===')
print(run(
    "mkdir -p /tmp/bahmni_patch && "
    "cp /opt/emr/core/bahmnicore-omod-1.2.0.omod /tmp/bahmni_patch/ && "
    "cd /tmp/bahmni_patch && "
    "unzip -o bahmnicore-omod-1.2.0.omod -d omod_extracted/ 2>&1 | tail -5"
))

print('=== List extracted contents ===')
print(run("ls /tmp/bahmni_patch/omod_extracted/"))

print('=== Find the api/impl jar ===')
print(run("ls /tmp/bahmni_patch/omod_extracted/*.jar 2>/dev/null; ls /tmp/bahmni_patch/omod_extracted/lib/ 2>/dev/null | head -20"))
