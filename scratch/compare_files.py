import paramiko
import os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

files_to_check = [
    "/opt/emr/apps/ui/app/bedmanagement/app.js",
    "/opt/emr/apps/ui/app/bedmanagement/index.html",
    "/opt/emr/apps/ui/app/bedmanagement/controllers/referFormPrintController.js",
    "/opt/emr/apps/ui/app/bedmanagement/controllers/referralManagementController.js",
    "/opt/emr/apps/ui/app/bedmanagement/views/referFormPrint.html",
    "/opt/emr/apps/ui/app/bedmanagement/views/referralManagement.html",
    "/opt/emr/apps/ui/app/clinical/consultation/controllers/dispositionController.js",
    "/opt/emr/apps/ui/app/clinical/consultation/views/disposition.html",
    "/opt/emr/apps/ui/app/common/domain/services/dispositionService.js",
    "/opt/emr/apps/ui/app/common/patient/services/patientService.js",
    "/opt/emr/apps/ui/app/common/util/httpErrorInterceptor.js",
    "/opt/emr/config/openmrs/apps/clinical/app.json",
    "/opt/emr/config/openmrs/apps/home/whiteLabel.json"
]

for f in files_to_check:
    out, err = run_sudo(f"ls -l {f}")
    print(out.strip())

ssh.close()
