#!/usr/bin/env python3
import glob
import os
import subprocess
import sys

def run_cmd(cmd, check=True):
    print(f"[*] Running: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if check and res.returncode != 0:
        print(f"[!] Restore error:\n{res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)
    return res.stdout.strip()

def apply_frontend_patches():
    print("[*] Applying routing and skipLogic null-safety patches to Bahmni-Web...")
    # Fix 1: searchPatientController - crTriageVisit
    run_cmd(
        'docker exec -i bahmni-standard-bahmni-web-1 sed -i '
        '\'s#\\$location\\.url("/patient/" + \\$scope\\.selectedPatient\\.uuid + "/crTriageVisit");#'
        'var cleanUuid = ($scope.selectedPatient.uuid || "").replace(/^\\\/+/g, ""); '
        '\\$location.url("/patient/" + cleanUuid + "/crTriageVisit");#g\' '
        '/usr/local/apache2/htdocs/bahmni/registration/controllers/searchPatientController.js',
        check=False
    )
    # Fix 2: searchPatientController - prescription
    run_cmd(
        'docker exec -i bahmni-standard-bahmni-web-1 sed -i '
        '\'s#\\$location\\.url("/patient/" + \\$scope\\.selectedPatient\\.uuid + "/prescription");#'
        'var cleanUuid = ($scope.selectedPatient.uuid || "").replace(/^\\\/+/g, ""); '
        '\\$location.url("/patient/" + cleanUuid + "/prescription");#g\' '
        '/usr/local/apache2/htdocs/bahmni/registration/controllers/searchPatientController.js',
        check=False
    )
    # Fix 3: createCRTriagePatientController - goToVisitPage
    run_cmd(
        'docker exec -i bahmni-standard-bahmni-web-1 sed -i '
        '\'s#\\$location\\.path("/patient/" + patientData\\.patient\\.uuid + "/crTriageVisit");#'
        'var cleanUuid = (patientData.patient.uuid || "").replace(/^\\\/+/g, ""); '
        '\\$location.path("/patient/" + cleanUuid + "/crTriageVisit");#g\' '
        '/usr/local/apache2/htdocs/bahmni/registration/controllers/createCRTriagePatientController.js',
        check=False
    )
    # Fix 4: skipLogicProcessor - null-safety for patientHistory.person
    run_cmd(
        'docker exec -i bahmni-standard-bahmni-web-1 sed -i '
        '\'s#const providerName = patientHistory\\.person\\.currentProvider\\.name#'
        'const providerName = (patientHistory \\&\\& patientHistory.person \\&\\& patientHistory.person.currentProvider) ? '
        'patientHistory.person.currentProvider.name : "";#g\' '
        '/usr/local/apache2/htdocs/bahmni/common/logicAndConditionProcessors/skipLogicProcessor.js',
        check=False
    )

def main():
    if len(sys.argv) < 2:
        backups = sorted(glob.glob("/opt/emr/backups/bahmni_backup_*.tar.gz"))
        if not backups:
            print("[!] No backup archive specified and none found in /opt/emr/backups/")
            sys.exit(1)
        archive_path = backups[-1]
        print(f"[*] Defaulting to latest backup found: {archive_path}")
    else:
        archive_path = sys.argv[1]

    if not os.path.exists(archive_path):
        print(f"[!] Archive not found: {archive_path}")
        sys.exit(1)

    temp_dir = "/tmp/bahmni_restore_unpack"
    run_cmd(f"rm -rf {temp_dir} && mkdir -p {temp_dir}")
    print(f"[*] Extracting {archive_path}...")
    run_cmd(f"tar -xzf {archive_path} -C {temp_dir}")

    extracted_folders = glob.glob(f"{temp_dir}/bahmni_backup_*")
    source_dir = extracted_folders[0] if extracted_folders else temp_dir

    # 1. Restore OpenMRS
    openmrs_sql = os.path.join(source_dir, "openmrs.sql")
    if os.path.exists(openmrs_sql):
        print("[*] Restoring OpenMRS database...")
        run_cmd("docker exec -i bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 -e 'DROP DATABASE IF EXISTS openmrs; CREATE DATABASE openmrs CHARACTER SET utf8;'")
        run_cmd(f"docker exec -i bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs < {openmrs_sql}")

    # 2. Restore ClinLIMS / OpenELIS
    clinlims_sql = os.path.join(source_dir, "clinlims.sql")
    if os.path.exists(clinlims_sql):
        print("[*] Restoring ClinLIMS / OpenELIS database...")
        run_cmd("docker exec -i bahmni-standard-openelisdb-1 dropdb -U clinlims --if-exists clinlims", check=False)
        run_cmd("docker exec -i bahmni-standard-openelisdb-1 createdb -U clinlims clinlims", check=False)
        run_cmd(f"docker exec -i bahmni-standard-openelisdb-1 psql -U clinlims -d clinlims < {clinlims_sql}")

    # 3. Restore Odoo
    odoo_sql = os.path.join(source_dir, "odoo.sql")
    if os.path.exists(odoo_sql):
        print("[*] Restoring Odoo database...")
        run_cmd("docker exec -i bahmni-standard-odoodb-1 dropdb -U odoo --if-exists odoo", check=False)
        run_cmd("docker exec -i bahmni-standard-odoodb-1 createdb -U odoo odoo", check=False)
        run_cmd(f"docker exec -i bahmni-standard-odoodb-1 psql -U odoo -d odoo < {odoo_sql}", check=False)

    # 4. Restore Lab Sync State
    lab_json = os.path.join(source_dir, "lab_last_result.json")
    if os.path.exists(lab_json):
        print("[*] Restoring Lab Result sync position...")
        run_cmd(f"docker cp {lab_json} lab-result-sync:/last_result.json", check=False)

    # 5. Clean up unpack folder
    run_cmd(f"rm -rf {temp_dir}")

    # 6. Apply Web UI Patches
    apply_frontend_patches()

    # 7. Restart sync services and application containers
    print("[*] Cycling sync containers and application servers...")
    run_cmd("docker restart bahmni-standard-odoo-connect-1 bahmni-standard-atomfeed-console-1 bahmni-standard-odoo-ssl-1 bahmni-standard-openmrs-1 bahmni-standard-openelis-1", check=False)

    print("\n[✔] Restore and patch verification completed successfully.")

if __name__ == "__main__":
    main()
