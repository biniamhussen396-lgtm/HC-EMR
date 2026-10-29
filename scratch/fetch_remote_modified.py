import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.10.5", username="bmh", password="   ", timeout=10)

files_to_fetch = [
    "/opt/bahmni-erp/bahmni-addons/uog_care/models/payment_methods_detail.py",
    "/opt/bahmni-erp/bahmni-addons/uog_care/models/sale_report.py",
    "/opt/bahmni-erp/bahmni-addons/bahmni_api_feed/models/order_save_service.py"
]

for remote_path in files_to_fetch:
    print(f"Fetching {remote_path}...")
    stdin, stdout, stderr = ssh.exec_command(f"docker exec bahmni-standard-odoo-1 cat {remote_path}")
    content = stdout.read()
    local_name = remote_path.split("/")[-1]
    with open(f"scratch/remote_{local_name}", "wb") as f:
        f.write(content)
    print(f"Saved scratch/remote_{local_name} ({len(content)} bytes)")

ssh.close()
