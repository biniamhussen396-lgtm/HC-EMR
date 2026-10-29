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
local_pages = [p for p in pages if 'localhost:8186' in p.get('url', '') or 'bedmanagement' in p.get('url', '')]
target = local_pages[0]
ws_url = target['webSocketDebuggerUrl']

print("1. Reloading Bed Management with ignore cache...")
simple_websocket_send(ws_url, "Page.reload", {"ignoreCache": True})
time.sleep(3)

print("2. Navigating to #/bedManagement...")
simple_websocket_eval(ws_url, "window.location.hash = '#/bedManagement'")
time.sleep(3)

print("3. Inspecting Bed Management state and error popups...")
res = simple_websocket_eval(ws_url, """
(function() {
    var dialogs = Array.from(document.querySelectorAll('.dialog, .alert, .ng-dialog, .ui-dialog, .toast, .notify-box, .error-message-box'));
    var dialogTexts = dialogs.map(function(d) { return d.innerText; });
    var bodyText = document.body.innerText;
    var hasErrorInBody = bodyText.indexOf('There was an unexpected issue on the server') !== -1 || bodyText.indexOf('500') !== -1;
    
    var patientDetails = document.querySelector('.patient-details, .patient-info, .dashboard-patient-details');
    var bedDetails = document.querySelector('.bed-details');
    var wards = Array.from(document.querySelectorAll('.ward-list li, .ward-container, select option')).map(function(o) { return o.textContent.trim(); }).filter(Boolean);
    
    return {
        url: window.location.href,
        dialogTexts: dialogTexts,
        hasErrorInBody: hasErrorInBody,
        patientDetailsFound: !!patientDetails,
        bedDetailsFound: !!bedDetails,
        bodySnippet: bodyText.slice(0, 300)
    };
})()
""")
print("Results:", json.dumps(res, indent=2))
