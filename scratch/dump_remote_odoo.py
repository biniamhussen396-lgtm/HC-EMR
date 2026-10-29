import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

print("Starting pg_dump on remote 192.168.10.5...")
t0 = time.time()
cmd = "docker exec bahmni-standard-odoodb-1 pg_dump -U odoo -Fc -Z 6 odoo > /home/bmh/remote_odoo_live_backup.dump"
stdin, stdout, stderr = ssh.exec_command(cmd)
exit_status = stdout.channel.recv_exit_status()
err = stderr.read().decode()
dur = time.time() - t0

print(f"Dump finished in {dur:.1f}s with status {exit_status}. Error: {err}")

# Check dump file size
stdin, stdout, stderr = ssh.exec_command("ls -lh /home/bmh/remote_odoo_live_backup.dump")
print(stdout.read().decode())

ssh.close()
