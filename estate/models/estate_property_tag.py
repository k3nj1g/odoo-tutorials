# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'The name must be unique'),
    ]
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer("Color")