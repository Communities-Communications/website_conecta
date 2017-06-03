# -*- coding: utf-8 -*-
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from random import randint

from odoo import api, fields, models

class ResPartnerInterest(models.Model):

    _name = "res.partner.interest"
    _description = "Partner Interest"

    name = fields.Char(string="Name")
    interest_category_id = fields.Many2one('res.partner.interest.category', string="Interest Category")
    num_interested = fields.Integer(string="Number with Interest", compute="_compute_num_interested")

    @api.one
    def _compute_num_interested(self):
        self.num_interested = self.env['res.partner'].search_count([('interest_list','=',self.id)])
    
class ResPartnerInterestCategory(models.Model):

    _name = "res.partner.interest.category"
    _description = "Partner Interest Category"

    name = fields.Char(string="Name")
    interest_list = fields.One2many('res.partner.interest', 'interest_category_id', string="Interest List")