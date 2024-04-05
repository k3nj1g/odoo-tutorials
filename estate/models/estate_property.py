# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero

class EstatePropertyModel(models.Model):
    _name = "estate.property"
    _description = "Real Estate"
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be positive'),
    ]
    _order = "id desc"
    
    name = fields.Char(string="Title", required=True)
    description = fields.Char()
    postcode = fields.Char()
    date_availability = fields.Date(string="Available From", copy=False, default=fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string="Status",
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ],
        required=True,
        copy=False,
        default='new',
        readonly=True
    )
    property_type_id = fields.Many2one('estate.property.type', )
    buyer = fields.Many2one('res.partner', copy=False)
    salesperson = fields.Many2one('res.users', string="Salesman", default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag')
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    total_area = fields.Integer(compute='_compute_total_area', string="Total Area (sqm)")
    best_price = fields.Float(compute='_compute_best_price', string="Best Offer")

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        """
        Compute the total area based on the living area and garden area for each record.
        """
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        """
        Compute the best price for each record.
        """
        for record in self:
            record.best_price = max(record.offer_ids.mapped('price')) if record.offer_ids else 0.0
            
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            affordable_price = record.expected_price * 0.9
            if (
                not float_is_zero(record.selling_price, precision_rounding=0.01)
                and float_compare(affordable_price, record.selling_price, precision_rounding=0.01) > 0
            ):
                raise exceptions.ValidationError("The selling price must be 90% of expected price at least")

    def set_as_canceled(self):
        for record in self:
            if record.state == 'sold':
                raise exceptions.UserError("Sold properties cannot be canceled")
            else:
                record.state = 'canceled'
        return True

    def set_as_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise exceptions.UserError("Canceled properties cannot be sold")
            else: 
                record.state = 'sold'
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancelled(self):
        for record in self:
            if record.state not in ('new', 'canceled'):
                raise exceptions.UserError("Properties can only be deleted if they are new or canceled")