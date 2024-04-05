# -*- coding: utf-8 -*-
from odoo import fields, models

class EstatePropertySalesPerson(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('estate.property', 'salesperson', string="Properties", domain="[('date_availability', '&lt;=', context_today())]")