import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Let's inspect webModuleApplicationContext.xml and find the controller
print("=== grep sql in extracted omod ===")
print(run("grep -rn 'sql' /tmp/bahmni_patch/omod_extracted/webModuleApplicationContext.xml /tmp/bahmni_patch/omod_extracted/config.xml 2>/dev/null"))

# Let's decompile SqlSearchController with javap -c -p
print("=== javap SqlSearchController ===")
print(run("docker exec bahmni-standard-openmrs-1 javap -p -c /tmp/SqlSearchController.class"))
