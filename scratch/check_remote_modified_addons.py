import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

commands = [
    # Check git status if it is a git repo
    "docker exec bahmni-standard-odoo-1 bash -c 'cd /opt/bahmni-erp/bahmni-addons && find . -name \"*.py\" -mtime -365'",
    "docker exec bahmni-standard-odoo-1 bash -c 'cat /opt/bahmni-erp/bahmni-addons/bahmni_api_feed/models/order_save_service.py | grep -n \"Lab Order\"'",
    "docker exec bahmni-standard-odoo-1 bash -c 'cat /opt/bahmni-erp/bahmni-addons/bahmni_api_feed/models/order_save_service.py | grep -n \"stock\"'",
    # Check if there are other addon directories in /mnt, /opt, /var/lib/odoo
    "docker exec bahmni-standard-odoo-1 bash -c 'find /var/lib/odoo -maxdepth 3'",
]

for cmd in commands:
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())

ssh.close()
