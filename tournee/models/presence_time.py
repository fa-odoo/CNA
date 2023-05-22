from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PresenceTime(models.Model):
    _name = 'presence.time'
    _description = 'Temps de présence'

    navire_id = fields.Many2one('navire.navire', string='Navire', required=True)
    organisation_id = fields.Many2one('organisation.organisation', string='Organisation', required=True)
    start_date = fields.Date(string='Date début')
    end_date = fields.Date(string='Date fin')
    hours_sold = fields.Float(string='Heures vendues', related='organisation_id.monthly_hours')

    @api.constrains('start_date', 'end_date')
    def validate_date(self):
        for rec in self:
            if rec.start_date >= rec.end_date:
                raise ValidationError("La date d'entrée doit être antérieure à la date de sortie")
