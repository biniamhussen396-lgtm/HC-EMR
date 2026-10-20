#!/usr/bin/env python3
import argparse
import datetime
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.abspath(__file__))
UI_REL = "apps/ui/app"
CFG_REL = "config"

UI_FILES = [
    "registration/controllers/prescriptionControl.js",
    "registration/controllers/searchPatientController.js",
    "registration/services/prescriptionService.js",
    "registration/services/pharmacyIntegrationService.js",
    "registration/views/prescription.html",
    "registration/views/prescriptionLayout.html",
    "registration/views/prescriptionSearch.html",
    "registration/app.js",
    "registration/index.html",
    "registration/common/auditLogEventDetails.js",
    "styles/registration.css",
    "styles/registrationPrint.css",
    "clinical/common/views/prescriptionPrint.html",
    "clinical/consultation/controllers/latestPrescriptionPrintController.js",
    "clinical/common/services/pharmacyIntegrationService.js",
    "common/displaycontrols/prescription/directives/prescription.js",
    "common/displaycontrols/prescription/init.js",
    "common/displaycontrols/prescription/views/prescription.html",
]

CFG_FILES = [
    "openmrs/apps/registration/app.json",
    "openmrs/apps/home/extension.json",
    "masterdata/configuration/sql/update_prescription_queries.sql",
]

SQL_FILES = [
    "config/masterdata/configuration/sql/update_prescription_queries.sql",
]


def manifest():
    items = []
    for f in UI_FILES:
        items.append(os.path.join(UI_REL, f).replace("\\", "/"))
    for f in CFG_FILES:
        items.append(os.path.join(CFG_REL, f).replace("\\", "/"))
    return items


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_tool(names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    for d in [r"C:\Program Files\PuTTY", r"C:\Program Files (x86)\PuTTY", os.path.expandvars(r"%LOCALAPPDATA%\Programs\PuTTY")]:
        for n in names:
            p = os.path.join(d, n)
            if os.path.isfile(p):
                return p
    return None


class Putty:
    def __init__(self, host, port, user, password=None, key=None, timeout=180):
        self.plink = find_tool(["plink", "plink.exe"])
        self.pscp = find_tool(["pscp", "pscp.exe"])
        if not self.plink or not self.pscp:
            sys.exit("PuTTY not found. Install PuTTY (plink.exe / pscp.exe) or add them to PATH.")
        self.base = ["-ssh", "-P", str(port)]
        if key:
            self.base += ["-i", key]
        if password is not None:
            self.base += ["-pw", password]
        self.target = "%s@%s" % (user, host)
        self.timeout = timeout

    def run(self, cmd, timeout=None, batch=True, stdin=None):
        args = [self.plink] + self.base
        if batch:
            args.append("-batch")
        args += [self.target, cmd]
        return subprocess.run(
            args, input=stdin, capture_output=True, timeout=timeout or self.timeout
        )

    def prime_host_key(self):
        try:
            self.run("exit", batch=False, stdin=b"y\n", timeout=30)
        except Exception:
            pass

    def upload(self, local_path, remote_dir):
        made = self.run("mkdir -p '%s'" % remote_dir, timeout=60)
        if made.returncode != 0:
            return made
        args = [self.pscp] + self.base + ["-batch", "-r", local_path, "%s:%s" % (self.target, remote_dir)]
        return subprocess.run(args, capture_output=True, timeout=600)


def build_staging(workdir):
    payload = os.path.join(workdir, "payload")
    missing = []
    for rel in manifest():
        src = os.path.join(REPO, rel.replace("/", os.sep))
        if not os.path.isfile(src):
            missing.append(rel)
            continue
        dst = os.path.join(payload, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    for rel in SQL_FILES:
        src = os.path.join(REPO, rel.replace("/", os.sep))
        if not os.path.isfile(src):
            missing.append(rel)
    if missing:
        sys.exit("Missing source files:\n  " + "\n  ".join(missing))
    lines = []
    for rel in manifest():
        lines.append("%s\t%s" % (rel, sha256(os.path.join(payload, rel.replace("/", os.sep)))))
    with open(os.path.join(workdir, "files.tsv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return workdir


HEADER_TEMPLATE = """#!/bin/bash
set -u
APPLY_SQL={apply_sql}
SQL_FILES="{sql_files}"
RESTART={restart}
DB_DUMP={db_dump}
FULL_BACKUP={full_backup}
COMMIT_IMAGE={commit_image}
RESTORE_DB={restore_db}
BACKUP_ROOT="${{BACKUP_ROOT:-{backup_root}}}"
"""


REMOTE_SCRIPT = r'''
STAGE_DIR="$(cd "$(dirname "$0")" && pwd)"
PAYLOAD="$STAGE_DIR/payload"
LIST="$STAGE_DIR/files.tsv"
TS="$(date +%Y%m%d_%H%M%S)"
MODE=""; DC=""; WEB_CT=""; OMRS_CT=""; DB_CT=""; CFG_SRC=""; BK=""

log(){ echo "[prescription-deploy] $*"; }
fail(){ echo "[prescription-deploy][ERROR] $*" >&2; exit 9; }

detect(){
  if command -v docker >/dev/null 2>&1 && docker ps >/dev/null 2>&1; then
    DC="docker"
  elif command -v sudo >/dev/null 2>&1 && sudo -n docker ps >/dev/null 2>&1; then
    DC="sudo docker"
  fi
  if [ -n "$DC" ]; then
    MODE="docker"
    WEB_CT=$($DC ps --format '{{.Names}}' | grep -E 'bahmni-web' | head -n1)
    [ -n "$WEB_CT" ] || fail "docker is available but no bahmni-web container is running"
    OMRS_CT=$($DC ps --format '{{.Names}}' | grep -E 'openmrs' | grep -vE 'db|mysql' | head -n1)
    DB_CT=$($DC ps --format '{{.Names}}' | grep -E 'openmrs.*db|openmrsdb' | head -n1)
    CFG_SRC=$($DC inspect "$WEB_CT" --format '{{range .Mounts}}{{.Destination}} {{.Source}}{{println}}{{end}}' | awk '/bahmni_config/{print $2; exit}')
    [ -n "$CFG_SRC" ] || fail "config volume mount not found on container $WEB_CT"
  else
    MODE="rpm"
    [ -d /var/www/bahmni ] || [ -d /etc/bahmni ] || fail "no docker and no Bahmni rpm paths (/var/www/bahmni, /etc/bahmni) found"
    WEB_CT=""; OMRS_CT=""; DB_CT=""; CFG_SRC="/etc/bahmni"
  fi
  log "mode=$MODE web_container=${WEB_CT:--} openmrs_container=${OMRS_CT:--} db_container=${DB_CT:--} config_root=$CFG_SRC"
}

target_of(){
  case "$1" in
    apps/ui/app/*)
      r="${1#apps/ui/app/}"
      if [ "$MODE" = "docker" ]; then echo "/usr/local/apache2/htdocs/bahmni/$r"; else echo "/var/www/bahmni/$r"; fi ;;
    config/*)
      r="${1#config/}"
      if [ "$MODE" = "docker" ]; then echo "$CFG_SRC/$r"; else echo "/etc/bahmni/$r"; fi ;;
    *) return 1 ;;
  esac
}

hash_file(){
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}' | sed 's/^\\//'; else echo "nosum"; fi
}

copy_out(){
  fullrel="$1"; dest="$2"
  src="$PAYLOAD/$fullrel"
  case "$fullrel" in
    apps/ui/app/*)
      if [ "$MODE" = "docker" ]; then
        $DC exec "$WEB_CT" sh -c "mkdir -p '$(dirname "$dest")'" || return 1
        $DC exec -i "$WEB_CT" sh -c "cat > '$dest'" < "$src" || return 1
      else
        mkdir -p "$(dirname "$dest")" || return 1
        cp -p "$src" "$dest" || return 1
      fi ;;
    *)
      mkdir -p "$(dirname "$dest")" || return 1
      cp -p "$src" "$dest" || return 1 ;;
  esac
}

backup_one(){
  fullrel="$1"
  dest=$(target_of "$fullrel") || fail "cannot map $fullrel"
  bkdest="$BK/$fullrel"
  mkdir -p "$(dirname "$bkdest")"
  case "$fullrel" in
    apps/ui/app/*)
      if [ "$MODE" = "docker" ]; then
        if $DC exec "$WEB_CT" sh -c "test -f '$dest'" 2>/dev/null; then
          $DC exec "$WEB_CT" sh -c "cat '$dest'" > "$bkdest" || fail "backup failed for $fullrel"
        fi
      else
        [ -f "$dest" ] && cp -p "$dest" "$bkdest"
      fi ;;
    *)
      [ -f "$dest" ] && cp -p "$dest" "$bkdest" ;;
  esac
}

plan(){
  while IFS=$(printf '\t') read -r fullrel sum; do
    [ -z "$fullrel" ] && continue
    dest=$(target_of "$fullrel") || fail "cannot map $fullrel"
    state="NEW"
    case "$fullrel" in
      apps/ui/app/*)
        if [ "$MODE" = "docker" ]; then
          $DC exec "$WEB_CT" sh -c "test -f '$dest'" 2>/dev/null && state="EXISTS"
        else
          [ -f "$dest" ] && state="EXISTS"
        fi ;;
      *) [ -f "$dest" ] && state="EXISTS" ;;
    esac
    echo "PLAN $fullrel -> $dest [$state]"
  done < "$LIST"
}

do_backup(){
  BK="$BACKUP_ROOT/prescription_app_$TS"
  mkdir -p "$BK" || fail "cannot create backup dir $BK"
  log "backing up files to $BK"
  while IFS=$(printf '\t') read -r fullrel sum; do
    [ -z "$fullrel" ] && continue
    backup_one "$fullrel"
  done < "$LIST"
  if [ "$FULL_BACKUP" = "1" ]; then
    log "full backup of config + UI"
    if [ "$MODE" = "docker" ]; then
      tar -czf "$BK/full_config_backup.tar.gz" -C "$CFG_SRC" . 2>/dev/null || log "WARN: config full backup failed"
      $DC exec "$WEB_CT" sh -c "tar -czf - -C '/usr/local/apache2/htdocs/bahmni' ." > "$BK/full_ui_backup.tar.gz" 2>/dev/null || log "WARN: UI full backup failed"
    else
      tar -czf "$BK/full_config_backup.tar.gz" -C "$CFG_SRC" . 2>/dev/null || log "WARN: config full backup failed"
      tar -czf "$BK/full_ui_backup.tar.gz" -C /var/www/bahmni . 2>/dev/null || log "WARN: UI full backup failed"
    fi
  fi
  if [ "$DB_DUMP" = "1" ] && [ -n "$DB_CT" ]; then
    log "dumping openmrs database"
    $DC exec "$DB_CT" sh -c 'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --single-transaction --routines --triggers openmrs' > "$BK/openmrs_dump.sql" 2>"/tmp/rx_dump_err.$$"
    if [ -s "$BK/openmrs_dump.sql" ]; then log "db dump ok ($(wc -c < "$BK/openmrs_dump.sql") bytes)"; else log "WARN: db dump failed: $(head -c 300 "/tmp/rx_dump_err.$$")"; rm -f "$BK/openmrs_dump.sql"; fi
    rm -f "/tmp/rx_dump_err.$$"
  fi
  (cd "$BK" && find . -type f | sort | xargs -r sha256sum > backup_checksums.txt) 2>/dev/null
  echo "$TS" > "$BK/BACKUP_INFO.txt"
  echo "host=$(hostname) mode=$MODE web=$WEB_CT" >> "$BK/BACKUP_INFO.txt"
}

do_deploy(){
  count=0; bad=0
  while IFS=$(printf '\t') read -r fullrel sum; do
    [ -z "$fullrel" ] && continue
    dest=$(target_of "$fullrel") || fail "cannot map $fullrel"
    copy_out "$fullrel" "$dest" || { log "ERROR copy failed: $fullrel"; bad=$((bad+1)); continue; }
    got=""
    case "$fullrel" in
      apps/ui/app/*)
        if [ "$MODE" = "docker" ]; then got=$($DC exec "$WEB_CT" sh -c "sha256sum '$dest'" 2>/dev/null | awk '{print $1}'); else got=$(hash_file "$dest"); fi ;;
      *) got=$(hash_file "$dest") ;;
    esac
    if [ "$got" = "$sum" ]; then count=$((count+1)); else log "WARN checksum mismatch: $fullrel"; bad=$((bad+1)); fi
  done < "$LIST"
  log "deployed=$count problems=$bad"
  [ "$bad" -eq 0 ] || fail "one or more files failed verification"
}

do_sql(){
  [ -n "$DB_CT" ] || fail "no openmrs database container found"
  for f in $SQL_FILES; do
    [ -f "$PAYLOAD/$f" ] || fail "sql payload missing: $f"
    log "applying $(basename "$f")"
    $DC exec -i "$DB_CT" sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" --default-character-set=utf8mb4 openmrs' < "$PAYLOAD/$f" || fail "SQL failed: $f"
  done
}

omrs_http_code(){
  if [ "$MODE" = "docker" ] && [ -n "$OMRS_CT" ]; then
    $DC exec "$OMRS_CT" sh -c "curl -s -o /dev/null -m 5 -w '%{http_code}' http://localhost:8080/openmrs/ws/rest/v1/session" 2>/dev/null
  elif command -v curl >/dev/null 2>&1; then
    curl -s -o /dev/null -m 5 -w '%{http_code}' http://localhost:8080/openmrs/ws/rest/v1/session 2>/dev/null
  else
    echo "000"
  fi
}

wait_openmrs(){
  [ -n "$OMRS_CT" ] || { log "WARN: no openmrs container to wait for"; return 0; }
  i=0
  while [ $i -lt 60 ]; do
    code=$(omrs_http_code)
    case "$code" in
      200|401) log "OpenMRS is up (http $code)"; return 0 ;;
    esac
    if [ "$MODE" = "docker" ] && [ "$($DC inspect -f '{{.State.Running}}' "$OMRS_CT" 2>/dev/null)" != "true" ]; then
      log "WARN: openmrs container not running"; return 1
    fi
    sleep 5; i=$((i+1))
  done
  log "WARN: OpenMRS did not answer within 300s (last http code: ${code:-none})"
}

do_restart(){
  if [ "$MODE" = "docker" ]; then
    [ -n "$WEB_CT" ] && { log "restarting $WEB_CT"; $DC restart "$WEB_CT" >/dev/null; }
    if [ -n "$OMRS_CT" ]; then log "restarting $OMRS_CT"; $DC restart "$OMRS_CT" >/dev/null; wait_openmrs; fi
    if [ "$COMMIT_IMAGE" = "1" ] && [ -n "$WEB_CT" ]; then
      img=$($DC inspect -f '{{.Config.Image}}' "$WEB_CT")
      log "committing container image $img so UI files survive container recreation"
      $DC commit "$WEB_CT" "$img" >/dev/null || log "WARN: docker commit failed"
    fi
  else
    if command -v systemctl >/dev/null 2>&1; then
      systemctl restart openmrs 2>/dev/null || log "WARN: could not restart openmrs service"
      systemctl restart bahmni 2>/dev/null || true
    else
      service openmrs restart 2>/dev/null || log "WARN: could not restart openmrs service"
    fi
    wait_openmrs
  fi
}

do_rollback(){
  BK="$1"
  [ -d "$BK" ] || fail "backup dir not found: $BK"
  log "restoring files from $BK"
  count=0
  while IFS=$(printf '\t') read -r fullrel sum; do
    [ -z "$fullrel" ] && continue
    src="$BK/$fullrel"
    [ -f "$src" ] || { log "skip (was not present before): $fullrel"; continue; }
    dest=$(target_of "$fullrel") || fail "cannot map $fullrel"
    case "$fullrel" in
      apps/ui/app/*)
        if [ "$MODE" = "docker" ]; then
          $DC exec "$WEB_CT" sh -c "mkdir -p '$(dirname "$dest")'" || fail "restore failed $fullrel"
          $DC exec -i "$WEB_CT" sh -c "cat > '$dest'" < "$src" || fail "restore failed $fullrel"
        else
          mkdir -p "$(dirname "$dest")" || fail "restore failed $fullrel"
          cp -p "$src" "$dest" || fail "restore failed $fullrel"
        fi ;;
      *)
        mkdir -p "$(dirname "$dest")" || fail "restore failed $fullrel"
        cp -p "$src" "$dest" || fail "restore failed $fullrel" ;;
    esac
    count=$((count+1))
  done < "$LIST"
  log "restored=$count"
  if [ "$RESTORE_DB" = "1" ] && [ -f "$BK/openmrs_dump.sql" ]; then
    [ -n "$DB_CT" ] || fail "no db container"
    log "restoring openmrs database from dump"
    $DC exec "$DB_CT" sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" openmrs' < "$BK/openmrs_dump.sql" || fail "db restore failed"
  fi
  [ "$RESTART" = "1" ] && do_restart
  log "ROLLBACK DONE"
}

run_all(){
  do_backup
  do_deploy
  [ "$APPLY_SQL" = "1" ] && do_sql
  [ "$RESTART" = "1" ] && do_restart
  log "BACKUP_DIR=$BK"
  log "DONE"
}

cmd="${1:-run}"
detect
case "$cmd" in
  detect) log "DETECT OK" ;;
  plan) plan ;;
  run) run_all ;;
  rollback) do_rollback "${2:-}" ;;
  *) fail "unknown command: $cmd" ;;
esac
'''


def make_header(args, restore_db):
    return HEADER_TEMPLATE.format(
        apply_sql=0 if args.no_sql else 1,
        sql_files=" ".join(SQL_FILES),
        restart=0 if args.no_restart else 1,
        db_dump=0 if args.no_db_dump or args.no_sql else 1,
        full_backup=0 if args.no_full_backup else 1,
        commit_image=1 if args.commit_image else 0,
        restore_db=1 if restore_db else 0,
        backup_root=args.backup_root,
    )


def extract(out, key):
    marker = key + "="
    for line in out.splitlines():
        if marker in line:
            return line.split(marker, 1)[1].strip()
    return None


def main():
    ap = argparse.ArgumentParser(
        description="Deploy updated Prescription App from local EMR to remote Bahmni server.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--host", required=True, help="target Bahmni server IP/hostname")
    ap.add_argument("--port", type=int, default=22, help="SSH port (default 22)")
    ap.add_argument("--user", default="kphcs", help="SSH user (default kphcs)")
    ap.add_argument("--password", help="SSH password (passed to plink -pw)")
    ap.add_argument("--key", help="PPK private key file for plink -i")
    ap.add_argument("--dry-run", action="store_true", help="detect target layout and show the plan, change nothing")
    ap.add_argument("--no-sql", action="store_true", help="do not run the SQL scripts")
    ap.add_argument("--no-restart", action="store_true", help="do not restart services")
    ap.add_argument("--no-db-dump", action="store_true", help="skip the openmrs database dump")
    ap.add_argument("--no-full-backup", action="store_true", help="backup only the files being replaced, not whole config/UI trees")
    ap.add_argument("--commit-image", action="store_true", help="docker commit the web container so UI edits survive container recreation")
    ap.add_argument("--rollback", metavar="BACKUP_DIR", help="restore files (and DB dump if present) from a backup dir on the server")
    ap.add_argument("--restore-db", action="store_true", help="with --rollback, also restore openmrs_dump.sql")
    ap.add_argument("--backup-root", default="$HOME/bahmni_backups", help="backup folder on the server (default $HOME/bahmni_backups)")
    ap.add_argument("--list", action="store_true", help="print the deployed file list and exit")
    ap.add_argument("--keep-remote", action="store_true", help="keep the upload folder on the server")
    args = ap.parse_args()

    if args.list:
        for rel in manifest():
            print(rel)
        print("-- SQL --")
        for rel in SQL_FILES:
            print(rel)
        return

    items = manifest()
    print("Prescription App structure: %d files + %d SQL scripts" % (len(items), len(SQL_FILES)))

    base = tempfile.mkdtemp(prefix="rx_deploy_")
    workdir = os.path.join(base, "staging")
    os.makedirs(workdir, exist_ok=True)
    build_staging(workdir)
    remote_dir = "/tmp/rx_deploy_%s" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    p = Putty(args.host, args.port, args.user, args.password, args.key)
    p.prime_host_key()

    print("Connecting to %s@%s:%d ..." % (args.user, args.host, args.port))
    rc = p.run("echo CONNECTED", timeout=30).returncode
    if rc != 0:
        sys.exit("SSH connection failed. Check host and credentials.")

    cmd = "rollback '%s'" % args.rollback.replace("\\", "/") if args.rollback else ("plan" if args.dry_run else "run")
    header = make_header(args, args.restore_db)
    with open(os.path.join(workdir, "remote.sh"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header + REMOTE_SCRIPT)

    print("Uploading payload ...")
    up = p.upload(workdir, remote_dir)
    if up.returncode != 0:
        sys.exit("pscp upload failed: " + up.stderr.decode(errors="replace"))

    script = "%s/staging/remote.sh" % remote_dir
    print("Running remote steps: %s" % cmd)
    try:
        res = p.run("bash %s %s" % (script, cmd), timeout=1800)
    except subprocess.TimeoutExpired:
        sys.exit("remote command timed out after 30 min; check the server")
    out = (res.stdout or b"").decode(errors="replace")
    err = (res.stderr or b"").decode(errors="replace")
    sys.stdout.write(out)
    if err.strip():
        sys.stderr.write(err)

    if res.returncode != 0:
        print("\nRemote step failed (exit %d). Nothing was removed on the server." % res.returncode)
        print("Upload folder kept for inspection: %s" % remote_dir)
        sys.exit(res.returncode)

    bk = extract(out, "BACKUP_DIR")
    if bk:
        print("\nBackup saved on server: %s" % bk)
        print("Emergency rollback:")
        print("  python %s --host %s --port %d --user %s%s --rollback '%s' --restore-db"
              % (os.path.basename(__file__), args.host, args.port, args.user,
                 " --key %s" % args.key if args.key else (" --password ****" if args.password else ""), bk))
    if args.dry_run:
        print("\nDry run only - no files were changed.")

    if not args.keep_remote and res.returncode == 0:
        p.run("rm -rf %s" % remote_dir, timeout=120)
    shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    main()
