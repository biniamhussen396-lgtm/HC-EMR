import time
import json
from ws_utils import simple_websocket_eval, simple_websocket_send, get_target_ws_url

ws_url = get_target_ws_url()

print("[1] Current URL check...")
status = simple_websocket_eval(ws_url, "window.location.href")
curr_url = status.get('result', {}).get('result', {}).get('value', '')
print("Current URL:", curr_url)

if 'login' in curr_url:
    print("[2] Logging in...")
    simple_websocket_eval(ws_url, """
    (function() {
        var u = document.getElementById('username');
        var p = document.getElementById('password');
        if (u && p) {
            u.value = 'admin';
            u.dispatchEvent(new Event('input', { bubbles: true }));
            p.value = 'Admin123';
            p.dispatchEvent(new Event('input', { bubbles: true }));
            var btn = document.querySelector('button[type="submit"]');
            if (btn) btn.click();
        }
    })()
    """)
    time.sleep(3)
    
    # Pick first location if prompted
    simple_websocket_eval(ws_url, """
    (function() {
        var locBtns = Array.from(document.querySelectorAll('button, li, a, .location-button')).filter(function(el) {
            return el.textContent.includes('OPD') || el.textContent.includes('Delivery') || el.textContent.includes('Hospital');
        });
        if (locBtns.length > 0) {
            locBtns[0].click();
        }
    })()
    """)
    time.sleep(3)

print("[3] Navigating directly to Bed Management...")
simple_websocket_send(ws_url, "Page.navigate", {"url": "http://localhost:8186/bahmni/bedmanagement/#/bedManagement"})
time.sleep(4)

print("[4] Inspecting Bed Management UI elements...")
res_bed = simple_websocket_eval(ws_url, """
(function() {
    var tabs = Array.from(document.querySelectorAll('.bed-management-nav li a')).map(function(a) { return a.textContent.trim(); });
    var btn = document.querySelector('.btn-admitted-table-view');
    return {
        url: window.location.href,
        tabs: tabs,
        hasAdmittedBtn: !!btn,
        admittedBtnText: btn ? btn.textContent.trim() : null
    };
})()
""")
print("Bed Management:", json.dumps(res_bed, indent=2))

print("[5] Navigating to Admission Register...")
simple_websocket_send(ws_url, "Page.navigate", {"url": "http://localhost:8186/bahmni/bedmanagement/#/admissionRegister"})
time.sleep(4)

print("[6] Inspecting Admission Register...")
res_reg = simple_websocket_eval(ws_url, """
(function() {
    var rows = document.querySelectorAll('.moh-register-table tbody tr');
    var statCards = Array.from(document.querySelectorAll('.stat-card')).map(function(c) {
        return {
            label: (c.querySelector('.stat-label') || {}).textContent,
            number: (c.querySelector('.stat-number') || {}).textContent
        };
    });
    var headers = Array.from(document.querySelectorAll('.header-group-row th, .header-cols-row th')).map(function(th) {
        return th.textContent.trim().replace(/\\s+/g, ' ');
    });
    var sampleFirstRow = rows.length > 0 ? Array.from(rows[0].querySelectorAll('td')).map(function(td) {
        return td.textContent.trim().replace(/\\s+/g, ' ');
    }) : [];

    return {
        url: window.location.href,
        rowsCount: rows.length,
        statCards: statCards,
        headersCount: headers.length,
        sampleRowCells: sampleFirstRow.slice(0, 12)
    };
})()
""")
print("Admission Register:", json.dumps(res_reg, indent=2))
