import subprocess

redirect_html = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Appointment Scheduling</title>
    <link rel="shortcut icon" type="image/x-icon" href="/bahmni/favicon.ico">
    <link rel="icon" type="image/x-icon" href="/bahmni/favicon.ico">
    <link rel="shortcut icon" type="image/x-icon" href="/appointments/favicon.ico">
    <link rel="icon" type="image/x-icon" href="/appointments/favicon.ico">
    <script>
        var search = window.location.search || '';
        var hash = window.location.hash || '';
        window.location.replace('/appointments/' + search + hash);
    </script>
</head>
<body>
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; text-align: center; margin-top: 80px; color: #446565;">
        <h2>Opening Appointment Scheduling...</h2>
        <p style="margin-top: 15px; color: #777;">If not redirected automatically, <a href="/appointments/" style="color: #27AE60; font-weight: bold; text-decoration: none;">click here</a>.</p>
    </div>
</body>
</html>
"""

# Write locally to scratch/redirect_index.html
with open('scratch/redirect_index.html', 'w', encoding='utf-8') as f:
    f.write(redirect_html)

# Upload to /tmp on remote
cmd_pscp = ['pscp', '-batch', '-pw', '   ', 'scratch/redirect_index.html', 'bmh@192.168.10.5:/tmp/redirect_index.html']
subprocess.run(cmd_pscp, check=True)

# Sudo copy to /opt/emr/apps/ui/app/appointments/index.html and backup original
remote_cmd = (
    "echo '   ' | sudo -S cp /opt/emr/apps/ui/app/appointments/index.html /opt/emr/apps/ui/app/appointments/index.html.bak && "
    "echo '   ' | sudo -S cp /tmp/redirect_index.html /opt/emr/apps/ui/app/appointments/index.html && "
    "echo '   ' | sudo -S cp /opt/emr/apps/ui/app/favicon.ico /opt/emr/apps/ui/app/appointments/favicon.ico && "
    "echo '   ' | sudo -S chmod 644 /opt/emr/apps/ui/app/appointments/index.html /opt/emr/apps/ui/app/appointments/favicon.ico && "
    "echo SUCCESS"
)
cmd = ['plink', '-batch', '-ssh', '-pw', '   ', 'bmh@192.168.10.5', remote_cmd]
p = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", p.stdout)
print("STDERR:", p.stderr)
