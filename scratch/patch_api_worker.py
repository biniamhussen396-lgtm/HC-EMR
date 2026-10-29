# 1. Update api_event_worker.py
with open('erp/bahmni-odoo-modules/bahmni_api_feed/models/api_event_worker.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

old_dispatch = """            elif category == "void.order":
                self._void_order(vals)
                return "Order has been voided successfully."
            else:"""

new_dispatch = """            elif category == "void.order":
                self._void_order(vals)
                return "Order has been voided successfully."
            elif category == "add.available.lab.tests":
                self._add_available_lab_tests(vals)
                return "Available lab tests added to sale order successfully."
            else:"""

assert old_dispatch in text, "old_dispatch not found"
text = text.replace(old_dispatch, new_dispatch, 1)

method_code = '''
    @api.model
    def _add_available_lab_tests(self, vals):
        """Add lab tests that have been evaluated and confirmed AVAILABLE in OpenELIS to Odoo sale order"""
        patient_ref = vals.get("patientId") or vals.get("customer_id")
        test_names = vals.get("availableTestNames", [])
        if not patient_ref or not test_names:
            return

        partner = self.env['res.partner'].search([('ref', '=', str(patient_ref))], limit=1)
        if not partner:
            try:
                import urllib.request
                import json as json_lib
                import base64
                url = f"http://openmrs:8080/openmrs/ws/rest/v1/patient?q={patient_ref}&v=full"
                req = urllib.request.Request(url)
                req.add_header('Authorization', 'Basic ' + base64.b64encode(b'admin:Admin123').decode('ascii'))
                resp = urllib.request.urlopen(req, timeout=5)
                res_data = json_lib.loads(resp.read().decode('utf-8'))
                results = res_data.get('results', [])
                p_name = str(patient_ref)
                p_uuid = None
                if results:
                    p = results[0]
                    p_name = p.get('person', {}).get('display', str(patient_ref))
                    p_uuid = p.get('uuid')
                partner = self.env['res.partner'].sudo().create({
                    'name': p_name,
                    'ref': str(patient_ref),
                    'uuid': p_uuid,
                    'customer_rank': 1
                })
            except Exception:
                partner = self.env['res.partner'].sudo().create({
                    'name': str(patient_ref),
                    'ref': str(patient_ref),
                    'customer_rank': 1
                })

        sale_order = self.env['sale.order'].search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'draft')
        ], order='id desc', limit=1)

        sale_shop = self.env['sale.shop'].search([], limit=1)
        shop_id = sale_shop.id if sale_shop else False

        if not sale_order:
            sale_order = self.env['sale.order'].sudo().create({
                'partner_id': partner.id,
                'shop_id': shop_id,
                'state': 'draft',
                'origin': 'API FEED SYNC',
            })

        for test_name in test_names:
            test_name = test_name.strip()
            if not test_name:
                continue

            existing_line = False
            for line in sale_order.order_line:
                prod_name = (line.product_id.name or '').lower()
                if test_name.lower() in prod_name or prod_name.startswith(test_name.lower()):
                    existing_line = True
                    break
            if existing_line:
                continue

            product = self.env['product.product'].search([
                ('name', 'ilike', test_name)
            ], limit=1)
            if not product:
                tmpl = self.env['product.template'].search([
                    ('name', 'ilike', test_name)
                ], limit=1)
                if tmpl and tmpl.product_variant_ids:
                    product = tmpl.product_variant_ids[0]

            if not product:
                tmpl = self.env['product.template'].sudo().create({
                    'name': test_name,
                    'type': 'service',
                    'sale_ok': True,
                    'list_price': 1.0,
                })
                product = tmpl.product_variant_ids[0]

            price_unit = product.list_price or 1.0
            if sale_order.pricelist_id:
                try:
                    price_unit = sale_order.pricelist_id._get_product_price(product, 1.0, partner)
                except Exception:
                    pass

            self.env['sale.order.line'].sudo().create({
                'order_id': sale_order.id,
                'product_id': product.id,
                'name': product.name or test_name,
                'product_uom_qty': 1.0,
                'price_unit': price_unit,
                'state': 'draft',
                'tax_id': [(5, 0, 0)],
            })
            _logger.info("Added evaluated available test [%s] to sale order %s for patient %s", test_name, sale_order.name, partner.name)
'''

text = text + "\n" + method_code

with open('erp/bahmni-odoo-modules/bahmni_api_feed/models/api_event_worker.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print("Updated api_event_worker.py successfully!")
