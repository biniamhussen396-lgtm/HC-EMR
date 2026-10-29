import subprocess

PW = "   "
HOST = "192.168.10.5"
USER = "bmh"

def run_remote(cmd):
    res = subprocess.run(
        ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return res.returncode, res.stdout, res.stderr

print("=== CHECK DOCKER MOUNTS FOR BAHMNI-WEB ===")
rc, out, err = run_remote("docker inspect --format '{{json .Mounts}}' bahmni-standard-bahmni-web-1")
print("RC:", rc)
print("OUT:", out)

print("\n=== CHECK CLINICAL CONTROLLER IN CONTAINER ===")
rc, out, err = run_remote("docker exec bahmni-standard-bahmni-web-1 sed -n '30,50p' /var/www/bahmni_config/openmrs/apps/clinical/dashboard/controllers/patientDashboardController.js 2>&1 || true")
print("PATH 1:", out)

rc, out, err = run_remote("docker exec bahmni-standard-bahmni-web-1 find /var/www -name 'patientDashboardController.js'")
print("CONTAINER PATHS:", out)

print("\n=== CHECK CLINICAL CONTROLLER ON HOST ===")
rc, out, err = run_remote("find /opt /var/www -name 'patientDashboardController.js' 2>/dev/null")
print("HOST PATHS:", out)
