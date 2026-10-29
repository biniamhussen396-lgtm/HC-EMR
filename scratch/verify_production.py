import urllib.request
import ssl
import paramiko

# 1. Test HTTP / HTTPS serving
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base = "https://192.168.10.5"

def check_url(path, search_str):
    url = base + path
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, context=ctx, timeout=10)
        content = res.read().decode('utf-8', errors='replace')
        status = res.getcode()
        has_str = search_str in content
        print(f"[HTTP] {url} => Status {status} | Contains '{search_str}': {has_str}")
        return has_str
    except Exception as e:
        print(f"[HTTP ERR] {url} => {e}")
        return False

check_url('/bahmni/bedmanagement/index.html', 'app.js?v=2.4')
check_url('/bahmni/bedmanagement/index.html', 'httpErrorInterceptor.js?v=2.4')
check_url('/bahmni/bedmanagement/controllers/referFormPrintController.js?v=2.4', 'seniorPhysicianApprovedBy')
check_url('/bahmni/common/util/httpErrorInterceptor.js?v=2.4', '/bahmnicore/disposition/')
check_url('/bahmni/common/domain/services/dispositionService.js?v=2.4', 'ignoreErrors: true')
check_url('/bahmni/clinical/consultation/controllers/dispositionController.js', 'referralApprovedBy')

# 2. Test SQL query execution in OpenMRS DB
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.10.5', username='bmh', password='   ', timeout=15)

# Get a location uuid to test with
test_sql = """
SET @loc_uuid = (SELECT uuid FROM location LIMIT 1);
SELECT count(*) FROM global_property WHERE property = 'emrapi.sqlSearch.referralManagement';
"""
stdin, stdout, stderr = ssh.exec_command(f"echo '   ' | sudo -S docker exec -i bahmni-standard-openmrsdb-1 mysql -uroot -padminAdmin!123 openmrs -e \"{test_sql}\"")
print("\n[DB Test] Global property count:\n", stdout.read().decode('utf-8', errors='replace'))

ssh.close()
print("\n[DONE] Production verification complete.")
