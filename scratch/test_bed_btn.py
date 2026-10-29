import time
import json
from ws_utils import simple_websocket_eval, simple_websocket_send, get_target_ws_url

ws_url = get_target_ws_url()
# Navigate via location.hash
simple_websocket_eval(ws_url, "window.location.hash = '#/bedManagement';")
time.sleep(3)

res = simple_websocket_eval(ws_url, """
(function() {
    var btn = document.querySelector('.btn-admitted-table-view');
    var header = document.querySelector('.bed-management-header');
    return {
        url: window.location.href,
        hasBtn: !!btn,
        btnText: btn ? btn.textContent.trim() : null,
        headerHtml: header ? header.innerHTML : null
    };
})()
""")
print(json.dumps(res, indent=2))
