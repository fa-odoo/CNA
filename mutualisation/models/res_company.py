from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    sync_mobile = fields.Boolean(string=" Connexion API", default=True)
