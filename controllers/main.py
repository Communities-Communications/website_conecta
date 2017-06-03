# -*- coding: utf-8 -*-
import werkzeug
from datetime import datetime
import json
import math
import base64
import logging
_logger = logging.getLogger(__name__)

from odoo import http
from odoo.http import request

class WebsiteConectaController(http.Controller):

    @http.route('/conecta/interests', type="http", auth="user", website=True)
    def conecta_interests(self, **kwargs):
        interest_categories = request.env['res.partner.interest.category'].search([])
        return http.request.render('website_conecta.conecta_interests', {'interest_categories': interest_categories} )

###########################################################################################################

    @http.route('/conecta/interests/process', type="http", auth="user", website=True)
    def conecta_interests_process(self, **kwargs):
        
        values = {}
	for field_name, field_value in kwargs.items():
	    values[field_name] = field_value
	    request.env.user.partner_id.interest_list = [(4, int(field_name) )]

        return werkzeug.utils.redirect("/conecta/interests/list")

###########################################################################################################

    @http.route('/conecta/interests/list', type="http", auth="user", website=True)
    def conecta_interests_list(self, **kwargs):
        
        values = {}
	for field_name, field_value in kwargs.items():
	    values[field_name] = field_value
	
	like_matches = []

        for member in request.env['res.partner'].search([('conecta','=',True), ('profile_visibility','!=','not_listed')]):
            interests_shared = 0
            #Go through each interest the user has
            for interest in request.env.user.partner_id.interest_list:
            
                if interest in member.interest_list:
                    interests_shared += 1
            
            if interests_shared > 0:
                like_matches.append( {'member':member,'interest_count': interests_shared})

        like_matches_sorted = sorted(like_matches, key=lambda k: k['interest_count'], reverse=True)
        
        return http.request.render('website_conecta.conecta_interests_list', {'like_matches_sorted': like_matches_sorted} )

###########################################################################################################

    @http.route('/conecta/profile/register', type="http", auth="public", website=True)
    def conecta_profile_register(self, **kwargs):
        categs = request.env['res.partner.categ'].search([])
        countries = request.env['res.country'].search([])
        states = request.env['res.country.state'].search([])
        cities = request.env['res.country.state.city'].search([])
        
        return http.request.render('website_conecta.my_conecta_register', {'categs': categs, 'countries': countries, 'states': states, 'cities': cities} )

###########################################################################################################

    @http.route('/conecta/profile/register/process', type="http", auth="public", website=True, csrf=False)
    def conecta_profile_register_process(self, **kwargs):
        
        values = {}
	for field_name, field_value in kwargs.items():
	    values[field_name] = field_value
	    
	#Create the new user
	new_user = request.env['res.users'].sudo().create({'name': values['name'], 'login': values['login'], 'password': values['password'] })	
	#Add the user to the conecta group
	conecta_group = request.env['ir.model.data'].sudo().get_object('website_conecta', 'conecta_group')
        conecta_group.users = [(4, new_user.id)]

   #Remove 'Contact Creation' permission        
	contact_creation_group = request.env['ir.model.data'].sudo().get_object('base', 'group_partner_manager')
        contact_creation_group.users = [(3,new_user.id)]

   #Also remove them as an employee
	human_resources_group = request.env['ir.model.data'].sudo().get_object('base', 'group_user')
        human_resources_group.users = [(3,new_user.id)]

   #Modify the users partner record
	new_user.partner_id.write({'is_company': True, 'conecta': True, 'website_published': True, 'name': values['name'], 'first_name': values['first_name'], 'last_name': values['last_name'], 'categ': values['categ'], 'profile_micro': values['self_description'], 'profile_text': values['profile_text'], 'street': values['street'], 'zip': values['zip'], 'website': values['website'], 'email': values['email'],'profile_visibility': 'members_only', 'country_id': values['country'], 'state_id': values['state'], 'city': values['city'], 'image': base64.encodestring(values['file'].read()) })
	
        #Automatically sign the new user in
        request.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
	#request.session.authenticate(request.env.cr.dbname, values['email'], values['password'])
	request.session.authenticate(request.env.cr.dbname, values['login'], values['password'])
        #Redirect them to thier profile page	
        return werkzeug.utils.redirect("/conecta/profiles/" + str(new_user.partner_id.id) )

###########################################################################################################
        
    @http.route('/conecta/profiles/like', type="http", auth="user", website=True)
    def conecta_like(self, **kwargs):
        
        values = {}
	for field_name, field_value in kwargs.items():
	    values[field_name] = field_value
	 
	member_id = int(values['member_id'])	
	
	like_list = http.request.env.user.partner_id.like_list
        
        #check if the partner has already liked this member
        already_liked = False
        
        if http.request.env['res.partner'].browse(member_id) in like_list:
            already_liked = True
         
        
        if already_liked == False:
            #add to like list
            http.request.env.user.partner_id.like_list = [(4, member_id)]
            
            #message the member
            message = http.request.env.user.partner_id.first_name + " likes you.\n\nClick <a href=\"/conecta/profiles/" + str(http.request.env.user.partner_id.id) + "\"/>here</a> to view this members profile."
            http.request.env["res.conecta.message"].sudo().create({'partner_id': http.request.env.user.partner_id.id, 'to_id': member_id, 'type': 'like', 'message':message})
    
        return werkzeug.utils.redirect("/conecta/profiles/" + str(member_id) )

###########################################################################################################

    @http.route('/conecta/profile/update', type="http", auth="user", website=True)
    def conecta_profile_update(self, **kwargs):
        
        values = {}
	for field_name, field_value in kwargs.items():
	    values[field_name] = field_value
	 
	
	member_id = int(values['member_id'])
	
	#Only the owner can update there profile
	if http.request.env.user.partner_id.id != member_id:
            return "Permission Denied"
	
	member = http.request.env['res.partner'].search([('id','=',member_id), ('conecta','=',True)])[0]
        
        member.profile_visibility = values['profile_visibility']
        member.message_setting = values['message_setting']
        
        
        return werkzeug.utils.redirect("/conecta/profiles/" + str(member_id) )

###########################################################################################################
    
    @http.route('/conecta/profiles', type="http", auth="public", website=True)    
    def conecta_list(self, **kwargs):

        values = {}
	for field_name, field_value in kwargs.items():
	    values[field_name] = field_value 
 
        search_list = []
        return_dict = {}
        
        #only conecta members
        search_list.append(('conecta','=','True'))
        
        if http.request.env.user.partner_id.name == 'Public user':
            #if not logged in only show public profiles
	    search_list.append(('profile_visibility','=','public'))                
        else:
            #if logged in they can view all non private profiles
            search_list.append(('profile_visibility','!=','not_listed'))        


# This is new. Review for search fields      

        #categ preference
        if 'categ' in values and values['categ'] != '':
            search_list.append(('categ','=',values['categ']))
            
        #country preference
        if 'country' in values and values['country'] != '':
            search_list.append(('country_id','=',values['country']))            

        if 'state' in values and values['state'] != '':
            search_list.append(('state_id','=',values['state']))
            
        my_dates = http.request.env['res.partner'].sudo().search(search_list, limit=15)
        my_dates_count = len(my_dates)

        categs = request.env['res.partner.categ'].search([])
        countries = request.env['res.country'].search([])
        states = request.env['res.country.state'].search([])
           

        return http.request.render('website_conecta.my_conecta_list', {'categs': categs, 'countries': countries, 'states': states, 'my_dates': my_dates, 'my_dates_count': my_dates_count} )

###########################################################################################################

    @http.route('/conecta/profiles/settings', type="http", auth="user", website=True)
    def conecta_profile_settings(self, **kwargs):
        
        #only logged in members can view this page
        if http.request.env.user.partner_id.name != 'Public user':
            return http.request.render('website_conecta.my_conecta_profile_settings', {'my_date': http.request.env.user.partner_id} )
        else:
            return "Permission Denied"

###########################################################################################################
 
    @http.route('/conecta/profiles/messages/send', type="http", auth="user", website=True)
    def conecta_profile_messages_send(self, **kwargs):

        values = {}
	for field_name, field_value in kwargs.items():
	    values[field_name] = field_value 
 
        can_message = False
	        
	member_id = values['member_id']
	member = http.request.env['res.partner'].sudo().search([('id','=',values['member_id']), ('conecta','=',True)])[0]
	partner = http.request.env.user.partner_id
	        
	        
	for you_likes in partner.like_list:
	    if int(member_id) == int(you_likes.id):
	        you_like = True
	        break
	            
	for they_likes in member.like_list:
	    if partner.id == they_likes.id:
	        they_like = True
	        break
	        
	#Can Message Checks
	if member.message_setting == "public":
	    can_message = True
	            
	if member.message_setting == "members_only":
	    if http.request.env.user.partner_id.name != 'Public user':
	        can_message = True
	            
	if member.message_setting == "i_like":
	    if they_like == True:
                can_message = True
 
        if can_message == True:
            in_contacts = False
            for cont in partner.contacts:
                if cont.to_id == int(member_id):
                    in_contacts = True
                    
            if in_contacts == False:
                http.request.env['res.conecta.contacts'].sudo().create({'partner_id':partner.id, 'to_id': member.id})
            
            comment =  values['comment']
            
            #sender gets a copy
            http.request.env['res.conecta.messages'].sudo().create({'message_owner': partner.id, 'message_partner_id': partner.id, 'message_to_id': member_id, 'message_text': comment, 'read':True})

            #recipient also gets a copy
            http.request.env['res.conecta.messages'].sudo().create({'message_owner': member.id,'message_partner_id': partner.id, 'message_to_id': member_id, 'message_text': comment})

        return werkzeug.utils.redirect("/conecta/profiles/" + str(member_id) )

###########################################################################################################
 
    @http.route('/conecta/questionnaire/<questionnaire_id>', type="http", auth="user", website=True)
    def conecta_questionnaire(self, questionnaire_id, **kwargs):
        questionnaire = request.env['res.conecta.questionnaire'].browse(int(questionnaire_id))
        return http.request.render('website_conecta.conecta_questionnaire', {'questionnaire': questionnaire} )

###########################################################################################################

    @http.route('/conecta/questionnaire/process', type="http", auth="user", website=True)
    def conecta_questionnaire_process(self, **kwargs):

        values = {}
	for field_name, field_value in kwargs.items():
	    values[field_name] = field_value
	    
	questionnaire_id = values['questionnaire_id']
	questionnaire = request.env['res.conecta.questionnaire'].sudo().browse( int(questionnaire_id) )
	
	#Currently logged in user can only submit answers for a questionnaire once
	if request.env['res.conecta.questionnaire.answer'].sudo().search_count([('questionnaire_id','=',questionnaire.id), ('partner_id','=',http.request.env.user.partner_id.id) ]) > 0:
	    return "You can only answer this questionnaire once"
	
	new_questionnaire_answer = request.env['res.conecta.questionnaire.answer'].sudo().create({'questionnaire_id': questionnaire.id, 'partner_id': http.request.env.user.partner_id.id})
	
	#Go through each question in this questionnaire
	for question in questionnaire.question_ids:
	    #Go through each option and determine if it was selected(prevents submitting options from other questions)
	    for option in question.option_ids:
	        if values["question_" + str(question.id)] == str(option.id):
	            request.env['res.conecta.questionnaire.answer.question'].sudo().create({'questionnaire_answer_id': new_questionnaire_answer.id, 'question_id': question.id, 'option_id': option.id})
	            
	            #Only one option is allowed(prevent multi option injection)
	            break
	            
        return werkzeug.utils.redirect("/conecta/questionnaire/answer/" + str(new_questionnaire_answer.id) )

###########################################################################################################

    @http.route('/conecta/questionnaire/answer/<questionnaire_answer_id>', type="http", auth="user", website=True)
    def conecta_questionnaire_answer(self, questionnaire_answer_id, **kwargs):
	"""Perform the conecta match making code"""
	
	questionnaire_answer = request.env['res.conecta.questionnaire.answer'].sudo().browse( int(questionnaire_answer_id) )
	questionnaire = request.env['res.conecta.questionnaire'].sudo().browse( int(questionnaire_answer.questionnaire_id.id) )

	categ_letter = ""
	if http.request.env.user.partner_id.categ.letter == "I":
	    categ_letter = "S"

	if http.request.env.user.partner_id.categ.letter == "S":
	    categ_letter = "I"
	
	output_string = ""
	candidate_list = []
	
	#First through all the answers to this questionaires which are owned by individuals of the opposite categ and are not private
	for candidate_questionnaire_answer in request.env['res.conecta.questionnaire.answer'].sudo().search([('questionnaire_id','=', questionnaire.id), ('partner_id.categ.letter','=',categ_letter),('partner_id.profile_visibility','!=','not_listed') ]):
	    match_score = 0
	    skip = False
	    
	    #Go through each match rule and determine the candidate final score
	    for match_rule in questionnaire.matching_rule_ids:
	        
	        #Check if user has compare option
	        user_match_compare_option = len( request.env['res.conecta.questionnaire.answer.question'].sudo().search([('questionnaire_answer_id.partner_id','=', http.request.env.user.partner_id.id), ('option_id','=', match_rule.question_compare_option_id.id)]) )
                
           #And candidate has match option
	        candidate_match_match_option = len( request.env['res.conecta.questionnaire.answer.question'].sudo().search([('questionnaire_answer_id.partner_id','=', candidate_questionnaire_answer.partner_id.id), ('option_id','=', match_rule.question_match_option_id.id)]) )

           #Check if user has match option
	        user_match_match_option = len( request.env['res.conecta.questionnaire.answer.question'].sudo().search([('questionnaire_answer_id.partner_id','=', http.request.env.user.partner_id.id), ('option_id','=', match_rule.question_match_option_id.id)]) )

	        #And candidate has compare option
	        candidate_match_compare_option = len( request.env['res.conecta.questionnaire.answer.question'].sudo().search([('questionnaire_answer_id.partner_id','=', candidate_questionnaire_answer.partner_id.id), ('option_id','=', match_rule.question_compare_option_id.id)]) )
	        
	        if user_match_compare_option and candidate_match_match_option:
	            if match_rule.option == "match":
	                match_score += match_rule.weight
	            elif match_rule.option == "penalise":
	                match_score -= match_rule.weight
	            elif match_rule.option == "exclude":
	                skip = True
	                break
	        
	        if user_match_match_option and candidate_match_compare_option:
	            if match_rule.option == "match":
	                match_score += match_rule.weight
	            elif match_rule.option == "penalise":
	                match_score -= match_rule.weight
	            elif match_rule.option == "exclude":
	                skip = True
	                break
	                
	    #Do not add this person to the candidate list
	    if skip:
	        continue
	    else:
	        candidate_list.append( {'partner_id': candidate_questionnaire_answer.partner_id.id, 'name':candidate_questionnaire_answer.partner_id.name, 'score': match_score} )	        
	 
	candidate_list_sorted = sorted(candidate_list, key=lambda k: k['score'], reverse=True)
	
	for cand in candidate_list_sorted:
	    output_string += "<a href=\"/conecta/profiles/" + str(cand["partner_id"]) + "\">" + cand["name"] + " " + str(cand["score"]) + "</a><br/>\n"
	    
	return output_string


###########################################################################################################
	        
    @http.route('/conecta/profiles/messages/<member_id>', type="http", auth="user", website=True)
    def conecta_profile_messages(self, member_id, **kwargs):
        
        member = http.request.env['res.partner'].sudo().search([('id','=',member_id), ('conecta','=',True)])[0]
        partner = http.request.env.user.partner_id
        
        message_list = http.request.env['res.conecta.messages'].search([('message_owner','=', partner.id)])
        
        for mess in message_list:
            _logger.error(mess.message_text)
        
        
        #only logged in members can view this page
        if http.request.env.user.partner_id.name != 'Public user':
            #return "Messages..."
            return http.request.render('website_conecta.my_conecta_messages', {'my_date':member, 'message_list': message_list} )
        else:
            return "Permission Denied"

#############################################################################################################
            
    @http.route('/conecta/profiles/<member_id>', type="http", auth="public", website=True)
    def conecta_profile(self, member_id, **kwargs):
        
        you_like = False
        they_like = False
        can_view = False
        can_message = False
        
        #search_list = []
        
        member = http.request.env['res.partner'].sudo().search([('id','=',member_id), ('conecta','=',True)])[0]
        partner = http.request.env.user.partner_id

        my_reviews = http.request.env['res.conecta.review'].sudo().search([('review_owner', '=', member.id)], limit=5, order='id desc')            
        my_reviews_count = len(my_reviews)
               
        my_reviews_rating = len(my_reviews)
     
        for you_likes in partner.like_list:
            if int(member_id) == int(you_likes.id):
                you_like = True
                break
            
        for they_likes in member.like_list:
            if partner.id == they_likes.id:
                they_like = True
                break
        
        #Can Message Checks
        if member.message_setting == "public":
            can_message = True
            
        if member.message_setting == "members_only":
            if http.request.env.user.partner_id.name != 'Public user':
                can_message = True
            
        if member.message_setting == "i_like":
            if they_like == True:
                can_message = True
            
        #Profile visiable checks
        if member.profile_visibility == "public":
            #everyone can view public profiles
            can_view = True
        elif member.profile_visibility == "members_only":
            #only logged in can view this profile
            if http.request.env.user.partner_id.name != 'Public user':
                can_view = True
        elif member.profile_visibility == "not_listed":
            #if this member likes you, you can view this profile
            if they_like == True:
                can_view = True
             
        #the owner can view there own profile
        if http.request.env.user.partner_id.id == int(member_id):
            can_view = True
      
        if can_view:
            questionnaires = request.env['res.conecta.questionnaire'].search([])
            return http.request.render('website_conecta.my_conecta_profile', {'my_date': member, 'can_message': can_message, 'you_like':you_like, 'they_like':they_like, 'questionnaires': questionnaires, 'my_reviews': my_reviews, 'my_reviews_count': my_reviews_count, 'my_reviews_rating': my_reviews_rating} )
        else:
            return "Permission Denied"
            
###########################################################################################################
 
    @http.route('/conecta/profiles/review/send', type="http", auth="user", website=True)
    def conecta_profile_review_send(self, **kwargs):

        values = {}
	for field_name, field_value in kwargs.items():
	    values[field_name] = field_value 
 
        can_message = False
	        
	member_id = values['member_id']
	member = http.request.env['res.partner'].sudo().search([('id','=',values['member_id']), ('conecta','=',True)])[0]
	partner = http.request.env.user.partner_id
	        
   	#Can Message Checks
	if member.message_setting == "public":
	    can_message = True
	            
	if member.message_setting == "members_only":
	    if http.request.env.user.partner_id.name != 'Public user':
	        can_message = True
	            
	if member.message_setting == "i_like":
	    if they_like == True:
                can_message = True
 
        if can_message == True:
            in_contacts = False
            for cont in partner.contacts:
                if cont.to_id == int(member_id):
                    in_contacts = True
                    
            if in_contacts == False:
                http.request.env['res.conecta.contacts'].sudo().create({'partner_id':partner.id, 'to_id': member.id})
            
            comment =  values['comment']
            rating =  values['rating']

            http.request.env['res.conecta.review'].sudo().create( {'review_owner': member.id,'review_partner_id': partner.id, 'review_to_id': member_id, 'review_text': comment, 'review_star': rating} )

        return werkzeug.utils.redirect("/conecta/profiles/" + str(member_id) )

###########################################################################################################

    @http.route('/conecta/event/register', type="http", auth="public", website=True)
    def conecta_event_register(self, **kwargs):
        categs = request.env['event.type'].search([])
        countries = request.env['res.country'].search([])
        local = request.env['res.partner'].search([])
        
        return http.request.render('website_conecta.my_conecta_event', {'categs': categs, 'countries': countries, 'local': local} )
        
########################################################################################################### Criação de Evento 
 
    @http.route('/conecta/event/send', type="http", auth="user", website=True)
    def conecta_event_send(self, **kwargs):

        values = {}
	for field_name, field_value in kwargs.items():
	    values[field_name] = field_value  
	        
	#member_id = values['member_id']
	#member = http.request.env['res.partner'].sudo().search([('id','=',values['member_id']), ('conecta','=',True)])[0]
	partner = http.request.env.user.partner_id

	http.request.env['event.event'].sudo().create({'organizer_id': partner.id, 'create_uid': partner.id, 'event_type_id': values['category'], 'country_id': values['country'], 'address_id': values['local'], 'description': values['comment'], 'date_begin': values['begin'], 'date_end': values['end'], 'name': values['name'], 'image_main': base64.encodestring(values['image_main'].read()) })	

#        return werkzeug.utils.redirect("/conecta/profiles/" + str(member_id) )
	return werkzeug.utils.redirect("/conecta/profiles/")
