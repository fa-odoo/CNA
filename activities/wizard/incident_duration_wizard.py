# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class IncidentDurationWizard(models.TransientModel):
    _name = "incident.duration.wizard"
    _description = "Rapport d'incidents"

    start_date = fields.Date(string="Date début", required=True)
    end_date = fields.Date(string="Date fin", required=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        return res

    def generate_report(self):
        self.ensure_one()
        return self.env.ref('activities.incident_duration_xlsx_report_action').report_action(self, data={'start_date': self.start_date, 'end_date': self.end_date})