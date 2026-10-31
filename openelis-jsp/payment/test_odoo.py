import xmlrpclib
proxy = xmlrpclib.ServerProxy("http://bahmni-standard-odoo-1:8069/xmlrpc/2/common")
uid = proxy.authenticate("odoo", "admin", "admin", {})
print "UID:", uid
if uid:
    models = xmlrpclib.ServerProxy("http://bahmni-standard-odoo-1:8069/xmlrpc/2/object")
    invoices = models.execute_kw("odoo", uid, "admin", "account.move", "search_read", [[["invoice_origin", "=", "S01905"]]], {"fields": ["name", "payment_state", "state", "partner_id", "amount_total"], "limit": 5})
    print "Invoices:", invoices
