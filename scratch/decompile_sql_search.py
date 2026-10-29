import subprocess

PLINK = r"C:\Program Files\PuTTY\plink.EXE"
PW = "   "
HOST = "196.189.94.149"
USER = "bmh"

def run_cmd(cmd):
    wrapped = f"echo '{PW}' | sudo -S bash -c \"{cmd}\""
    res = subprocess.run([PLINK, "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd], capture_output=True, text=True, timeout=25)
    return res.stdout.strip()

print(run_cmd("docker exec bahmni-standard-openmrs-1 javap -p -cp /openmrs/data/modules/bahmnicore-omod-1.2.0.omod org.bahmni.module.bahmnicore.web.v1_0.controller.SqlSearchController"))
