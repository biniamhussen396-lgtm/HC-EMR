import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ASSETS_DIR = r"c:\Users\COMPUTER\Documents\emr\user_guide_assets"
OUTPUT_DOCX = r"c:\Users\COMPUTER\Documents\emr\Boru_Meda_EMR_User_Guide.docx"

doc = Document()

# Set Margins to 1 inch
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.different_first_page_header_footer = True

# Helper Colors
COLOR_NAVY = RGBColor(10, 37, 64)       # #0A2540 Primary Header
COLOR_TEAL = RGBColor(0, 121, 109)      # #00796D Bahmni Medical Teal
COLOR_DARK = RGBColor(30, 41, 59)       # #1E293B Text Dark
COLOR_MUTED = RGBColor(100, 116, 139)   # #64748B Secondary Text
COLOR_BLUE = RGBColor(37, 99, 235)      # #2563EB Accent Blue
COLOR_AMBER = RGBColor(217, 119, 6)     # #D97706 Warning/Note

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_heading_1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    return p

def add_heading_2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = COLOR_TEAL
    return p

def add_heading_3(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = COLOR_DARK
    return p

def add_p(text, bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix + ": ")
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(11)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_TEAL
    r_body = p.add_run(text)
    r_body.font.name = 'Calibri'
    r_body.font.size = Pt(11)
    r_body.font.color.rgb = COLOR_DARK
    return p

def add_bullet(bold_prefix, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    r_pre = p.add_run(bold_prefix + ": ")
    r_pre.font.name = 'Calibri'
    r_pre.font.size = Pt(11)
    r_pre.font.bold = True
    r_pre.font.color.rgb = COLOR_NAVY
    r_body = p.add_run(text)
    r_body.font.name = 'Calibri'
    r_body.font.size = Pt(11)
    r_body.font.color.rgb = COLOR_DARK
    return p

def add_callout(title, text, callout_type="info"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)

    if callout_type == "warning":
        bg_color = "FEF3C7"  # Amber light
        border_color = "D97706"
        title_color = COLOR_AMBER
    elif callout_type == "success":
        bg_color = "ECFDF5"  # Teal light
        border_color = "059669"
        title_color = COLOR_TEAL
    else:
        bg_color = "EFF6FF"  # Blue light
        border_color = "2563EB"
        title_color = COLOR_BLUE

    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    r_t = p.add_run(title.upper())
    r_t.font.name = 'Calibri'
    r_t.font.size = Pt(10)
    r_t.font.bold = True
    r_t.font.color.rgb = title_color

    p2 = cell.add_paragraph()
    p2.paragraph_format.space_after = Pt(0)
    r_b = p2.add_run(text)
    r_b.font.name = 'Calibri'
    r_b.font.size = Pt(10.5)
    r_b.font.color.rgb = COLOR_DARK

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(4)

def add_image_figure(image_filename, caption, width=Inches(6.2)):
    img_path = os.path.join(ASSETS_DIR, image_filename)
    if os.path.isfile(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run = p_img.add_run()
        run.add_picture(img_path, width=width)

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.keep_with_next = True
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = 'Calibri'
        r_cap.font.size = Pt(9.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_MUTED
    else:
        print(f"[!] Warning: Image {image_filename} not found.")

print("[*] Generating MS Word User Guide Document...")

# ── COVER PAGE ─────────────────────────────────────────────────────────────────
p_cov_pre = doc.add_paragraph()
p_cov_pre.paragraph_format.space_before = Pt(36)
p_cov_pre.paragraph_format.space_after = Pt(4)
r_gov = p_cov_pre.add_run("FEDERAL DEMOCRATIC REPUBLIC OF ETHIOPIA\nAMHARA NATIONAL REGIONAL STATE HEALTH BUREAU")
r_gov.font.name = 'Calibri'
r_gov.font.size = Pt(11)
r_gov.font.bold = True
r_gov.font.color.rgb = COLOR_MUTED

p_hosp = doc.add_paragraph()
p_hosp.paragraph_format.space_after = Pt(16)
r_hosp = p_hosp.add_run("BORU MEDA GENERAL HOSPITAL")
r_hosp.font.name = 'Calibri'
r_hosp.font.size = Pt(26)
r_hosp.font.bold = True
r_hosp.font.color.rgb = COLOR_NAVY

p_div = doc.add_paragraph()
p_div.paragraph_format.space_after = Pt(18)
r_div = p_div.add_run("━" * 48)
r_div.font.color.rgb = COLOR_TEAL

p_title = doc.add_paragraph()
p_title.paragraph_format.space_after = Pt(8)
r_title = p_title.add_run("HOSPITAL ELECTRONIC MEDICAL RECORD (EMR)\nSYSTEM USER GUIDE & OPERATIONAL MANUAL")
r_title.font.name = 'Calibri'
r_title.font.size = Pt(20)
r_title.font.bold = True
r_title.font.color.rgb = COLOR_TEAL

p_sub = doc.add_paragraph()
p_sub.paragraph_format.space_after = Pt(36)
r_sub = p_sub.add_run("Standard Operating Procedures & Clinical Workflows for Doctors, Nurses, Laboratory, Radiology, Administrative, and IT Personnel")
r_sub.font.name = 'Calibri'
r_sub.font.size = Pt(13)
r_sub.font.color.rgb = COLOR_MUTED

# Metadata Table
meta_table = doc.add_table(rows=5, cols=2)
meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
meta_data = [
    ("System Server Host", "https://196.189.94.149"),
    ("EMR Software Platform", "Bahmni Standard Edition (OpenMRS 2.x, OpenELIS, Odoo, PACS)"),
    ("Document Version", "2.1 (Production Release)"),
    ("Publication Date", "October 2026"),
    ("Responsible Authority", "Boru Meda General Hospital Health Informatics & IT Department")
]
for row_idx, (k, v) in enumerate(meta_data):
    c0 = meta_table.cell(row_idx, 0)
    c1 = meta_table.cell(row_idx, 1)
    c0.width = Inches(2.2)
    c1.width = Inches(4.3)
    set_cell_background(c0, "F1F5F9")
    set_cell_background(c1, "FFFFFF")
    set_cell_margins(c0, 60, 60, 100, 100)
    set_cell_margins(c1, 60, 60, 100, 100)

    p_k = c0.paragraphs[0]
    r_k = p_k.add_run(k)
    r_k.font.bold = True
    r_k.font.size = Pt(10)
    r_k.font.color.rgb = COLOR_NAVY

    p_v = c1.paragraphs[0]
    r_v = p_v.add_run(v)
    r_v.font.size = Pt(10)
    r_v.font.color.rgb = COLOR_DARK

doc.add_page_break()

# Setup running header and footer on following pages
body_section = doc.sections[0]
header = body_section.header
hp = header.paragraphs[0]
hp.text = "Boru Meda General Hospital  |  Bahmni EMR System User Manual (https://196.189.94.149)"
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hp.runs[0].font.size = Pt(8.5)
hp.runs[0].font.color.rgb = COLOR_MUTED

footer = body_section.footer
fp = footer.paragraphs[0]
fp.text = "Confidential  •  Boru Meda General Hospital Health Information System  •  October 2026"
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fp.runs[0].font.size = Pt(8.5)
fp.runs[0].font.color.rgb = COLOR_MUTED

# ── TABLE OF CONTENTS ──────────────────────────────────────────────────────────
add_heading_1("Table of Contents")
toc_items = [
    ("Chapter 1: System Architecture & Access Guidelines", "4"),
    ("Chapter 2: User Authentication & Security Protocols", "5"),
    ("Chapter 3: Home Dashboard Navigation & Overview", "6"),
    ("Chapter 4: Patient Registration & Demographics Management", "8"),
    ("Chapter 5: Emergency Triage & Vital Signs Recording", "10"),
    ("Chapter 6: Outpatient Clinical Consultation & Electronic Health Records", "12"),
    ("Chapter 7: Investigations, Laboratory Orders & Radiology", "14"),
    ("Chapter 8: Inpatient Ward Management, Bed Allocation & Discharge", "16"),
    ("Chapter 9: Inter-Facility Referral Management & Printable Referral Slip", "18"),
    ("Chapter 10: Digital Document Archiving & Radiology Scan Uploads", "20"),
    ("Chapter 11: System Administration & Master Data Controls", "22"),
    ("Chapter 12: Disaster Recovery, System Backups & Restoration", "24"),
    ("Appendix A: Troubleshooting & Frequently Asked Questions", "26"),
    ("Appendix B: Hospital Helpdesk & Technical Escalation Contacts", "27")
]

toc_table = doc.add_table(rows=len(toc_items), cols=2)
toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
for r_i, (t_title, t_pg) in enumerate(toc_items):
    cell_t = toc_table.cell(r_i, 0)
    cell_p = toc_table.cell(r_i, 1)
    cell_t.width = Inches(5.8)
    cell_p.width = Inches(0.7)
    set_cell_margins(cell_t, 40, 40, 60, 60)
    set_cell_margins(cell_p, 40, 40, 60, 60)

    pt = cell_t.paragraphs[0]
    rt = pt.add_run(t_title)
    rt.font.name = 'Calibri'
    rt.font.size = Pt(10.5)
    rt.font.color.rgb = COLOR_NAVY
    if "Chapter" in t_title or "Appendix" in t_title:
        rt.font.bold = True

    pp = cell_p.paragraphs[0]
    pp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    rp = pp.add_run(t_pg)
    rp.font.name = 'Calibri'
    rp.font.size = Pt(10)
    rp.font.color.rgb = COLOR_MUTED

doc.add_page_break()

# ── CHAPTER 1: SYSTEM ARCHITECTURE & ACCESS GUIDELINES ─────────────────────────
add_heading_1("Chapter 1: System Architecture & Access Guidelines")

add_p("Boru Meda General Hospital operates an enterprise-grade Electronic Medical Record (EMR) system built upon the Bahmni platform. The system coordinates patient workflows across outpatient clinics, emergency triage, inpatient wards, laboratory diagnostic services, pharmaceutical inventory, and digital imaging archives.")

add_heading_2("1.1 Network Connection & Server Address")
add_p("The EMR is hosted on the hospital's dedicated on-premises infrastructure. All authorized hospital computers, nursing workstations, clinical consultation rooms, and laboratory terminals access the EMR using standard web browsers over encrypted HTTPS:")
add_bullet("Production Server URL", "https://196.189.94.149")
add_bullet("Network Connectivity", "Workstations must be connected to the Boru Meda Hospital internal local area network (LAN) or authorized clinical Wi-Fi subnet.")
add_bullet("Supported Browsers", "Google Chrome (recommended, version 100+) or Microsoft Edge. Ensure browser zoom is maintained at 100% on standard 1366x768 or 1920x1080 monitors.")

add_heading_2("1.2 SSL Certificate Notice")
add_p("Upon connecting to https://196.189.94.149 for the first time, browsers may present a security notification regarding the hospital's internal SSL certificate. This is standard behavior for internal hospital intranet servers.")
add_callout(
    "Browser Security Step",
    "When prompted with 'Your connection is not private', click 'Advanced' and choose 'Proceed to 196.189.94.149 (unsafe)'. This establishes an encrypted SSL channel with the hospital host.",
    callout_type="info"
)

add_heading_2("1.3 Core Component Architecture")
add_p("The Bahmni EMR framework at Boru Meda General Hospital unifies multiple best-in-class open-source healthcare components into a seamless operational suite:")
add_bullet("OpenMRS (Electronic Medical Records)", "Manages patient demographics, clinical consultation notes, standardized diagnoses (ICD-10/CIEL), vital signs flowsheets, and clinical encounters.")
add_bullet("OpenELIS (Laboratory Information Management)", "Coordinates sample collection, laboratory test routing, analyzer integration, test validation, and electronic results dispatch.")
add_bullet("Odoo ERP (Billing, Inventory & Pharmacy)", "Tracks patient billing accounts, pharmaceutical stock dispensing, purchase orders, and financial reconciliation.")
add_bullet("DCM4CHEE & OHIF Viewer (PACS Digital Radiology)", "Stores diagnostic radiological imaging (X-Ray, CT Scans, Ultrasound) and provides digital DICOM viewing directly within patient charts.")
add_bullet("Bahmni Web UI & Apache Reverse Proxy", "Provides a modern, responsive single-page AngularJS interface protected behind an Apache 2.4 reverse proxy.")

add_image_figure("01_home_dashboard_bmh.png", "Figure 1.1: Boru Meda General Hospital Bahmni EMR Home Dashboard")

doc.add_page_break()

# ── CHAPTER 2: USER AUTHENTICATION & SECURITY PROTOCOLS ────────────────────────
add_heading_1("Chapter 2: User Authentication & Security Protocols")

add_p("Security and patient confidentiality are paramount in clinical informatics. Bahmni EMR enforces strict Role-Based Access Control (RBAC), ensuring healthcare providers only access functionality and patient data appropriate to their duty designation.")

add_heading_2("2.1 Logging into the EMR")
add_p("To log into the system, complete the following steps:")
add_bullet("Step 1", "Navigate to https://196.189.94.149/bahmni/home/index.html#/login in Google Chrome or Microsoft Edge.")
add_bullet("Step 2", "Enter your assigned username (e.g., Doctor, Nurse, Receptionist, or Administrator).")
add_bullet("Step 3", "Enter your secret password.")
add_bullet("Step 4", "Click the 'Login' button or press Enter on the keyboard.")

add_image_figure("03_login_page_bmh.png", "Figure 2.1: Secure Login Interface of Boru Meda General Hospital EMR")

add_heading_2("2.2 Location & Ward Session Selection")
add_p("Following credential validation, the system prompts the user to select their active clinical duty location. The selected location determines patient queues, ward visibility, and default ordering locations:")
add_bullet("Outpatient Clinics (OPD)", "Select your specific consultation room (e.g., OPD 1, Medical OPD, Surgical OPD, Pediatric OPD, Ophthalmology).")
add_bullet("Inpatient Wards", "Select the relevant admission ward (e.g., General Ward, Maternity Ward, Surgical Ward, ICU).")
add_bullet("Diagnostic Departments", "Select Laboratory, Radiology, or Pharmacy for ancillary workflows.")

add_callout(
    "Duty Rotation Notice",
    "If your assignment changes during a shift (for example, moving from OPD to Emergency Triage), logout and log in again to select your new active location.",
    callout_type="info"
)

add_heading_2("2.3 Password Security & Automatic Session Timeout")
add_p("To protect patient privacy and comply with national healthcare data governance guidelines:")
add_bullet("Never Share Credentials", "Every order, diagnosis, prescription, and triage note is digitally signed with your login ID.")
add_bullet("Inactivity Lock", "Workstations automatically lock after an inactivity threshold. Move the mouse and re-enter your password to resume.")
add_bullet("Logout at Shift End", "Always click the user avatar in the top-right corner and select 'Logout' when leaving a workstation unattended.")

doc.add_page_break()

# ── CHAPTER 3: HOME DASHBOARD NAVIGATION & OVERVIEW ────────────────────────────
add_heading_1("Chapter 3: Home Dashboard Navigation & Overview")

add_p("Upon successful authentication and location selection, the user is presented with the Bahmni Home Dashboard. The dashboard acts as a central application launcher, displaying role-appropriate tiles.")

add_heading_2("3.1 Available Hospital Applications")
add_p("The Boru Meda General Hospital EMR features twelve primary modules accessible from the home dashboard:")

# Table of Modules
mod_table = doc.add_table(rows=13, cols=2)
mod_table.alignment = WD_TABLE_ALIGNMENT.CENTER
modules_info = [
    ("Triage", "Emergency department and OPD triage assessment, vital signs capture, acuity categorization (Red/Yellow/Green)."),
    ("Registration", "Patient search, demographic registration, national ID linkage, Ethiopian calendar birthdate converter, visit creation."),
    ("Programs", "Longitudinal chronic care management programs (HIV/ART, TB, Hypertension, Diabetes, Antenatal Care)."),
    ("Clinical", "Doctor consultation dashboard, clinical notes, ICD-10 diagnosis, lab and radiology orders, disposition decisions."),
    ("InPatient", "Inpatient ward floor plans, visual bed status (Available, Occupied), bed allocation, transfers, and discharges."),
    ("Radiology Upload", "Upload digital radiological scans (X-Ray, CT, Ultrasound) and DICOM image files directly to the patient's record."),
    ("Patient Documents", "Upload paper referral letters, external lab printouts, consent forms, and scanned identity documentation."),
    ("Bed Management", "Ward bed layout administration, physical bed numbering, room setup, and ward capacity oversight."),
    ("Admin", "Hospital administrative portal for CSV bulk data operations, audit logs, order sets, and system backup/restoration."),
    ("Appointment Scheduling", "Schedule, reschedule, and track patient follow-up appointments across outpatient departments."),
    ("Reports", "Generate clinical, statistical, demographic, and financial reports for hospital management and regional health bureau."),
    ("OPD Assignment", "Assign registered patients to specific doctor consultation rooms or triage nurse queues.")
]

for r_idx, (m_name, m_desc) in enumerate(modules_info):
    c0 = mod_table.cell(r_idx + 1, 0) if r_idx > 0 else mod_table.cell(0, 0)
    c1 = mod_table.cell(r_idx + 1, 1) if r_idx > 0 else mod_table.cell(0, 1)
    if r_idx == 0:
        c0.text = "Application Module"
        c1.text = "Operational Purpose & Workflow Scope"
        set_cell_background(c0, "0A2540")
        set_cell_background(c1, "0A2540")
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        c1.paragraphs[0].runs[0].font.bold = True
        c1.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    else:
        c0.text = m_name
        c1.text = m_desc
        set_cell_background(c0, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
        set_cell_background(c1, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.color.rgb = COLOR_NAVY
        c1.paragraphs[0].runs[0].font.color.rgb = COLOR_DARK
    c0.width = Inches(2.0)
    c1.width = Inches(4.5)
    set_cell_margins(c0, 60, 60, 80, 80)
    set_cell_margins(c1, 60, 60, 80, 80)

add_heading_2("3.2 Global Header Elements")
add_p("Every page across the EMR features a standardized top header:")
add_bullet("Home Icon", "Located on the far left. Clicking the home icon returns you immediately to the main application launcher.")
add_bullet("Back Links", "Contextual navigation links allow returning to the previous screen without using browser back buttons.")
add_bullet("User & Location Indicator", "Located on the far right. Displays the logged-in username and active clinic/ward designation.")

doc.add_page_break()

# ── CHAPTER 4: PATIENT REGISTRATION & DEMOGRAPHICS ─────────────────────────────
add_heading_1("Chapter 4: Patient Registration & Demographics Management")

add_p("The Registration module is the entry point for all patient interactions at Boru Meda General Hospital. It maintains unique patient identity, historical records, and prevents duplicate medical record numbers (MRNs).")

add_heading_2("4.1 Searching for an Existing Patient")
add_p("To avoid creating duplicate medical records, always search for the patient prior to registering a new file:")
add_bullet("Step 1", "Open the 'Registration' tile from the Home Dashboard.")
add_bullet("Step 2", "In the search bar, enter the patient's Medical Record Number (MRN), Full Name, or Phone Number.")
add_bullet("Step 3", "The search results display matching patient records, showing Name, Age, Gender, Kebele, and MRN.")
add_bullet("Step 4", "Click on the patient row to view their profile, past visits, or start a new clinical encounter.")

add_image_figure("07_patient_search_bmh.png", "Figure 4.1: Patient Search Interface with Demographic Filtering")

add_heading_2("4.2 Registering a New Patient")
add_p("If the patient does not exist in the database, click the 'Create New' button to open the registration form:")
add_bullet("Personal Demographics", "Enter Given Name, Middle Name, Family Name, and Gender (Male / Female).")
add_bullet("Ethiopian Date Calendar Integration", "Enter the birthdate in Ethiopian Calendar (EC) format (Year/Month/Day). The system automatically calculates age and synchronizes with the international Gregorian date.")
add_bullet("Address Details", "Select Region (Amhara), Zone (South Wollo), Woreda (Dessie / Kombolcha / Kalu), and enter Kebele and House Number.")
add_bullet("Contact Information", "Record primary mobile phone number and secondary relative contact for critical communications.")
add_bullet("Payment & Sponsoring Entity", "Specify payment category: Paying Cash, Community-Based Health Insurance (CBHI), or Free / Exempted.")

add_image_figure("08_registration_form_bmh.png", "Figure 4.2: Comprehensive Patient Demographic Registration Form")

add_callout(
    "Data Quality Best Practice",
    "Accurate recording of Phone Number and Kebele is mandatory to support public health tracing, referral feedback, and laboratory critical value notifications.",
    callout_type="success"
)

doc.add_page_break()

# ── CHAPTER 5: EMERGENCY TRIAGE & VITAL SIGNS ──────────────────────────────────
add_heading_1("Chapter 5: Emergency Triage & Vital Signs Recording")

add_p("The Triage module allows triage officers and emergency nurses to assess incoming patients rapidly, record physiological vital signs, and assign emergency triage priorities.")

add_heading_2("5.1 Recording Physiological Vital Signs")
add_p("Upon evaluating the patient in the triage bay, record the following standard parameters:")
add_bullet("Blood Pressure", "Enter Systolic BP and Diastolic BP in mmHg (e.g., 120/80). High or low values display visual color warnings.")
add_bullet("Pulse Rate", "Record heart rate in beats per minute (bpm).")
add_bullet("Respiratory Rate", "Record breaths per minute.")
add_bullet("Body Temperature", "Record axillary or tympanic temperature in degrees Celsius (e.g., 36.8°C).")
add_bullet("Oxygen Saturation (SpO2)", "Record arterial oxygen saturation via pulse oximeter as a percentage (e.g., 98%).")
add_bullet("Oxygen Therapy Status", "If the patient is receiving supplemental oxygen, check 'On Oxygen' and specify delivery method (Nasal Cannula / Mask).")

add_image_figure("06_triage_clinical_bmh.png", "Figure 5.1: Clinical Triage & Vital Signs Entry Interface")

add_heading_2("5.2 Acuity Categorization & Queue Routing")
add_p("Assign the appropriate triage priority code based on clinical urgency:")
add_bullet("Red (Emergency / Critical)", "Immediate life threat (e.g., severe respiratory distress, shock, unconsciousness). Fast-tracks patient immediately to the resuscitation room.")
add_bullet("Yellow (Urgent)", "Potentially serious condition requiring prompt medical attention within 30 minutes.")
add_bullet("Green (Stable / Non-Urgent)", "Stable routine complaints. Routes patient to the standard outpatient clinic queue.")

add_p("Once saved, triage vital signs instantly stream to the doctor's consultation dashboard, eliminating the need to re-take basic vitals.")

doc.add_page_break()

# ── CHAPTER 6: CLINICAL CONSULTATION & EHR ─────────────────────────────────────
add_heading_1("Chapter 6: Outpatient Clinical Consultation & Electronic Health Records")

add_p("The Clinical Consultation module provides medical doctors, specialists, and health officers with a centralized electronic medical chart to document clinical observations, order diagnostics, and prescribe therapies.")

add_heading_2("6.1 Patient Clinical Dashboard")
add_p("When a clinician selects a patient from their clinic queue, the holistic clinical dashboard displays:")
add_bullet("Patient Summary Card", "Displays photo, age, gender, MRN, active allergies, and active chronic medical conditions.")
add_bullet("Vital Signs Trend", "Displays recent and historical vital signs plotted on interactive graphical trend lines.")
add_bullet("Recent Laboratory Results", "Shows completed diagnostic reports and flagged abnormal values.")
add_bullet("Past Visits & Encounters", "Provides chronological access to historical consultation notes and previous discharge summaries.")

add_image_figure("09_consultation_dashboard_bmh.png", "Figure 6.1: Doctor's Outpatient Clinical Consultation Dashboard")

add_heading_2("6.2 Documenting the Clinical Encounter")
add_p("Clinicians document clinical findings using standardized electronic forms:")
add_bullet("Chief Complaint", "Record the primary presenting complaint and duration (e.g., 'Cough x 5 days').")
add_bullet("History of Present Illness (HPI)", "Detailed clinical narrative of disease progression, associated symptoms, and previous medications.")
add_bullet("Physical Examination (P/E)", "Structured systematic exam notes: General appearance, HEENT, Respiratory, Cardiovascular, Abdomen, CNS, and Musculoskeletal.")
add_bullet("Standardized Diagnosis (ICD-10)", "Search diagnoses by typing clinical terms. The system autocompletes with standardized ICD-10 / CIEL concepts. Designate Primary vs. Secondary diagnoses.")

add_heading_2("6.3 Clinical Dispositions")
add_p("Every consultation concludes with a definitive disposition decision:")
add_bullet("Discharge / Send Home", "Patient completes outpatient care with prescribed home medications and self-care instructions.")
add_bullet("Admit to Inpatient Ward", "Initiates admission workflow, prompting bed allocation in the relevant medical or surgical ward.")
add_bullet("Follow-Up Visit", "Schedules an outpatient return visit date.")
add_bullet("Inter-Facility Referral", "Initiates transfer workflow to a specialized tertiary or regional hospital.")

doc.add_page_break()

# ── CHAPTER 7: INVESTIGATIONS, ORDERS & LAB SYNC ───────────────────────────────
add_heading_1("Chapter 7: Investigations, Laboratory Orders & Radiology")

add_p("Clinicians can order diagnostic laboratory investigations, radiological imaging, and clinical procedures electronically directly from the consultation screen.")

add_heading_2("7.1 Placing Electronic Orders")
add_p("To order investigations:")
add_bullet("Step 1", "In the patient chart, click the 'Orders' tab.")
add_bullet("Step 2", "In the search bar, type the test name (e.g., 'Complete Blood Count', 'Serum Creatinine', 'Chest X-Ray').")
add_bullet("Step 3", "Select the test to add it to the pending order tray.")
add_bullet("Step 4", "Specify clinical indication notes and urgency status (Routine vs. STAT Emergency).")
add_bullet("Step 5", "Click 'Save' to transmit the orders electronically.")

add_image_figure("10_orders_investigations_bmh.png", "Figure 7.1: Electronic Investigation & Order Selection Interface")

add_heading_2("7.2 Order Templates for Clinical Bundles")
add_p("To optimize clinical time, clinicians can utilize pre-configured Order Templates:")
add_bullet("Antenatal Profile", "One-click ordering of Blood Group & Rh, Hemoglobin, VDRL, HBsAg, HIV, and Urinalysis.")
add_bullet("Diabetic Monitoring Bundle", "Fasting Blood Sugar (FBS), HbA1c, Renal Function Tests (RFT), and Lipid Profile.")
add_bullet("Acute Trauma Workup", "Crossmatch, CBC, Focused Assessment with Sonography for Trauma (FAST), and Extremity Radiographs.")

add_heading_2("7.3 OpenELIS Laboratory Integration")
add_p("Orders placed in Bahmni synchronize automatically with the OpenELIS laboratory database. When lab technologists perform the tests and validate results in OpenELIS, the verified numerical and qualitative results stream back into the Bahmni patient chart in real time.")

doc.add_page_break()

# ── CHAPTER 8: INPATIENT WARD & BED MANAGEMENT ─────────────────────────────────
add_heading_1("Chapter 8: Inpatient Ward Management, Bed Allocation & Discharge")

add_p("The InPatient and Bed Management modules provide nursing supervisors and ward staff with visual floor plans of all hospital wards, tracking real-time bed occupancy, admissions, transfers, and discharges.")

add_heading_2("8.1 Visual Ward Map & Bed Status")
add_p("The Bed Management interface represents hospital rooms and beds visually:")
add_bullet("Green Beds (Available)", "Cleaned and sanitized beds ready for immediate patient admission.")
add_bullet("Blue Beds (Occupied)", "Currently occupied by an admitted patient. Displays patient name, MRN, and admission duration.")
add_bullet("Gray Beds (Maintenance)", "Temporarily taken out of service for disinfection, mechanical repair, or isolation reservation.")

add_image_figure("11_bed_management_bmh.png", "Figure 8.1: Real-Time Inpatient Ward Floor Plan & Bed Allocation")

add_heading_2("8.2 Admitting a Patient to a Bed")
add_p("To allocate a bed to an admitted patient:")
add_bullet("Step 1", "Open 'InPatient' from the Home Dashboard.")
add_bullet("Step 2", "Select the designated ward (e.g., Surgical Ward).")
add_bullet("Step 3", "Click on any vacant (Green) bed.")
add_bullet("Step 4", "Select the admitted patient from the pending admission queue.")
add_bullet("Step 5", "Confirm bed allocation. The bed status immediately updates to Blue across all hospital terminals.")

add_heading_2("8.3 Inter-Ward Transfers & Clinical Discharge")
add_p("When patient care requirements evolve:")
add_bullet("Bed Transfer", "Click on the occupied bed, select 'Transfer', and choose the destination bed or ward (e.g., transferring from ICU to General Medical Ward).")
add_bullet("Discharge Processing", "When the physician approves discharge, click 'Discharge Patient'. This finalizes inpatient clinical care, prompts billing reconciliation in Odoo, and frees the bed for the next patient.")

doc.add_page_break()

# ── CHAPTER 9: REFERRAL MANAGEMENT & PRINTABLE REFERRAL SLIP ───────────────────
add_heading_1("Chapter 9: Inter-Facility Referral Management & Printable Referral Slip")

add_p("When a patient requires specialized tertiary care or diagnostic capabilities beyond the scope of Boru Meda General Hospital, clinicians initiate the formal inter-facility referral workflow.")

add_heading_2("9.1 Documenting the Referral Disposition")
add_p("In the clinical consultation window, select the 'Refer Patient' disposition. The system prompts for comprehensive transfer documentation:")
add_bullet("Receiving Facility", "Select or type the destination hospital (e.g., Dessie Comprehensive Specialized Hospital, Felege Hiwot Hospital, Tikur Anbessa Specialized Hospital).")
add_bullet("Receiving Department", "Specify the target specialty (e.g., Neurosurgery, Oncology, Cardiology, Neonatal ICU).")
add_bullet("Patient Condition at Referral", "Classify clinical state: Critical, Emergency, or Stable.")
add_bullet("Clinical Summary & Reason for Referral", "Document detailed justification (e.g., 'Requires urgent neurosurgical intervention', 'CT Angiography not available locally').")
add_bullet("Treatments Given", "Itemize all emergency medications, IV fluids, and stabilization therapies administered prior to transfer.")
add_bullet("Transport & Escort Logistics", "Check whether the patient requires ambulance dispatch and accompanying medical escort personnel.")

add_image_figure("12_referral_management_bmh.png", "Figure 9.1: Referral Queue & Patient Transfer Tracking Interface")

add_heading_2("9.2 Synchronized Facility Branding & Printable Referral Slip")
add_p("The system features a standardized A4 Patient Referral Slip that automatically formats all clinical, vital signs, and diagnostic data into an official printed document:")
add_bullet("Synchronized Facility Branding", "The header dynamically pulls the hospital name ('BORU MEDA GENERAL HOSPITAL') and official logo from the central system configuration (`whiteLabel.json`), ensuring consistent institutional branding.")
add_bullet("Standard Ministry Format", "Features official regional health bureau headers, dual Ethiopian/Gregorian dates, vitals grid, lab results, and referring doctor signature lines.")
add_bullet("One-Click Printing", "Click the 'Print Referral Form' button to print clean physical slips for ambulance handoff.")

add_image_figure("13_referral_form_print_bmh.png", "Figure 9.2: Standardized Official Patient Referral Slip with Synchronized Hospital Branding")

doc.add_page_break()

# ── CHAPTER 10: DIGITAL DOCUMENT & RADIOLOGY SCAN UPLOADS ──────────────────────
add_heading_1("Chapter 10: Digital Document Archiving & Radiology Scan Uploads")

add_p("To eliminate paper record loss and maintain a complete longitudinal health record, the Bahmni EMR features dedicated digital archiving tools for patient documents and diagnostic imaging scans.")

add_heading_2("10.1 Uploading Patient Documents")
add_p("The Patient Documents module allows scanning and attaching physical documents to a patient's electronic file:")
add_bullet("Supported Documents", "Paper referral slips from health centers, external laboratory sheets, national identity cards, legal consent forms, and previous discharge summaries.")
add_bullet("File Formats", "Accepts PDF documents, high-resolution JPEG images, and PNG scans up to 50MB per file.")
add_bullet("Step-by-Step", "Open 'Patient Documents' from Home Dashboard > Search patient > Choose file from computer > Add description title > Click 'Upload'.")

add_image_figure("04_patient_documents_bmh.png", "Figure 10.1: Digital Patient Documents Archiving & Upload Interface")

add_heading_2("10.2 Radiology Scans & Imaging Uploads")
add_p("The Radiology Upload module provides dedicated handling for diagnostic imaging files:")
add_bullet("Diagnostic Modalities", "Upload Plain Radiographs (X-Ray), Computed Tomography (CT), Magnetic Resonance Imaging (MRI), and Ultrasound scans.")
add_bullet("Instant Clinical Accessibility", "Uploaded images attach directly to the patient's radiology encounter, enabling clinicians to inspect scans directly within the consultation chart.")
add_bullet("Encrypted Volume Storage", "All imaging data is securely stored on dedicated Docker volumes (`bahmni-document-images`), safeguarded by automated daily backups.")

add_image_figure("05_radiology_upload_bmh.png", "Figure 10.2: Radiology Scan & Diagnostic Image Upload Portal")

doc.add_page_break()

# ── CHAPTER 11: SYSTEM ADMINISTRATION & MASTER DATA CONTROLS ───────────────────
add_heading_1("Chapter 11: System Administration & Master Data Controls")

add_p("The Admin portal provides hospital system administrators, health informatics officers, and medical directors with powerful governance, auditing, and configuration tools.")

add_image_figure("02_admin_dashboard_bmh.png", "Figure 11.1: Boru Meda General Hospital System Administration Dashboard")

add_heading_2("11.1 Core Administrative Tools")
add_bullet("CSV Bulk Upload", "Batch import patient demographic cohorts, clinical concept dictionaries (ICD-10/CIEL), and pharmaceutical formulary items via structured CSV templates.")
add_bullet("CSV Export", "Export clinical cohorts, disease registries, and operational hospital metrics for regional health bureau statistical reporting.")
add_bullet("Audit Log Inspector", "Inspect timestamped user activity trails. Tracks patient record access, prescription modifications, user logins, and administrative changes.")
add_bullet("Order Set Management", "Design and modify clinical order sets, custom drug protocols, and standardized investigation bundles.")
add_bullet("Bed Configuration", "Add new hospital wards, renumber beds, and update bed availability settings as physical capacity expands.")

doc.add_page_break()

# ── CHAPTER 12: DISASTER RECOVERY & SYSTEM BACKUPS ──────────────────────────────
add_heading_1("Chapter 12: Disaster Recovery, System Backups & Restoration")

add_p("Data integrity and high availability are vital to hospital operations. The newly integrated Backup & Restore module provides automated disaster recovery capabilities directly within the EMR Admin portal.")

add_image_figure("14_backup_restore_app.png", "Figure 12.1: Integrated System Backup & Disaster Recovery Dashboard")

add_heading_2("12.1 Backup Options Explained")
add_p("The system provides two distinct backup procedures tailored for operational agility:")
add_bullet("Full System Backup (Disaster Recovery)", "Archives the entire hospital server environment: All five databases (OpenMRS, OpenELIS, Odoo, Reports, PACS), 11 Docker data volumes (patient documents, radiology scans, clinical forms, lab results), and application configuration trees. Recommended weekly.")
add_bullet("Database-Only Backup (Fast Daily Dump)", "Generates a high-speed SQL archive of all relational databases: OpenMRS MySQL, OpenELIS ClinLIMS PostgreSQL, Odoo PostgreSQL, Reports MySQL, and PACS PostgreSQL. Creates a 520MB archive in approximately 4 minutes without disrupting clinical users.")

add_heading_2("12.2 Executing a Backup via the Web UI")
add_bullet("Step 1", "Log in as an Administrator and navigate to 'Admin' > 'Backup & Restore'.")
add_bullet("Step 2", "Click 'Run Full Backup Now' or 'Run Database Backup Now'.")
add_bullet("Step 3", "The live progress bar activates immediately, and the activity terminal streams real-time database dumping logs.")
add_bullet("Step 4", "Upon completion, the newly generated `.tar.gz` archive appears in the available backups table with exact file size and timestamp.")

add_heading_2("12.3 Performing a Disaster Recovery Restore")
add_callout(
    "Critical Restoration Warning",
    "Restoring an archive will overwrite current database records with the backed-up data and restart application containers. Only perform restoration during scheduled maintenance or following hardware failure.",
    callout_type="warning"
)
add_p("To restore from an archive:")
add_bullet("Step 1", "Locate the desired backup in the archives table.")
add_bullet("Step 2", "Click the orange 'Restore' button.")
add_bullet("Step 3", "Review the red confirmation dialog and click 'Yes, Restore System'.")
add_bullet("Step 4", "The service unpacks the archive, drops and recreates databases, extracts data volumes, automatically re-applies frontend null-safety patches, and cycles application containers cleanly.")

add_heading_2("12.4 Command-Line Interface (CLI)")
add_p("System administrators can also execute backups and restores directly on the Linux server terminal:")
add_bullet("Full Backup CLI", "python3 /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py --backup-full")
add_bullet("Database Backup CLI", "python3 /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py --backup-db")
add_bullet("List Backups CLI", "python3 /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py --list")
add_bullet("Restore Archive CLI", "python3 /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py --restore <filename.tar.gz>")

doc.add_page_break()

# ── APPENDIX A & B: TROUBLESHOOTING & CONTACTS ─────────────────────────────────
add_heading_1("Appendix A: Troubleshooting & Frequently Asked Questions")

add_bullet("Cannot Connect to Server", "Verify workstation ethernet cable. Ensure IP address is configured on the hospital subnet (196.189.94.x). Verify server is running.")
add_bullet("Browser Displays 'Page Not Found' (404)", "Clear browser cache (Ctrl + Shift + Delete) and reload the page. Single-page applications require refreshed assets following updates.")
add_bullet("Forgot Password / Account Locked", "Contact the Hospital IT Department. IT officers can unlock accounts and reset passwords via OpenMRS Admin console.")
add_bullet("Lab Orders Not Appearing in OpenELIS", "Ensure the lab result synchronization service (`lab-result-sync`) is running. Check network connectivity between OpenMRS and OpenELIS containers.")
add_bullet("Printer Not Responding", "Verify local USB or network printer connection. When printing referral slips, ensure print layout is set to 'A4' with 'Background graphics' enabled in browser print dialog.")

add_heading_1("Appendix B: Hospital Helpdesk & Technical Contacts")

contact_table = doc.add_table(rows=5, cols=3)
contact_table.alignment = WD_TABLE_ALIGNMENT.CENTER
contact_data = [
    ("Department / Role", "Contact Person", "Phone / Extension"),
    ("Hospital IT & Health Informatics", "EMR System Administrator", "Ext. 101 / +251 33 241 50 06"),
    ("Medical Director Office", "Clinical Quality Team", "Ext. 102"),
    ("Hospital Liaison & Referral Desk", "Liaison Officer", "Ext. 105"),
    ("HMIS & Statistical Department", "Health Information Specialist", "Ext. 108")
]

for r_i, (c_dep, c_per, c_ph) in enumerate(contact_data):
    for c_i, val in enumerate([c_dep, c_per, c_ph]):
        cell = contact_table.cell(r_i, c_i)
        cell.width = Inches(2.1)
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]
        r = p.add_run(val)
        if r_i == 0:
            set_cell_background(cell, "0A2540")
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        else:
            set_cell_background(cell, "F8FAFC" if r_i % 2 == 1 else "FFFFFF")
            r.font.color.rgb = COLOR_DARK
            if c_i == 0:
                r.font.bold = True

doc.save(OUTPUT_DOCX)
print(f"[OK] Word document saved: {OUTPUT_DOCX} ({os.path.getsize(OUTPUT_DOCX)} bytes)")
