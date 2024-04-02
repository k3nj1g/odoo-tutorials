# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The price must be strictly positive'),
    ]
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        copy=False
    )
    partner_id = fields.Many2one('res.partner', required=True, string="Partner")
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline', string="Deadline")
    property_type_id = fields.Many2one('estate.property.type', related="property_id.property_type_id", store="True")

    @api.depends('validity')
    def _compute_date_deadline(self):
        """
        Compute the date deadline based on the validity field.
        """
        for record in self:
            start_date = record.create_date if record.create_date else fields.Date.today()
            record.date_deadline = fields.Date.add(start_date, days=record.validity)

    def _inverse_date_deadline(self):
        """
        Calculate the validity of each record based on the date deadline.
        """
        for offer in self:
            start_date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - start_date).days

    def action_accept(self):
        for offer in self:
            if offer.status == 'refused':
                raise exceptions.UserError("Offer already refused")
            else:
                other_offers = offer.property_id.offer_ids
                for other_offer in other_offers:
                    if other_offer.status == 'accepted':
                        raise exceptions.UserError("Another offer already accepted")
                offer.status = 'accepted'
                offer.property_id.state = 'offer_accepted'
                offer.property_id.selling_price = offer.price
                offer.property_id.buyer = offer.partner_id
        return True

    def action_refuse(self):
        for offer in self:
            if offer.status == 'accepted':
                raise exceptions.UserError("Offer already accepted")
            else:
                offer.status = 'refused'
        return True
