# -*- coding: utf-8 -*
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from random import randint

from odoo import api, fields, models

class ResConectaQuestionnaireAnswer(models.Model):

    _name = "res.conecta.questionnaire.answer"
    _description = "Conecta Questionaire Answer"
    
    questionnaire_id = fields.Many2one('res.conecta.questionnaire', string="Questionnaire")
    partner_id = fields.Many2one('res.partner', string="Partner")
    question_ids = fields.One2many('res.conecta.questionnaire.answer.question', 'questionnaire_answer_id', string='Questions')
    
class ResConectaQuestionnaireAnswerQuestion(models.Model):

    _name = "res.conecta.questionnaire.answer.question"
    _description = "Conecta Questionaire Answer Question"
    
    questionnaire_answer_id = fields.Many2one('res.conecta.questionnaire.answer', string='Questionnaire Answer')
    question_id = fields.Many2one('res.conecta.questionnaire.question', string='Question', readonly="True")
    option_id = fields.Many2one('res.conecta.questionnaire.question.option', string="Option", readonly="True")