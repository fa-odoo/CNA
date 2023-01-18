from odoo import api, fields, models
from odoo.exceptions import ValidationError

class NavireTransitTimeWizard(models.TransientModel):
    _name = 'navire.transit.time.wizard'

    date_start = fields.Date(string="Date début", reqiured=True)
    date_end = fields.Date(string="Date fin", reqiured=True)
    navire_ids = fields.Many2many('navire.navire', string='Navires', reqiured=True)

    @api.constrains('date_start', 'date_end')
    def _check_tourne_date(self):
        for tourne in self:
            if tourne.date_end < tourne.date_start:
                raise ValidationError('La date de fin ne peut pas être antérieure à la date de début.')
            if tourne.date_start.weekday() != 0 or tourne.date_end.weekday() != 4:
                raise ValidationError('La semaine doit commencer lundi au vendredi')
            if int((tourne.date_end - tourne.date_start).days) > 6:
                raise ValidationError('Veuillez choisir une seule semaine')

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
        return self.env.ref('tournee.navire_transit_time_xlsx_action').report_action(self, data={'date_start': self.date_start, 'date_end': self.date_end, 'navire_ids': self.navire_ids.ids})


