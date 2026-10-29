import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=30):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Find report config or sql for MRU Report Based on Payment Type Deteil
print(run("grep -rn 'Payment Type Deteil\\|MRU Report Based on Payment' /opt/emr/ 2>/dev/null | head -10"))
