#!/usr/bin/env python3
import glob
import os
import subprocess
import sys

def run_cmd(cmd, check=True):
    print(f"[*] Running: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if check and res.returncode != 0:
        print(f"[!] Error:\n{res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)
    return res.stdout.strip()

def find_odoo_sql(target_path):
    if os.path.isfile(target_path) and target_path.endswith("odoo.sql"):
        return target_path
    
    # Check directly inside target folder
    direct_sql = os.path.join(target_path, "odoo.sql")
    if os.path.isfile(direct_sql):
        return direct_sql
    
    # Check inside nested backup folder structure
    matches = glob.glob(f"{target_path}/**/odoo.sql", recursive=True)
    if matches:
        return matches[0]
    
    return None

def main():
    if len(sys.argv) > 1:
        search_path = sys.argv[1]
    else:
        # Default search paths if no folder argument is provided
        default_folders = sorted(glob.glob("/opt/emr/backups/bahmni_backup_*"))
        default_folders = [f for f in default_folders if os.path.isdir(f)]
        if default_folders:
            search_path = default_folders[-1]
            print(f"[*] No path provided. Defaulting to: {search_path}")
        else:
            search_path = "/opt/emr/backups"

    odoo_sql = find_odoo_sql(search_path)
    if not odoo_sql or not os.path.exists(odoo_sql):
        print(f"[!] Could not locate odoo.sql in: {search_path}")
        print("Usage: python3 restore_odoo_only.py /path/to/extracted_backup_folder")
        sys.exit(1)

    print(f"[✔] Found Odoo dump: {odoo_sql} ({os.path.getsize(odoo_sql) / (1024*1024):.2f} MB)")

    confirm = input("[?] Are you sure you want to drop and restore only the Odoo database? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("[*] Aborted by user.")
        sys.exit(0)

    # 1. Terminate active connections, recreate database, and restore
    print("[*] Resetting Odoo database on bahmni-standard-odoodb-1...")
    run_cmd(
        'docker exec -i bahmni-standard-odoodb-1 psql -U odoo -d postgres -c '
        '"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = \'odoo\' AND pid <> pg_backend_pid();"',
        check=False
    )
    run_cmd("docker exec -i bahmni-standard-odoodb-1 dropdb -U odoo --if-exists odoo", check=False)
    run_cmd("docker exec -i bahmni-standard-odoodb-1 createdb -U odoo odoo", check=True)

    print(f"[*] Importing {odoo_sql} into Odoo container...")
    run_cmd(f"docker exec -i bahmni-standard-odoodb-1 psql -U odoo -d odoo < {odoo_sql}", check=False)

    # 2. Restart Odoo web and integration containers to reload the DB connection pool
    print("[*] Restarting Odoo application and sync services...")
    run_cmd(
        "docker restart bahmni-standard-odoo-1 bahmni-standard-odoo-connect-1 bahmni-standard-odoo-ssl-1",
        check=False
    )

    print("\n[✔] Odoo database restored and services successfully restarted.")

if __name__ == "__main__":
    main()