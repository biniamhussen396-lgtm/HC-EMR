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

print("=== CHECK AI ASSISTANT ON REMOTE ===")
rc, out, err = run_remote('grep -n "AI Assistant" /opt/emr/apps/ui/app/clinical/dashboard/views/clinicalDashboardHeader.html /opt/emr/apps/ui/app/common/ui-helper/header.html 2>/dev/null || true')
print("STDOUT:\n", out)
print("STDERR:\n", err)

print("=== FIND STYLES AND FONTS ===")
rc, out, err = run_remote('docker exec bahmni-standard-bahmni-web-1 ls -la /usr/local/apache2/htdocs/bahmni/styles/ 2>/dev/null || true')
print("STYLES:\n", out)
rc, out, err = run_remote('docker exec bahmni-standard-bahmni-web-1 find /usr/local/apache2/htdocs -name "*fa*" -o -name "*font*" 2>/dev/null | head -n 30')
print("FONTS:\n", out)




