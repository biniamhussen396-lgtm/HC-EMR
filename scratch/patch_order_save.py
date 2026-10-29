with open('erp/bahmni-odoo-modules/bahmni_api_feed/models/order_save_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

old_filter_block = """    @api.model
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

new_filter_block = """    @api.model
    def _is_lab_test_eligible_for_billing(self, order):
        \"\"\"
        Check if a lab test has been evaluated and confirmed AVAILABLE by OpenELIS.
        Tests that are stock-out, pending evaluation, or not yet evaluated by OpenELIS must NOT reach Odoo.
        \"\"\"
        concept_name = (order.get('conceptName') or order.get('productName') or '').strip()
        if not concept_name:
            return False
        try:
            import psycopg2
            conn = psycopg2.connect(host='openelisdb', port=5432, dbname='clinlims', user='clinlims', password='clinlims', connect_timeout=3)
            cur = conn.cursor()
            cur.execute(\"\"\"
                SELECT status FROM stock_out_selection 
                WHERE (LOWER(TRIM(test_name)) = LOWER(%s) OR %s ILIKE '%%' || LOWER(TRIM(test_name)) || '%%' OR LOWER(TRIM(test_name)) ILIKE '%%' || %s || '%%')
                ORDER BY id DESC LIMIT 1
            \"\"\", (concept_name, concept_name.lower(), concept_name.lower()))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                _logger.info("HOLDING BILLING: Lab order [%s] %s has NOT been evaluated by OpenELIS yet. Excluding from Odoo billing.", order.get('orderId'), concept_name)
                return False
            status = (row[0] or '').lower()
            if status == 'available':
                _logger.info("PERMITTING BILLING: Lab order [%s] %s evaluated and AVAILABLE in OpenELIS. Permitted in Odoo billing.", order.get('orderId'), concept_name)
                return True
            else:
                _logger.info("CRITICAL BILLING PROTECTION: Lab order [%s] %s evaluated as '%s' in OpenELIS. Excluding from Odoo billing.", order.get('orderId'), concept_name, status)
                return False
        except Exception as e:
            _logger.warning("Error checking OpenELIS evaluation for %s: %s", concept_name, e)
            return False

    @api.model
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
            order_type = order.get('type')
            if order_type == 'Lab Order':
                if not self._is_lab_test_eligible_for_billing(order):
                    continue
            else:
                if self._is_test_stock_out(order):
                    _logger.info("CRITICAL BILLING PROTECTION: Excluding stock-out test [%s] %s from sale order processing", order.get('orderId'), order.get('conceptName'))
                    continue
            if self._is_order_revised_processed(orders, order):
                continue"""

assert old_filter_block in text, "old_filter_block not found"
text = text.replace(old_filter_block, new_filter_block, 1)

with open('erp/bahmni-odoo-modules/bahmni_api_feed/models/order_save_service.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print("Updated order_save_service.py with OpenELIS evaluation gate successfully!")
