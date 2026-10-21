import os
import time
from playwright.sync_api import sync_playwright

OUT_DIR = r"c:\Users\COMPUTER\Documents\emr\user_guide_screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

URL = "https://196.189.94.149"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1400, "height": 850}
        )
        page = context.new_page()

        print("[1] Login Page...")
        page.goto(f"{URL}/bahmni/home/index.html#/login", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(OUT_DIR, "01_login_page.png"))

        # Enter credentials
        page.fill("#username", "Admin")
        page.fill("#password", "Admin123")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(OUT_DIR, "02_login_form.png"))

        # Click location if visible or submit
        page.keyboard.press("Enter")
        page.wait_for_timeout(4000)

        # Check if location selection appeared
        loc_btns = page.locator("button.location-button, .login-location button, button:has-text('General'), button:has-text('OPD')")
        if loc_btns.count() > 0:
            print("[2] Location Picker...")
            page.screenshot(path=os.path.join(OUT_DIR, "03_location_picker.png"))
            loc_btns.first.click()
            page.wait_for_timeout(4000)

        # Home Dashboard
        print("[3] Home Dashboard...")
        page.goto(f"{URL}/bahmni/home/index.html#/dashboard", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(OUT_DIR, "04_home_dashboard.png"))

        # Admin Dashboard
        print("[4] Admin Dashboard...")
        page.goto(f"{URL}/bahmni/admin/#/dashboard", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(OUT_DIR, "05_admin_dashboard.png"))

        # Backup & Restore
        print("[5] Backup & Restore...")
        page.goto(f"{URL}/bahmni/admin/#/backupRestore", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUT_DIR, "06_backup_restore.png"))

        # Registration Search
        print("[6] Registration Search...")
        page.goto(f"{URL}/bahmni/registration/#/search", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUT_DIR, "07_patient_registration.png"))

        # Registration New Patient Form
        print("[7] Registration New Patient...")
        page.goto(f"{URL}/bahmni/registration/#/patient/new", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUT_DIR, "08_new_patient_form.png"))

        # Clinical Dashboard
        print("[8] Clinical Dashboard...")
        page.goto(f"{URL}/bahmni/clinical/#/default/patients", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUT_DIR, "09_clinical_patients.png"))

        # InPatient / Bed Management
        print("[9] Inpatient / Bed Management...")
        page.goto(f"{URL}/bahmni/bedmanagement/#/home", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUT_DIR, "10_bed_management.png"))

        # Referral Management
        print("[10] Referral Management...")
        page.goto(f"{URL}/bahmni/bedmanagement/#/referralManagement", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUT_DIR, "11_referral_management.png"))

        # Document Upload
        print("[11] Document Upload...")
        page.goto(f"{URL}/bahmni/document-upload/?encounterType=Patient%20Document", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUT_DIR, "12_patient_documents.png"))

        # Radiology Upload
        print("[12] Radiology Upload...")
        page.goto(f"{URL}/bahmni/document-upload/?encounterType=RADIOLOGY&topLevelConcept=Radiology%20Orders", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUT_DIR, "13_radiology_upload.png"))

        # Reports
        print("[13] Reports Dashboard...")
        page.goto(f"{URL}/bahmni/reports/#/dashboard", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        page.screenshot(path=os.path.join(OUT_DIR, "14_reports_dashboard.png"))

        browser.close()
        print("DONE_CAPTURING")

if __name__ == "__main__":
    run()
