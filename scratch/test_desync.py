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

r = urllib.request.urlopen("http://localhost:9222/json")
pages = json.loads(r.read().decode())
target = [p for p in pages if "appointments" in p.get("url", "")][0]
ws_url = target["webSocketDebuggerUrl"]

code = """
(function() {
    var tr = document.querySelector('.app-list-view table tbody tr');
    var childScope = window.angular.element(tr).scope();
    var parentScope = childScope.$parent;

    // Reset selection
    parentScope.selectedAppointment = null;
    parentScope.$apply();
    var cb = tr.querySelector('.row-cb');
    cb.checked = false;

    // 1. User clicks the row
    tr.querySelectorAll('td')[2].click();
    var state1 = {
        parentSelected: parentScope.selectedAppointment ? parentScope.selectedAppointment.uuid : null,
        cbChecked: cb.checked
    };

    // 2. User clicks the checkbox
    cb.click();
    var state2 = {
        parentSelected: parentScope.selectedAppointment ? parentScope.selectedAppointment.uuid : null,
        cbChecked: cb.checked,
        fieldsetDisabled: document.querySelector('.appointment-action-btn-container').disabled
    };

    return { state1: state1, state2: state2 };
})()
"""

res = simple_websocket_eval(ws_url, code)
print("EVAL RESULT:")
print(json.dumps(res, indent=2))
