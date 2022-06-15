# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class Incident(models.Model):
    _name = 'cna.incident'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def action_rapport_incident_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env['ir.model.data'].xmlid_to_res_id('activities.email_template_rapport_incident',
                                                                raise_if_not_found=False)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]

        ctx = {
            'default_model': 'cna.incident',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True,
        }
        print('template_itemplate_idd', template_id, ctx)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def get_default_priority(self):
        rec = self.env['model.importance'].search([('name', '=', 'cna.incident')])
        if rec:
            return rec.priority
        else:
            return '0'

    def get_default_site(self):
        site_ids = self.env['site.site'].search([])
        if site_ids:
            return site_ids[0]

    name = fields.Char('ID', default='/', readonly=True, tracking=True)
    # incident = fields.Boolean(tracking=True)
    date_start = fields.Datetime('Heure début', required=True, tracking=True, default=fields.Datetime.now)
    date_end = fields.Datetime('Heure fin', tracking=True)
    description = fields.Text("Description", tracking=True)
    action = fields.Text("Actions", tracking=True)
    site = fields.Many2one('site.site', string="Site", tracking=True, default=get_default_site)
    lieu = fields.Many2one('site.lieu', "Lieu", tracking=True)
    auteur = fields.Char("Auteur", tracking=True)
    auteur_company = fields.Char("Société d'auteur", tracking=True)
    auteur_badge = fields.Char("Badge", tracking=True)
    victime = fields.Char("Victime", tracking=True)
    victime_company = fields.Char("Société victime", tracking=True)

    victime_badge = fields.Char("Badge", tracking=True)
    company_id = fields.Many2one('res.company', default=lambda s: s.env.company, tracking=True, string='Société')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Critique')], string="Importance", default=get_default_priority, tracking=True)
    state = fields.Selection([
        ('draft', 'En cours'),
        ('done', 'Clôturé')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, tracking=True)

    person_av = fields.Many2many(comodel_name="incident.personne.avise", relation="incident_person_av_rel", string="Personnes avisées", tracking=True)
    agent_int = fields.Many2many(comodel_name="agent.intervenant", relation="incident_agent_int_rel", string="Agents intervenants", tracking=True)
    secour = fields.Many2many(comodel_name="secours.secours", string="Secours demandés", tracking=True)
    mesure = fields.Many2many(comodel_name="mesure.prise", string="Mesure prise", tracking=True)

    attachemnt_ids = fields.Many2many('ir.attachment', compute='get_record_attachment', tracking=True)

    incident_type_id = fields.Many2one(comodel_name="incident.type", string="Type d'incident", tracking=True)
    short_description_id = fields.Many2one(comodel_name="incident.type.short.description", string="Courte description",
                                           required=False, tracking=True)
    object = fields.Text(string="Objet", required=False, tracking=True, compute='compute_incident_objet', store=True)
    object_complementaire = fields.Text("Objet complémentaire")
    access_point = fields.Selection(string="Point d'Accès", selection=[('navire', 'Navire'), ('sol', 'Sol')],
                                    required=False, tracking=True)
    navire_id = fields.Many2one(comodel_name="navire.navire", string="Navire", required=False, tracking=True)
    tag_id = fields.Many2one(comodel_name="tags.tags", string="Tag", required=False, tracking=True)
    report_type = fields.Selection([('activity', 'Activité'), ('incident', 'Incident')], default='incident', string='Type de rapport', required=True)
    type_activitie_id = fields.Many2one(comodel_name = "cna.type.activitie", string = "Type d'activité",
                                         tracking = True)
    type_activitie_short_desc_id = fields.Many2one(comodel_name = "cna.type.activitie.short.desc",
                                                   string = "Courte description",  tracking = True)
    @api.depends('date_start', 'report_type', 'short_description_id', 'type_activitie_short_desc_id', 'lieu', 'auteur', 'auteur_company', 'auteur_badge',
                 'victime', 'victime_company', 'victime_badge',)
    def compute_incident_objet(self):
        for rec in self:
            object = ""
            if rec.date_start:
                object += str(rec.date_start)+' '
            if rec.report_type == 'incident' and rec.short_description_id:
                object += rec.short_description_id.name+' '
            if rec.report_type == 'activity' and rec.type_activitie_short_desc_id:
                object += rec.type_activitie_short_desc_id.name+' '
            if rec.lieu:
                object += rec.lieu.name+' '
            if rec.auteur:
                object += rec.auteur+' '
            if rec.auteur_company:
                object += rec.auteur_company+' '
            if rec.auteur_badge:
                object += rec.auteur_badge+' '
            if rec.victime:
                object += rec.victime+' '
            if rec.victime_company:
                object += rec.victime_company+' '

            if rec.victime_badge:
                object += rec.victime_badge+' '
            rec.object = object




    def get_record_attachment(self):
        for rec in self:
            attachement = self.env['ir.attachment'].search([('res_id', '=', rec.id),
                                                            ('res_model', '=', 'cna.incident')])
            if attachement:
                rec.attachemnt_ids = attachement
            else:
                rec.attachemnt_ids = False

    def action_done(self):
        return self.write({'state': 'done'})

    def action_to_draft(self):
        return self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        res = super(Incident, self).create(vals)

        res.name = self.env['ir.sequence'].next_by_code('cna.incident') or ''

        # add followers
        if res.incident_type_id:
            res.sudo().message_follower_ids.unlink()
            res.sudo().message_follower_ids = [
                (0, 0, {'res_model': 'cna.incident', 'res_id': res.id, 'partner_id': follower.id}) for follower in
                res.incident_type_id.follower_ids]

        if res.auteur:
            res.auteur = res.auteur.upper()
        if res.auteur_company:
            res.auteur_company = res.auteur_company.upper()

        if res.victime:
            res.victime = res.victime.upper()
        if res.victime_company:
            res.victime_company = res.victime_company.upper()


        return res

    def write(self, values):

        for incident in self:
            if incident.state == 'done' and not self.env.user.has_group('activities.group_change_incident_done'):
                raise UserError("Vous n'êtes pas autorisé de modifier une incident cloturé")

        if values.get('auteur'):
            values['auteur'] = values['auteur'].upper()

        if values.get('victime'):
            values['victime'] = values['victime'].upper()

        if values.get('auteur_company'):
            values['auteur_company'] = values['auteur_company'].upper()
        if values.get('victime_company'):
            values['victime_company'] = values['victime_company'].upper()

        res = super(Incident, self).write(values)

        # change followers if incident type changed
        if values.get('incident_type_id'):
            for rec in self:
                rec.sudo().message_follower_ids.unlink()
                rec.sudo().message_follower_ids = [
                    (0, 0, {'res_model': 'cna.incident', 'res_id': rec.id, 'partner_id': follower.id}) for follower in
                    rec.incident_type_id.follower_ids]

        return res

    @api.onchange('access_point')
    def _onchange_access_point(self):
        self.navire_id = False
        self.lieu = False

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError('Vous ne pouvez pas supprimer une incident cloturé !')
        return super(Incident, self).unlink()

    #
    # def get_attachment_ids(self):
    #     for rec in self:
    #         attachment_ids = self.env['ir.attachment'].search([('res_id', '=', rec.id),
    #                                                            ('res_model', '=', 'cna.activitie')])
    #         return attachment_ids or False
    #
    #

class PersonneAvise(models.Model):
    _name = 'incident.personne.avise'

    name = fields.Char(required=True, string='Nom')

class AgentIntervenant(models.Model):
    _name = 'agent.intervenant'

    name = fields.Char(required=True, string='Nom')


class Site(models.Model):
    _name = 'site.site'

    name = fields.Char(required=True, string='Nom')
    lieu_ids = fields.One2many('site.lieu', 'site_id', 'Lieux')
    navire_ids = fields.One2many('navire.navire', 'site_id', 'Navires')


class SiteLieu(models.Model):
    _name = 'site.lieu'

    name = fields.Char(required=True, string='Nom')
    site_id = fields.Many2one('site.site', 'Site', required=True)
    type = fields.Selection(string="Type", selection=[('navire', 'Navire'), ('sol', 'Sol')],
                            required=False)
    navire_id = fields.Many2one(comodel_name="navire.navire", string="Navire", required=False)


class Secours(models.Model):
    _name = 'secours.secours'

    name = fields.Char(required=True, string='Nom')


class ModelImportance(models.Model):
    _name = 'model.importance'

    name = fields.Char(required=True, string='Model')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Critique')], string="Importance")


class MesurePrise(models.Model):
    _name = 'mesure.prise'

    name = fields.Char(string="Nom", required=True, )




class Navire(models.Model):
    _name = 'navire.navire'

    name = fields.Char('Navire', required=True)
    site_id = fields.Many2one('site.site', 'Site', required=True)
