import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

print(run("docker exec bahmni-standard-openmrs-1 javap -v /tmp/SqlSearchController.class | grep -E '#(55|56|57|58|59|60|61|62|66|67|72|73) ='"))
