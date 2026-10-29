import urllib.request
import json
import time
import socket
import base64
import struct
import os

def simple_websocket_send(ws_url, method, params=None):
    parts = ws_url.replace("ws://", "").split("/", 1)
    host, port = parts[0].split(":")
    path = "/" + parts[1]
    port = int(port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect((host, port))

    key = base64.b64encode(os.urandom(16)).decode('utf-8')
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n\r\n"
    )
    s.sendall(req.encode('utf-8'))

    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk: break
        resp += chunk

    payload = json.dumps({
        "id": 1,
        "method": method,
        "params": params or {}
    }).encode('utf-8')

    length = len(payload)
    mask = os.urandom(4)
    if length <= 125:
        header = bytes([0x81, 0x80 | length])
    elif length <= 65535:
        header = bytes([0x81, 0x80 | 126]) + struct.pack("!H", length)
    else:
        header = bytes([0x81, 0x80 | 127]) + struct.pack("!Q", length)

    masked_payload = bytearray(length)
    for i in range(length):
        masked_payload[i] = payload[i] ^ mask[i % 4]

    s.sendall(header + mask + bytes(masked_payload))

    data = s.recv(65536)
    if len(data) > 2:
        payload_len = data[1] & 0x7F
        offset = 2
        if payload_len == 126:
            payload_len = struct.unpack("!H", data[2:4])[0]
            offset = 4
        elif payload_len == 127:
            payload_len = struct.unpack("!Q", data[2:10])[0]
            offset = 10
        raw_msg = data[offset:offset+payload_len].decode('utf-8', errors='ignore')
        s.close()
        return json.loads(raw_msg)
    s.close()
    return None

def simple_websocket_eval(ws_url, expr):
    return simple_websocket_send(ws_url, "Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": True
    })

r = urllib.request.urlopen('http://localhost:9222/json')
pages = json.loads(r.read().decode())
local_pages = [p for p in pages if 'bedmanagement' in p.get('url', '')]
if not local_pages:
    print("No bedmanagement pages found!")
    exit(1)

target = local_pages[0]
ws_url = target['webSocketDebuggerUrl']

print("1. Checking current page content and tabs...")
time.sleep(2)
res1 = simple_websocket_eval(ws_url, """
(function() {
    var tabs = Array.from(document.querySelectorAll('a, button, [ui-sref]')).map(function(el) {
        return { text: el.textContent.trim(), href: el.getAttribute('href') || el.getAttribute('ui-sref') };
    }).filter(function(x) { return x.text.includes('Bed') || x.text.includes('Referral') || x.text.includes('Patient'); });
    
    var errorDialog = document.querySelector('.dialog, .alert, .ng-dialog');
    var errorText = errorDialog ? errorDialog.innerText : null;

    var referralsCount = (window.angular && document.querySelector('[ng-controller="ReferralManagementController"]')) ?
        window.angular.element(document.querySelector('[ng-controller="ReferralManagementController"]')).scope().referrals.length : null;

    return {
        tabs: tabs,
        errorText: errorText,
        referralsCount: referralsCount,
        title: document.title
    };
})()
""")
print("Initial state:", json.dumps(res1, indent=2))

print("\n2. Switching to Bed Management tab...")
simple_websocket_eval(ws_url, "window.location.hash = '#/bedManagement'")
time.sleep(2)

print("\n3. Switching back to Referral Management tab...")
simple_websocket_eval(ws_url, "window.location.hash = '#/referralManagement'")
time.sleep(2)

print("\n4. Checking state and any errors after switching back...")
res2 = simple_websocket_eval(ws_url, """
(function() {
    var errorDialog = document.querySelector('.dialog, .alert, .ng-dialog, .ui-dialog, .toast');
    var allText = document.body.innerText;
    var hasApplyFiltersError = allText.indexOf('applyFilters is not a function') !== -1;
    
    var ctrlEl = document.querySelector('[ng-controller="ReferralManagementController"]');
    var scope = (window.angular && ctrlEl) ? window.angular.element(ctrlEl).scope() : null;
    
    return {
        hasApplyFiltersError: hasApplyFiltersError,
        dialogFound: errorDialog ? errorDialog.innerText : null,
        referralsCount: scope && scope.referrals ? scope.referrals.length : null,
        filteredCount: scope && scope.filteredReferrals ? scope.filteredReferrals.length : null,
        cachedCount: (window.angular && window.angular.element(document.body).injector()) ? 
            window.angular.element(document.body).injector().get('$rootScope').cachedReferrals.length : null
    };
})()
""")
print("Result after switching back:", json.dumps(res2, indent=2))
