# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'

    # ----------------------------
    # SALE ORDER FIELDS
    # ----------------------------
    partner_id = fields.Many2one(
        'res.partner',
        string='Patient Name',
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True,
        change_default=True,
        index=True,
        track_visibility='always'
    )
    partner_village = fields.Many2one("village.village", string="Patient Kebele")
    shop_id = fields.Many2one('sale.shop', string='Service Unit', required=True)
    date_order = fields.Datetime(
        string='Charge Date',
        required=True,
        readonly=True,
        index=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        copy=False,
        default=fields.Datetime.now
    )
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

    # Partner Attributes
    attribute_ids = fields.One2many(
        related='partner_id.attribute_ids',
        string='Attributes',
        readonly=True
    )

    # ----------------------------
    # ATTRIBUTE → SALE ORDER FIELD MAPPING
    # ----------------------------
    ATTRIBUTE_MAPPING = {
        "PaymentMethod": ("payment_method", "many2one", "payment.method"),
        "CreditType": ("credit_type", "many2one", "credit.type"),
        "FreePaymentDetails": ("free_service", "many2one", "free.service"),
        "CreditCompany": ("credit_company_name", "many2one", "credit.company"),
        "CBHIAgreedWoreda": ("cbhi_woreda_name", "many2one", "cbhi.woreda"),
        "Reference Number": ("id_number", "char", None),
    }

    # ----------------------------
    # FUNCTION THAT FILLS FIELDS FROM ATTRIBUTES
    # ----------------------------
    def _fill_fields_from_attributes(self):
        for order in self:
            if not order.partner_id:
                continue

            attributes = order.partner_id.attribute_ids
            for attr in attributes:
                # Safely get attribute name
                attr_name = attr.name
                if hasattr(attr.name, 'name'):
                    attr_name = attr.name.name
                attr_value = attr.value

                if not attr_name or not attr_value:
                    continue

                if attr_name not in self.ATTRIBUTE_MAPPING:
                    continue

                field_name, field_type, model_name = self.ATTRIBUTE_MAPPING[attr_name]

                if field_type == "char":
                    setattr(order, field_name, attr_value)

                elif field_type == "many2one":
                    record = self.env[model_name].sudo().search(
                        [('name', 'ilike', attr_value)],
                        limit=1
                    )
                    if record:
                        setattr(order, field_name, record.id)

    # ----------------------------
    # MANUAL BUTTON ACTION
    # ----------------------------
    def action_fill_from_attributes(self):
        self._fill_fields_from_attributes()

    # ----------------------------
    # COMPUTE FIELDS
    # ----------------------------
    patient_detail = fields.Char(
        compute="_compute_fieldvalue",
        string="Patient Detail",
        store=True
    )
    patient_detail_without_date = fields.Char(
        compute="_compute_fieldvalue",
        string="Patient Detail Without Date",
        store=True
    )
    patient_kebele = fields.Char(
        compute="_compute_fieldvalue",
        string="Patient Kebele",
        store=True
    )

    @api.depends(
        'partner_id.display_name',
        'id_number',
        'date_order',
        'partner_id.street2',
        'payment_term_id',
        'working_place',
        'campus_name',
        'credit_company_name'
    )
    def _compute_fieldvalue(self):
        for each in self:
            if not each.partner_id.street2:
                each.patient_kebele = 'N/A'
            elif each.credit_company_name and each.credit_company_name.id == 3:
                each.patient_kebele = each.campus_name.name if each.campus_name else ''
            elif each.payment_term_id and each.payment_term_id.id == 5:
                each.patient_kebele = each.working_place.name if each.working_place else ''
            else:
                each.patient_kebele = each.partner_id.street2

            # Common for all
            each.patient_detail = each.partner_id.display_name
            each.patient_detail_without_date = each.partner_id.display_name