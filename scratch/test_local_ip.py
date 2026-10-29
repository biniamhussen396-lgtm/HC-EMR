import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "

# 1. Ping 192.168.10.5
res_ping = subprocess.run(["ping", "-n", "2", "-w", "1000", "192.168.10.5"], capture_output=True, text=True)
print("Ping 192.168.10.5:")
print(res_ping.stdout)

# 2. Try SSH to 192.168.10.5
res_ssh = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, "bmh@192.168.10.5", "hostname -I"], capture_output=True, text=True, timeout=5)
print("SSH 192.168.10.5:")
print("RC:", res_ssh.returncode)
print("OUT:", res_ssh.stdout)
print("ERR:", res_ssh.stderr)
