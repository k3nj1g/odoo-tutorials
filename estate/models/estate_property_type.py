# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'The name must be unique'),
    ]

    name = fields.Char(required=True)