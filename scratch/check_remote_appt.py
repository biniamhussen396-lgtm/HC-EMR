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

cmd = "docker inspect bahmni-standard-appointments-1 --format \"{{range .Mounts}}{{println .Source .Destination}}{{end}}\""
rc, out, err = run_remote(cmd)
print("APPOINTMENTS MOUNTS:\n", out)
