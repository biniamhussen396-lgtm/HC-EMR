import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

commands = [
    "cat /opt/emr/bahmni-docker/bahmni-standard/docker-compose.override.yml",
    "cat /opt/emr/bahmni-docker/bahmni-standard/sync_unsynced_orders.sh",
    "ls -la /opt/emr/bahmni-docker/bahmni-standard/extra-odoo-addons/bahmni_manual_sync",
    "find /opt/emr/bahmni-docker/bahmni-standard/extra-odoo-addons/bahmni_manual_sync -type f",
    "docker inspect bahmni-standard-odoo-connect-1 --format '{{.Config.Image}} {{json .Config.Env}} {{json .Config.Cmd}}'",
]

for cmd in commands:
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())

ssh.close()
