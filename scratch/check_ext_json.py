import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

def run_remote(cmd):
    wrapped = f"echo '{pw}' | sudo -S bash -c \"{cmd}\""
    res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", wrapped], capture_output=True, text=True, timeout=25)
    return res.stdout.strip()

print("Check register in extension.json on remote:")
print(run_remote("grep -n -C 5 'register' /opt/emr/config/openmrs/apps/home/extension.json || true"))
