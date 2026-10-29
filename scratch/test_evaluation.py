import urllib.request
import json
import socket
import os
import base64
import struct

def simple_websocket_eval(ws_url, expr):
    parts = ws_url.replace("ws://", "").split("/", 1)
    host, port = parts[0].split(":")
    path = "/" + parts[1]
    port = int(port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
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
        "method": "Runtime.evaluate",
        "params": {
            "expression": expr,
            "returnByValue": True,
            "awaitPromise": True
        }
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
    s.close()

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
        return json.loads(raw_msg)
    return None

r = urllib.request.urlopen('http://localhost:9222/json')
pages = json.loads(r.read().decode())
target = [p for p in pages if 'appointments' in p.get('url', '')][0]
ws_url = target['webSocketDebuggerUrl']

def fire_websocket(ws_url, expr):
    parts = ws_url.replace("ws://", "").split("/", 1)
    host, port = parts[0].split(":")
    path = "/" + parts[1]
    port = int(port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    key = base64.b64encode(os.urandom(16)).decode('utf-8')
    req = f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
    s.sendall(req.encode('utf-8'))
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = s.recv(4096)
        if not chunk: break
        resp += chunk

    payload = json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": expr}}).encode('utf-8')
    length = len(payload)
    mask = os.urandom(4)
    header = bytes([0x81, 0x80 | length]) if length <= 125 else bytes([0x81, 0x80 | 126]) + struct.pack("!H", length)
    masked = bytearray(length)
    for i in range(length): masked[i] = payload[i] ^ mask[i % 4]
    s.sendall(header + mask + bytes(masked))
    time.sleep(0.1)
    s.close()

# Reload without waiting for response
import time
fire_websocket(ws_url, "window.location.reload()")
time.sleep(4)

# Re-fetch
r = urllib.request.urlopen('http://localhost:9222/json')
pages = json.loads(r.read().decode())
target = [p for p in pages if 'appointments' in p.get('url', '')][0]
ws_url = target['webSocketDebuggerUrl']

code = """
(function() {
    var table = document.querySelector('.app-list-view table');
    var tr = table ? table.querySelector('tbody tr') : null;
    if (!tr) return { error: 'No appointments in table' };

    var childScope = window.angular ? window.angular.element(tr).scope() : null;
    var parentScope = childScope ? childScope.$parent : null;
    var cb = tr.querySelector('.row-cb');
    var activeBtn = document.getElementById('active-visit-btn');
    var fieldset = document.querySelector('.appointment-action-btn-container');

    // 1. Initial State
    var s0 = {
        cbChecked: cb ? cb.checked : null,
        parentSelected: parentScope && parentScope.selectedAppointment ? parentScope.selectedAppointment.uuid : null,
        fieldsetDisabled: fieldset ? fieldset.disabled : null,
        activeBtnDisabled: activeBtn ? activeBtn.disabled : null
    };

    // 2. Click Checkbox
    cb.click();
    var s1 = {
        cbChecked: cb.checked,
        parentSelected: parentScope && parentScope.selectedAppointment ? parentScope.selectedAppointment.uuid : null,
        fieldsetDisabled: fieldset.disabled,
        activeBtnDisabled: activeBtn.disabled,
        activeBtnText: activeBtn.textContent
    };

    // 3. Click Checkbox again (uncheck)
    cb.click();
    var s2 = {
        cbChecked: cb.checked,
        parentSelected: parentScope && parentScope.selectedAppointment ? parentScope.selectedAppointment.uuid : null,
        fieldsetDisabled: fieldset.disabled,
        activeBtnDisabled: activeBtn.disabled,
        activeBtnText: activeBtn.textContent
    };

    return { s0: s0, s1: s1, s2: s2 };
})()
"""

res = simple_websocket_eval(ws_url, code)
print("EVAL RESULT:")
print(json.dumps(res, indent=2))
