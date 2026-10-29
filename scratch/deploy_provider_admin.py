import subprocess

# 1. Upload local provider-admin.html to /tmp/provider-admin.html on remote
cmd_pscp = ['pscp', '-batch', '-pw', '   ', 'scratch/local_appointments_app/provider-admin.html', 'bmh@192.168.10.5:/tmp/provider-admin.html']
subprocess.run(cmd_pscp, check=True)
print("Uploaded to /tmp/provider-admin.html")

# 2. Deploy into appointments container and /opt/emr/apps/ui/app/appointments/
remote_cmd = (
    "docker cp /tmp/provider-admin.html bahmni-standard-appointments-1:/usr/local/apache2/htdocs/appointments/provider-admin.html && "
    "echo '   ' | sudo -S cp /tmp/provider-admin.html /opt/emr/apps/ui/app/appointments/provider-admin.html && "
    "echo '   ' | sudo -S chmod 644 /opt/emr/apps/ui/app/appointments/provider-admin.html && "
    "echo DEPLOYED_SUCCESS"
)
cmd_plink = ['plink', '-batch', '-ssh', '-pw', '   ', 'bmh@192.168.10.5', remote_cmd]
p = subprocess.run(cmd_plink, capture_output=True, text=True)
print("STDOUT:", p.stdout)
print("STDERR:", p.stderr)
