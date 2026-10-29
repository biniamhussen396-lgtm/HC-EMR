import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

cmd = "ip addr show ; hostname -I"
res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=30)
print("Returncode:", res.returncode)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
