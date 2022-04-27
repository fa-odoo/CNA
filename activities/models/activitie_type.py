from odoo import api, fields, models


class TypeActivitie(models.Model):
    _name = 'cna.type.activitie'

    name = fields.Char(string="Nom", required=True, )
    short_desc_ids = fields.One2many(comodel_name="cna.type.activitie.short.desc", inverse_name="type_activitie_id", string="Courte Description", required=False, )


class ShortDescriptionTypeActivitie(models.Model):
    _name = 'cna.type.activitie.short.desc'

    name = fields.Char(string=" ", required=True, )
    type_activitie_id = fields.Many2one(comodel_name="cna.type.activitie", required=False)


