import time
import json
from ws_utils import simple_websocket_eval, get_target_ws_url

ws_url = get_target_ws_url()

tabs = [
    ("#/home", "Patient List"),
    ("#/bedManagement", "Bed Management"),
    ("#/admissionRegister", "Admission Register"),
    ("#/referralManagement", "Referral Management"),
    ("#/bedManagement", "Bed Management (Return)")
]

results = []
for hash_target, tab_name in tabs:
    simple_websocket_eval(ws_url, f"window.location.hash = '{hash_target}';")
    time.sleep(2)
    res = simple_websocket_eval(ws_url, """
    (function() {
        var errors = Array.from(document.querySelectorAll('.dialog-error, .modal-dialog, .growl-item-error')).map(function(e) { return e.textContent.trim(); });
        var activeTab = document.querySelector('.bed-management-nav li.active a, .bed-management-nav li a.active');
        return {
            hash: window.location.hash,
            activeTab: activeTab ? activeTab.textContent.trim() : null,
            hasErrors: errors.length > 0,
            errors: errors
        };
    })()
    """)
    val = res.get('result', {}).get('result', {}).get('value', {})
    results.append({
        "target": tab_name,
        "currentHash": val.get("hash"),
        "activeTab": val.get("activeTab"),
        "hasErrors": val.get("hasErrors"),
        "errors": val.get("errors")
    })

print(json.dumps(results, indent=2))
