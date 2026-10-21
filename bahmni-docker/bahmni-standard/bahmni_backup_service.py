#!/usr/bin/env python3
"""
Bahmni Unified Backup and Restore Service & CLI.
Supports:
  - Full System Backup (Databases, Modules/Images, Docker Volumes, Patches & Configs)
  - Database-Only Backup (OpenMRS, OpenELIS clinlims, Odoo, Reports, PACS)
  - Restore (Databases, Volumes, Web UI Patches, Service Cycling)
  - Built-in HTTP API daemon for web UI integration
"""

import argparse
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import tarfile
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

BACKUP_DIR = os.environ.get("BACKUP_DIR") or (
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backups"))
    if os.name == "nt" or not os.path.exists("/opt/emr/backups")
    else "/opt/emr/backups"
)
CONFIG_DIR = os.environ.get("CONFIG_DIR") or (
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config"))
    if os.name == "nt" or not os.path.exists("/opt/emr/config")
    else "/opt/emr/config"
)
VOL_BASE = os.environ.get("VOL_BASE", "/var/lib/docker/volumes")
RETENTION_LIMIT = int(os.environ.get("RETENTION_LIMIT", 10))
PORT = int(os.environ.get("BACKUP_PORT", 5055))

MYSQL_PASS = os.environ.get("MYSQL_ROOT_PASSWORD", "adminAdmin!123")

# Thread-safe operation lock and state
op_lock = threading.Lock()
current_op = {
    "status": "idle",       # "idle", "running", "completed", "error"
    "type": None,           # "full_backup", "db_backup", "restore"
    "message": "System ready",
    "started_at": None,
    "completed_at": None,
    "progress": 0,
    "logs": []
}

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry, flush=True)
    current_op["logs"].append(entry)
    if len(current_op["logs"]) > 200:
        current_op["logs"].pop(0)

def run_cmd(cmd, check=True):
    log(f"CMD: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if res.stdout.strip():
        for line in res.stdout.strip().splitlines()[:10]:
            log(f"  {line}")
    if res.returncode != 0:
        err_msg = res.stderr.strip() or "Command failed with code " + str(res.returncode)
        log(f"ERROR: {err_msg}")
        if check:
            raise RuntimeError(err_msg)
    return res.stdout.strip()

def run_cmd_pipe_in(cmd, in_file_path, check=True):
    log(f"CMD (PIPE): {cmd} < {os.path.basename(in_file_path)}")
    try:
        with open(in_file_path, "rb") as f:
            res = subprocess.run(cmd, shell=True, stdin=f, capture_output=True)
        if res.returncode != 0:
            err_msg = res.stderr.decode("utf-8", errors="replace").strip() or f"Command failed with code {res.returncode}"
            log(f"ERROR: {err_msg}")
            if check:
                raise RuntimeError(err_msg)
        return res.stdout.decode("utf-8", errors="replace").strip()
    except Exception as e:
        log(f"PIPE ERROR: {e}")
        if check:
            raise
        return ""

def enforce_retention():
    try:
        archives = sorted(glob.glob(os.path.join(BACKUP_DIR, "bahmni_*.tar.gz")), key=os.path.getmtime, reverse=True)
        if len(archives) > RETENTION_LIMIT:
            log(f"Pruning archives exceeding limit of {RETENTION_LIMIT}...")
            for old in archives[RETENTION_LIMIT:]:
                try:
                    os.remove(old)
                    log(f"Removed old backup: {os.path.basename(old)}")
                except OSError:
                    pass
    except Exception as e:
        log(f"Retention check warning: {e}")

def get_container(name_hint):
    try:
        res = subprocess.run(f'docker ps --filter "name={name_hint}" --format "{{{{.Names}}}}"', shell=True, capture_output=True, text=True)
        names = [n.strip() for n in res.stdout.strip().splitlines() if n.strip()]
        for n in names:
            if n == f"bahmni-standard-{name_hint}-1" or n == name_hint:
                return n
        if names:
            return names[0]
    except Exception:
        pass
    return f"bahmni-standard-{name_hint}-1"

def dump_databases(target_dir):
    log("Dumping OpenMRS MySQL Database...")
    omrs = get_container("openmrsdb")
    run_cmd(f'docker exec {omrs} mysqldump -uroot -p"{MYSQL_PASS}" --single-transaction --routines --triggers openmrs > "{target_dir}/openmrs.sql"')

    log("Dumping OpenELIS ClinLIMS Database...")
    oelis = get_container("openelisdb")
    run_cmd(f'docker exec {oelis} pg_dump -U clinlims clinlims > "{target_dir}/clinlims.sql"', check=False)

    log("Dumping Odoo PostgreSQL Database...")
    odoo = get_container("odoodb")
    run_cmd(f'docker exec {odoo} pg_dump -U odoo odoo > "{target_dir}/odoo.sql"', check=False)

    log("Dumping Bahmni Reports Database...")
    reports = get_container("reportsdb")
    run_cmd(f'docker exec {reports} mysqldump -uroot -p"{MYSQL_PASS}" --single-transaction bahmni_reports > "{target_dir}/bahmni_reports.sql"', check=False)

    log("Dumping PACS Databases...")
    pacs = get_container("pacsdb")
    run_cmd(f'docker exec {pacs} pg_dump -U postgres pacs_db > "{target_dir}/pacs_db.sql"', check=False)
    run_cmd(f'docker exec {pacs} pg_dump -U postgres pacs_integration_db > "{target_dir}/pacs_integration_db.sql"', check=False)
    run_cmd(f'docker exec {pacs} pg_dump -U postgres bahmni_pacs > "{target_dir}/bahmni_pacs.sql"', check=False)

def dump_volumes(target_dir):
    volumes_dir = os.path.join(target_dir, "volumes")
    os.makedirs(volumes_dir, exist_ok=True)
    volume_list = [
        "bahmni-standard_bahmni-document-images",
        "bahmni-standard_bahmni-patient-images",
        "bahmni-standard_bahmni-clinical-forms",
        "bahmni-standard_bahmni-lab-results",
        "bahmni-standard_bahmni-uploaded-files",
        "bahmni-standard_bahmni-queued-reports",
        "bahmni-standard_dcm4chee-archive",
        "bahmni-standard_dcm4chee-config",
        "bahmni-standard_odoofilestore",
        "bahmni-standard_odooappdata",
        "bahmni-standard_odooconfig",
        "bahmni-standard_sms-token",
    ]
    for vol in volume_list:
        src = f"{VOL_BASE}/{vol}/_data"
        dest = f"{volumes_dir}/{vol}.tar.gz"
        if os.path.isdir(src):
            log(f"Archiving volume from host path: {vol}")
            run_cmd(f'tar -czf "{dest}" -C "{src}" . 2>/dev/null', check=False)
        else:
            log(f"Archiving volume via docker: {vol}")
            try:
                run_cmd(f'docker run --rm -v "{vol}:/voldata:ro" alpine tar -czf - -C /voldata . > "{dest}"', check=False)
            except Exception as e:
                log(f"Volume archive warning for {vol}: {e}")

def dump_modules(target_dir):
    modules_dir = os.path.join(target_dir, "modules")
    os.makedirs(modules_dir, exist_ok=True)
    images = [
        "selamsew/openmrs:1.1.1-uog-1.0.2",
        "selamsew/odoo-16:1.0.0-uog-1.0.3",
        "selamsew/openelis:1.0.0-uog-1.0.5",
        "selamsew/bahmni-web:1.1.0-uog-1.0.0",
        "selamsew/lab-result-sync:1.0.2-remove-validation",
        "selamsew/global_property:uog-1.0.2",
        "bahmni/patient-documents:1.1.1",
        "bahmni/implementer-interface:1.1.1",
        "bahmni/reports:1.1.0",
        "bahmni/odoo-connect:1.0.0",
        "bahmni/proxy:1.1.0",
        "bahmni/dcm4chee:1.0.0",
        "bahmni/pacs-integration:1.0.0",
        "bahmni/microfrontend-ipd:1.0.0",
        "bahmni/appointments:1.1.1",
        "bahmni/atomfeed-console:1.0.0",
        "bahmni/openmrs-db:1.0.0-standard",
        "bahmni/odoo-16-db:1.0.0-standard",
        "bahmni/openelis-db:1.0.0-standard",
        "postgres:9.6",
        "mysql:8.0",
    ]
    # Record metadata list of images
    with open(os.path.join(modules_dir, "manifest.json"), "w") as f:
        json.dump({"images": images, "created_at": datetime.datetime.now().isoformat()}, f, indent=2)
    log(f"Saved module and image manifests ({len(images)} container images)")

def dump_patches_and_config(target_dir):
    # Lab sync state
    run_cmd(f'docker cp lab-result-sync:/last_result.json "{target_dir}/lab_last_result.json"', check=False)
    # EMR app config
    if os.path.isdir(CONFIG_DIR):
        log("Archiving EMR Configs...")
        run_cmd(f'tar -czf "{target_dir}/emr_config.tar.gz" -C "{CONFIG_DIR}" .', check=False)
    # Web UI Patches
    web_dir = os.path.join(target_dir, "bahmni_web_patches")
    os.makedirs(web_dir, exist_ok=True)
    run_cmd(f'docker cp bahmni-standard-bahmni-web-1:/usr/local/apache2/htdocs/bahmni/registration/controllers/searchPatientController.js "{web_dir}/searchPatientController.js"', check=False)
    run_cmd(f'docker cp bahmni-standard-bahmni-web-1:/usr/local/apache2/htdocs/bahmni/registration/controllers/createCRTriagePatientController.js "{web_dir}/createCRTriagePatientController.js"', check=False)
    run_cmd(f'docker cp bahmni-standard-bahmni-web-1:/usr/local/apache2/htdocs/bahmni/common/logicAndConditionProcessors/skipLogicProcessor.js "{web_dir}/skipLogicProcessor.js"', check=False)
    run_cmd(f'docker cp bahmni-standard-bahmni-web-1:/usr/local/apache2/htdocs/bahmni/common/patient-search/controllers/patientsListController.js "{web_dir}/patientsListController.js"', check=False)
    run_cmd(f'docker cp bahmni-standard-bahmni-web-1:/usr/local/apache2/htdocs/bahmni/document-upload/index.html "{web_dir}/document_upload_index.html"', check=False)

def execute_full_backup():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"bahmni_full_backup_{ts}"
    staging = os.path.join(BACKUP_DIR, folder_name)
    archive_path = f"{staging}.tar.gz"

    os.makedirs(staging, exist_ok=True)
    metadata = {
        "type": "Full Backup",
        "description": "Entire system backup (Databases, Modules, Volumes, Config)",
        "timestamp": ts,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(staging, "backup_meta.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    current_op["progress"] = 10
    current_op["message"] = "Dumping databases..."
    dump_databases(staging)

    current_op["progress"] = 40
    current_op["message"] = "Archiving Docker data volumes..."
    dump_volumes(staging)

    current_op["progress"] = 70
    current_op["message"] = "Recording system modules and configs..."
    dump_modules(staging)
    dump_patches_and_config(staging)

    current_op["progress"] = 85
    current_op["message"] = f"Compressing into {os.path.basename(archive_path)}..."
    log(f"Compressing into {archive_path}...")
    try:
        run_cmd(f'tar -czf "{archive_path}" -C "{BACKUP_DIR}" "{folder_name}"')
    except Exception as e:
        log(f"tar command fallback to python tarfile: {e}")
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(staging, arcname=folder_name)
    shutil.rmtree(staging, ignore_errors=True)

    enforce_retention()
    current_op["progress"] = 100
    size_mb = os.path.getsize(archive_path) / (1024 * 1024)
    current_op["message"] = f"Full backup completed successfully: {os.path.basename(archive_path)} ({size_mb:.1f} MB)"
    log(current_op["message"])
    return archive_path

def execute_db_backup():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"bahmni_db_backup_{ts}"
    staging = os.path.join(BACKUP_DIR, folder_name)
    archive_path = f"{staging}.tar.gz"

    os.makedirs(staging, exist_ok=True)
    metadata = {
        "type": "Database Backup",
        "description": "Database-only backup (OpenMRS, OpenELIS, Odoo, Reports, PACS)",
        "timestamp": ts,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(staging, "backup_meta.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    current_op["progress"] = 20
    current_op["message"] = "Dumping all databases..."
    dump_databases(staging)

    current_op["progress"] = 70
    current_op["message"] = "Backing up sync tracker..."
    run_cmd(f'docker cp lab-result-sync:/last_result.json "{staging}/lab_last_result.json"', check=False)

    current_op["progress"] = 85
    current_op["message"] = f"Compressing into {os.path.basename(archive_path)}..."
    try:
        run_cmd(f'tar -czf "{archive_path}" -C "{BACKUP_DIR}" "{folder_name}"')
    except Exception as e:
        log(f"tar command fallback to python tarfile: {e}")
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(staging, arcname=folder_name)
    shutil.rmtree(staging, ignore_errors=True)

    enforce_retention()
    current_op["progress"] = 100
    size_mb = os.path.getsize(archive_path) / (1024 * 1024)
    current_op["message"] = f"Database backup completed successfully: {os.path.basename(archive_path)} ({size_mb:.1f} MB)"
    log(current_op["message"])
    return archive_path

def apply_frontend_patches():
    log("Applying routing, patient search, and null-safety patches to Bahmni-Web...")
    bweb = get_container("bahmni-web")
    # Safe UUID formatting
    run_cmd(
        f'docker exec -i {bweb} sed -i '
        r'\'s#\$location\.url("/patient/" + \$scope\.selectedPatient\.uuid + "/crTriageVisit");#'
        r'var cleanUuid = ($scope.selectedPatient.uuid || "").replace(/^\/+/g, ""); '
        r'\$location.url("/patient/" + cleanUuid + "/crTriageVisit");#g\' '
        '/usr/local/apache2/htdocs/bahmni/registration/controllers/searchPatientController.js',
        check=False
    )
    run_cmd(
        f'docker exec -i {bweb} sed -i '
        r'\'s#\$location\.url("/patient/" + \$scope\.selectedPatient\.uuid + "/prescription");#'
        r'var cleanUuid = ($scope.selectedPatient.uuid || "").replace(/^\/+/g, ""); '
        r'\$location.url("/patient/" + cleanUuid + "/prescription");#g\' '
        '/usr/local/apache2/htdocs/bahmni/registration/controllers/searchPatientController.js',
        check=False
    )
    # Safe patient search disposition injection
    run_cmd(
        f'docker exec -i {bweb} sed -i '
        '\'s#if(patient.activeVisitUuid){#if(patient.activeVisitUuid && dispositionService){#g\' '
        '/usr/local/apache2/htdocs/bahmni/common/patient-search/controllers/patientsListController.js',
        check=False
    )
    # Document upload dispositionService inclusion
    run_cmd(
        f'docker exec -i {bweb} grep -q "dispositionService.js" /usr/local/apache2/htdocs/bahmni/document-upload/index.html || '
        f'docker exec -i {bweb} sed -i \'/observationsService\\.js/a \\        <script src="../common/domain/services/dispositionService.js"></script>\' '
        '/usr/local/apache2/htdocs/bahmni/document-upload/index.html',
        check=False
    )

def execute_restore(archive_path):
    if not os.path.exists(archive_path):
        # Try finding in BACKUP_DIR
        alt_path = os.path.join(BACKUP_DIR, archive_path)
        if os.path.exists(alt_path):
            archive_path = alt_path
        else:
            raise FileNotFoundError(f"Backup archive not found: {archive_path}")

    temp_dir = os.path.join(tempfile.gettempdir(), "bahmni_restore_unpack")
    shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir, exist_ok=True)
    log(f"Extracting archive {os.path.basename(archive_path)}...")
    current_op["progress"] = 15
    current_op["message"] = "Extracting backup archive..."
    try:
        run_cmd(f'tar -xzf "{archive_path}" -C "{temp_dir}"')
    except Exception:
        try:
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(temp_dir, filter="data")
        except TypeError:
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(temp_dir)

    # Locate source directory containing database dumps
    source_dir = temp_dir
    for root, dirs, files in os.walk(temp_dir):
        if "openmrs.sql" in files or "clinlims.sql" in files or "odoo.sql" in files or "backup_meta.json" in files:
            source_dir = root
            break

    # 1. OpenMRS
    openmrs_sql = os.path.join(source_dir, "openmrs.sql")
    if os.path.exists(openmrs_sql):
        current_op["progress"] = 30
        current_op["message"] = "Restoring OpenMRS database..."
        log("Restoring OpenMRS database...")
        omrs = get_container("openmrsdb")
        run_cmd(f'docker exec -i {omrs} mysql -uroot -p"{MYSQL_PASS}" -e "DROP DATABASE IF EXISTS openmrs; CREATE DATABASE openmrs CHARACTER SET utf8;"')
        run_cmd_pipe_in(f'docker exec -i {omrs} mysql -uroot -p"{MYSQL_PASS}" --default-character-set=utf8 openmrs', openmrs_sql)

    # 2. ClinLIMS / OpenELIS
    clinlims_sql = os.path.join(source_dir, "clinlims.sql")
    if os.path.exists(clinlims_sql):
        current_op["progress"] = 45
        current_op["message"] = "Restoring OpenELIS ClinLIMS database..."
        log("Restoring OpenELIS ClinLIMS database...")
        oelis = get_container("openelisdb")
        run_cmd(
            f'docker exec -i {oelis} psql -U clinlims -d postgres -c '
            '"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = \'clinlims\' AND pid <> pg_backend_pid();"',
            check=False
        )
        run_cmd(f"docker exec -i {oelis} dropdb -U clinlims --if-exists clinlims", check=False)
        run_cmd(f"docker exec -i {oelis} createdb -U clinlims clinlims", check=False)
        run_cmd_pipe_in(f'docker exec -i {oelis} psql -U clinlims -d clinlims', clinlims_sql, check=False)

    # 3. Odoo
    odoo_sql = os.path.join(source_dir, "odoo.sql")
    if os.path.exists(odoo_sql):
        current_op["progress"] = 60
        current_op["message"] = "Restoring Odoo ERP database..."
        log("Restoring Odoo ERP database...")
        odoo = get_container("odoodb")
        run_cmd(
            f'docker exec -i {odoo} psql -U odoo -d postgres -c '
            '"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = \'odoo\' AND pid <> pg_backend_pid();"',
            check=False
        )
        run_cmd(f"docker exec -i {odoo} dropdb -U odoo --if-exists odoo", check=False)
        run_cmd(f"docker exec -i {odoo} createdb -U odoo odoo", check=True)
        run_cmd_pipe_in(f'docker exec -i {odoo} psql -U odoo -d odoo', odoo_sql, check=False)

    # 4. Reports
    reports_sql = os.path.join(source_dir, "bahmni_reports.sql")
    if os.path.exists(reports_sql) and os.path.getsize(reports_sql) > 0:
        current_op["progress"] = 70
        current_op["message"] = "Restoring Bahmni Reports database..."
        log("Restoring Bahmni Reports database...")
        reports = get_container("reportsdb")
        run_cmd(f'docker exec -i {reports} mysql -uroot -p"{MYSQL_PASS}" -e "DROP DATABASE IF EXISTS bahmni_reports; CREATE DATABASE bahmni_reports CHARACTER SET utf8;"', check=False)
        run_cmd_pipe_in(f'docker exec -i {reports} mysql -uroot -p"{MYSQL_PASS}" --default-character-set=utf8 bahmni_reports', reports_sql, check=False)

    # 5. PACS
    pacs = get_container("pacsdb")
    pacs_sql = os.path.join(source_dir, "pacs_db.sql")
    if os.path.exists(pacs_sql):
        log("Restoring PACS databases...")
        run_cmd_pipe_in(f'docker exec -i {pacs} psql -U postgres -d pacs_db', pacs_sql, check=False)
    pacs_int_sql = os.path.join(source_dir, "pacs_integration_db.sql")
    if os.path.exists(pacs_int_sql):
        run_cmd_pipe_in(f'docker exec -i {pacs} psql -U postgres -d pacs_integration_db', pacs_int_sql, check=False)
    bahmni_pacs_sql = os.path.join(source_dir, "bahmni_pacs.sql")
    if os.path.exists(bahmni_pacs_sql):
        run_cmd_pipe_in(f'docker exec -i {pacs} psql -U postgres -d bahmni_pacs', bahmni_pacs_sql, check=False)

    # 6. Volumes (if present in archive)
    volumes_dir = os.path.join(source_dir, "volumes")
    if os.path.isdir(volumes_dir):
        current_op["progress"] = 80
        current_op["message"] = "Restoring Docker volumes..."
        log("Restoring Docker data volumes...")
        for vol_tar in glob.glob(f"{volumes_dir}/*.tar.gz"):
            vol_name = os.path.basename(vol_tar).replace(".tar.gz", "")
            vol_dest = f"{VOL_BASE}/{vol_name}/_data"
            if os.path.isdir(vol_dest):
                log(f"Extracting volume from host path: {vol_name}...")
                run_cmd(f'tar -xzf "{vol_tar}" -C "{vol_dest}"', check=False)
            else:
                log(f"Restoring volume via docker stdin: {vol_name}")
                run_cmd_pipe_in(f'docker run --rm -i -v "{vol_name}:/voldata" alpine tar -xzf - -C /voldata', vol_tar, check=False)

    # 7. Lab sync state
    lab_json = os.path.join(source_dir, "lab_last_result.json")
    if os.path.exists(lab_json):
        sync_c = get_container("lab-result-sync")
        run_cmd_pipe_in(f'docker exec -i {sync_c} sh -c "cat > /last_result.json"', lab_json, check=False)

    # Clean unpack
    shutil.rmtree(temp_dir, ignore_errors=True)

    # 8. Apply frontend patches
    current_op["progress"] = 90
    current_op["message"] = "Applying Web UI patches..."
    apply_frontend_patches()

    # 9. Cycling services
    current_op["progress"] = 95
    current_op["message"] = "Restarting application containers..."
    log("Restarting application containers...")
    c_list = [get_container(x) for x in ["odoo-connect", "atomfeed-console", "openmrs", "openelis", "odoo"]]
    run_cmd(f"docker restart {' '.join(c_list)}", check=False)

    current_op["progress"] = 100
    current_op["message"] = f"Restore completed successfully from {os.path.basename(archive_path)}"
    log(current_op["message"])

def list_backups():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    archives = glob.glob(os.path.join(BACKUP_DIR, "bahmni_*.tar.gz"))
    archives.sort(key=os.path.getmtime, reverse=True)
    items = []
    for arc in archives:
        stat = os.stat(arc)
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        size_mb = round(stat.st_size / (1024 * 1024), 2)
        base = os.path.basename(arc)
        if "full" in base:
            b_type = "Full Backup (DB + Volumes + Modules)"
        elif "db" in base:
            b_type = "Database Only Backup"
        else:
            b_type = "Standard Backup"
        items.append({
            "name": base,
            "path": arc,
            "size_mb": size_mb,
            "modified": mtime,
            "type": b_type,
            "download_url": f"/backup-api/download/{base}"
        })
    return items

def run_async(op_type, func, *args):
    with op_lock:
        if current_op["status"] == "running":
            return False, "An operation is already in progress."
        current_op["status"] = "running"
        current_op["type"] = op_type
        current_op["message"] = f"Starting {op_type}..."
        current_op["started_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_op["completed_at"] = None
        current_op["progress"] = 5
        current_op["logs"] = []

    def worker():
        try:
            func(*args)
            with op_lock:
                current_op["status"] = "completed"
                current_op["completed_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                current_op["progress"] = 100
        except Exception as e:
            with op_lock:
                current_op["status"] = "error"
                current_op["message"] = f"Failed: {str(e)}"
                current_op["completed_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log(f"FATAL ERROR in {op_type}: {e}")

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return True, "Operation started successfully."

# ── HTTP Server Request Handler ──────────────────────────────────────────────

class BackupAPIHandler(BaseHTTPRequestHandler):
    def _send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors()
    def do_HEAD(self):
        self.do_GET(head_only=True)

    def do_GET(self, head_only=False):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        # Handle path prefix if mounted at /backup-api or /api
        path = path.replace("/backup-api", "")
        if not path:
            path = "/"

        query_params = parse_qs(parsed.query)
        download_file = None
        if path.startswith("/download/") or path.startswith("/api/download/"):
            parts = path.split("/download/")
            if len(parts) > 1 and parts[1]:
                download_file = parts[1]
        elif path in ("/download", "/api/download") and "file" in query_params:
            download_file = query_params["file"][0]

        if download_file:
            self._serve_download(download_file, head_only=head_only)
            return

        if path in ("/api/backups", "/backups"):
            data = {"backups": list_backups(), "status": current_op}
            self._send_json(200, data)
        elif path in ("/api/status", "/status"):
            self._send_json(200, current_op)
        else:
            self._send_json(404, {"error": "Endpoint not found", "path": path})

    def _serve_download(self, filename, head_only=False):
        safe_name = os.path.basename(filename.strip())
        if not safe_name or not safe_name.endswith(".tar.gz"):
            self._send_json(400, {"error": "Invalid backup archive filename"})
            return

        file_path = os.path.join(BACKUP_DIR, safe_name)
        if not os.path.isfile(file_path):
            self._send_json(404, {"error": f"Backup file not found: {safe_name}"})
            return

        try:
            file_size = os.path.getsize(file_path)
            self.send_response(200)
            self.send_header("Content-Type", "application/gzip")
            self.send_header("Content-Disposition", f'attachment; filename="{safe_name}"')
            self.send_header("Content-Length", str(file_size))
            self._send_cors()
            self.end_headers()

            if head_only:
                return

            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            log(f"Download error for {safe_name}: {e}")

    def _handle_upload(self, query_params):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            self._send_json(400, {"success": False, "error": "Content-Length header required for upload"})
            return

        content_type = self.headers.get("Content-Type", "")
        raw_name = query_params.get("filename", [""])[0] or self.headers.get("X-File-Name", "")
        do_restore = query_params.get("restore", ["false"])[0].lower() in ("true", "1", "yes") or \
                     self.headers.get("X-Restore-Now", "").lower() in ("true", "1", "yes")

        os.makedirs(BACKUP_DIR, exist_ok=True)

        if "multipart/form-data" in content_type:
            boundary = None
            for p in content_type.split(";"):
                p = p.strip()
                if p.startswith("boundary="):
                    boundary = p.split("=", 1)[1].strip('"').encode("latin1")
                    break
            if not boundary:
                self._send_json(400, {"success": False, "error": "Invalid multipart boundary"})
                return

            body_bytes = self.rfile.read(content_length)
            parts = body_bytes.split(b"--" + boundary)
            file_found = False
            for part in parts:
                if b'filename="' in part:
                    if not raw_name:
                        match = re.search(rb'filename="([^"]+)"', part)
                        if match:
                            raw_name = match.group(1).decode("utf-8", errors="replace")
                    header_end = part.find(b"\r\n\r\n")
                    if header_end != -1:
                        data = part[header_end + 4:]
                        if data.endswith(b"\r\n"):
                            data = data[:-2]
                        safe_name = os.path.basename(raw_name.strip() if raw_name else f"uploaded_backup_{int(time.time())}.tar.gz")
                        safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', safe_name)
                        if not (safe_name.endswith(".tar.gz") or safe_name.endswith(".tgz")):
                            safe_name += ".tar.gz"
                        dest_path = os.path.join(BACKUP_DIR, safe_name)
                        with open(dest_path, "wb") as f:
                            f.write(data)
                        file_found = True
                        break
            if not file_found:
                self._send_json(400, {"success": False, "error": "No file content found in multipart body"})
                return
        else:
            safe_name = os.path.basename(raw_name.strip() if raw_name else f"uploaded_backup_{int(time.time())}.tar.gz")
            safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', safe_name)
            if not (safe_name.endswith(".tar.gz") or safe_name.endswith(".tgz")):
                safe_name += ".tar.gz"
            dest_path = os.path.join(BACKUP_DIR, safe_name)
            remaining = content_length
            with open(dest_path, "wb") as f:
                while remaining > 0:
                    chunk = self.rfile.read(min(remaining, 65536))
                    if not chunk:
                        break
                    f.write(chunk)
                    remaining -= len(chunk)

        # Validate archive integrity
        try:
            with tarfile.open(dest_path, "r:*") as t:
                members = t.getnames()
                if not members:
                    raise ValueError("Archive is empty")
        except Exception as e:
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except OSError:
                    pass
            self._send_json(400, {"success": False, "error": f"Uploaded file is not a valid tar/gzip archive: {e}"})
            return

        size_mb = round(os.path.getsize(dest_path) / (1024 * 1024), 2)
        log(f"Received uploaded backup: {safe_name} ({size_mb} MB)")

        if do_restore:
            ok, msg = run_async("restore", execute_restore, safe_name)
            if not ok:
                self._send_json(409, {"success": False, "error": msg, "filename": safe_name})
                return
            self._send_json(200, {
                "success": True,
                "message": f"Archive uploaded successfully ({size_mb} MB) and restore started.",
                "filename": safe_name,
                "restoring": True
            })
        else:
            self._send_json(200, {
                "success": True,
                "message": f"Backup archive '{safe_name}' ({size_mb} MB) uploaded successfully.",
                "filename": safe_name,
                "restoring": False
            })

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/").replace("/backup-api", "")
        query_params = parse_qs(parsed.query)

        if path in ("/api/upload", "/upload"):
            self._handle_upload(query_params)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else ""
        payload = {}
        if body:
            try:
                payload = json.loads(body)
            except Exception:
                pass

        if path in ("/api/backup/full", "/backup/full"):
            ok, msg = run_async("full_backup", execute_full_backup)
            status_code = 200 if ok else 409
            self._send_json(status_code, {"success": ok, "message": msg})

        elif path in ("/api/backup/db", "/backup/db"):
            ok, msg = run_async("db_backup", execute_db_backup)
            status_code = 200 if ok else 409
            self._send_json(status_code, {"success": ok, "message": msg})

        elif path in ("/api/restore", "/restore"):
            archive_name = payload.get("archive")
            if not archive_name:
                self._send_json(400, {"success": False, "error": "Missing 'archive' in payload"})
                return
            ok, msg = run_async("restore", execute_restore, archive_name)
            status_code = 200 if ok else 409
            self._send_json(status_code, {"success": ok, "message": msg})

        else:
            self._send_json(404, {"error": "Endpoint not found", "path": path})

    def _send_json(self, code, data):
        content = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self._send_cors()
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        # Quiet standard HTTP logs to avoid cluttering
        pass

def start_server():
    server_address = ("0.0.0.0", PORT)
    httpd = ThreadingHTTPServer(server_address, BackupAPIHandler)
    log(f"Bahmni Backup Service running on http://0.0.0.0:{PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log("Server stopping...")
        httpd.server_close()

def main():
    parser = argparse.ArgumentParser(description="Bahmni Backup & Restore Tool")
    parser.add_argument("--backup-full", action="store_true", help="Run full system backup")
    parser.add_argument("--backup-db", action="store_true", help="Run database-only backup")
    parser.add_argument("--restore", type=str, help="Restore from archive filename or path")
    parser.add_argument("--list", action="store_true", help="List existing backups")
    parser.add_argument("--daemon", action="store_true", help="Run background HTTP API daemon")
    args = parser.parse_args()

    os.makedirs(BACKUP_DIR, exist_ok=True)

    if args.backup_full:
        print("[*] Starting Full System Backup...")
        arc = execute_full_backup()
        print(f"[✔] Full backup complete: {arc}")
    elif args.backup_db:
        print("[*] Starting Database-Only Backup...")
        arc = execute_db_backup()
        print(f"[✔] Database backup complete: {arc}")
    elif args.restore:
        print(f"[*] Starting Restore from: {args.restore}...")
        execute_restore(args.restore)
        print("[✔] Restore complete.")
    elif args.list:
        backups = list_backups()
        print(json.dumps(backups, indent=2))
    elif args.daemon:
        start_server()
    else:
        # Default if no arguments: start server daemon
        start_server()

if __name__ == "__main__":
    main()
