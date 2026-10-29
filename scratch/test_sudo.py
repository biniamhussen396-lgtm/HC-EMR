import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

def run_sudo(cmd):
    print(f"=== Running sudo: {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out:
        print("STDOUT:\n" + out)
    if err:
        print("STDERR:\n" + err)
    return out

run_sudo('whoami')
run_sudo('ls -la /opt/emr/bahmni-docker/bahmni-standard/.env')
run_sudo('grep -i "mysql" /opt/emr/bahmni-docker/bahmni-standard/.env || true')

ssh.close()
