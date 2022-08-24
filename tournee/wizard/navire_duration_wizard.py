# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class NavireDurationWizard(models.TransientModel):
    _name = "navire.duration.wizard"
    _description = "Durée Navire Wizard"

    navire_ids = fields.Many2many('navire.navire', string='Navires', required=True)
    start_date = fields.Date(string="Date début", required=True)
    end_date = fields.Date(string="Date fin", required=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['navire_ids'] = self.env.context.get('active_ids')
        return res

    def generate_report(self):
        self.ensure_one()
        return self.env.ref('tournee.navire_duration_report_xlsx_id').report_action(self, data={'start_date': self.start_date,
                                                                                                    'end_date': self.end_date,
                                                                                                    'navire_ids': self.navire_ids.ids})