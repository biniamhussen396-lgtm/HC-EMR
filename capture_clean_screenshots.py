import os
import time
from playwright.sync_api import sync_playwright

OUT = r"c:\Users\COMPUTER\Documents\emr\user_guide_screenshots"
os.makedirs(OUT, exist_ok=True)
URL = "https://196.189.94.149"

pages_to_capture = [
    ("01_login_page.png", f"{URL}/bahmni/home/index.html#/login"),
    ("04_home_dashboard.png", f"{URL}/bahmni/home/index.html#/dashboard"),
    ("05_admin_dashboard.png", f"{URL}/bahmni/admin/index.html#/dashboard"),
    ("06_backup_restore.png", f"{URL}/bahmni/admin/index.html#/backupRestore"),
    ("07_registration_search.png", f"{URL}/bahmni/registration/index.html#/search"),
    ("08_registration_new.png", f"{URL}/bahmni/registration/index.html#/patient/new"),
    ("09_clinical_dashboard.png", f"{URL}/bahmni/clinical/index.html#/default/patients"),
    ("10_bed_management.png", f"{URL}/bahmni/bedmanagement/index.html#/home"),
    ("11_referral_management.png", f"{URL}/bahmni/bedmanagement/index.html#/referralManagement"),
    ("12_patient_documents.png", f"{URL}/bahmni/document-upload/?encounterType=Patient%20Document"),
    ("13_radiology_upload.png", f"{URL}/bahmni/document-upload/?encounterType=RADIOLOGY&topLevelConcept=Radiology%20Orders"),
    ("14_reports_dashboard.png", f"{URL}/bahmni/reports/index.html#/dashboard"),
]

def main():
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

        print("[*] Logging in...")
        page.goto(f"{URL}/bahmni/home/index.html#/login", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(2500)
        page.screenshot(path=os.path.join(OUT, "01_login_page.png"))

        page.fill("#username", "Admin")
        page.fill("#password", "Admin123")
        page.screenshot(path=os.path.join(OUT, "02_login_credentials.png"))
        page.keyboard.press("Enter")
        page.wait_for_timeout(4000)

        # Check location picker
        loc_btn = page.locator("button.location-button, .login-location button, button:has-text('General'), button:has-text('OPD')")
        if loc_btn.count() > 0:
            page.screenshot(path=os.path.join(OUT, "03_location_picker.png"))
            loc_btn.first.click()
            page.wait_for_timeout(3500)

        for filename, target_url in pages_to_capture[1:]:
            try:
                print(f"[*] Navigating to {filename} ({target_url})...")
                page.goto(target_url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(3000)
                out_path = os.path.join(OUT, filename)
                page.screenshot(path=out_path)
                print(f"  [OK] Saved {filename} ({os.path.getsize(out_path)} bytes)")
            except Exception as e:
                print(f"  [!] Failed {filename}: {e}")

        browser.close()
        print("[DONE] Capture finished.")

if __name__ == "__main__":
    main()
