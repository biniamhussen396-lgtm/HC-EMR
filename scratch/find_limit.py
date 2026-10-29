import subprocess

plink = r'C:\Program Files\PuTTY\plink.EXE'
host = '196.189.94.149'
user = 'bmh'
pw = '   '

def run(cmd, timeout=60):
    result = subprocess.run([plink, '-batch', '-ssh', host, '-l', user, '-pw', pw, cmd],
        capture_output=True, text=True, timeout=timeout)
    return result.stdout + result.stderr

# Find the SqlSearchServiceImpl class file
print('=== Find SqlSearchServiceImpl in extracted omod ===')
print(run("find /tmp/bahmni_patch/omod_extracted -name 'SqlSearch*.class' 2>/dev/null"))
print(run("find /tmp/bahmni_patch/omod_extracted -name '*.class' | grep -i sql | head -10"))

# Extract bahmnicore-api jar and search for 200 in bytecode
print('=== Extract bahmnicore-api jar ===')
print(run(
    "mkdir -p /tmp/bahmni_patch/api_extracted && "
    "cd /tmp/bahmni_patch/api_extracted && "
    "jar xf /tmp/bahmni_patch/omod_extracted/lib/bahmnicore-api-1.2.0.jar && "
    "find . -name 'SqlSearch*.class' | head -10"
))

# Decompile the class with javap to find 200 hardcode
print('=== javap on SqlSearchServiceImpl ===')
print(run(
    "javap -c /tmp/bahmni_patch/api_extracted/org/bahmni/module/bahmnicore/service/impl/SqlSearchServiceImpl.class 2>/dev/null | grep -A2 -B2 '200\\|batchSize\\|maxResults\\|limit' | head -40"
))
