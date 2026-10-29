import subprocess
import difflib
import json

HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

# 1. Fetch remote dashboard.json using plink cat
res = subprocess.run(
    ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", "cat /opt/emr/config/openmrs/apps/clinical/dashboard.json"],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
remote_content = res.stdout

with open("scratch/remote_dashboard.json", "w", encoding="utf-8") as f:
    f.write(remote_content)

with open("config/openmrs/apps/clinical/dashboard.json", "r", encoding="utf-8") as f:
    local_content = f.read()

print(f"Remote length: {len(remote_content)} chars")
print(f"Local length: {len(local_content)} chars")

remote_lines = remote_content.splitlines(keepends=True)
local_lines = local_content.splitlines(keepends=True)

diff = list(difflib.unified_diff(remote_lines, local_lines, fromfile="remote", tofile="local"))
print("=== UNIFIED DIFF (first 50 lines) ===")
for line in diff[:50]:
    print(line, end="")
