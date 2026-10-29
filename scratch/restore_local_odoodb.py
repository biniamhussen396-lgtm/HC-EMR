import subprocess
import time

print("Terminating existing connections and recreating database odoo...")
recreate_sql = """
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'odoo' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS odoo;
CREATE DATABASE odoo WITH OWNER = odoo ENCODING = 'UTF8';
"""
cmd = ["docker", "exec", "-i", "bahmni-standard-odoodb-1", "psql", "-U", "odoo", "-d", "postgres"]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate(recreate_sql.encode())
print("Recreated DB:", out.decode(), err.decode())

print("Restoring database dump /tmp/remote_odoo_live_backup.dump...")
t0 = time.time()
restore_cmd = [
    "docker", "exec", "-i", "bahmni-standard-odoodb-1", 
    "pg_restore", "-U", "odoo", "-d", "odoo", "--no-owner", "--no-privileges", "/tmp/remote_odoo_live_backup.dump"
]
p = subprocess.Popen(restore_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
dur = time.time() - t0
print(f"pg_restore completed in {dur:.1f}s. Return code: {p.returncode}")
if err:
    print("Stderr (last 10 lines):", "\n".join(err.decode().splitlines()[-10:]))

# Verify counts in restored database
verify_cmd = [
    "docker", "exec", "-i", "bahmni-standard-odoodb-1", 
    "psql", "-U", "odoo", "-d", "odoo", "-c", 
    "SELECT count(*) FROM res_partner; SELECT count(*) FROM product_product; SELECT count(*) FROM sale_order;"
]
subprocess.run(verify_cmd)
