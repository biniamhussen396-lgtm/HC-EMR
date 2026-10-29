import subprocess

HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

def run_sudo(cmd):
    wrapped = f"echo '{PW}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    res = subprocess.run(
        ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", wrapped],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return res.stdout, res.stderr

sql = """
INSERT IGNORE INTO user_role (user_id, role) VALUES (1, 'SuperAdmin'), (1, 'Privilege Level: Full');
INSERT IGNORE INTO role_privilege (role, privilege) VALUES 
('System Developer', 'app:orders'), 
('Admin-App', 'app:orders'), 
('SuperAdmin', 'app:orders'),
('Privilege Level: Full', 'app:orders');
"""
out, err = run_sudo(f'docker exec bahmni-standard-openmrsdb-1 mysql -uroot -p"adminAdmin!123" openmrs -e "{sql}"')
print("SQL OUT:", out)
print("SQL ERR:", err)
