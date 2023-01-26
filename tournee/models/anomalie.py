# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'barcodes.barcode_events_mixin', "timer.mixin"]

    tag_anomalie_ids = fields.One2many('task.tags.line', 'task_id', 'Tags')
    anomalie_ids = fields.One2many('tags.task.anomalie', 'task_id', 'Anomalie')
    has_anomalies = fields.Boolean(compute='compute_has_anomalies', store=True)
    navire_id = fields.Many2one('navire.navire', 'Navire')
    ronde_id = fields.Many2one('ronde.ronde', 'Ronde')
    score = fields.Float(string="Score", compute='_compute_score', store=True)
    comments = fields.Text(string="commentaires", required=False)
    tourne_duration = fields.Float('Temps total passé à bord (min)', compute='compute_temps_total', store=True)
    temps_passage_avg = fields.Float('Temps passage moyen', compute='compute_temps_passage_avg', store=True)
    first_scan = fields.Datetime(string='Premier scan', compute='compute_temps_total', store=True)
    last_scan = fields.Datetime(string='Dernier scan', compute='compute_temps_total', store=True)
    access_point = fields.Selection(string = "Point d'Accès", selection = [('navire', 'Navire'), ('sol', 'Sol')],
                                    required = True, tracking = True, default = 'navire')
    lieu = fields.Many2one('site.lieu', "Lieu", tracking = True)


    @api.depends('anomalie_ids')
    def compute_has_anomalies(self):
        for rec in self:
            rec.has_anomalies = True if rec.anomalie_ids else False

    @api.depends('tag_anomalie_ids', 'tag_anomalie_ids.temps_passage', 'tag_anomalie_ids.date_scan_ok')
    def compute_temps_passage_avg(self):
        for rec in self:
            temps_passage_avg =0
            if rec.tag_anomalie_ids:
                tag_anomalie_ids = rec.tag_anomalie_ids.filtered(lambda r: r.date_scan_ok)
                if tag_anomalie_ids and len(tag_anomalie_ids)>1:
                    temps_passage_avg = sum(t.temps_passage for t in tag_anomalie_ids)/(len(tag_anomalie_ids)-1)
            rec.temps_passage_avg =temps_passage_avg

    @api.depends('tag_anomalie_ids', 'tag_anomalie_ids.scan_date')
    def compute_temps_total(self):
        for rec in self:
            tourne_duration =0
            tag_anomalie_ids = rec.tag_anomalie_ids.filtered(lambda r: r.scan_date).sorted('scan_date')
            if tag_anomalie_ids and len(tag_anomalie_ids)>1:
                tourne_duration = (tag_anomalie_ids[-1].scan_date - tag_anomalie_ids[0].scan_date).total_seconds()/60
            if tag_anomalie_ids:
                rec.first_scan = tag_anomalie_ids[0].scan_date
                rec.last_scan = tag_anomalie_ids[-1].scan_date
            else:
                rec.first_scan = False
                rec.last_scan = False
            rec.tourne_duration = tourne_duration

    @api.depends('stage_id')
    def _compute_fsm_done(self):
        super()._compute_fsm_done()

    @api.depends('tag_anomalie_ids', 'tag_anomalie_ids.state')
    def _compute_score(self):
        for rec in self:
            all_tags = rec.tag_anomalie_ids.filtered(lambda line: line.hors_parcours == False)
            all_scaned_tags = rec.tag_anomalie_ids.filtered(
                lambda line: line.hors_parcours == False and line.state == 'done')

            if len(all_tags) != 0:
                rec.score = (len(all_scaned_tags) / len(all_tags)) * 100
            else:
                rec.score = 0

    @api.onchange('ronde_id')
    def onchange_ronde(self):
        if self.tag_anomalie_ids and all(l.state == 'draft' for l in self.tag_anomalie_ids):
            self.tag_anomalie_ids.unlink()
        if self.ronde_id.tag_ids:
            for tag in self.ronde_id.tag_ids:
                tag_add = self.tag_anomalie_ids.new({
                    'tag_id': tag.tag_id.id,
                    'is_required': tag.is_required,

                })
                self.tag_anomalie_ids += tag_add

    def action_fsm_validate(self):
        result = super(ProjectTask, self).action_fsm_validate()

        for task in self:
            for tag in task.tag_anomalie_ids:
                if tag.is_required and (tag.state == 'draft' or not tag.scan_date):
                    raise UserError('Attention, il faut scanner tous les tags obligatoire')
        return result

    def task_done(self):
        return {
            'name': 'Cloturé tourné',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'context': {'default_is_required': True if self.score != 1 else False},
            'res_model': 'add.comment.task.wizard',
            'target': 'new',
            'view_type': 'form'
        }

    def on_barcode_scanned(self, barcode):

        tag = self.env['tags.tags'].search([('name', '=', barcode)], limit=1)

        if not tag:
            raise UserError('Aucun tag trouvé pour avec le nom %s' % barcode)
        else:
            if tag.is_start_scan and tag.is_end_scan:
                raise UserError("Ce tag est un tag de démarrage et d'arrêt en même temps")
            elif tag.is_start_scan:
                self.action_timer_start()
            elif tag.is_end_scan:
                self.action_timer_stop()

            if tag in self.tag_anomalie_ids.mapped('tag_id'):
                self.tag_anomalie_ids.filtered(lambda r: r.tag_id == tag).write({'state': 'done',
                                                                                 'scan_date': fields.Datetime.now(
                                                                                     self)})
            else:
                tag_add = self.tag_anomalie_ids.new({
                    'tag_id': tag.id,

                })
                self.tag_anomalie_ids += tag_add

        if self._origin and self.display_timer_start_primary or self.display_timer_start_secondary:
            self._origin.action_timer_start()
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    def get_all_comments(self):
        return self.env['tags.task.anomalie'].search([('line_id', 'in', self.tag_anomalie_ids.mapped('id'))]).mapped(
            'anomalie_commentaire_id.name') or False

    def action_timer_stop(self):

        if self.user_timer_id.timer_start and self.display_timesheet_timer:
            rounded_hours = self._get_rounded_hours(self.user_timer_id._get_minutes_spent())
            wizard_object = self.env['project.task.create.timesheet'].create({
                'time_spent': rounded_hours,
                'description': 'Tournée .....',
                'task_id': self.id
            })
            wizard_object.save_timesheet()
        else:
            return False
    def open_all_anomalies(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Anomalies',
            'res_model': 'tags.task.anomalie',
            'view_mode': 'tree',
            'domain': [('task_id', '=', self.id)]
        }


class TaskTagsLine(models.Model):
    _name = 'task.tags.line'
    _rec_name = 'task_id'

    tag_id = fields.Many2one('tags.tags', 'Tag', required=True)
    navire_id = fields.Many2one(related='tag_id.navire_id', store=True, string='Navire', index=True)

    task_id = fields.Many2one('project.task', 'Tournée')
    anomalie_ids = fields.One2many('tags.task.anomalie', 'line_id', 'Anomalies')
    state = fields.Selection([('draft', 'Brouillon'), ('done', 'Scané')], default='draft', string='Etat')
    scan_date = fields.Datetime('Moment du scan')
    is_required = fields.Boolean(string="Obligatoire")
    hors_parcours = fields.Boolean(string="Hors Parcours", compute='_compute_hors_parcours', store=True)
    temps_passage = fields.Float(compute='compute_temps_passage', store=True, string='Temps passage(min)')
    temps_passage_daily = fields.Float(compute='compute_temps_passage_daily', store=True, string='Temps passage journalière(min)')
    date_scan_ok = fields.Boolean(compute='check_scan_date', store=True)
    scan_week = fields.Char(compute='compute_date_parameters', store=True, string="Semaine")
    scan_month = fields.Char(compute='compute_date_parameters', store=True, string="Mois")
    scan_year = fields.Char(compute='compute_date_parameters', store=True, string="Année")
    scan_week_first_day = fields.Date(compute='compute_date_parameters', store=True,
                                      string="Premier jours de la semaine")
    scan_week_last_day = fields.Date(compute='compute_date_parameters', store=True,
                                     string="Premier jours de la semaine")

    @api.depends('scan_date')
    def compute_date_parameters(self):
        for rec in self:
            scan_week = ''
            scan_month = ''
            scan_year = ''
            scan_week_first_day = False
            scan_week_last_day = False
            if rec.scan_date:
                scan_week = rec.scan_date.isocalendar()[1]
                scan_month = rec.scan_date.month
                scan_year = rec.scan_date.year
                scan_week_first_day = rec.scan_date - timedelta(days=rec.scan_date.weekday())
                scan_week_last_day = scan_week_first_day + timedelta(days=6)
            rec.scan_week = scan_week
            rec.scan_month = scan_month
            rec.scan_year = scan_year
            rec.scan_week_first_day = scan_week_first_day
            rec.scan_week_last_day = scan_week_last_day
    @api.depends('scan_date')
    def check_scan_date(self):
        for rec in self:
            date_scan_ok = False
            if rec.scan_date:
                if 0<= rec.scan_date.weekday() <=4 and  6<=rec.scan_date.hour<=22:
                    date_scan_ok = True
                elif rec.scan_date.weekday() ==5 and 6<=rec.scan_date.hour<=14:
                    date_scan_ok = True
            rec.date_scan_ok = date_scan_ok

    @api.depends('task_id', 'task_id.tag_anomalie_ids','task_id.tag_anomalie_ids.scan_date', 'scan_date')
    def compute_temps_passage(self):
        for rec in self:
            temps_passage =0
            if rec.scan_date and rec.date_scan_ok:
                previous_scans = rec.task_id.tag_anomalie_ids.filtered(lambda r:  r.id != rec.id and r.scan_date and r.scan_date <rec.scan_date).sorted('scan_date', reverse=True)
                if previous_scans  and  previous_scans[0].date_scan_ok:
                    temps_passage = (rec.scan_date - previous_scans[0].scan_date).total_seconds()/60
            rec.temps_passage = temps_passage

    @api.depends('task_id', 'task_id.tag_anomalie_ids', 'task_id.tag_anomalie_ids.scan_date', 'scan_date')
    def compute_temps_passage(self):
        for rec in self:
            temps_passage = 0
            if rec.scan_date and rec.date_scan_ok:
                print('====rec.scan_date', rec.scan_date)
                previous_scans = rec.task_id.tag_anomalie_ids.filtered(lambda r:  r.id != rec.id and r.scan_date and r.scan_date <rec.scan_date and r.scan_date.strftime('%d/%m/%Y') == rec.scan_date.strftime('%d/%m/%Y')).sorted('scan_date', reverse=True)
                print('previous_scans',previous_scans)
                if previous_scans and previous_scans[0].date_scan_ok:
                    temps_passage = (rec.scan_date - previous_scans[0].scan_date).total_seconds()/60
            rec.temps_passage = temps_passage

    @api.depends('tag_id')
    def _compute_hors_parcours(self):
        for rec in self:
            rec.hors_parcours = False
            if not rec.task_id.ronde_id.tag_ids.filtered(lambda line: line.tag_id == rec.tag_id):
                rec.hors_parcours = True

    def open_tags_anomalie(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('tournee.action_tags_anomalie_tournee')
        action['domain'] = [('line_id', '=', self.id)]
        action['context'] = {'default_line_id': self.id,
                             'default_tag_id': self.tag_id.id}
        if not self.anomalie_ids:
            return {'res_model': 'tags.task.anomalie',
             'type'     : 'ir.actions.act_window',
             'context'  : {'default_line_id': self.id,
                             'default_tag_id': self.tag_id.id},
             'view_mode': 'form',
             'view_type': 'form',
             'view_id'  : self.env.ref("tournee.task_tags_anomalie_form_view").id,
             'target'   : 'new'}
        else:
            return {'res_model': 'tags.task.anomalie',
            'type': 'ir.actions.act_window',
            'context': {'default_line_id': self.id,
                             'default_tag_id': self.tag_id.id},

            'domain': [('line_id', '=', self.id)],
            'view_mode': 'tree,form,pivot,graph',
            'view_type': 'form',
            'target': 'current'}



    def get_anomalies(self):
        return self.env['tags.task.anomalie'].search([('line_id', '=', self.id)]) or False


class TagsTaskAnomalie(models.Model):
    _name = "tags.task.anomalie"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'documents.mixin']
    _order = "anomalie_id, anomalie_commentaire_id"

    def _get_document_tags(self):
        return self.company_id.project_tags

    def _get_document_folder(self):
        return self.company_id.project_folder

    def _check_create_documents(self):
        return self.company_id.documents_project_settings and super()._check_create_documents()

    def action_anomalie_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env['ir.model.data']._xmlid_to_res_id('tournee.email_template_anomalie')
        template = self.env['mail.template'].browse(template_id)

        ctx = {
            'default_model': 'tags.task.anomalie',
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

    def name_get(self):
        res = []
        for record in self:
            name = record.tag_id.name
            if record.task_id:
                name += '/ ' + record.task_id.name
            res.append((record.id, name))
        return res

    tag_id = fields.Many2one('tags.tags', 'Lieu')
    navire_id = fields.Many2one('navire.navire', related='tag_id.navire_id', store=True, string='Navire')
    designation = fields.Char('Designation', related='tag_id.designation', store=True)
    line_id = fields.Many2one('task.tags.line', 'Ligne de tournée')
    task_id = fields.Many2one('project.task', related='line_id.task_id', store=True, string='Tournée')
    partner_id = fields.Many2one('res.partner', related='task_id.partner_id', store=True, string='Client')
    anomalie_id = fields.Many2one('tags.anomalie', string="Anomalie", required=True)
    anomalie_commentaire_id = fields.Many2one('tags.anomalie.commentaire', 'Commentaire')
    criticite = fields.Char('Criticité', related='anomalie_commentaire_id.criticite', store=True)
    date_anomalie = fields.Datetime(default=fields.Datetime.now())
    date = fields.Date(compute='split_date_anomalie', store=True)
    hour = fields.Float(compute='split_date_anomalie', store=True, string='Heure')
    respo_zone_id = fields.Many2one('res.users', 'Responsable zone', related="tag_id.respo_zone_id",
                                         store=True)
    depuis_le = fields.Datetime('Depuis le', default=fields.Datetime.now)
    state = fields.Selection([('draft', 'Prise en compte'), ('resolu', 'Résolu')], string='Etat')
    comment = fields.Char("Notes")
    document_id = fields.Many2one('documents.document', compute="compute_attachement")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    url = fields.Char(related='create_share_id.full_url', string="Lien photo")
    create_share_id = fields.Many2one('documents.share', compute="compute_attachement")

    # attachement_id = fields.Many2one('documents.share', compute="compute_doc_url")

    # use it for report (anomalies)
    year = fields.Char(string="Année", required=False, compute="_compute_dates", store=True)
    month = fields.Selection(string="Mois", selection=[('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'), ('5', 'Mail'), ('6', 'Juin'),
                                                       ('7', 'Juillet'), ('8', 'Aout'), ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
                                                       ], compute="_compute_dates", store=True)
    week = fields.Char(string="Semaine", required=False, compute="_compute_dates", store=True)
    day = fields.Selection(string="Jour", selection=[('0', 'Lundi'), ('1', 'Mardi'), ('2', 'Mercredi'), ('3', 'Jeudi'), ('4', 'Vendredi'), ('5', 'Samedi'), ('6', 'Dimande')], compute="_compute_dates", store=True)

    lot = fields.Char(string="Lot", related="tag_id.lot", store=True)
    pont = fields.Char(string="Pont", related="tag_id.pont", store=True)
    bd_td_axe = fields.Selection(string="Bd/Td/Axe", related="tag_id.bd_td_axe", store=True)

    couple = fields.Char(string="Couple", related="tag_id.couple", store=True)
    respo_zone_id = fields.Many2one(string="Responsable zone", related="tag_id.respo_zone_id", store=True)

    red_color_criticite = fields.Boolean(compute="_compute_criticite_colors", default=False)
    orange_color_criticite = fields.Boolean(compute="_compute_criticite_colors", default=False)
    yellow_color_criticite = fields.Boolean(compute="_compute_criticite_colors", default=False)

    green_color_state = fields.Boolean(compute="_compute_state_colors", default=False)
    blue_color_state = fields.Boolean(compute="_compute_state_colors", default=False)

    already_reported = fields.Boolean(compute='compute_already_reported', default=False)


    @api.depends('tag_id', 'anomalie_id', 'anomalie_commentaire_id', 'date_anomalie')
    def compute_already_reported(self):
        for record in self:
            already_reported = False
            same_tags_task_anomalies = record.env['tags.task.anomalie'].sudo().search(
                [('tag_id', '=', record.tag_id.id), ('date_anomalie', '<=', record.date_anomalie), ('date_anomalie', '!=', False), ('id', '!=', record.id)]).sorted('date_anomalie')
            if same_tags_task_anomalies:

                if same_tags_task_anomalies[-1].anomalie_id == record.anomalie_id and same_tags_task_anomalies[-1].anomalie_commentaire_id == record.anomalie_commentaire_id:
                    already_reported = True
            record.already_reported = already_reported

    @api.depends('date_anomalie')
    def _compute_dates(self):
        for anomalie in self:
            anomalie.year = anomalie.date_anomalie.year
            anomalie.month = str(anomalie.date_anomalie.month)
            anomalie.week = anomalie.date_anomalie.isocalendar()[1]
            anomalie.day = str(anomalie.date_anomalie.weekday())

    @api.depends('criticite')
    def _compute_criticite_colors(self):
        for anomalie in self:
            if anomalie.criticite == "1":
                anomalie.red_color_criticite = True
                anomalie.yellow_color_criticite = False
                anomalie.orange_color_criticite = False
            elif anomalie.criticite == "2":
                anomalie.red_color_criticite = False
                anomalie.yellow_color_criticite = False
                anomalie.orange_color_criticite = True
            elif anomalie.criticite == "3":
                anomalie.red_color_criticite = False
                anomalie.yellow_color_criticite = True
                anomalie.orange_color_criticite = False
            else:
                anomalie.red_color_criticite = False
                anomalie.orange_color_criticite = False
                anomalie.yellow_color_criticite = False

    @api.depends('state')
    def _compute_state_colors(self):
        for anomalie in self:
            if anomalie.state == "resolu":
                anomalie.green_color_state = True
                anomalie.blue_color_state = False
            elif anomalie.state == "draft":
                anomalie.green_color_state = False
                anomalie.blue_color_state = True
            else:
                anomalie.green_color_state = False
                anomalie.blue_color_state = False

    def compute_attachement(self):
        for rec in self:
            document = self.env['documents.document'].search([('res_id', '=', rec.id), ('type', '=', 'binary'),
                                                              ('mimetype', 'like', 'image'),
                                                              ('res_model', '=', 'tags.task.anomalie')])
            if document:
                rec.document_id = document[0].id

                share = self.env['documents.share'].search([('document_ids', 'in', document[0].id)])
                if share:
                    rec.create_share_id = share[0].id
                else:
                    vals = {
                        'type'        : 'ids',
                        'document_ids': [(6, 0, document[0].ids)],
                        'folder_id'   : document[0].folder_id.id,
                    }
                    new_context = dict(self.env.context)
                    new_context.update({
                        'default_owner_id'    : self.env.uid,
                        'default_folder_id'   : vals.get('folder_id'),
                        'default_tag_ids'     : vals.get('tag_ids'),
                        'default_type'        : vals.get('type', 'domain'),
                        'default_domain'      : vals.get('domain') if vals.get('type', 'domain') == 'domain' else False,
                        'default_document_ids': vals.get('document_ids', False),
                    })
                    share = self.with_context(new_context).env['documents.share'].create(vals)
                    share.action_generate_url()
                    # document[0].create_share()
                    # share = self.env['documents.share'].search([('document_ids', 'in', document[0].id)])
                    if share:

                        rec.create_share_id = share.id
                    else:
                        rec.create_share_id = False

            else:
                rec.document_id = False
                rec.create_share_id = False

    def open_tournee(self):
        return {
            'name': 'Mes tourné',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'project.task',
            'target': 'self',

            'context': {'fsm_mode': True,
                        'show_address': True,},

            'view_type': 'form',
            'res_id': self.task_id.id
        }
    @api.depends('date_anomalie')
    def split_date_anomalie(self):
        for rec in self:
            rec.date = rec.date_anomalie.date()
            time = fields.Datetime.context_timestamp(self, rec.date_anomalie)
            rec.hour = time.hour + time.minute / 60.0

    # def compute_attachement(self):
    # 	for rec in self:
    # 		attachement = self.env['ir.attachment'].search([('res_id', '=', rec.id),
    #                                                         ('res_model', '=', 'tags.task.anomalie')])
    # 		if attachement:
    #
    # 			document = self.env['documents.document'].search([('attachment_id', '=', attachement[0].id)])
    #
    # 			if document:
    # 				rec.document_id = document[0].id
    # 				rec.document_id.create_share()
    #
    # 			else:
    # 				attach = attachement[0]
    # 				# vals = {'name': attach.name,
    # 				# 		'description': attach.description,
    # 				# 		'res_model': attach.res_model,
    # 				# 		'res_field': attach.res_field,
    # 				# 		'res_id': attach.res_id,
    # 				# 		'type': attach.type,
    # 				# 		'url': attach.url,
    # 				# 		'public': attach.public,
    # 				# 		'access_token': attach.access_token,
    # 				# 		'raw': attach.raw,
    # 				# 		'datas': attach.datas,
    # 				# 		'db_datas': attach.db_datas,
    # 				# 		'store_fname': attach.store_fname,
    # 				# 		'file_size': attach.file_size,
    # 				# 		'checksum': attach.checksum,
    # 				# 		'mimetype': attach.mimetype,
    # 				# 		'index_content': attach.index_content,
    # 				# 		'company_id': attach.company_id and attach.company_id.id,
    # 				# 		}
    # 				# doc = attachement[0].sudo()._create_document(vals)
    # 				# print('dooooooooooooc', doc)
    #
    # 				document = self.env['documents.document'].search(
    # 					[('attachment_id', '=', attachement[0].id)])
    # 				if document:
    #
    # 					rec.document_id = document[0].id
    # 					rec.document_id.create_share()
    # 				else:
    # 					rec.document_id = False
    #
    #
    #
    # 		else:
    # 			rec.document_id =False



class TagsAnomalie(models.Model):
    _name = 'tags.anomalie'
    _order = "name"
    _rec_name ='name'

    name = fields.Char('Nom', required=True)
    commentaire_ids = fields.One2many('tags.anomalie.commentaire', 'anomalie_id', string="Commentaires")


class TagsAnomalieCommentaire(models.Model):
    _name = "tags.anomalie.commentaire"

    name = fields.Char('commentaire', required=True)
    criticite = fields.Char('Criticité', required=True)
    anomalie_id = fields.Many2one('tags.anomalie', 'Anomalie')
