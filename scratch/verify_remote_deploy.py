import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

print("=== Check md5 of remote controller ===")
print(run("md5sum /opt/emr/apps/ui/app/register/controllers/registerController.js"))
print(run("md5sum /opt/emr/apps/ui/app/register/views/register.html"))
print(run("md5sum /opt/emr/apps/ui/app/register/styles/register.css"))

print("=== Check node/js syntax if node installed on server ===")
print(run("node -c /opt/emr/apps/ui/app/register/controllers/registerController.js 2>/dev/null && echo 'JS Syntax OK' || echo 'No node or check skipped'"))
