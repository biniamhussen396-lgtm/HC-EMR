import subprocess

for src, dst in [
    (r'c:\Users\COMPUTER\Documents\emr\apps\ui\app\admin\index.html', '/tmp/admin_index.html'),
    (r'c:\Users\COMPUTER\Documents\emr\apps\ui\app\orders\index.html', '/tmp/orders_index.html'),
]:
    subprocess.run(['pscp', '-batch', '-pw', '   ', src, f'bmh@192.168.10.5:{dst}'], check=True)

cmd = 'cp /tmp/admin_index.html /opt/emr/apps/ui/app/admin/index.html && cp /tmp/orders_index.html /opt/emr/apps/ui/app/orders/index.html && chmod 644 /opt/emr/apps/ui/app/admin/index.html /opt/emr/apps/ui/app/orders/index.html && rm -f /tmp/*_index.html'
wrapped = f"echo '   ' | sudo -S bash -c {subprocess.list2cmdline([cmd])}"

subprocess.run([
    'plink', '-batch', '-ssh', '-pw', '   ', 'bmh@192.168.10.5', wrapped
], check=True)
print('INDEX_HTML_SYNCED_OK')
