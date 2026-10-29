import os
import uuid

def escape_sql(sql):
    return sql.replace("'", "''")

with open('config/masterdata/configuration/sql/emrapi.sqlSearch.icuRegister.sql', 'r', encoding='utf-8') as f:
    icu_sql = f.read().strip()

with open('config/masterdata/configuration/sql/emrapi.sqlSearch.opdRegister.sql', 'r', encoding='utf-8') as f:
    opd_sql = f.read().strip()

with open('config/masterdata/configuration/sql/emrapi.sqlSearch.liaisonRegister.sql', 'r', encoding='utf-8') as f:
    liaison_sql = f.read().strip()

statements = []
for prop, sql_content in [
    ('emrapi.sqlSearch.icuRegister', icu_sql),
    ('emrapi.sqlSearch.opdRegister', opd_sql),
    ('emrapi.sqlSearch.liaisonRegister', liaison_sql)
]:
    escaped = escape_sql(sql_content)
    u = str(uuid.uuid4())
    stmt = f"""
    INSERT INTO openmrs.global_property (property, property_value, uuid)
    VALUES ('{prop}', '{escaped}', '{u}')
    ON DUPLICATE KEY UPDATE property_value = '{escaped}';
    """
    statements.append(stmt)

full_sql = "\n".join(statements)
with open('scratch/update_registers_gp.sql', 'w', encoding='utf-8') as f:
    f.write(full_sql)

print("Generated scratch/update_registers_gp.sql successfully!")
