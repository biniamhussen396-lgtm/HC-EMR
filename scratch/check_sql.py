import subprocess

res = subprocess.run(
    ["docker", "exec", "bahmni-standard-openmrsdb-1", "mysql", "-uroot", "-padminAdmin!123", "openmrs", "-e",
     "SELECT property, property_value FROM global_property WHERE property LIKE '%OrdersSearch';"],
    capture_output=True, text=True
)
print(res.stdout)
