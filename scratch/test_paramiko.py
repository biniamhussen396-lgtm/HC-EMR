import paramiko

HOST = '196.189.94.149'
USER = 'bmh'
PW = '   '

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOST}...")
    ssh.connect(HOST, username=USER, password=PW, timeout=15)
    print("Paramiko connection SUCCESS!")
    sftp = ssh.open_sftp()
    print("SFTP SUCCESS!")
    sftp.close()
    ssh.close()
except Exception as e:
    print(f"Paramiko connection failed: {e}")
