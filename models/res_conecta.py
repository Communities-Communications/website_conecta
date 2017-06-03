# -*- coding: utf-8 -*
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from random import randint

from odoo import api, fields, models

class ResConecta(models.Model):

    _name = "res.conecta"
    _description = "Conecta"
    
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string="State")
    num_profiles = fields.Integer(string="Num Profiles", default="1000")
    min_employees = fields.Integer(string="Min Employees", default="18")
    max_employees = fields.Integer(string="Max Employees", default="60")

    @api.one
    def delete_fake_profiles(self):
        """Delete all fake conecta profiles"""
        for fake in self.env['res.partner'].search([('fake_profile','=',True)]):
            fake.unlink()
    
    @api.one
    def create_fake_profiles(self):
        """Create a large amount of fake profile to aid in testing of conecta algorithm"""
        
        #Check if there are suburbs for the choosen state
        #if self.env['res.country.state.city'].search_count([('state_id','=',self.state_id.id)]) > 0:
        #    return "Import suburbs first"
        
        calc_min_days = 365 * self.min_employees
        calc_max_days = 365 * self.max_employees
                
        my_delta_young_time = datetime.utcnow() - timedelta(days=calc_min_days)
        my_delta_old_time = datetime.utcnow() - timedelta(days=calc_max_days)	        

        suburb_list = self.state_id.city_ids

        industry_categ = self.env['ir.model.data'].get_object('website_conecta', 'website_conecta_industry')
        services_categ = self.env['ir.model.data'].get_object('website_conecta', 'website_conecta_services')
        
        for i in range(0, self.num_profiles):
	    #random name and with it categ
            first_name = self.env['res.conecta.fake.first'].browse(randint(1, 4999))
            last_name = self.env['res.conecta.fake.last'].browse(randint(1, 4999))
            
            categ = self.env['res.partner.categ'].search([('name','=',first_name.categ)])[0].id

            #random employees
	    birth_date = my_delta_old_time + timedelta(seconds=randint(0, int((my_delta_young_time - my_delta_old_time).total_seconds())))
            employees = relativedelta(date.today(), birth_date).years

            #random employees pref
            min_employees_pref = randint(self.min_employees, self.max_employees)
            max_employees_pref = randint(min_employees_pref, self.max_employees)

            #random relation type
            relation_type = self.env['res.partner.relation'].browse(randint(1, self.env['res.partner.relation'].search_count([]) ) )
            
            #random suburb
            rand_suburb = suburb_list[randint(0, len(suburb_list) - 1)]
                
            #random profile visibilty
            rand_profile_vis = randint(1, 100)
            profile_vis = ""
            if rand_profile_vis <= 80:
                #80% of being members only
                profile_vis = "members_only"
            elif rand_profile_vis <= 100:
                #20% of being public
                profile_vis = "public"
            
            #random message settings
            rand_message_setting = randint(1, 100)
            message_setting = ""
            if rand_message_setting <= 80:
                #80% of being members only
                message_setting = "members_only"
            elif rand_message_setting <= 100:
                #20% of being public
                message_setting = "public"

            
            #random profile text
            profile_text = "I am " + str(age) + " year old " + first_name.categ + " seeking " + str(relation_type.name)
            
            #create the partner
            new_partner = self.env['res.partner'].create({'message_setting':message_setting, 'profile_micro': profile_text, 'profile_text': profile_text,'profile_visibility': profile_vis,'conecta':'True', 'fake_profile':'True', 'birth_date': birth_date, 'name': first_name.name + " " + last_name.name, 'first_name':first_name.name, 'last_name':last_name.name,'categ':categ, 'country_id':rand_suburb.state_id.country_id.id, 'state_id':rand_suburb.state_id.id, 'city':rand_suburb.name, 'employees':employees, 'relation_type': relation_type.id, 'min_employees_pref':min_employees_pref,'max_employees_pref':max_employees_pref, 'latitude': rand_suburb.latitude, 'latitude': rand_suburb.latitude, 'longitude': rand_suburb.longitude})

class ResConectaContacts(models.Model):

    _name = "res.conecta.contacts"
    
    partner_id = fields.Many2one('res.partner', string='From Partner')
    to_id = fields.Many2one('res.partner', string='To Partner')
    unread_message_count = fields.Integer()
    
class ResConectaMessages(models.Model):

    _name = "res.conecta.messages"

    message_owner = fields.Many2one('res.partner', string='Owner')
    message_partner_id = fields.Many2one('res.partner', string='From Partner')
    message_to_id = fields.Many2one('res.partner', string='To Partner')
    message_text = fields.Text(string="Message")
    type =  fields.Selection([('regular','Regular'), ('like','Like')], string="Type")
    read = fields.Boolean(string="Read")
    
class ResConectaReview(models.Model):

    _name = "res.conecta.review"

    review_owner = fields.Many2one('res.partner', string='Owner')
    review_partner_id = fields.Many2one('res.partner', string='From Partner')
    review_to_id = fields.Many2one('res.partner', string='To Partner')
    review_text = fields.Text(string="Message")
    review_star = fields.Float(size=8, string="Rating")
    
class ResConectaEvent(models.Model):

    _name = "event.event"
    _inherit = "event.event"
    _inherit = [_name, "base_multi_image.owner"]
    
    show_registration = fields.Boolean('Show Registration')