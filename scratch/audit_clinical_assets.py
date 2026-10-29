import re
import os
import subprocess

REPO_ROOT = r"c:\Users\COMPUTER\Documents\emr"
HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

def run_remote(cmd):
    res = subprocess.run(
        ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return res.returncode, res.stdout, res.stderr

with open(os.path.join(REPO_ROOT, "apps", "ui", "app", "clinical", "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# Extract script src
scripts = re.findall(r'<script\s+[^>]*src=["\']([^"\']+)["\']', html)
# Extract link href
links = re.findall(r'<link\s+[^>]*href=["\']([^"\']+)["\']', html)

urls_to_check = []
for s in scripts:
    if s.startswith("http") or s.startswith("//"): continue
    if s.startswith("/"):
        urls_to_check.append(s)
    elif s.startswith("../"):
        urls_to_check.append("/bahmni/" + s[3:])
    else:
        urls_to_check.append("/bahmni/clinical/" + s)

for l in links:
    if l.startswith("http") or l.startswith("//"): continue
    if l.startswith("/"):
        urls_to_check.append(l)
    elif l.startswith("../"):
        urls_to_check.append("/bahmni/" + l[3:])
    else:
        urls_to_check.append("/bahmni/clinical/" + l)

# Clean query strings
cleaned_urls = [u.split("?")[0] for u in urls_to_check]
unique_urls = list(dict.fromkeys(cleaned_urls))

print(f"Total unique URLs referenced in clinical/index.html: {len(unique_urls)}")

# Check each URL with curl on remote
curl_cmds = []
for u in unique_urls:
    curl_cmds.append(f"curl -k -s -o /dev/null -w '{u}: %{{http_code}}\\n' https://localhost{u}")

# Run in chunks of 30
chunk_size = 30
missing = []
for i in range(0, len(curl_cmds), chunk_size):
    chunk = curl_cmds[i:i+chunk_size]
    rc, out, err = run_remote("; ".join(chunk))
    for line in out.strip().split("\n"):
        if ": " in line:
            url, code = line.split(": ", 1)
            if code.strip() != "200":
                print(f"[MISSING/ERROR] {url} -> {code.strip()}")
                missing.append(url)

print(f"\nTotal missing/error URLs: {len(missing)}")
