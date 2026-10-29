with open('erp/bahmni-odoo-modules/bahmni_api_feed/models/order_save_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Normalize CRLF to LF
text = text.replace('\r\n', '\n')

# 1. Auto-sync missing patient
old_cust = """        customer_ids = self.env['res.partner'].search([('ref', '=', customer_id)])
        if customer_ids:
            cus_id = customer_ids[0]"""

new_cust = """        customer_ids = self.env['res.partner'].search([('ref', '=', customer_id)])
        if not customer_ids:
            _logger.info("Patient ref %s not found in Odoo. Auto-syncing from OpenMRS...", customer_id)
            try:
                import urllib.request
                import json as json_lib
                import base64
                url = "http://openmrs:8080/openmrs/ws/rest/v1/patient?q=" + str(customer_id) + "&v=full"
                req = urllib.request.Request(url)
                req.add_header('Authorization', 'Basic ' + base64.b64encode(b'admin:Admin123').decode('ascii'))
                resp = urllib.request.urlopen(req, timeout=5)
                res_data = json_lib.loads(resp.read().decode('utf-8'))
                results = res_data.get('results', [])
                if results:
                    p = results[0]
                    p_person = p.get('person', {})
                    p_name = p_person.get('display', str(customer_id))
                    partner_vals = {
                        'name': p_name,
                        'ref': str(customer_id),
                        'uuid': p.get('uuid'),
                        'customer_rank': 1
                    }
                    new_partner = self.env['res.partner'].sudo().create(partner_vals)
                    customer_ids = self.env['res.partner'].browse([new_partner.id])
                    _logger.info("Auto-synced patient %s (%s) into Odoo res.partner ID %s", customer_id, p_name, new_partner.id)
            except Exception as e:
                _logger.warning("Could not fetch patient %s from OpenMRS: %s. Creating minimal partner.", customer_id, e)
                try:
                    new_partner = self.env['res.partner'].sudo().create({
                        'name': str(customer_id),
                        'ref': str(customer_id),
                        'customer_rank': 1
                    })
                    customer_ids = self.env['res.partner'].browse([new_partner.id])
                except Exception as e2:
                    _logger.error("Could not create fallback partner: %s", e2)

        if customer_ids:
            cus_id = customer_ids[0]"""

assert old_cust in text, 'old_cust not found'
text = text.replace(old_cust, new_cust, 1)

# 2. Add _is_test_stock_out and filter in _filter_processed_orders
old_filter = """    @api.model
    def _filter_processed_orders(self, orders):
        unprocessed_orders = []
        # sort the orders so that the revised ones appear later
        orders.sort(key=lambda order_item: 1 if order_item.get('previousOrderId', '') == '' else 2)
        for order in orders:
            if self._is_order_revised_processed(orders, order):
                continue"""

new_filter = """    @api.model
    def _is_test_stock_out(self, order):
        \"\"\"Check if order is marked as stock-out in OpenELIS stock_out_selection\"\"\"
        try:
            concept_name = (order.get('conceptName') or order.get('productName') or '').strip()
            if not concept_name:
                return False
            import psycopg2
            conn = psycopg2.connect(host='openelisdb', port=5432, dbname='clinlims', user='clinlims', password='clinlims', connect_timeout=3)
            cur = conn.cursor()
            cur.execute(\"\"\"
                SELECT id FROM stock_out_selection 
                WHERE status = 'stockout' 
                  AND (LOWER(TRIM(test_name)) = LOWER(%s) OR %s ILIKE '%%' || LOWER(TRIM(test_name)) || '%%' OR LOWER(TRIM(test_name)) ILIKE '%%' || %s || '%%')
                LIMIT 1
            \"\"\", (concept_name, concept_name.lower(), concept_name.lower()))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                _logger.info("CRITICAL BILLING PROTECTION: Test [%s] %s is marked STOCK-OUT in OpenELIS. Excluding from Odoo billing.", order.get('orderId'), concept_name)
                return True
        except Exception as e:
            _logger.warning("Error checking stock_out status for %s: %s", order.get('conceptName'), e)
        return False

    @api.model
    def _filter_processed_orders(self, orders):
        unprocessed_orders = []
        # sort the orders so that the revised ones appear later
        orders.sort(key=lambda order_item: 1 if order_item.get('previousOrderId', '') == '' else 2)
        for order in orders:
            if self._is_test_stock_out(order):
                _logger.info("CRITICAL BILLING PROTECTION: Excluding stock-out test [%s] %s from sale order processing", order.get('orderId'), order.get('conceptName'))
                continue
            if self._is_order_revised_processed(orders, order):
                continue"""

assert old_filter in text, 'old_filter not found'
text = text.replace(old_filter, new_filter, 1)

# 3. Auto-heal missing product in _get_product_ids
old_prod = """    @api.model
    def _get_product_ids(self, order):
        if order['productId']:
            prod_ids = self.env['product.product'].search([('uuid', '=', order['productId'])])
            if not prod_ids:
                #log message indicating this product/service was skipped, because it wasn’t found in Odoo.
                _logger.warning("Order Id [%s] unprocessed as [%s] %s does not exists or is inactive in master", order["orderId"], order["productId"], order['productName'])
        else:
            prod_ids = self.env['product.template'].search([('name', '=', order['conceptName'])])
        return prod_ids.ids"""

new_prod = """    @api.model
    def _get_product_ids(self, order):
        prod_ids = []
        if order.get('productId'):
            prod_ids = self.env['product.product'].search([('uuid', '=', order['productId'])])
            if not prod_ids and order.get('conceptName'):
                prod_ids = self.env['product.product'].search([('name', 'ilike', order['conceptName'])])
            if not prod_ids and order.get('conceptName'):
                tmpl = self.env['product.template'].search([('name', 'ilike', order['conceptName'])])
                if tmpl:
                    prod_ids = tmpl.product_variant_ids
        else:
            prod_ids = self.env['product.product'].search([('name', 'ilike', order.get('conceptName', ''))])
            if not prod_ids and order.get('conceptName'):
                tmpl = self.env['product.template'].search([('name', 'ilike', order['conceptName'])])
                if tmpl:
                    prod_ids = tmpl.product_variant_ids

        # Auto-create product if still not found in master
        if not prod_ids and (order.get('productId') or order.get('conceptName')):
            p_name = order.get('conceptName') or order.get('productName') or 'Lab Test'
            p_uuid = order.get('productId') or None
            _logger.info("Product [%s] %s missing in Odoo master. Auto-creating...", p_uuid, p_name)
            try:
                tmpl = self.env['product.template'].sudo().create({
                    'name': p_name,
                    'type': 'service',
                    'uuid': p_uuid,
                    'sale_ok': True,
                    'list_price': 1.0,
                })
                prod_ids = tmpl.product_variant_ids
                if p_uuid and prod_ids:
                    prod_ids.sudo().write({'uuid': p_uuid})
                _logger.info("Auto-created product %s with variant ID %s", p_name, prod_ids.ids)
            except Exception as e:
                _logger.warning("Failed to auto-create product %s: %s", p_name, e)

        return prod_ids.ids if prod_ids else []"""

assert old_prod in text, 'old_prod not found'
text = text.replace(old_prod, new_prod, 1)

with open('erp/bahmni-odoo-modules/bahmni_api_feed/models/order_save_service.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print('SUCCESS: order_save_service.py updated successfully!')
