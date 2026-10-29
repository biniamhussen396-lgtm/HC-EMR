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

print("=== FIND HTTP ERROR INTERCEPTOR IN CONTAINER ===")
rc, out, err = run_remote("docker exec bahmni-standard-bahmni-web-1 find /usr/local/apache2/htdocs -name 'httpErrorInterceptor.js'")
print("PATH:", out)

rc, out, err = run_remote("docker exec bahmni-standard-bahmni-web-1 grep -n -C 5 'requested information does not exist' /usr/local/apache2/htdocs/bahmni/common/util/httpErrorInterceptor.js 2>/dev/null || true")
print("GREP:", out)

print("=== CHECK LISTENING PORTS ON REMOTE ===")
rc, out, err = run_remote("netstat -tlpn 2>/dev/null || ss -tlpn 2>/dev/null || true")
print(out)







print("=== CHECK APACHE LOGS FOR CLINICAL ===")
rc, out, err = run_remote("docker logs --tail 30 bahmni-standard-bahmni-web-1")
print(out)










print("=== CHECK HOST /opt/emr/openelis-custom ===")
rc, out, err = run_remote("ls -la /opt/emr/openelis-custom/pages/test/ /opt/emr/openelis-custom/pages/location/ 2>/dev/null || true")
print(out)






