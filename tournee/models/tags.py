# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Tags(models.Model):
	_name = 'tags.tags'

	name = fields.Char('Nom', compute="compute_tags_name", store=True)
	site_id = fields.Many2one('site.site', 'Site', required=True)
	navire_id = fields.Many2one('navire.navire', 'Navire', required=True)
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

	@api.depends('tag_line_ids', 'tag_line_ids.scan_date')
	def compute_last_scan(self):
		for rec in self:
			last_date_scan = False
			if rec.tag_line_ids:
				tag_line_ids = rec.tag_line_ids.filtered(lambda r: r.scan_date)
				if tag_line_ids:
					last_date_scan = tag_line_ids.sorted('scan_date')[-1].scan_date
			rec.last_date_scan = last_date_scan

	@api.depends('navire_id', 'pont', 'designation', 'numero', 'lot', 'couple' )
	def compute_tags_name(self):
		for rec in self:
			name = rec.numero or ''
			if rec.designation:
				name += ' ' + rec.designation
			if rec.navire_id:
				name += ' - '+rec.navire_id.name
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


	name = fields.Char('Ronde')
	tag_ids = fields.One2many('ronde.tags', 'ronde_id', 'Tags')
	navire_id = fields.Many2one('navire.navire', 'Navire')


class RondeTags(models.Model):
	_name = 'ronde.tags'

	sequence = fields.Integer(default=1)
	tag_id = fields.Many2one('tags.tags', 'Tag', required=True)
	ronde_id = fields.Many2one('ronde.ronde', 'Ronde')
	is_required = fields.Boolean(string="Obligatoire")
