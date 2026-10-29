import urllib.request, json, time
from test_admission_register_page import simple_websocket_eval, simple_websocket_send

r = urllib.request.urlopen('http://localhost:9222/json')
target = [p for p in json.loads(r.read().decode()) if 'localhost:8186' in p.get('url', '')][0]
ws_url = target['webSocketDebuggerUrl']

print("1. Filling login credentials...")
res1 = simple_websocket_eval(ws_url, """
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
        return { submitted: true };
    }
    return { error: 'Inputs not found' };
})()
""")
print("Login submit:", res1)
time.sleep(3)

print("2. Selecting location if prompted...")
res2 = simple_websocket_eval(ws_url, """
(function() {
    var locBtns = Array.from(document.querySelectorAll('button, li, a, .location-button')).filter(function(el) {
        return el.textContent.includes('OPD') || el.textContent.includes('Delivery') || el.textContent.includes('General') || el.textContent.includes('Hospital');
    });
    if (locBtns.length > 0) {
        locBtns[0].click();
        return { clickedLocation: locBtns[0].textContent.trim() };
    }
    return { url: window.location.href };
})()
""")
print("Location step:", res2)
time.sleep(3)

print("3. Navigating to #/bedManagement...")
simple_websocket_eval(ws_url, "window.location.href = 'http://localhost:8186/bahmni/bedmanagement/#/bedManagement'")
time.sleep(4)

print("4. Inspecting Bed Management page...")
res3 = simple_websocket_eval(ws_url, """
(function() {
    var btn = document.querySelector('.btn-admitted-table-view');
    var navTabs = Array.from(document.querySelectorAll('.bed-management-nav li a')).map(function(a) { return a.textContent.trim(); });
    return {
        url: window.location.href,
        navTabs: navTabs,
        hasTableBtn: !!btn,
        tableBtnText: btn ? btn.textContent.trim() : null
    };
})()
""")
print("Bed Management Inspection:", json.dumps(res3, indent=2))
