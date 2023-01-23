# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Navire(models.Model):
	_inherit = 'navire.navire'

	ronde_ids = fields.One2many('project.task', 'navire_id', 'Ronde')
	temps_passage_avg = fields.Float('Temps passage moyen', compute = 'compute_temps_passage_avg', store = True)
	tourne_duration = fields.Float('temps moyen passé à bord', compute = 'compute_temps_total', store = True)
	duration_ids = fields.One2many('navire.duration', 'navire_id', 'Duration')

	def create_navire_time(self):
		self.env.cr.execute("""delete from navire_time;""")
		for navire in self:
			self.env.cr.execute("""
WITH added_row_number AS (
  SELECT
    tag_id, navire_id, scan_date, scan_week, scan_month, scan_year,id,scan_week_first_day, scan_week_last_day,
    ROW_NUMBER() OVER(PARTITION BY scan_week, tag_id, navire_id ORDER BY scan_date DESC) AS row_number
  FROM task_tags_line  where date_scan_ok=True
)
SELECT
  *
FROM added_row_number 
WHERE (row_number = 1 OR row_number = 2) and navire_id =%s;"""%(navire.id))
			dict_times = self.env.cr.dictfetchall()
			tag_dict = {(l['tag_id'],l['scan_week'],l['scan_month'], l['scan_year']) : [] for l in dict_times}
			for l in dict_times:
				tag_dict[(l['tag_id'],l['scan_week'],l['scan_month'], l['scan_year']) ].append((l['scan_week_first_day'], l['scan_date'], l['scan_week_last_day']))
			print('sssssssssssss',tag_dict )
			for elem in tag_dict:
				if len(tag_dict[elem])==2:
					self.env.cr.execute("insert into navire_time (navire_id, tag_id, week_col, month_col, year_col, passage_time, start_date, end_date) values"
										"(%s, %s, %s, %s, %s, %s, '%s', '%s')"
										%(navire.id, elem[0], elem[1], elem[2], elem[3],
										  (tag_dict[elem][0][1] - tag_dict[elem][1][1]).total_seconds() / 3600, tag_dict[elem][0][0],
										  tag_dict[elem][0][2] ))
					self.env.cr.commit()




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
