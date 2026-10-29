import time
from test_bed_management_tab import simple_websocket_eval, ws_url

print('1. Switch to Referral Management tab...')
simple_websocket_eval(ws_url, "window.location.hash = '#/referralManagement'")
time.sleep(2)

print('2. Switch to Bed Management tab...')
simple_websocket_eval(ws_url, "window.location.hash = '#/bedManagement'")
time.sleep(2)

print('3. Switch to Patient List tab...')
simple_websocket_eval(ws_url, "window.location.hash = '#/home'")
time.sleep(2)

print('4. Switch back to Bed Management tab...')
simple_websocket_eval(ws_url, "window.location.hash = '#/bedManagement'")
time.sleep(2)

res = simple_websocket_eval(ws_url, """
(function() {
    var dialog = document.querySelector('.ngdialog-content, .alert-danger, .dialog');
    return {
        hash: window.location.hash,
        hasDialog: !!dialog,
        dialogText: dialog ? dialog.innerText : null
    };
})()
""")
print('Final state:', res)
