# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Tags(models.Model):
	_name = 'tags.tags'

	name = fields.Char('Nom', compute="compute_tags_name", store=True)
	site_id = fields.Many2one('site.site', 'Site', required=True)
	navire_id = fields.Many2one('navire.navire', 'Navire', required=False)
	respo_zone_id = fields.Many2one('res.users', 'Responsable zone')
	pont = fields.Char()
	couple = fields.Char()
	lot = fields.Char()
	numero = fields.Char(required=True, default='/')
	designation = fields.Char()
	last_date_scan = fields.Datetime(string="Dernier date du scan", required=False, compute="compute_last_scan", store=True)
	bd_td_axe = fields.Selection(string="Bd/Td/Axe", selection=[('bd', 'bd'), ('td', 'td'), ('axe', 'axe')], required=False)
	tag_file = fields.Binary(string="Fichier de tag")
	tag_line_ids = fields.One2many('task.tags.line', 'tag_id', 'Scan')
	is_start_scan = fields.Boolean(string="Tag de démarrage", )
	is_end_scan = fields.Boolean(string="Tag d'arrêt", )
	access_point = fields.Selection(string = "Point d'Accès", selection = [('navire', 'Navire'), ('sol', 'Sol')],
									required = True, tracking = True, default='navire')
	lieu = fields.Many2one('site.lieu', "Lieu", tracking = True)

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
			if rec.designation:
				name += ' ' + rec.designation
			if rec.navire_id:
				name += ' - '+rec.navire_id.name
			elif rec.lieu:
				name += ' - '+ rec.lieu.name
			if rec.lot:
				name += ' Lot '+rec.lot
			if rec.couple:
				name +=  ' - '+rec.couple
			if rec.pont:
				name += ' '+ rec.pont
			rec.name = name.strip()


	@api.model
	def create(self, vals):
		if not vals.get('numero', False) or vals['numero'] == '/':
			vals['numero'] = self.env['ir.sequence'].next_by_code('tags.tags') or ''
		return super(Tags, self).create(vals)

	def action_see_all_scan(self):
		return {
			'name': _('Tout les scan'),
			'type': 'ir.actions.act_window',
			'view_mode': 'tree',
			'res_model': 'task.tags.line',
			'domain': [('tag_id', '=', self.id)],
		}


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
	tag_id = fields.Many2one('tags.tags', 'Tag', required=True)
	ronde_id = fields.Many2one('ronde.ronde', 'Ronde')
	is_required = fields.Boolean(string="Obligatoire")
