from odoo import api, fields, models
from odoo.exceptions import UserError


class Activitie(models.Model):
    _name = 'cna.activitie'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(related='type_activitie_id.name', required=False, tracking=True)
    type_activitie_id = fields.Many2one(comodel_name="cna.type.activitie", string="Type d'activité", required=True, tracking=True)
    type_activitie_short_desc_id = fields.Many2one(comodel_name="cna.type.activitie.short.desc",
                                                   string="Courte description", required=False, tracking=True)
    site = fields.Many2one('site.site', string="Site", tracking=True)
    access_point = fields.Selection(string="Point d'Accès", selection=[('navire', 'Navire'), ('sol', 'Sol')],
                                    required=False, tracking=True)
    navire_id = fields.Many2one(comodel_name="navire.navire", string="Navire", required=False, tracking=True)
    lieu_id = fields.Many2one(comodel_name="site.lieu", string="Lieu", required=False, tracking=True)

    actions = fields.Text(required=False, help="Entrez ici les actions", tracking=True)
    state = fields.Selection([
        ('draft', 'En cours'),
        ('done', 'Clôturé')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, tracking=True)
    company_id = fields.Many2one('res.company', default=lambda s: s.env.company, tracking=True)

    def action_done(self):
        for rec in self:
            rec.write({'state': 'done'})

    def action_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    @api.onchange('access_point')
    def _onchange_access_point(self):
        self.navire_id = False

    def write(self, values):
        for activitie in self:
            if activitie.state == 'done' and not self.env.user.has_group('activities.group_change_incident_done'):
                raise UserError("Vous n'êtes pas autorisé de modifier une activité cloturé")

        return super(Activitie, self).write(values)

    def action_valide_mass_activitie(self):
        for incident in self.env['cna.activitie'].browse(self.env.context.get('active_ids')):
            incident.action_done()

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError('Vous ne pouvez pas supprimer une activité cloturé !')
        return super(Activitie, self).unlink()

    def get_attachment_ids(self):
        for rec in self:
            attachment_ids = self.env['ir.attachment'].search([('res_id', '=', rec.id),
                                                               ('res_model', '=', 'cna.activitie')])
            return attachment_ids or False
