import subprocess

HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

def run_sudo(cmd):
    wrapped = f"echo '{PW}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    res = subprocess.run(
        ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", wrapped],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return res.stdout

print(run_sudo('docker exec bahmni-standard-openmrsdb-1 mysql -uroot -p"adminAdmin!123" openmrs -e "SELECT u.user_id, u.username, ur.role FROM users u JOIN user_role ur ON u.user_id = ur.user_id WHERE u.username IN (\'admin\', \'superman\');"'))
