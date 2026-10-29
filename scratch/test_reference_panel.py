import time
import json
from ws_utils import simple_websocket_eval, simple_websocket_send, get_target_ws_url

ws_url = get_target_ws_url()

print("[1] Reloading Admission Register with ignoreCache=True...")
simple_websocket_send(ws_url, "Page.navigate", {"url": "http://localhost:8186/bahmni/bedmanagement/#/admissionRegister"})
time.sleep(1)
simple_websocket_send(ws_url, "Page.reload", {"ignoreCache": True})
time.sleep(5)

print("[2] Inspecting Reference Guide button and initial state...")
res1 = simple_websocket_eval(ws_url, """
(function() {
    var btn = document.querySelector('.btn-reference-guide');
    var container = document.querySelector('.data-source-reference-container');
    return {
        url: window.location.href,
        hasToggleBtn: !!btn,
        toggleBtnText: btn ? btn.textContent.trim() : null,
        isContainerVisible: container ? window.getComputedStyle(container).display !== 'none' : false
    };
})()
""")
print("Initial:", json.dumps(res1, indent=2))

print("[3] Clicking toggle button to open Reference Guide...")
simple_websocket_eval(ws_url, """
(function() {
    var btn = document.querySelector('.btn-reference-guide');
    if (btn) btn.click();
})()
""")
time.sleep(2)

print("[4] Inspecting opened Reference Guide...")
res2 = simple_websocket_eval(ws_url, """
(function() {
    var container = document.querySelector('.data-source-reference-container');
    var rows = document.querySelectorAll('.ref-dictionary-table tbody tr');
    var categories = Array.from(document.querySelectorAll('.ref-category-pills .pill-btn')).map(function(b) { return b.textContent.trim(); });
    var firstRow = rows.length > 0 ? Array.from(rows[0].querySelectorAll('td')).map(function(td) { return td.textContent.trim().replace(/\\s+/g, ' '); }) : [];
    
    return {
        isContainerVisible: container ? window.getComputedStyle(container).display !== 'none' : false,
        totalReferenceRows: rows.length,
        categories: categories,
        sampleFirstRow: firstRow
    };
})()
""")
print("Opened:", json.dumps(res2, indent=2))

print("[5] Testing clicking Col 10 (Diagnosis) Info Icon...")
simple_websocket_eval(ws_url, """
(function() {
    var infoIcons = document.querySelectorAll('.th-info-icon');
    // Click on 7th or 8th icon (which corresponds to Col 10 Diagnosis)
    var diagIcon = document.querySelector('.col-diag .th-info-icon');
    if (diagIcon) {
        diagIcon.click();
    }
})()
""")
time.sleep(2)

res3 = simple_websocket_eval(ws_url, """
(function() {
    var activeCard = document.querySelector('.active-col-card');
    return {
        hasActiveCard: !!activeCard,
        cardHeaderText: activeCard ? (activeCard.querySelector('.active-col-header') || {}).textContent.trim().replace(/\\s+/g, ' ') : null,
        cardDetails: activeCard ? Array.from(activeCard.querySelectorAll('.active-col-row')).map(function(r) { return r.textContent.trim().replace(/\\s+/g, ' '); }) : []
    };
})()
""")
print("Active Card Details:", json.dumps(res3, indent=2))
