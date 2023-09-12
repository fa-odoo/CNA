# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import datetime

class IncidentDurationWizard(models.TransientModel):
    _name = "presence.time.wizard"
    _description = "Temps de présence Assistant"

    start_date = fields.Date(string="Date début", required=True)
    end_date = fields.Date(string="Date fin", required=True, compute='compute_end_date',)

    @api.depends('start_date')
    def compute_end_date(self):
        for rec in self:
            if rec.start_date:
                next_month = rec.start_date.replace(day=28) + datetime.timedelta(days=4)
                rec.end_date = next_month - datetime.timedelta(days=next_month.day)
            else:
                rec.end_date = False

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        return res

    def generate_report(self):
        self.ensure_one()
        return self.env.ref('tournee.presence_time_xlsx_report_action').report_action(self, data={'start_date': self.start_date, 'end_date': self.end_date})