import paramiko
import os

HOST = "196.189.94.149"
USER = "bmh"
PASS = "   "

print("Connecting to remote server via SSH/SFTP...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=30)
sftp = ssh.open_sftp()
print("Connected.")

ui_root = r"C:\Users\COMPUTER\Documents\emr\apps\ui\app\register"
ui_files = [
    (r"controllers\registerController.js", "/opt/emr/apps/ui/app/register/controllers/registerController.js"),
    (r"views\register.html", "/opt/emr/apps/ui/app/register/views/register.html"),
    (r"styles\register.css", "/opt/emr/apps/ui/app/register/styles/register.css"),
    (r"services\registerService.js", "/opt/emr/apps/ui/app/register/services/registerService.js"),
    (r"services\ethiopianCalendarService.js", "/opt/emr/apps/ui/app/register/services/ethiopianCalendarService.js"),
    (r"app.js", "/opt/emr/apps/ui/app/register/app.js"),
    (r"index.html", "/opt/emr/apps/ui/app/register/index.html"),
]

for src_rel, dest_path in ui_files:
    src_full = os.path.join(ui_root, src_rel)
    sftp.put(src_full, dest_path)
    print(f"Uploaded UI: {src_rel} -> {dest_path}")

sftp.close()
ssh.close()
print("Multiselect UI deployment completed successfully.")
