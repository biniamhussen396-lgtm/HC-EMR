# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderInherited(models.Model):
    _inherit = _inherit = 'sale.order'

    partner_id = fields.Many2one('res.partner', string='Patient Name', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')
    partner_village = fields.Many2one("village.village", string="Patient Kebele")
    shop_id = fields.Many2one('sale.shop', string='Service Unit', required=True)
    date_order = fields.Datetime(string='Charge Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
    credit_type = fields.Many2one('credit.type', string='Credit Type')
    free_service = fields.Many2one('free.service', string='Free Service')
    credit_company_name = fields.Many2one('credit.company', string='Credit Company')
    cbhi_woreda_name = fields.Many2one('cbhi.woreda', string='CBHI Woreda')
    brigade_name = fields.Many2one('ethiopia.brigade', string='Brigade Name')
    campus_name = fields.Many2one('uog.campus', string='Campus Name')
    working_place = fields.Many2one('working.place', string='Workplace')
    battalion = fields.Char(string='Battalion')
    id_number = fields.Char(string='ID Number')
    payment_method = fields.Many2one('payment.method', string='Payment Method')
    patient_detail = fields.Char(compute="_compute_fieldvalue", string="Patient Detail", store=True)
    patient_detail_without_date = fields.Char(compute="_compute_fieldvalue", string="Patient Detail Without Date", store=True)
    patient_kebele = fields.Char(compute="_compute_fieldvalue", string="Patient Kebele", store=True)
    attribute_ids = fields.One2many('res.partner.attributes', 'partner_id', string='Attributes')
   
    @api.depends('partner_id.display_name', 'id_number', 'date_order', 'partner_id.street2', 'payment_term_id', 'working_place', 'campus_name')
    def _compute_fieldvalue(self):
        for each in self:

         if each.partner_id.street2 == '':
            each.patient_kebele  = 'N/A'
            each.patient_detail  = each.partner_id.display_name
            each.patient_detail_without_date  = each.partner_id.display_name
         elif each.credit_company_name.id == 3:
            each.patient_kebele  = each.campus_name.name
            each.patient_detail  = each.partner_id.display_name
            each.patient_detail_without_date  = each.partner_id.display_name
         elif each.payment_term_id.id == 5:
            each.patient_kebele  = each.working_place.name
            each.patient_detail  = each.partner_id.display_name
            each.patient_detail_without_date  = each.partner_id.display_name   
         else:   
            each.patient_kebele  = each.partner_id.street2
            each.patient_detail  = each.partner_id.display_name
            each.patient_detail_without_date  = each.partner_id.display_name
