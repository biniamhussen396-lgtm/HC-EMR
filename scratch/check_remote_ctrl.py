import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Check dateRangeKey in deployed registerController.js on remote
print('=== Check remote registerController.js for dateRangeKey default ===')
print(run("grep -n 'dateRangeKey\\|ALL\\|TODAY' /opt/emr/apps/ui/app/register/controllers/registerController.js | head -20"))

print('=== Check md5 hash of remote vs local reference ===')
print(run("md5sum /opt/emr/apps/ui/app/register/controllers/registerController.js"))
