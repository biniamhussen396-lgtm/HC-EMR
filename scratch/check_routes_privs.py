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

print("=== 1. Checking admin/app.js on remote ===")
rc, out, err = run_remote("grep -n -C 3 'admin.branding' /opt/emr/apps/ui/app/admin/app.js")
print(out)

print("=== 2. Checking admin/index.html on remote ===")
rc, out, err = run_remote("grep -n 'brandingController' /opt/emr/apps/ui/app/admin/index.html")
print(out)

print("=== 3. Checking app:orders and role privileges in MySQL on remote ===")
sql = """
SELECT role, privilege FROM role_privilege WHERE privilege LIKE '%order%' OR privilege LIKE 'app:%' LIMIT 30;
"""
rc, out, err = run_sudo(f'docker exec bahmni-standard-openmrsdb-1 mysql -uroot -p"adminAdmin!123" openmrs -e "{sql}"')
print(out)
