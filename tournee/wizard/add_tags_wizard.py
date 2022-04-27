# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AddTagsWizard(models.TransientModel):
	_name  = 'add.tags.wizard'

	tag_ids = fields.Many2many('tags.tags', string='Tags')

	def add_tags(self):
		if self.env.context.get('active_id', False) and self.tag_ids:
			active_ronde = self.env['ronde.ronde'].browse(self.env.context.get('active_id', False))
			tags_to_add = self.tag_ids
			if active_ronde.tag_ids:
				tags_to_add = tags_to_add - active_ronde.tag_ids.mapped('tag_id')
			if tags_to_add:
				active_ronde.write({'tag_ids': [(0,0, {'tag_id': tag.id}) for tag in tags_to_add]})


