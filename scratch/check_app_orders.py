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

def run_sudo(cmd):
    wrapped = f"echo '{PW}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    return run_remote(wrapped)

print("Checking privilege app:orders:")
rc, out, err = run_sudo('docker exec bahmni-standard-openmrsdb-1 mysql -uroot -p"adminAdmin!123" openmrs -e "SELECT * FROM privilege WHERE privilege = \'app:orders\'; SELECT * FROM role_privilege WHERE privilege = \'app:orders\';"')
print(out)
