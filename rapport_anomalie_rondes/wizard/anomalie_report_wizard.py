# -*- coding: utf-8 -*-

from odoo import models, fields, api



class AnomalieReportWizard(models.TransientModel):
    _name = 'anomalie.report.wizard'
    _description = 'Rapport Anomalie rondes'


    def print_report(self):
        # active_ids = self.env.context.get('active_ids')

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'tags_ids': self.env['tags.task.anomalie'].sudo().search([]).mapped('id'),
            }}
        return self.env.ref('rapport_anomalie_rondes.report_anomalies_rondes').report_action(self, data=data)


