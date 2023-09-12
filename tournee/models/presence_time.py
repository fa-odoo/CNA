from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import timedelta

class PresenceTime(models.Model):
    _name = 'presence.time'
    _description = 'Temps de présence'

    navire_id = fields.Many2one('navire.navire', string='Navire', required=True)
    organisation_id = fields.Many2one('organisation.organisation', string='Organisation', required=True)
    start_date = fields.Date(string='Date début')
    end_date = fields.Date(string='Date fin', compute='compute_end_date', store=True)
    hours_sold = fields.Float(string='Heures vendues', related='organisation_id.monthly_hours')

    @api.depends('start_date')
    def compute_end_date(self):
        for rec in self:
            if rec.start_date:
                next_month = rec.start_date.replace(day=28) + timedelta(days=4)
                rec.end_date = next_month - timedelta(days=next_month.day)
            else:
                rec.end_date = False

    @api.constrains('start_date', 'end_date')
    def validate_date(self):
        for rec in self:
            if rec.start_date >= rec.end_date:
                raise ValidationError("La date d'entrée doit être antérieure à la date de sortie")
            if rec.start_date.day != 1:
                raise ValidationError("La date d'entrée doit être le premier jour du mois")

