#!/usr/bin/env python3
import sys
import time
import pymysql
import subprocess

OPENMRS_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "adminAdmin!123",
    "database": "openmrs",
    "charset": "utf8mb4"
}

def escape_sql(val):
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''").strip()
    return f"'{s}'" if s else "NULL"

def run_odoo_psql(sql_content):
    cmd = ["docker", "exec", "-i", "bahmni-standard-odoodb-1", "psql", "-U", "odoo", "-d", "odoo"]
    res = subprocess.run(cmd, input=sql_content, text=True, capture_output=True)
    if res.returncode != 0:
        print(f"[!] Odoo PostgreSQL Error:\n{res.stderr}", file=sys.stderr)
        return False
    return True

def main():
    print("=" * 70)
    print(" OPENMRS TO ODOO DIRECT BATCH PATIENT SYNC PIPELINE")
    print("=" * 70)

    print("[*] Connecting to OpenMRS MySQL database...")
    try:
        mysql_conn = pymysql.connect(**OPENMRS_CONFIG)
        cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)
        print("[✔] OpenMRS database connected.")
    except Exception as e:
        print(f"[!] Failed to connect to OpenMRS: {e}")
        sys.exit(1)

    # 1. Fetch company ID from Odoo
    res = subprocess.run(
        ["docker", "exec", "-i", "bahmni-standard-odoodb-1", "psql", "-U", "odoo", "-d", "odoo", "-t", "-c", "SELECT id FROM res_company LIMIT 1;"],
        text=True, capture_output=True
    )
    company_id = res.stdout.strip() or "1"
    print(f"[*] Detected Odoo Company ID: {company_id}")

    # 2. Query patient demographic records using person (pe) for uuid
    print("[*] Querying patient demographic records from OpenMRS...")
    query = """
    SELECT 
        pe.uuid AS patient_uuid,
        pi.identifier AS mrn,
        pn.given_name,
        pn.middle_name,
        pn.family_name,
        pa.city_village AS kebele,
        pa.county_district AS woreda,
        pattr.value AS phone
    FROM patient p
    JOIN person pe ON p.patient_id = pe.person_id AND pe.voided = 0
    JOIN person_name pn ON p.patient_id = pn.person_id AND pn.voided = 0
    JOIN patient_identifier pi ON p.patient_id = pi.patient_id AND pi.preferred = 1 AND pi.voided = 0
    LEFT JOIN person_address pa ON p.patient_id = pa.person_id AND pa.voided = 0
    LEFT JOIN person_attribute pattr ON p.patient_id = pattr.person_id AND pattr.person_attribute_type_id = 9 AND pattr.voided = 0
    WHERE p.voided = 0;
    """
    cursor.execute(query)
    patients = cursor.fetchall()
    total_pts = len(patients)
    print(f"[✔] Fetched {total_pts} active patients from OpenMRS.")

    if total_pts == 0:
        print("[!] No active patients found to sync.")
        sys.exit(0)

    batch_size = 1000
    synced_count = 0
    start_time = time.time()

    print("[*] Starting fast bulk sync into Odoo...")

    for i in range(0, total_pts, batch_size):
        batch = patients[i:i + batch_size]
        sql_lines = ["BEGIN;"]

        for pt in batch:
            name_parts = [pt["given_name"] or "", pt["middle_name"] or "", pt["family_name"] or ""]
            full_name = " ".join([p.strip() for p in name_parts if p.strip()]) or "Unknown Patient"

            ref = pt["mrn"] or pt["patient_uuid"]
            phone = pt["phone"]
            city = pt["kebele"]
            street = pt["woreda"]

            sql = f"""
            INSERT INTO res_partner (
                name, ref, phone, city, street, company_id, 
                customer_rank, active, type, is_company, create_date, write_date
            )
            VALUES (
                {escape_sql(full_name)}, {escape_sql(ref)}, {escape_sql(phone)}, 
                {escape_sql(city)}, {escape_sql(street)}, {company_id}, 
                1, true, 'contact', false, NOW(), NOW()
            )
            ON CONFLICT (ref) DO UPDATE SET
                name = EXCLUDED.name,
                phone = COALESCE(EXCLUDED.phone, res_partner.phone),
                city = COALESCE(EXCLUDED.city, res_partner.city),
                street = COALESCE(EXCLUDED.street, res_partner.street),
                customer_rank = 1,
                active = true,
                write_date = NOW();
            """
            sql_lines.append(sql)

        sql_lines.append("COMMIT;")
        batch_sql = "\n".join(sql_lines)

        if not run_odoo_psql(batch_sql):
            print(f"[!] Failed syncing batch starting at record {i}.")
            break

        synced_count += len(batch)
        if synced_count % 5000 == 0 or synced_count == total_pts:
            elapsed = time.time() - start_time
            rate = synced_count / elapsed if elapsed > 0 else 0
            print(f"[Activity] Synced {synced_count}/{total_pts} patients into Odoo ({rate:.1f} pts/sec)...")

    cursor.close()
    mysql_conn.close()

    print("\n" + "=" * 70)
    print(f"[✔] SYNC COMPLETED: {synced_count} patients available in Odoo.")
    print("=" * 70)

if __name__ == "__main__":
    main()
