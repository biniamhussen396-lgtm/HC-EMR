import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

def run_cmd(cmd):
    print(f"=== Running: {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out:
        print("STDOUT:\n" + out)
    if err:
        print("STDERR:\n" + err)
    return out

run_cmd('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
run_cmd('ls -la /home/bmh')
run_cmd('find /home/bmh -maxdepth 3 -name "docker-compose*.yml" -o -name "bahmni-standard"')

ssh.close()
