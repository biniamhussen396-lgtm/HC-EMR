import paramiko
import time
import os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

sftp = ssh.open_sftp()
remote_file = "/home/bmh/remote_odoo_live_backup.dump"
local_file = "scratch/remote_odoo_live_backup.dump"

print(f"Downloading {remote_file} to {local_file}...")
t0 = time.time()

def progress_cb(transferred, total):
    if total > 0 and transferred % (5 * 1024 * 1024) < 65536:
        print(f"  {transferred / 1024 / 1024:.1f} MB / {total / 1024 / 1024:.1f} MB ({(transferred/total)*100:.1f}%)")

sftp.get(remote_file, local_file, callback=progress_cb)
dur = time.time() - t0
size = os.path.getsize(local_file)
print(f"Download complete! {size / 1024 / 1024:.2f} MB in {dur:.1f}s ({size/1024/1024/dur:.2f} MB/s)")

# Also download remote filestore archive
print("Archiving remote filestore...")
cmd = "tar -czf /home/bmh/remote_filestore.tar.gz -C /var/lib/docker/volumes/bahmni-standard_odoofilestore/_data ."
stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
stdout.channel.recv_exit_status()

print("Downloading filestore archive...")
sftp.get("/home/bmh/remote_filestore.tar.gz", "scratch/remote_filestore.tar.gz")
print("Filestore downloaded:", os.path.getsize("scratch/remote_filestore.tar.gz") / 1024 / 1024, "MB")

sftp.close()
ssh.close()
