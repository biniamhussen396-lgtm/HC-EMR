import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

def run_remote(cmd):
    res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", cmd], capture_output=True, text=True, timeout=20)
    return res.returncode, res.stdout, res.stderr

rc, out, err = run_remote("docker ps --filter 'name=proxy' --format '{{.Ports}}'")
print("Proxy ports on remote:\n", out)

rc, out, err = run_remote("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'proxy|web|openmrs'")
print("Docker containers on remote:\n", out)
