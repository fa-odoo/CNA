# -*- coding: utf-8 -*-

from odoo import fields, models, api


class TagsTaskAnomalie(models.Model):
    _inherit = "tags.task.anomalie"

    def action_open_anomalie_report(self):
        res_ids = self.env.context.get('active_ids')
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'tags_ids': res_ids,
            }}
        return self.env.ref('rapport_anomalie_rondes.report_anomalies_rondes').report_action(self, data=data)
