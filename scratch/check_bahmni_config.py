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

print("=== Check bahmni-web mounts in docker-compose ===")
rc, out, err = run_remote("docker inspect bahmni-standard-bahmni-web-1 --format '{{json .Mounts}}'")
print(out)

print("=== Check proxy config for bahmni_config ===")
rc, out, err = run_remote("docker exec bahmni-standard-proxy-1 grep -n -C 3 'bahmni_config' /usr/local/apache2/conf/bahmni-proxy.conf")
print(out)

print("=== Check curl of extension.json ===")
rc, out, err = run_remote("curl -k -s https://localhost/bahmni_config/openmrs/apps/admin/extension.json")
print(out)
