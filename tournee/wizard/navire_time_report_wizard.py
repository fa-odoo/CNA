from odoo import api, fields, models


class NavireTimeReportWizard(models.TransientModel):
    _name = 'navire.time.report.wizard'

    date_start = fields.Date(string="Date début",)
    date_end = fields.Date(string="Date fin",)
    navire_ids = fields.Many2many('navire.navire', string='Navires')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['navire_ids'] = self.env.context.get('active_ids')
        return res

    def generate_report(self):
        print('Print Report')
        # check date
        if self.date_start and self.date_end:
            if self.date_start > self.date_end:
                raise Warning('Vous devez choisir une date valide')

        data = {
            'ids'  : self.ids,
            'model': self._name,
            'form' : {
                'date_start' : self.date_start,
                'date_end'   : self.date_end,
                'navire_ids': self.navire_ids.ids,
            }}
        return self.env.ref('tournee.action_report_navire_time').report_action(self, data = data)


