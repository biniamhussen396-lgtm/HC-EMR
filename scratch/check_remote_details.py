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

run_cmd('ls -la /opt/emr/apps/ui/app/bedmanagement/controllers/')
run_cmd('ls -la /opt/emr/apps/ui/app/bedmanagement/views/')
run_cmd('docker exec bahmni-standard-openmrsdb-1 mysql -uopenmrs-user -ppassword openmrs -e "SELECT property FROM global_property WHERE property LIKE \'%referral%\';"')

ssh.close()
