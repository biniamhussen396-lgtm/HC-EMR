import os
import shutil

ASSETS_DIR = r"c:\Users\COMPUTER\Documents\emr\user_guide_assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

APP_DATA_DIR = r"C:\Users\COMPUTER\.gemini\antigravity-ide\brain\fbf7d444-d0f5-4a31-b6ec-102c83b01e0a"
SHOTS_DIR = r"c:\Users\COMPUTER\Documents\emr\user_guide_screenshots"

copies = [
    # User uploaded authentic high-res screenshots from 196.189.94.149
    (os.path.join(APP_DATA_DIR, ".user_uploaded", "media_1792508800236.png"), "01_home_dashboard_bmh.png"),
    (os.path.join(APP_DATA_DIR, ".user_uploaded", "media_1792508830606.png"), "02_admin_dashboard_bmh.png"),
    (os.path.join(APP_DATA_DIR, "login_page_1792504480894.png"), "03_login_page_bmh.png"),
    (os.path.join(APP_DATA_DIR, "patient_documents_success_1792504591515.png"), "04_patient_documents_bmh.png"),
    (os.path.join(APP_DATA_DIR, "radiology_upload_success_1792504634395.png"), "05_radiology_upload_bmh.png"),
    (os.path.join(APP_DATA_DIR, ".tempmediaStorage", "media_1792504068602.png"), "06_triage_clinical_bmh.png"),
    (os.path.join(APP_DATA_DIR, ".tempmediaStorage", "media_1792504107642.png"), "07_patient_search_bmh.png"),
    (os.path.join(APP_DATA_DIR, ".tempmediaStorage", "media_1792504154540.png"), "08_registration_form_bmh.png"),
    (os.path.join(APP_DATA_DIR, ".tempmediaStorage", "media_1792504250986.png"), "09_consultation_dashboard_bmh.png"),
    (os.path.join(APP_DATA_DIR, ".tempmediaStorage", "media_1792504354037.png"), "10_orders_investigations_bmh.png"),
    (os.path.join(APP_DATA_DIR, ".tempmediaStorage", "media_1792515618653.png"), "11_bed_management_bmh.png"),
    (os.path.join(APP_DATA_DIR, ".tempmediaStorage", "media_1792515654539.png"), "12_referral_management_bmh.png"),
    (os.path.join(APP_DATA_DIR, ".tempmediaStorage", "media_1792515683413.png"), "13_referral_form_print_bmh.png"),
]

for src, dest_name in copies:
    dest = os.path.join(ASSETS_DIR, dest_name)
    if os.path.isfile(src):
        shutil.copy2(src, dest)
        print(f"[OK] Copied {dest_name} ({os.path.getsize(dest)} bytes)")
    else:
        print(f"[!] Source missing: {src}")

# Also copy newly captured backup & restore screenshot
b_res = os.path.join(SHOTS_DIR, "06_backup_restore.png")
if os.path.isfile(b_res):
    shutil.copy2(b_res, os.path.join(ASSETS_DIR, "14_backup_restore_app.png"))
    print("[OK] Copied 14_backup_restore_app.png")

print(f"Total assets in {ASSETS_DIR}: {len(os.listdir(ASSETS_DIR))}")
