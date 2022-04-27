# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Tags(models.Model):
	_name = 'tags.tags'

	name = fields.Char('Nom', compute="compute_tags_name", store=True)
	site_id = fields.Many2one('site.site', 'Site', required=True)
	navire_id = fields.Many2one('navire.navire', 'Navire', required=True)
	charge_security_id = fields.Many2one('res.users', 'Chargé de sécurité')
	bloc = fields.Char()
	couple = fields.Char()
	lot = fields.Char()
	numero = fields.Char(required=True, default='/')
	position = fields.Char()
	last_date_scan = fields.Datetime(string="Dernier date du scan", required=False)
	tag_file = fields.Boolean(string="Fichier de tag")

	@api.depends('navire_id', 'bloc', 'position', 'numero', 'lot', 'couple' )
	def compute_tags_name(self):
		for rec in self:
			name = rec.numero or ''
			if rec.position:
				name += ' '+ rec.position
			if rec.navire_id:
				name += ' - '+rec.navire_id.name
			if rec.lot:
				name += ' Lot '+rec.lot
			if rec.couple:
				name +=  ' - '+rec.couple
			if rec.bloc:
				name += ' '+ rec.bloc
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
