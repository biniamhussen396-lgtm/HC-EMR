import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=15)

def run_sudo(cmd):
    stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S {cmd}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out.strip()

# Let's test execution time WITHOUT the screening subquery
q_base = """
SELECT 
    v.visit_id,
    p.uuid as patient_uuid,
    v.uuid as visit_uuid,
    pi.identifier as mrn,
    TRIM(CONCAT(pn.given_name, IF(pn.middle_name IS NOT NULL AND pn.middle_name != '', CONCAT(' ', pn.middle_name), ''), IF(pn.family_name IS NOT NULL AND pn.family_name != '', CONCAT(' ', pn.family_name), ''))) as patient_name,
    p.gender as sex,
    TIMESTAMPDIFF(YEAR, p.birthdate, v.date_started) as age,
    COALESCE(pa.city_village, pa.address1, '-') as woreda,
    COALESCE(pa.address2, pa.state_province, '-') as subcity,
    v.date_started as admission_date,
    v.date_stopped as discharge_date,
    IF(v.date_stopped IS NULL, 'Admitted', 'Discharged') as status,
    DATEDIFF(IFNULL(v.date_stopped, NOW()), v.date_started) as length_of_stay,
    vt.name as ward_name,
    IFNULL(b.bed_number, '-') as bed_number,
    IF(p.dead = 1, IF(TIMESTAMPDIFF(HOUR, v.date_started, IFNULL(p.death_date, v.date_stopped)) <= 24, 'Within 24 hrs', 'After 24 hrs'), '-') as death_in_ipd,
    IF(p.dead = 1, 'Yes', 'No') as death_notification,
    IFNULL(pm_attr.value, 'Free') as payment_method,
    IFNULL(ref_attr.value, '-') as voucher_no,
    '-' as remark
FROM visit v
JOIN visit_type vt ON v.visit_type_id = vt.visit_type_id AND (vt.name LIKE '%ward%' OR vt.name IN ('Emergency OPD', 'Delivery Room', 'IPD'))
JOIN patient_identifier pi ON v.patient_id = pi.patient_id
JOIN patient_identifier_type pit ON pi.identifier_type = pit.patient_identifier_type_id
JOIN global_property gp ON gp.property = 'bahmni.primaryIdentifierType' AND gp.property_value = pit.uuid
JOIN person p ON v.patient_id = p.person_id
JOIN person_name pn ON v.patient_id = pn.person_id AND pn.voided = 0
LEFT JOIN person_address pa ON v.patient_id = pa.person_id AND pa.voided = 0
LEFT JOIN (
    SELECT bp.patient_id, bp.bed_id, bp.date_started, bp.date_stopped
    FROM bed_patient_assignment_map bp
    WHERE bp.voided = 0
) bed_map ON v.patient_id = bed_map.patient_id AND (bed_map.date_stopped IS NULL OR bed_map.date_started >= v.date_started)
LEFT JOIN bed b ON bed_map.bed_id = b.bed_id
LEFT JOIN person_attribute pm_attr ON v.patient_id = pm_attr.person_id AND pm_attr.person_attribute_type_id = 17 AND pm_attr.voided = 0
LEFT JOIN person_attribute ref_attr ON v.patient_id = ref_attr.person_id AND ref_attr.person_attribute_type_id = 15 AND ref_attr.voided = 0
WHERE v.voided = 0
GROUP BY v.visit_id
ORDER BY v.date_started DESC
LIMIT 500;
"""

print("Testing base query without obs subqueries...")
t0 = time.time()
res = run_sudo(f"docker exec bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"{q_base}\"")
t1 = time.time()
print(f"Base query time: {t1 - t0:.2f}s | Rows: {len(res.splitlines())}")

ssh.close()
