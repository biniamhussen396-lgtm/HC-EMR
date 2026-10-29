import urllib.request
import json
import time
import socket
import os
import base64
import struct

def simple_websocket_send(ws_url, method, params=None):
    parts = ws_url.replace("ws://", "").split("/", 1)
    host, port = parts[0].split(":")
    path = "/" + parts[1]
    port = int(port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
local_pages = [p for p in pages if 'localhost:8186' in p.get('url', '')]
if not local_pages:
    print("No local pages found!")
    exit(1)

target = local_pages[0]
ws_url = target['webSocketDebuggerUrl']

print("Navigating to appointments list view...")
simple_websocket_send(ws_url, "Page.navigate", {"url": "http://localhost:8186/appointments/#/home/manage/appointments/list"})
time.sleep(6)

code = """
(function() {
    var table = document.querySelector('.app-list-view table');
    var tr = table ? table.querySelector('tbody tr') : null;
    if (!tr) return { error: 'No appointments in table', html: document.body.innerHTML.slice(0, 300) };

    var childScope = window.angular ? window.angular.element(tr).scope() : null;
    var parentScope = childScope ? childScope.$parent : null;
    var cb = tr.querySelector('.row-cb');
    var activeBtn = document.getElementById('active-visit-btn');
    var fieldset = document.querySelector('.appointment-action-btn-container');

    // Initial state
    var initial = {
        hasTr: !!tr,
        hasCb: !!cb,
        cbChecked: cb ? cb.checked : false,
        activeBtnDisabled: activeBtn ? activeBtn.disabled : null,
        activeBtnText: activeBtn ? activeBtn.textContent : null,
        fieldsetDisabled: fieldset ? fieldset.disabled : null
    };

    // 1. Click checkbox to select
    cb.click();
    var afterCbClick = {
        cbChecked: cb.checked,
        parentSelected: parentScope && parentScope.selectedAppointment ? parentScope.selectedAppointment.uuid : null,
        activeBtnDisabled: activeBtn.disabled,
        activeBtnText: activeBtn.textContent,
        fieldsetDisabled: fieldset.disabled
    };

    // 2. Click checkbox again to deselect
    cb.click();
    var afterCbUncheck = {
        cbChecked: cb.checked,
        parentSelected: parentScope && parentScope.selectedAppointment ? parentScope.selectedAppointment.uuid : null,
        activeBtnDisabled: activeBtn.disabled,
        activeBtnText: activeBtn.textContent,
        fieldsetDisabled: fieldset.disabled
    };

    // 3. Click the ROW (td 2)
    var td = tr.querySelectorAll('td')[2];
    td.click();
    
    return { initial: initial, afterCbClick: afterCbClick, afterCbUncheck: afterCbUncheck };
})()
"""

res = simple_websocket_eval(ws_url, code)
print("EVAL RESULT:")
print(json.dumps(res, indent=2))
