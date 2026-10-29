# -*- coding: utf-8 -*-
from odoo import fields, models

class SaleReport(models.Model):
    _inherit = "sale.report"

    # ---------------------------------------------------------
    # Raw fields from sale_order (Table Alias 's')
    # ---------------------------------------------------------
    credit_type = fields.Many2one('credit.type', string='Credit Type', readonly=True)
    free_service = fields.Many2one('free.service', string='Free Service', readonly=True)
    credit_company_name = fields.Many2one('credit.company', string='Credit Company', readonly=True)
    cbhi_woreda_name = fields.Many2one('cbhi.woreda', string='CBHI Woreda', readonly=True)
    brigade_name = fields.Many2one('ethiopia.brigade', string='Brigade Name', readonly=True)
    campus_name = fields.Many2one('uog.campus', string='Campus Name', readonly=True)
    working_place = fields.Many2one('working.place', string='Workplace', readonly=True)
    battalion = fields.Char(string='Battalion', readonly=True)
    id_number = fields.Char(string='ID Number', readonly=True)
    payment_method = fields.Many2one('payment.method', string='Payment Method', readonly=True)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True)
    patient_kebele = fields.Char(string='Patient Kebele', readonly=True)
    shop_id = fields.Many2one('sale.shop', string='Service Unit', readonly=True)

    # ---------------------------------------------------------
    # Concatenated fields for the Report View
    # ---------------------------------------------------------
    patient_detail = fields.Char(string="Patient Detail", readonly=True)
    patient_detail_without_date = fields.Char(string="Patient Detail Without Date", readonly=True)

    def _select_additional_fields(self):
        """
        Extend the SQL SELECT clause.
        Brackets removed. Separated by comma and space.
        """
        res = super()._select_additional_fields()
        res.update({
            'credit_type': 's.credit_type',
            'free_service': 's.free_service',
            'credit_company_name': 's.credit_company_name',
            'cbhi_woreda_name': 's.cbhi_woreda_name',
            'brigade_name': 's.brigade_name',
            'campus_name': 's.campus_name',
            'working_place': 's.working_place',
            'battalion': 's.battalion',
            'id_number': 's.id_number',
            'payment_method': 's.payment_method',
            'payment_term_id': 's.payment_term_id',
            'patient_kebele': 's.patient_kebele',
            'shop_id': 's.shop_id',
            'care_setting': 's.care_setting',
            
            # Concatenation logic: [Detail], [ID], [Care], [Date], [Kebele]
            'patient_detail': """
                COALESCE(s.patient_detail, '') || ', ' || 
                COALESCE(s.id_number, '') || ', ' || 
                COALESCE(s.care_setting, '') || ', ' || 
                COALESCE(CAST(s.date_order AS VARCHAR), '') || ', ' || 
                COALESCE(s.patient_kebele, '')
            """,
            
            # Concatenation logic: [Detail], [ID], [Care], [Kebele]
            'patient_detail_without_date': """
                COALESCE(s.patient_detail_without_date, '') || ', ' || 
                COALESCE(s.id_number, '') || ', ' || 
                COALESCE(s.care_setting, '') || ', ' || 
                COALESCE(s.patient_kebele, '')
            """,
        })
        return res

    def _group_by_sale(self):
        """
        Extend the SQL GROUP BY clause.
        Included all stored fields from the SELECT to prevent SQL errors.
        """
        res = super()._group_by_sale()
        res += """,
            s.credit_type,
            s.free_service,
            s.credit_company_name,
            s.cbhi_woreda_name,
            s.brigade_name,
            s.campus_name,
            s.working_place,
            s.battalion,
            s.id_number,
            s.payment_method,
            s.payment_term_id,
            s.patient_kebele,
            s.shop_id,
            s.care_setting,
            s.patient_detail,
            s.patient_detail_without_date"""
        return res