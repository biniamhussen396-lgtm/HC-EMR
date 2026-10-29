import paramiko
import sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

password = "   " # 3 spaces
print(f"Connecting to 192.168.10.5 as bmh with password length {len(password)}...")

try:
    ssh.connect("192.168.10.5", username="bmh", password=password, timeout=10)
    print("SSH connection successful!")
    
    stdin, stdout, stderr = ssh.exec_command("hostname; whoami; uname -a")
    print("Output:", stdout.read().decode())
    
    # Check docker or odoo on remote server
    stdin, stdout, stderr = ssh.exec_command("docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'")
    print("Docker containers:\n", stdout.read().decode())
    
    ssh.close()
except Exception as e:
    print(f"Error connecting: {e}")
