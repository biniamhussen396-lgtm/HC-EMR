import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=15)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

# Prepare SQL file
with open('config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql', 'r', encoding='utf-8') as f:
    sql_query = f.read().strip()

escaped_query = sql_query.replace('\\', '\\\\').replace("'", "''")

full_sql = f"""
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

-- Global Property
INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.referralManagement', '{escaped_query}', 'Referral In/Out Register SQL Search query with Senior Physician Approval', UUID())
ON DUPLICATE KEY UPDATE property_value = '{escaped_query}', description = 'Referral In/Out Register SQL Search query with Senior Physician Approval';
"""

# Upload to remote /tmp/deploy_referral.sql via SFTP
sftp = ssh.open_sftp()
with sftp.file('/tmp/deploy_referral.sql', 'w') as rf:
    rf.write(full_sql)
sftp.close()

print("[+] Uploaded /tmp/deploy_referral.sql to remote.")
out, err = run_sudo("bash -c 'docker exec -i bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs < /tmp/deploy_referral.sql'")
print("SQL Execution Out:\n", out)
if err and 'Warning' not in err and '[sudo]' not in err:
    print("SQL Execution Err:\n", err)

# Verification
verify_sql = """
SELECT c.concept_id, c.uuid, cn.name
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
SELECT property, LENGTH(property_value) FROM global_property WHERE property = 'emrapi.sqlSearch.referralManagement';
"""
sftp = ssh.open_sftp()
with sftp.file('/tmp/verify_referral.sql', 'w') as rf:
    rf.write(verify_sql)
sftp.close()

out, err = run_sudo("bash -c 'docker exec -i bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs < /tmp/verify_referral.sql'")
print("Verification Result:\n", out)

# Clean up /tmp sql files
run_sudo("rm -f /tmp/deploy_referral.sql /tmp/verify_referral.sql")

ssh.close()
