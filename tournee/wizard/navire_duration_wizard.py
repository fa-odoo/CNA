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
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'navire_ids': self.navire_ids.ids,
            }}
        return self.env.ref('tournee.action_report_navire_duration').report_action(self, data=data)
