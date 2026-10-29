import subprocess

plink = r"C:\Program Files\PuTTY\plink.EXE"
pw = "   "
host = "196.189.94.149"
user = "bmh"

def run_cmd(cmd):
    wrapped = f"echo '{pw}' | sudo -S bash -c \"{cmd}\""
    res = subprocess.run([plink, "-batch", "-ssh", "-pw", pw, f"{user}@{host}", wrapped], capture_output=True, text=True, timeout=25)
    return res.stdout.strip()

print("Docker containers:")
print(run_cmd("docker ps --format '{{.Names}}: {{.Image}}'"))
print("\nWeb mounts:")
print(run_cmd("docker inspect bahmni-standard-bahmni-web-1 --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}\n{{end}}'"))
print("\nFiles in /opt/emr/apps/ui/app/register:")
print(run_cmd("ls -la /opt/emr/apps/ui/app/register"))
