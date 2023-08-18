# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    session_time_out = fields.Integer(default=60, string="Expiration de la session(min)")
