from odoo import api, fields, models


class Incident(models.Model):
    _inherit = 'cna.incident'

    tag_id = fields.Many2one(comodel_name="tags.tags", string="Tag", required=False)
