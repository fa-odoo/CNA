# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Navire(models.Model):
	_inherit = 'navire.navire'

	ronde_ids = fields.One2many('project.task', 'navire_id', 'Ronde')
	temps_passage_avg = fields.Float('Temps passage moyen', compute = 'compute_temps_passage_avg', store = True)
	tourne_duration = fields.Float('temps moyen passé à bord', compute = 'compute_temps_total', store = True)

	@api.depends('ronde_ids', 'ronde_ids.tourne_duration')
	def compute_temps_total(self):
		for rec in self:
			tourne_duration =0.0
			ronde_ids = rec.ronde_ids.filtered(lambda r: r.tourne_duration)
			if ronde_ids:
				tourne_duration = sum(r.tourne_duration for r in ronde_ids)/len(ronde_ids)
			rec.tourne_duration = tourne_duration

	@api.depends('ronde_ids', 'ronde_ids.temps_passage_avg')
	def compute_temps_passage_avg(self):
		for rec in self:
			temps_passage_avg = 0.0
			ronde_ids = rec.ronde_ids.filtered(lambda r: r.temps_passage_avg)
			if ronde_ids:
				temps_passage_avg = sum(r.temps_passage_avg for r in ronde_ids)/len(ronde_ids)
			rec.temps_passage_avg = temps_passage_avg

class Lieu(models.Model):
	_inherit = 'site.lieu'

	ronde_ids = fields.One2many('project.task', 'lieu', 'Ronde')
	temps_passage_avg = fields.Float('Temps passage moyen', compute = 'compute_temps_passage_avg', store = True)
	tourne_duration = fields.Float('temps moyen passé à bord', compute = 'compute_temps_total', store = True)

	@api.depends('ronde_ids', 'ronde_ids.tourne_duration')
	def compute_temps_total(self):
		for rec in self:
			tourne_duration =0.0
			ronde_ids = rec.ronde_ids.filtered(lambda r: r.tourne_duration)
			if ronde_ids:
				tourne_duration = sum(r.tourne_duration for r in ronde_ids)/len(ronde_ids)
			rec.tourne_duration = tourne_duration

	@api.depends('ronde_ids', 'ronde_ids.temps_passage_avg')
	def compute_temps_passage_avg(self):
		for rec in self:
			temps_passage_avg = 0.0
			ronde_ids = rec.ronde_ids.filtered(lambda r: r.temps_passage_avg)
			if ronde_ids:
				temps_passage_avg = sum(r.temps_passage_avg for r in ronde_ids)/len(ronde_ids)
			rec.temps_passage_avg = temps_passage_avg
