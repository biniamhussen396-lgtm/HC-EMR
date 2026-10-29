import subprocess

sql = """
SELECT table_name, column_name, column_type, is_nullable 
FROM information_schema.columns 
WHERE table_schema='openmrs' 
AND table_name IN (
    'appointment_speciality', 'appointment_service', 'appointment_service_attribute_type', 
    'appointment_service_attribute', 'patient_appointment_reason', 'patient_appointment_provider', 
    'appointment_service_weekly_availability', 'patient_appointment_audit', 'appointment_service_type', 
    'patient_appointment', 'patient_appointment_recurring_time'
) 
ORDER BY table_name, ordinal_position;
"""

# Local
cmd_local = ['docker', 'exec', 'bahmni-standard-openmrsdb-1', 'mysql', '-uroot', '-padminAdmin!123', 'openmrs', '-e', sql]
p_local = subprocess.run(cmd_local, capture_output=True, text=True)
local_lines = [l.strip() for l in p_local.stdout.splitlines() if l.strip() and not l.startswith('mysql:')]

# Remote
cmd_remote = ['plink', '-batch', '-ssh', '-pw', '   ', 'bmh@192.168.10.5', f"docker exec -i bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"{sql}\""]
p_remote = subprocess.run(cmd_remote, capture_output=True, text=True)
remote_lines = [l.strip() for l in p_remote.stdout.splitlines() if l.strip() and not l.startswith('mysql:')]

local_set = set(local_lines)
remote_set = set(remote_lines)

print("=== IN LOCAL BUT NOT REMOTE ===")
for item in sorted(local_set - remote_set):
    print(item)

print("\n=== IN REMOTE BUT NOT LOCAL ===")
for item in sorted(remote_set - local_set):
    print(item)
