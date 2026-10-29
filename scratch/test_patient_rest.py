import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=10)

cmd = "docker exec bahmni-standard-openmrs-1 curl -s -u admin:Admin123 'http://localhost:8080/openmrs/ws/rest/v1/patient/fe28b2fb-6d7b-4022-a10e-056551395d66?v=full'"
stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
raw = stdout.read().decode('utf-8', errors='replace')
# remove sudo prompt
lines = raw.split('\n')
json_str = '\n'.join([l for l in lines if l.startswith('{') or l.startswith(' ') or l.startswith('}')])
data = json.loads(json_str)

print('Top level keys:', list(data.keys()))
print('patient.identifier:', data.get('identifier'))
print('patient.age:', data.get('age'))
print('patient.gender:', data.get('gender'))
print('patient.identifiers:', [(i.get('identifier'), i.get('preferred')) for i in data.get('identifiers', [])])
print('person.age:', data.get('person', {}).get('age'))
print('person.gender:', data.get('person', {}).get('gender'))

ssh.close()
