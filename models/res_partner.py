# -*- coding: utf-8 -*-
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

class ResPartnerWebsiteConecta(models.Model):

    _inherit = "res.partner"

    conecta = fields.Boolean(string="Conecta")
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    employees = fields.Integer(string="Employees")
    social_twitter = fields.Char('Twitter Account')
    social_facebook = fields.Char('Facebook Account')
    social_github = fields.Char('GitHub Account')
    social_linkedin = fields.Char('LinkedIn Account')
    social_youtube = fields.Char('Youtube Account')
    social_googleplus = fields.Char('Google+ Account')
    city_id = fields.Many2one('res.country.state.city', string="City")
    categ = fields.Many2one('res.partner.categ', string="Category")
    dist_pref = fields.Integer(string="Distance Pref")
    relation_type = fields.Many2one('res.partner.relation', string="Relation Type", help="The type of relation this member is seeking")
    interest_list = fields.Many2many('res.partner.interest', string="Interest List")
    #messages_list = fields.Many2many('res.conecta.messages', string="Messages List")
    profile_visibility = fields.Selection([('public','Public'), ('members_only','Members Only'), ('not_listed','Not Listed')], default="not_listed", string="Profile Visibility", help="Public: can be viewed by anyone on the internet\nMembers Only: Can only be viewed by people who have an account\nNot Listed: Profile will only be visiable to members you have contacted")
    profile_text = fields.Text(string="Profile Text")
    profile_micro = fields.Char(size=200, string="Profile Micro Summary")
    like_list = fields.Many2many(comodel_name='res.partner', relation='like_list', column1='like1', column2='like2', string='Like List')
    message_setting = fields.Selection([('public','Anyone'), ('members_only','Members Only'), ('i_like','Members I Like')], string="Message Setting")
    contacts = fields.One2many('res.conecta.contacts', 'partner_id', string="Contact List", help="A member that has contacted you or you have contacted them")
    questionnaire_answers = fields.One2many('res.conecta.questionnaire.answer', 'partner_id')
        
                
class ResPartnerWebsiteConectaCategory(models.Model):

    _name = "res.partner.categ"
    _description = "Partner Category"
    
    name = fields.Char(string="Category")
    letter = fields.Char(string="Letter")
    
class ResPartnerRelation(models.Model):

    _name = "res.partner.relation"
    _description = "Partner Relation"

    name = fields.Char(string="Name")
