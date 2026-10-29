import subprocess

PW = "   "
HOST = "192.168.10.5"
USER = "bmh"

# 1. Upload to /tmp/app.json
cmd_pscp = ['pscp', '-batch', '-pw', PW, 'config/openmrs/apps/appointments/app.json', f'{USER}@{HOST}:/tmp/app.json']
subprocess.run(cmd_pscp, check=True)
print("Uploaded to /tmp/app.json")

# 2. Copy to /opt/emr/config/openmrs/apps/appointments/app.json
remote_cmd = (
    f"echo '{PW}' | sudo -S cp /tmp/app.json /opt/emr/config/openmrs/apps/appointments/app.json && "
    f"echo '{PW}' | sudo -S chmod 644 /opt/emr/config/openmrs/apps/appointments/app.json && "
    "echo DEPLOYED_SUCCESS"
)
cmd_plink = ['plink', '-batch', '-ssh', '-pw', PW, f'{USER}@{HOST}', remote_cmd]
p = subprocess.run(cmd_plink, capture_output=True, text=True)
print("STDOUT:", p.stdout)
print("STDERR:", p.stderr)

# 3. Verify on remote
cmd_verify = "cat /opt/emr/config/openmrs/apps/appointments/app.json | grep -E 'enableResetAppointmentStatuses|allowedActionsByStatus' -A 6"
res_v = subprocess.run(
    ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd_verify],
    capture_output=True, text=True, encoding="utf-8", errors="replace"
)
print("Remote verification:\n", res_v.stdout)
