# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class TransitTimeGraphWizard(models.TransientModel):
    _name = "transit.time.graph.wizard"
    _description = "Temps de passage graphique"

    navire_ids = fields.Many2many('navire.navire', string='Navires', required=True)
    start_date = fields.Date(string="Date début", required=True)
    end_date = fields.Date(string="Date fin", required=True)
    binary_file = fields.Binary(string='File', readonly=True)

    def generate_report(self):
        self.ensure_one()
        return self.env.ref('tournee.transit_time_graph_xlsx_id').report_action(self, data={
            'start_date': self.start_date,
            'end_date': self.end_date,
            'navire_ids': self.navire_ids.ids,
            'navire_names': ", ".join(navire_id.name for navire_id in self.navire_ids)})
