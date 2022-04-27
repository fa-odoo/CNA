from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    start_code = fields.Char(string="Code de démarrage", required=False)
    end_code = fields.Char(string="Code d'arrêt", required=False)
