import subprocess, json

def sh(remote_cmd):
    return subprocess.run(['plink', '-batch', '-ssh', '-pw', '   ', 'bmh@192.168.10.5', remote_cmd], capture_output=True, text=True)

p_uuid = '784d88ef-6562-4a5a-a938-d3bb9c78249c'
attr_type = 'e2aaac17-5e07-11ef-8f7c-0242ac120002'

# 1. Add
post_cmd = f"curl -k -s -u admin:Admin123 -X POST -H 'Content-Type: application/json' -d '{{\"attributeType\": \"{attr_type}\", \"value\": true}}' 'https://127.0.0.1/openmrs/ws/rest/v1/provider/{p_uuid}/attribute'"
res = sh(post_cmd)
attr_json = json.loads(res.stdout)
new_uuid = attr_json['uuid']
print('Added attribute UUID:', new_uuid)

# 2. Check active
get_cmd = f"curl -k -s -u admin:Admin123 'https://127.0.0.1/openmrs/ws/rest/v1/provider/{p_uuid}?v=custom:(attributes:(uuid,attributeType:(uuid,display),value,voided))'"
res2 = sh(get_cmd)
attrs = json.loads(res2.stdout)['attributes']
active = [a for a in attrs if not a.get('voided') and a['attributeType']['display'] == 'Available for appointments']
print('Active count after add:', len(active))

# 3. Delete
del_cmd = f"curl -k -s -u admin:Admin123 -X DELETE 'https://127.0.0.1/openmrs/ws/rest/v1/provider/{p_uuid}/attribute/{new_uuid}'"
sh(del_cmd)

# 4. Check active again
res3 = sh(get_cmd)
attrs3 = json.loads(res3.stdout)['attributes']
active3 = [a for a in attrs3 if not a.get('voided') and a['attributeType']['display'] == 'Available for appointments']
print('Active count after delete:', len(active3))
