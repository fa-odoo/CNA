# -*- coding: utf-8 -*-

from odoo import api, fields, models
class NavireTimeReport(models.AbstractModel):
	_name = "report.tournee.navire_time_report"

	@api.model
	def _get_report_values(self, docids, data = None):
		docs = self.env['navire.navire'].browse(data['form']['navire_ids']).sudo()
		start_date = fields.Date.from_string(data['form']['date_start'])
		date_end = fields.Date.from_string(data['form']['date_end'])


		report_data ={}
		for navire in docs:
			report_data[navire] = {'temps_passage_avg': 0.0, 'tourne_duration': 0.0}
			ronde_ids = navire.ronde_ids.filtered(lambda r: r.is_fsm and r.first_scan and r.last_scan and
																										   start_date<=r.first_scan.date()<=date_end and
																										   start_date<=r.last_scan.date()<= date_end)

			if ronde_ids:
				print('dddddddd', len(ronde_ids), sum(l.temps_passage_avg for l in ronde_ids)/len(ronde_ids))
				print('ddddddddssssssss',  sum(l.tourne_duration for l in ronde_ids)/len(ronde_ids))
				report_data[navire]['temps_passage_avg'] = sum(l.temps_passage_avg for l in ronde_ids)/len(ronde_ids)
				report_data[navire]['tourne_duration'] = sum(l.tourne_duration for l in ronde_ids)/len(ronde_ids)


		print('report_datareport_data', report_data)
		return {
			'doc_ids'            : data['form']['navire_ids'],
			'doc_model'          : 'navire.navire',
			'docs'               : docs,
			# 'facture_fournisseur':facture_fournisseur,
			'report_data': report_data,
			'date_start':  start_date,
			'date_end':  date_end
		}
