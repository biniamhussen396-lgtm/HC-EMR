with open('config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql', 'r', encoding='utf-8') as f:
    sql = f.read().strip()

escaped = sql.replace("'", "''")
content = f"""DELETE FROM global_property WHERE property = 'emrapi.sqlSearch.referralManagement';

INSERT INTO global_property (property, property_value, description, uuid)
VALUES ('emrapi.sqlSearch.referralManagement', '{escaped}', 'Referral Management SQL search handler', 'a1b2c3d4-e5f6-7890-abcd-100000000020');
"""

with open('config/masterdata/configuration/sql/register_referral_mgmt_v2.sql', 'w', encoding='utf-8') as f:
    f.write(content)

with open('config/masterdata/configuration/sql/register_referral_mgmt.sql', 'w', encoding='utf-8') as f:
    f.write(content)

with open('config/masterdata/configuration/sql/add_referral_management_sql.sql', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully synchronized register_referral_mgmt.sql, register_referral_mgmt_v2.sql, and add_referral_management_sql.sql")
