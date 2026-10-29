import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

commands = [
    "docker exec bahmni-standard-odoodb-1 psql -U odoo -d odoo -c \"SELECT name, state FROM ir_module_module WHERE state='installed' AND (name LIKE '%bahmni%' OR name LIKE '%sync%');\"",
    "docker exec bahmni-standard-odoodb-1 psql -U odoo -d odoo -c \"SELECT count(*) FROM res_partner;\"",
    "docker exec bahmni-standard-odoodb-1 psql -U odoo -d odoo -c \"SELECT count(*) FROM sale_order;\"",
    "docker exec bahmni-standard-odoodb-1 psql -U odoo -d odoo -c \"SELECT count(*) FROM product_product;\"",
    "docker exec bahmni-standard-odoodb-1 psql -U odoo -d odoo -c \"SELECT count(*) FROM failed_events;\" 2>/dev/null || true",
    "docker exec bahmni-standard-odoodb-1 psql -U odoo -d odoo -c \"SELECT feed_uri, last_read_entry_id FROM markers;\" 2>/dev/null || true"
]

for cmd in commands:
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())

ssh.close()
