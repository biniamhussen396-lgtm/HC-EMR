import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

def check_file(path, start, end):
    cmd = f"sed -n '{start},{end}p' {path}"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f"=== {path} ({start}-{end}) ===")
    print(stdout.read().decode('utf-8', errors='replace'))

check_file('/opt/emr/apps/ui/app/bedmanagement/controllers/referFormPrintController.js', 60, 95)
check_file('/opt/emr/apps/ui/app/bedmanagement/controllers/referFormPrintController.js', 235, 285)
check_file('/opt/emr/apps/ui/app/bedmanagement/views/referFormPrint.html', 390, 445)
check_file('/opt/emr/apps/ui/app/bedmanagement/index.html', 255, 275)

ssh.close()
