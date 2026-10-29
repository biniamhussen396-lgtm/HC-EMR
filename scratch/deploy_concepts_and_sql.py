import paramiko
import sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=15)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def run_mysql(sql):
    escaped_sql = sql.replace('"', '\\"').replace('`', '\\`')
    cmd = f'docker exec -i bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs'
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    stdin.write(sql)
    stdin.flush()
    stdin.channel.shutdown_write()
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

concepts_sql = """
-- Concept 1: Referral Approved By
INSERT INTO concept (retired, datatype_id, class_id, is_set, creator, date_created, uuid)
SELECT 0, 3, 7, 0, 1, NOW(), 'a1b2c3d4-e5f6-7890-abcd-100000000005'
WHERE NOT EXISTS (SELECT 1 FROM concept WHERE uuid = 'a1b2c3d4-e5f6-7890-abcd-100000000005');

INSERT INTO concept_name (concept_id, name, locale, locale_preferred, creator, date_created, concept_name_type, voided, uuid)
SELECT c.concept_id, 'Referral Approved By', 'en', 1, 1, NOW(), 'FULLY_SPECIFIED', 0, UUID()
FROM concept c
WHERE c.uuid = 'a1b2c3d4-e5f6-7890-abcd-100000000005'
AND NOT EXISTS (SELECT 1 FROM concept_name WHERE name = 'Referral Approved By' AND voided = 0);

-- Concept 2: Referral Senior Physician Specialty
INSERT INTO concept (retired, datatype_id, class_id, is_set, creator, date_created, uuid)
SELECT 0, 3, 7, 0, 1, NOW(), 'a1b2c3d4-e5f6-7890-abcd-100000000006'
WHERE NOT EXISTS (SELECT 1 FROM concept WHERE uuid = 'a1b2c3d4-e5f6-7890-abcd-100000000006');

INSERT INTO concept_name (concept_id, name, locale, locale_preferred, creator, date_created, concept_name_type, voided, uuid)
SELECT c.concept_id, 'Referral Senior Physician Specialty', 'en', 1, 1, NOW(), 'FULLY_SPECIFIED', 0, UUID()
FROM concept c
WHERE c.uuid = 'a1b2c3d4-e5f6-7890-abcd-100000000006'
AND NOT EXISTS (SELECT 1 FROM concept_name WHERE name = 'Referral Senior Physician Specialty' AND voided = 0);

-- Concept 3: Referral Approval Method
INSERT INTO concept (retired, datatype_id, class_id, is_set, creator, date_created, uuid)
SELECT 0, 3, 7, 0, 1, NOW(), 'a1b2c3d4-e5f6-7890-abcd-100000000007'
WHERE NOT EXISTS (SELECT 1 FROM concept WHERE uuid = 'a1b2c3d4-e5f6-7890-abcd-100000000007');

INSERT INTO concept_name (concept_id, name, locale, locale_preferred, creator, date_created, concept_name_type, voided, uuid)
SELECT c.concept_id, 'Referral Approval Method', 'en', 1, 1, NOW(), 'FULLY_SPECIFIED', 0, UUID()
FROM concept c
WHERE c.uuid = 'a1b2c3d4-e5f6-7890-abcd-100000000007'
AND NOT EXISTS (SELECT 1 FROM concept_name WHERE name = 'Referral Approval Method' AND voided = 0);

-- Concept 4: Referral Approval DateTime
INSERT INTO concept (retired, datatype_id, class_id, is_set, creator, date_created, uuid)
SELECT 0, 3, 7, 0, 1, NOW(), 'a1b2c3d4-e5f6-7890-abcd-100000000008'
WHERE NOT EXISTS (SELECT 1 FROM concept WHERE uuid = 'a1b2c3d4-e5f6-7890-abcd-100000000008');

INSERT INTO concept_name (concept_id, name, locale, locale_preferred, creator, date_created, concept_name_type, voided, uuid)
SELECT c.concept_id, 'Referral Approval DateTime', 'en', 1, 1, NOW(), 'FULLY_SPECIFIED', 0, UUID()
FROM concept c
WHERE c.uuid = 'a1b2c3d4-e5f6-7890-abcd-100000000008'
AND NOT EXISTS (SELECT 1 FROM concept_name WHERE name = 'Referral Approval DateTime' AND voided = 0);

-- Concept 5: Referral Approval Notes
INSERT INTO concept (retired, datatype_id, class_id, is_set, creator, date_created, uuid)
SELECT 0, 3, 7, 0, 1, NOW(), 'a1b2c3d4-e5f6-7890-abcd-100000000009'
WHERE NOT EXISTS (SELECT 1 FROM concept WHERE uuid = 'a1b2c3d4-e5f6-7890-abcd-100000000009');

INSERT INTO concept_name (concept_id, name, locale, locale_preferred, creator, date_created, concept_name_type, voided, uuid)
SELECT c.concept_id, 'Referral Approval Notes', 'en', 1, 1, NOW(), 'FULLY_SPECIFIED', 0, UUID()
FROM concept c
WHERE c.uuid = 'a1b2c3d4-e5f6-7890-abcd-100000000009'
AND NOT EXISTS (SELECT 1 FROM concept_name WHERE name = 'Referral Approval Notes' AND voided = 0);
"""

print("[1] Executing concept creation SQL on 192.168.10.5...")
out, err = run_mysql(concepts_sql)
if err and 'Warning' not in err and '[sudo]' not in err:
    print("ERR:", err)

print("[2] Verifying concepts created...")
verify_sql = """
SELECT c.concept_id, c.uuid, cn.name, cn.concept_name_type
FROM concept_name cn
JOIN concept c ON cn.concept_id = c.concept_id
WHERE c.uuid IN (
    'a1b2c3d4-e5f6-7890-abcd-100000000005',
    'a1b2c3d4-e5f6-7890-abcd-100000000006',
    'a1b2c3d4-e5f6-7890-abcd-100000000007',
    'a1b2c3d4-e5f6-7890-abcd-100000000008',
    'a1b2c3d4-e5f6-7890-abcd-100000000009'
)
AND cn.voided = 0;
"""
out, err = run_mysql(verify_sql)
print("Result:\n", out)

print("[3] Updating global property emrapi.sqlSearch.referralManagement...")
with open('config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql', 'r', encoding='utf-8') as f:
    sql_query = f.read().strip()

escaped_query = sql_query.replace('\\', '\\\\').replace("'", "''")
update_gp_sql = f"""
INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.referralManagement', '{escaped_query}', 'Referral In/Out Register SQL Search query with Senior Physician Approval', UUID())
ON DUPLICATE KEY UPDATE property_value = '{escaped_query}', description = 'Referral In/Out Register SQL Search query with Senior Physician Approval';
"""
out, err = run_mysql(update_gp_sql)
if err and 'Warning' not in err and '[sudo]' not in err:
    print("ERR GP:", err)

print("[4] Verifying global property updated...")
gp_verify = "SELECT property, LENGTH(property_value), date_changed FROM global_property WHERE property = 'emrapi.sqlSearch.referralManagement';"
out, err = run_mysql(gp_verify)
print("GP Result:\n", out)

ssh.close()
print("Done database updates.")
