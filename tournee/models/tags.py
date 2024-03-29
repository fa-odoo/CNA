# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import unicodedata
import regex
import datetime

class Tags(models.Model):
	_name = 'tags.tags'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char('Nom', compute="compute_tags_name", store=True, tracking = True)
	site_id = fields.Many2one('site.site', 'Site', required=True, tracking = True)
	navire_id = fields.Many2one('navire.navire', 'Navire', required=False, tracking = True)
	respo_zone_id = fields.Many2one('res.users', 'Responsable zone', tracking = True)
	pont = fields.Char( tracking = True)
	couple = fields.Char( tracking = True)
	lot = fields.Char(tracking = True)
	numero = fields.Char(required=True, default='/', copy=False, tracking = True)
	designation = fields.Char( tracking = True)
	last_date_scan = fields.Datetime(string="Dernier date du scan", required=False, compute="compute_last_scan", store=True, tracking = True)
	bd_td_axe = fields.Selection(string="Bd/Td/Axe", selection=[('bd', 'bd'), ('td', 'td'), ('axe', 'axe')], required=False, tracking = True)
	tag_file = fields.Binary(string="Fichier de tag", tracking = True)
	tag_line_ids = fields.One2many('task.tags.line', 'tag_id', 'Scan')
	is_start_scan = fields.Boolean(string="Tag de démarrage", tracking = True)
	is_end_scan = fields.Boolean(string="Tag d'arrêt", tracking = True )
	access_point = fields.Selection(string = "Point d'Accès", selection = [('navire', 'Navire'), ('sol', 'Sol')],
									required = True, tracking = True, default='navire')
	lieu = fields.Many2one('site.lieu', "Lieu", tracking = True)
	active = fields.Boolean('Active', default=True, tracking=True)
	is_account_in_scan = fields.Boolean(string="Prise en compte temps de passage", default=True, tracking = True)
	date_no_scan_ids = fields.One2many(comodel_name="tags.date.no.scan", inverse_name="tag_id", string="Dates")

	def uncheck_is_account_in_scan(self):
		for rec in self:
			rec.is_account_in_scan = False


	@api.model
	def create(self, vals):
		if not vals.get('numero', False) or vals['numero'] == '/':
			vals['numero'] = self.env['ir.sequence'].next_by_code('tags.tags') or ''
		res = super(Tags, self).create(vals)
		if not res.is_account_in_scan:
			start_date = datetime.datetime.now().date() - datetime.timedelta(
				days=datetime.datetime.now().date().weekday())
			old_change = self.env['tags.date.no.scan'].search(
				[('tag_id', '=', res.id), ('start_date', '=', start_date)])
			if not old_change:
				self.env['tags.date.no.scan'].create({'change_date': fields.Date.context_today(self),
													  'tag_id': res.id,
													  'start_date': start_date
													  })
		return res
	def write(self, vals):
		is_account_in_scan_dict = {l.id: l.is_account_in_scan for l in self}
		res = super().write(vals)
		for rec in self:
			if any('is_account_in_scan' in value for value in vals):
				if rec.is_account_in_scan != is_account_in_scan_dict[rec.id]:
					if rec.is_account_in_scan:
						dates_lines = self.env['tags.date.no.scan'].search([('tag_id', '=', rec.id), ('end_date', '=', False)])
						dates_lines.write({'end_date': datetime.datetime.now().date() + datetime.timedelta(
								days=(6 - datetime.datetime.now().date().weekday()))})
					else:
						start_date = datetime.datetime.now().date() - datetime.timedelta(
							days=datetime.datetime.now().date().weekday())
						old_change = self.env['tags.date.no.scan'].search(
							[('tag_id', '=', rec.id), ('start_date', '=', start_date)])
						if not old_change:
							self.env['tags.date.no.scan'].create({'change_date': fields.Date.context_today(self),
																  'tag_id': rec.id,
																  'start_date': start_date
																  })
		return res

	@api.depends('is_account_in_scan')
	def _compute_date_no_scan_ids(self):
		for rec in self:
			if not rec.is_account_in_scan:
				start_date = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().date().weekday())
				old_change = self.env['tags.date.no.scan'].search([('tag_id', '=', self.id),('start_date', '=',start_date) ])
				if not old_change:
					self.env['tags.date.no.scan'].create({'change_date': fields.Date.context_today(self),
						'tag_id': self.id,
						'start_date': start_date
					})
			elif rec.is_account_in_scan:
				date = self.env['tags.date.no.scan'].search([('tag_id', '=', self.id), ('end_date', '=', False)])
				for d in date:
					d.end_date = datetime.datetime.now().date() + datetime.timedelta(days=(6 - datetime.datetime.now().date().weekday()))
	
	@api.onchange('access_point')
	def onchange_access_point(self):
		if self.access_point == 'navire':
			self.lieu = False
		elif self.access_point == 'sol':
			self.navire_id = False

	@api.constrains('is_start_scan', 'is_end_scan')
	def _check_start_end_tag(self):
		for tag in self:
			if tag.is_start_scan and tag.is_end_scan:
				raise UserError("Vous pouvez pas avoir un tag de démarrage et d'arrêt en même temps")

	@api.depends('tag_line_ids', 'tag_line_ids.scan_date')
	def compute_last_scan(self):
		for rec in self:
			last_date_scan = False
			if rec.tag_line_ids:
				tag_line_ids = rec.tag_line_ids.filtered(lambda r: r.scan_date)
				if tag_line_ids:
					last_date_scan = tag_line_ids.sorted('scan_date')[-1].scan_date
			rec.last_date_scan = last_date_scan

	@api.depends('navire_id', 'pont', 'designation', 'numero', 'lot', 'couple', 'lieu' )
	def compute_tags_name(self):
		for rec in self:
			name = rec.numero or ''
			if rec.access_point == 'sol':
				if rec.designation:
					name += ' ' + rec.designation
				if rec.lieu:
					name += ' - ' + rec.lieu.name
				if rec.lot:
					name += ' Lot ' + rec.lot
				if rec.couple:
					name += ' - ' + rec.couple
				if rec.pont:
					name += ' ' + rec.pont
			else:
				if rec.navire_id:
					name += ' - ' + rec.navire_id.name
				if rec.pont:
					name += ' - Pont ' + rec.pont
				if rec.lot:
					name += ' - Lot ' + rec.lot
				if rec.couple:
					name += ' - ' + rec.couple
				if rec.bd_td_axe:
					name += ' - ' + rec.bd_td_axe
				if rec.designation:
					name += ' - ' + rec.designation


			rec.name = regex.sub(r"\p{Mn}", "", unicodedata.normalize("NFKD", name.strip()))



	def action_see_all_scan(self):
		return {
			'name': _('Tout les scan'),
			'type': 'ir.actions.act_window',
			'view_mode': 'tree',
			'res_model': 'task.tags.line',
			'domain': [('tag_id', '=', self.id)],
		}


class TagsDateNoScan(models.Model):
	_name = 'tags.date.no.scan'
	_rec_name = 'start_date'

	start_date = fields.Date(string="Date Début", required=True)
	end_date = fields.Date(string="Date Fin", required=False)
	change_date = fields.Date()

	tag_id = fields.Many2one(comodel_name="tags.tags", string="Tag",  ondelete="cascade")

	def unlink(self):
		message_log_list = []
		for line in self:
			message_log= "Ligne 'date omis du temps de passage'du : " + str(line.start_date)
			if line.end_date:
				message_log +=' au '+str(line.end_date)
			message_log +=" supprimée par "+ self.env.user.partner_id.name
			message_log_dict ={'tag_id': line.tag_id,'message_log':message_log
						 }
			message_log_list.append(message_log_dict)
		res = super().unlink()
		if res:
			for log_dict in message_log_list:
				log_dict['tag_id'].message_post(body=log_dict['message_log'])
		return res

class Ronde(models.Model):
	_name = 'ronde.ronde'


	name = fields.Char('Ronde', required=True)
	tag_ids = fields.One2many('ronde.tags', 'ronde_id', 'Tags')
	access_point = fields.Selection(string = "Point d'Accès", selection = [('navire', 'Navire'), ('sol', 'Sol')],
									required = True, tracking = True, default = 'navire')
	navire_id = fields.Many2one('navire.navire', 'Navire')
	lieu = fields.Many2one('site.lieu', 'Lieu')

	@api.onchange('access_point')
	def onchange_access_point(self):
		if self.access_point == 'navire':
			self.lieu = False
		elif self.access_point == 'sol':
			self.navire_id = False

	def start_ronde(self):
		if len(self._context.get('active_ids')) > 1:
			raise UserError(_("Vous ne pouvez pas démarrer plusieurs rondes."))

		ctx = {
			'default_project_id': self.env.ref('industry_fsm.fsm_project').id or False,
			'default_partner_id': self.env.user.company_id.partner_id.id or False,
		}
		ronde = self.env['ronde.ronde'].search([('id', '=', self._context.get('active_ids')[0])])
		if ronde:
			ctx['default_name'] = ronde.name
			ctx['default_navire_id'] = ronde.navire_id and ronde.navire_id.id or False
			ctx['default_lieu'] = ronde.lieu and ronde.lieu.id or False
			ctx['default_ronde_id'] = ronde.id
			ctx['default_access_point'] = ronde.access_point




		return {
			'name': _('Ronde'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'project.task',
			'target': 'current',
			'context': ctx
		}


class RondeTags(models.Model):
	_name = 'ronde.tags'

	sequence = fields.Integer(default=1)
	tag_id = fields.Many2one('tags.tags', 'Tag', required=True, ondelete='restrict')
	ronde_id = fields.Many2one('ronde.ronde', 'Ronde')
	is_required = fields.Boolean(string="Obligatoire")
