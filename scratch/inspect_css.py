with open("scratch/local_appointments_app/appointment.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

import re
pos = content.find(".appointment-action-btn-container")
while pos != -1:
    print("--- MATCH AT", pos, "---")
    print(content[pos:pos+500].replace("\\n", "\n"))
    pos = content.find(".appointment-action-btn-container", pos + 1)
