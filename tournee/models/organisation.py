from odoo import api, fields, models


class Organisation(models.Model):
    _name = 'organisation.organisation'
    _description = 'Organisation'

    name = fields.Char(string='Nom organisation', required=True)
    monthly_hours = fields.Float(string='Heures mensuelles', required=True)
