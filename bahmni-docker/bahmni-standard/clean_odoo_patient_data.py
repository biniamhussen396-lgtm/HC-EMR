#!/usr/bin/env python3
import subprocess
import sys

def run_cmd(cmd, check=True):
    print(f"[*] Running: {cmd}")
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if check and res.returncode != 0:
        print(f"[!] Error:\n{res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)
    return res.stdout.strip()

def run_sql_stdin(sql_commands):
    cmd = ["docker", "exec", "-i", "bahmni-standard-odoodb-1", "psql", "-U", "odoo", "-d", "odoo"]
    res = subprocess.run(cmd, input=sql_commands, text=True, capture_output=True)
    if res.returncode != 0:
        print(f"[!] Database Error:\n{res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)
    return res.stdout.strip()

def main():
    confirm = input("Purge all Odoo patient orders, invoices, and customer partners? [y/N]: ").strip().lower()
    if confirm != 'y':
        sys.exit(0)

    run_cmd("docker compose stop odoo odoo-connect", check=False)

    cleanup_sql = """
    BEGIN;
    SET session_replication_role = 'replica';

    DELETE FROM account_analytic_line;
    DELETE FROM sale_order_line_invoice_rel;
    DELETE FROM sale_order_tag_rel;
    DELETE FROM sale_order_transaction_rel;
    DELETE FROM sale_advance_payment_inv_sale_order_rel;
    DELETE FROM sale_order_cancel;
    DELETE FROM sale_order_option;
    DELETE FROM sale_order_line;
    DELETE FROM sale_order;

    DELETE FROM account_payment_register_move_line_rel;
    DELETE FROM account_payment_register;
    DELETE FROM account_partial_reconcile;
    DELETE FROM account_full_reconcile;
    DELETE FROM account_payment;
    DELETE FROM account_move_line;
    DELETE FROM account_move;

    DELETE FROM pos_payment;
    DELETE FROM pos_order_line;
    DELETE FROM pos_order;

    DELETE FROM stock_valuation_layer;
    DELETE FROM stock_quant;
    DELETE FROM stock_move_line;
    DELETE FROM stock_move;
    DELETE FROM stock_picking;
    DELETE FROM procurement_group;

    DELETE FROM mail_tracking_value;
    DELETE FROM mail_message WHERE model IN ('sale.order', 'account.move', 'stock.picking', 'pos.order', 'res.partner');

    DELETE FROM res_partner 
    WHERE id NOT IN (
        SELECT DISTINCT partner_id FROM res_users WHERE partner_id IS NOT NULL
        UNION
        SELECT DISTINCT partner_id FROM res_company WHERE partner_id IS NOT NULL
    )
    AND id > 5;

    UPDATE ir_sequence SET number_next = 1 WHERE code IN ('sale.order', 'account.move', 'stock.picking', 'pos.order');

    SET session_replication_role = 'origin';
    COMMIT;
    """

    print("[*] Purging records...")
    print(run_sql_stdin(cleanup_sql))
    run_cmd("docker compose up -d odoo odoo-connect", check=True)
    print("[✔] Odoo cleanup complete.")

if __name__ == "__main__":
    main()
