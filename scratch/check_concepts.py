import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

sql = """
SELECT cn.concept_id, cn.name, c.datatype_id, cd.name as datatype
FROM concept_name cn
JOIN concept c ON cn.concept_id = c.concept_id
JOIN concept_datatype cd ON c.datatype_id = cd.concept_datatype_id
WHERE cn.name LIKE 'Referral Approv%' OR cn.name LIKE 'Referral Senior%'
AND cn.voided = 0;
"""

out, err = run_sudo(f'docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e "{sql}"')
print("Concepts on 192.168.10.5:\n", out)
ssh.close()
