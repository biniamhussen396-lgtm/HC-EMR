import os
import tarfile
import subprocess

REPO_ROOT = r"c:\Users\COMPUTER\Documents\emr"
HOST = "192.168.10.5"
USER = "bmh"
PW = "   "

DIRS_TO_COPY = [
    "apps/ui/app/common/displaycontrols/stockOut",
    "apps/ui/app/common/displaycontrols/pacsOrders",
]

FILES_TO_COPY = [
    "apps/ui/app/common/concept-set/directives/bodyDiagram.js",
    "apps/ui/app/common/concept-set/views/observationDataTypes/bodyDiagram.html",
]

def run_remote(cmd):
    res = subprocess.run(
        ["plink", "-batch", "-ssh", "-pw", PW, f"{USER}@{HOST}", cmd],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return res.returncode, res.stdout, res.stderr

def run_sudo(cmd):
    wrapped = f"echo '{PW}' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"
    return run_remote(wrapped)

def main():
    tar_path = os.path.join(REPO_ROOT, "scratch", "missing_controls.tar.gz")
    print(f"[*] Creating archive: {tar_path}")
    with tarfile.open(tar_path, "w:gz") as tar:
        for d in DIRS_TO_COPY:
            local_dir = os.path.join(REPO_ROOT, d.replace("/", os.sep))
            for root, dirs, files in os.walk(local_dir):
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, REPO_ROOT).replace("\\", "/")
                    tar.add(full_p, arcname=rel_p)
                    print(f"  + Added {rel_p}")
        for f in FILES_TO_COPY:
            full_p = os.path.join(REPO_ROOT, f.replace("/", os.sep))
            if os.path.exists(full_p):
                tar.add(full_p, arcname=f)
                print(f"  + Added {f}")

    print(f"[*] Uploading archive to {HOST}:/tmp/missing_controls.tar.gz ...")
    res = subprocess.run(
        ["pscp", "-batch", "-pw", PW, tar_path, f"{USER}@{HOST}:/tmp/missing_controls.tar.gz"],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if res.returncode != 0:
        print(f"[!] Upload failed: {res.stderr}")
        return False

    install_cmd = """
rm -rf /tmp/missing_controls
mkdir -p /tmp/missing_controls
tar -xzf /tmp/missing_controls.tar.gz -C /tmp/missing_controls

cp -r /tmp/missing_controls/apps/ui/app/common/displaycontrols/stockOut /opt/emr/apps/ui/app/common/displaycontrols/
cp -r /tmp/missing_controls/apps/ui/app/common/displaycontrols/pacsOrders /opt/emr/apps/ui/app/common/displaycontrols/
cp /tmp/missing_controls/apps/ui/app/common/concept-set/directives/bodyDiagram.js /opt/emr/apps/ui/app/common/concept-set/directives/bodyDiagram.js
cp /tmp/missing_controls/apps/ui/app/common/concept-set/views/observationDataTypes/bodyDiagram.html /opt/emr/apps/ui/app/common/concept-set/views/observationDataTypes/bodyDiagram.html

chmod -R 755 /opt/emr/apps/ui/app/common/displaycontrols/stockOut
chmod -R 755 /opt/emr/apps/ui/app/common/displaycontrols/pacsOrders
chmod 644 /opt/emr/apps/ui/app/common/concept-set/directives/bodyDiagram.js
chmod 644 /opt/emr/apps/ui/app/common/concept-set/views/observationDataTypes/bodyDiagram.html

echo "VERIFYING:"
ls -la /opt/emr/apps/ui/app/common/displaycontrols/stockOut
curl -k -s -o /dev/null -w "stockOut/init.js: %{http_code}\n" https://localhost/bahmni/common/displaycontrols/stockOut/init.js
curl -k -s -o /dev/null -w "bodyDiagram.js: %{http_code}\n" https://localhost/bahmni/common/concept-set/directives/bodyDiagram.js
curl -k -s -o /dev/null -w "dicomUpload.js: %{http_code}\n" https://localhost/bahmni/common/displaycontrols/pacsOrders/directives/dicomUpload.js
"""
    print("[*] Executing install command on remote server...")
    rc, stdout, stderr = run_sudo(install_cmd)
    print("STDOUT:\n", stdout)
    if rc != 0:
        print("STDERR:\n", stderr)
        return False

    print("[SUCCESS] Missing display controls deployed successfully!")
    return True

if __name__ == "__main__":
    main()
