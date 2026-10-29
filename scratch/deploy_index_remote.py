import subprocess

PW = "   "
HOST = "192.168.10.5"
USER = "bmh"

# 1. Upload local index.html to /tmp/appointments_index.html on remote
cmd_pscp = ['pscp', '-batch', '-pw', PW, 'scratch/local_appointments_app/index.html', f'{USER}@{HOST}:/tmp/appointments_index.html']
res_p = subprocess.run(cmd_pscp, capture_output=True, text=True)
print("PSCP Returncode:", res_p.returncode)
print("PSCP Output:", res_p.stdout)
if res_p.stderr:
    print("PSCP Stderr:", res_p.stderr)

# 2. Deploy into appointments container
remote_cmd = (
    "docker cp /tmp/appointments_index.html bahmni-standard-appointments-1:/usr/local/apache2/htdocs/appointments/index.html && "
    "echo '   ' | sudo -S chmod 644 /tmp/appointments_index.html && "
    "echo DEPLOY_SUCCESS"
)
cmd_plink = ['plink', '-batch', '-ssh', '-pw', PW, f'{USER}@{HOST}', remote_cmd]
p = subprocess.run(cmd_plink, capture_output=True, text=True)
print("PLINK Output:", p.stdout)
if p.stderr:
    print("PLINK Stderr:", p.stderr)

# 3. Verify on remote container
cmd_verify = "docker exec bahmni-standard-appointments-1 tail -n 40 /usr/local/apache2/htdocs/appointments/index.html"
res_v = subprocess.run(['plink', '-batch', '-ssh', '-pw', PW, f'{USER}@{HOST}', cmd_verify], capture_output=True, text=True)
print("Remote container tail:\n", res_v.stdout)
