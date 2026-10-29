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

print("=== CHECK CONTAINER CONTROLLER FILE ===")
rc, out, err = run_remote("docker exec bahmni-standard-bahmni-web-1 sed -n '30,55p' /usr/local/apache2/htdocs/bahmni/clinical/dashboard/controllers/patientDashboardController.js")
print(out)

print("=== CHECK CONTAINER INDEX.HTML ===")
rc, out, err = run_remote("docker exec bahmni-standard-bahmni-web-1 grep -n 'patientDashboardController' /usr/local/apache2/htdocs/bahmni/clinical/index.html")
print(out)

print("=== CHECK APACHE ACCESS LOG FOR CLINICAL ===")
rc, out, err = run_remote("docker exec bahmni-standard-bahmni-web-1 tail -n 20 /usr/local/apache2/logs/access_log 2>/dev/null || true")
print(out)

print("=== CHECK FILE PERMISSIONS IN CONTAINER ===")
rc, out, err = run_remote("docker exec bahmni-standard-bahmni-web-1 ls -la /usr/local/apache2/htdocs/bahmni/clinical/dashboard/controllers/patientDashboardController.js")
print(out)
