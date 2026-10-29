import subprocess

HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

def run_remote(cmd):
    res = subprocess.run(
        ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return res.returncode, res.stdout, res.stderr

print("Checking admin extension.json content:")
rc, out, err = run_remote("cat /opt/emr/config/openmrs/apps/admin/extension.json")
print(out)
