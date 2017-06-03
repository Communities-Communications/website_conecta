# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResCountryStateConecta(models.Model):

    _inherit = "res.country.state"
    
    city_ids = fields.One2many('res.country.state.city', 'state_id', string="Cities")