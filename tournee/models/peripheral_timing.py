from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PeripheralTiming(models.Model):
    _name = 'peripheral.timing'
    _description = 'Donnée d\'utilisation'

    name = fields.Char(string='Périphérique', required=True, )
    start_date = fields.Datetime(string='Heure début')
    end_date = fields.Datetime(string='Heure fin')
    emp_id = fields.Many2one(comodel_name='hr.employee', string='Employé')
    difference = fields.Float(compute="compute_diff", store=True)

    @api.depends('start_date', 'end_date')
    def compute_diff(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.difference =  (rec.end_date -rec.start_date).seconds/3600


    @api.constrains('start_date', 'end_date')
    def validate_date(self):
        for rec in self:
            if rec.start_date >= rec.end_date:
                raise ValidationError("La date d'entrée doit être antérieure à la date de sortie")
