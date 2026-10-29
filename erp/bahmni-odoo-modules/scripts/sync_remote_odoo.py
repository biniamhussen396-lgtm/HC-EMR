#!/usr/bin/env python3
"""Sync local Odoo patients and test products to remote Odoo.

Requirements:
- python3 with xmlrpc library (built‑in).
- Access to both Odoo instances via XML‑RPC.
- Remote Odoo credentials: user "bmh" and password obtained by pressing space three times on the login screen.
- Local Odoo admin credentials (default: admin / admin).

The script performs three steps:
1. Identify and delete remote‑only partners (patients) and service products (tests).
2. Export all local partners (with a non‑empty `ref`) and service products.
3. Import missing records into the remote instance, preserving key fields.

It is safe to run repeatedly – operations are idempotent.
"""
import xmlrpc.client
import sys

# ---------------------------------------------------------------------------
# Configuration – adjust if your environment differs.
# ---------------------------------------------------------------------------
LOCAL_URL = "http://localhost:8069"
REMOTE_URL = "http://192.168.10.5:8069"
LOCAL_DB = "odoo"
REMOTE_DB = "odoo"
LOCAL_USER = "admin"
LOCAL_PASSWORD = "admin"
REMOTE_USER = "bmh"
REMOTE_PASSWORD = "<press‑space‑three‑times>"  # replace with actual password

# Helper to obtain an authenticated object proxy
def get_proxy(url, db, user, pwd):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, user, pwd, {})
    if not uid:
        sys.exit(f"Authentication failed for {user}@{url}/{db}")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    return uid, models

# ---------------------------------------------------------------------------
# Step 1 – delete remote‑only records
# ---------------------------------------------------------------------------
def delete_remote_extras():
    local_uid, local_models = get_proxy(LOCAL_URL, LOCAL_DB, LOCAL_USER, LOCAL_PASSWORD)
    remote_uid, remote_models = get_proxy(REMOTE_URL, REMOTE_DB, REMOTE_USER, REMOTE_PASSWORD)

    # ----- Partners (patients) -----
    local_refs = set(
        remote_models.execute_kw(
            LOCAL_URL, LOCAL_DB, local_uid, LOCAL_PASSWORD,
            "res.partner", "search_read",
            [[("ref", "!=", False)]],
            {"fields": ["ref"]},
        )
    )
    # Extract just the ref values
    local_refs = {rec["ref"] for rec in local_refs}

    remote_partners = remote_models.execute_kw(
        REMOTE_URL, REMOTE_DB, remote_uid, REMOTE_PASSWORD,
        "res.partner", "search_read",
        [[("ref", "!=", False)]],
        {"fields": ["id", "ref"]},
    )
    to_delete = [p["id"] for p in remote_partners if p["ref"] not in local_refs]
    if to_delete:
        print(f"Deleting {len(to_delete)} remote‑only patients …")
        remote_models.execute_kw(
            REMOTE_URL, REMOTE_DB, remote_uid, REMOTE_PASSWORD,
            "res.partner", "unlink", [to_delete]
        )
    else:
        print("No remote‑only patients to delete.")

    # ----- Service products (tests) -----
    local_products = local_models.execute_kw(
        LOCAL_URL, LOCAL_DB, local_uid, LOCAL_PASSWORD,
        "product.template", "search_read",
        [[("type", "=", "service")]],
        {"fields": ["name"]},
    )
    local_names = {p["name"] for p in local_products}

    remote_products = remote_models.execute_kw(
        REMOTE_URL, REMOTE_DB, remote_uid, REMOTE_PASSWORD,
        "product.template", "search_read",
        [[("type", "=", "service")]],
        {"fields": ["id", "name"]},
    )
    prod_to_del = [p["id"] for p in remote_products if p["name"] not in local_names]
    if prod_to_del:
        print(f"Deleting {len(prod_to_del)} remote‑only test products …")
        remote_models.execute_kw(
            REMOTE_URL, REMOTE_DB, remote_uid, REMOTE_PASSWORD,
            "product.template", "unlink", [prod_to_del]
        )
    else:
        print("No remote‑only tests to delete.")

# ---------------------------------------------------------------------------
# Step 2 – export local data (patients & tests)
# ---------------------------------------------------------------------------
def export_local_data():
    uid, models = get_proxy(LOCAL_URL, LOCAL_DB, LOCAL_USER, LOCAL_PASSWORD)
    partners = models.execute_kw(
        LOCAL_URL, LOCAL_DB, uid, LOCAL_PASSWORD,
        "res.partner", "search_read",
        [[("ref", "!=", False)]],
        {"fields": ["name", "ref", "email", "phone", "street", "city", "country_id"]},
    )
    products = models.execute_kw(
        LOCAL_URL, LOCAL_DB, uid, LOCAL_PASSWORD,
        "product.template", "search_read",
        [[("type", "=", "service")]],
        {"fields": ["name", "list_price", "invoice_policy", "uom_id", "description_sale"]},
    )
    return partners, products

# ---------------------------------------------------------------------------
# Step 3 – import missing records into remote Odoo
# ---------------------------------------------------------------------------
def import_missing(partners, products):
    remote_uid, remote_models = get_proxy(REMOTE_URL, REMOTE_DB, REMOTE_USER, REMOTE_PASSWORD)

    # Existing remote refs / names for quick lookup
    remote_refs = set(
        r["ref"]
        for r in remote_models.execute_kw(
            REMOTE_URL, REMOTE_DB, remote_uid, REMOTE_PASSWORD,
            "res.partner", "search_read",
            [[("ref", "!=", False)]],
            {"fields": ["ref"]},
        )
    )
    remote_names = set(
        r["name"]
        for r in remote_models.execute_kw(
            REMOTE_URL, REMOTE_DB, remote_uid, REMOTE_PASSWORD,
            "product.template", "search_read",
            [[("type", "=", "service")]],
            {"fields": ["name"]},
        )
    )

    # ----- Partners -----
    new_partners = []
    for p in partners:
        if p["ref"] not in remote_refs:
            new_partners.append({
                "name": p["name"],
                "ref": p["ref"],
                "email": p.get("email"),
                "phone": p.get("phone"),
                "street": p.get("street"),
                "city": p.get("city"),
                "country_id": p.get("country_id"),
            })
    if new_partners:
        print(f"Creating {len(new_partners)} missing patients on remote …")
        remote_models.execute_kw(
            REMOTE_URL, REMOTE_DB, remote_uid, REMOTE_PASSWORD,
            "res.partner", "create", [new_partners]
        )
    else:
        print("All patients already present on remote.")

    # ----- Service products -----
    new_products = []
    for pr in products:
        if pr["name"] not in remote_names:
            new_products.append({
                "name": pr["name"],
                "type": "service",
                "list_price": pr.get("list_price", 0.0),
                "invoice_policy": pr.get("invoice_policy", "order"),
                "uom_id": pr.get("uom_id"),
                "description_sale": pr.get("description_sale"),
            })
    if new_products:
        print(f"Creating {len(new_products)} missing test products on remote …")
        remote_models.execute_kw(
            REMOTE_URL, REMOTE_DB, remote_uid, REMOTE_PASSWORD,
            "product.template", "create", [new_products]
        )
    else:
        print("All test products already present on remote.")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    delete_remote_extras()
    partners, products = export_local_data()
    import_missing(partners, products)
    print("Sync complete.")
