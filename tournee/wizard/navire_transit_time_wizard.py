from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from datetime import timedelta

class NavireTransitTimeWizard(models.TransientModel):
    _name = 'navire.transit.time.wizard'

    type = fields.Selection([('week', 'Semaine'), ('month', 'Mois')], default='week', string='Type', required=True)
    date_start = fields.Date(string="Date début", required=True)
    date_end = fields.Date(string="Date fin", compute="compute_date_end", readonly=True)
    navire_ids = fields.Many2many('navire.navire', string='Navires', required=True)

    @api.constrains('type', 'date_start')
    def _check_start_end_tag(self):
        for rec in self:
            if rec.date_start and rec.type:
                if rec.type == 'week' and rec.date_start.weekday() != 0 or rec.type == 'month' and rec.date_start.day != 1:
                    raise UserError("Veuillez choisir une date valide")


    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['navire_ids'] = self.env.context.get('active_ids')
        return res

    def generate_report(self):
        # check date
        if self.date_start and self.date_end:
            if self.date_start > self.date_end:
                raise Warning('Vous devez choisir une date valide')
        return self.env.ref('tournee.navire_transit_time_xlsx_action').report_action(self, data={'date_start': self.date_start, 'date_end': self.date_end, 'navire_ids': self.navire_ids.ids, 'type': self.type})

    @api.depends('date_start', 'type')
    def compute_date_end(self):
        for rec in self:
            if rec.date_start and rec.type:
                if rec.type == 'week':
                    rec.date_end = rec.date_start + timedelta(days=5)
                else:
                    input_dt = rec.date_start
                    next_month = input_dt.replace(month=input_dt.month +1) - timedelta(days=1)
                    # res = next_month - timedelta(days=next_month.day)
                    rec.date_end = next_month
            else:
                rec.date_end = False