from odoo import api, fields, models


class IncidentType(models.Model):
    _name = 'incident.type'

    name = fields.Char(string="Type d'incident", required=True)
    responsable_id = fields.Many2one(comodel_name="res.partner", string="Responsable")
    short_description_ids = fields.One2many(comodel_name="incident.type.short.description", inverse_name="incident_type_id", required=False)
    follower_ids = fields.Many2many(comodel_name="res.partner", string="Abonnés")
    
    
class IncidentTypeShortDescription(models.Model):
    _name = 'incident.type.short.description'
    
    name = fields.Char(string="Description", required=True, )
    incident_type_id = fields.Many2one(comodel_name="incident.type", string="Incident")

