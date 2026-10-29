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

print("Fixing permissions...")
run_sudo("find /opt/emr/apps/ui/app -type d -exec chmod 755 {} +")
run_sudo("find /opt/emr/apps/ui/app -type f -exec chmod 644 {} +")
run_sudo("find /opt/emr/config -type d -exec chmod 755 {} +")
run_sudo("find /opt/emr/config -type f -exec chmod 644 {} +")

print("Checking permissions on orders and admin directories:")
rc, out, err = run_remote("ls -ld /opt/emr/apps/ui/app/orders /opt/emr/apps/ui/app/orders/views /opt/emr/apps/ui/app/admin /opt/emr/apps/ui/app/admin/views")
print(out)

print("Testing HTTP codes:")
for url in [
    "https://localhost/bahmni/orders/views/orderSearch.html",
    "https://localhost/bahmni/admin/views/branding.html",
    "https://localhost/bahmni/admin/views/backupRestore.html",
    "https://localhost/bahmni/orders/controllers/orderSearchController.js",
    "https://localhost/bahmni/admin/controllers/brandingController.js",
    "https://localhost/bahmni_config/openmrs/apps/admin/extension.json"
]:
    rc, out, err = run_remote(f"curl -k -s -o /dev/null -w '%{{http_code}}' {url}")
    print(f"{url} -> HTTP {out.strip()}")
