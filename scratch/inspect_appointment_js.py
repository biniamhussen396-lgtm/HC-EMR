with open("scratch/local_appointments_app/appointment.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

import re

for term in ["appointment-action-btn-container", ".selected", "ng-disabled"]:
    matches = [m.start() for m in re.finditer(re.escape(term), content)]
    print(f"Term: {term}, Count: {len(matches)}")
    for pos in matches[:3]:
        start = max(0, pos - 150)
        end = min(len(content), pos + 150)
        print("  ...", content[start:end].replace("\n", " "), "...")
