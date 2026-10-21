import os
import time
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = r"c:\Users\COMPUTER\Documents\emr\user_guide_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

BASE_URL = "https://196.189.94.149"
USER = "Admin"
PASS = "Admin123"

def capture_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()

        print("[1] Navigating to Login Page...")
        page.goto(f"{BASE_URL}/bahmni/home/index.html#/login", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_login_page.png"))
        print("  -> Saved 01_login_page.png")

        # Fill credentials
        print("[2] Logging in...")
        try:
            page.fill("#username", USER)
            page.fill("#password", PASS)
            page.wait_for_timeout(1000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_login_credentials.png"))
            print("  -> Saved 02_login_credentials.png")

            # Click login button or submit
            page.click("button[type='submit']")
            page.wait_for_timeout(4000)

            # Location selection if present
            if "location" in page.url or page.locator(".location-picker, .login-location").count() > 0 or page.locator("select, button").count() > 0:
                print("[3] Location Selection...")
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_location_selection.png"))
                print("  -> Saved 03_location_selection.png")
                # Choose first available location button or select
                loc_buttons = page.locator(".location-button, .login-location button, button.btn")
                if loc_buttons.count() > 0:
                    loc_buttons.first.click()
                    page.wait_for_timeout(4000)

            # Home Dashboard
            print("[4] Home Dashboard...")
            page.goto(f"{BASE_URL}/bahmni/home/index.html#/dashboard", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_home_dashboard.png"))
            print("  -> Saved 04_home_dashboard.png")

            # Admin App
            print("[5] Admin Dashboard...")
            page.goto(f"{BASE_URL}/bahmni/admin/#/dashboard", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_admin_dashboard.png"))
            print("  -> Saved 05_admin_dashboard.png")

            # Backup & Restore App
            print("[6] Backup & Restore App...")
            page.goto(f"{BASE_URL}/bahmni/admin/#/backupRestore", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_backup_restore.png"))
            print("  -> Saved 06_backup_restore.png")

            # Registration App
            print("[7] Registration / Patient Search...")
            page.goto(f"{BASE_URL}/bahmni/registration/#/search", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "07_patient_registration.png"))
            print("  -> Saved 07_patient_registration.png")

            # Clinical App
            print("[8] Clinical App...")
            page.goto(f"{BASE_URL}/bahmni/clinical/#/default/patients", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(4000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "08_clinical_dashboard.png"))
            print("  -> Saved 08_clinical_dashboard.png")

            # InPatient / Bed Management
            print("[9] Bed Management...")
            page.goto(f"{BASE_URL}/bahmni/bedmanagement/#/home", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "09_bed_management.png"))
            print("  -> Saved 09_bed_management.png")

            # Referral Management
            print("[10] Referral Management...")
            page.goto(f"{BASE_URL}/bahmni/bedmanagement/#/referralManagement", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "10_referral_management.png"))
            print("  -> Saved 10_referral_management.png")

            # Patient Documents Upload
            print("[11] Patient Documents...")
            page.goto(f"{BASE_URL}/bahmni/document-upload/?encounterType=Patient%20Document", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "11_patient_documents.png"))
            print("  -> Saved 11_patient_documents.png")

            # Radiology Upload
            print("[12] Radiology Upload...")
            page.goto(f"{BASE_URL}/bahmni/document-upload/?encounterType=RADIOLOGY&topLevelConcept=Radiology%20Orders", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "12_radiology_upload.png"))
            print("  -> Saved 12_radiology_upload.png")

            # Reports Module
            print("[13] Reports Dashboard...")
            page.goto(f"{BASE_URL}/bahmni/reports/#/dashboard", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "13_reports_dashboard.png"))
            print("  -> Saved 13_reports_dashboard.png")

        except Exception as ex:
            print("[!] Exception during capture:", ex)

        browser.close()
        print("[✔] All screenshots captured successfully!")

if __name__ == "__main__":
    capture_all()
