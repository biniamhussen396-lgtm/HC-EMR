import urllib.request
import urllib.parse
import json
import ssl
import base64

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

auth_b64 = base64.b64encode(b"admin:Admin123").decode("ascii")
headers = {
    "Authorization": f"Basic {auth_b64}",
    "Content-Type": "application/json"
}

concept_uuid = "6092AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
base_url = f"https://localhost/openmrs/ws/rest/v1/concept/{concept_uuid}/name"

# 1. Get existing names
req = urllib.request.Request(base_url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as resp:
    data = json.loads(resp.read().decode("utf-8"))

print("Current names:")
for item in data.get("results", []):
    print(" -", item.get("display"), "uuid:", item.get("uuid"))
    display = item.get("display", "")
    name_uuid = item.get("uuid")
    # If it starts with $, void/delete it
    if display.startswith("$"):
        del_req = urllib.request.Request(f"{base_url}/{name_uuid}!purge", headers=headers, method="DELETE")
        try:
            with urllib.request.urlopen(del_req, context=ctx) as del_resp:
                print("Purged", display, del_resp.status)
        except Exception as e:
            # Try regular delete
            del_req2 = urllib.request.Request(f"{base_url}/{name_uuid}", headers=headers, method="DELETE")
            with urllib.request.urlopen(del_req2, context=ctx) as del_resp2:
                print("Deleted", display, del_resp2.status)

# 2. Add $active
add_payload = {
    "name": "$active",
    "locale": "en",
    "localePreferred": False,
    "conceptNameType": None
}
post_req = urllib.request.Request(base_url, data=json.dumps(add_payload).encode("utf-8"), headers=headers, method="POST")
with urllib.request.urlopen(post_req, context=ctx) as post_resp:
    res = json.loads(post_resp.read().decode("utf-8"))
    print("Created new name:", res.get("display"), res.get("uuid"))

# 3. Verify
with urllib.request.urlopen(urllib.request.Request(base_url, headers=headers), context=ctx) as resp:
    data2 = json.loads(resp.read().decode("utf-8"))
print("Final names:")
for item in data2.get("results", []):
    print(" -", item.get("display"), "uuid:", item.get("uuid"))
