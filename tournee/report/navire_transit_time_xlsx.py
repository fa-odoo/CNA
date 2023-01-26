# -*- coding: utf-8 -*-

from odoo import models, fields
from dateutil.rrule import rrule, MONTHLY
import random
from datetime import timedelta
import numpy as np

class NavireTransitTimeXlsx(models.AbstractModel):
    _name = 'report.tournee.navire_transit_time_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        diff_time = False
        i = 1
        docs = []
        cr = self.env.cr
        th_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9D9D9'})
        td_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
        tag_ids = self.env['tags.tags'].sudo().search([('navire_id', 'in', data['navire_ids'])], order='navire_id')

        cr.execute(""
                   "SELECT tag_id, scan_date, temps_passage_daily FROM "
                   "(SELECT *, ROW_NUMBER() OVER (PARTITION BY "
                   "tag_id, DATE(scan_date) ORDER BY scan_date DESC) AS Row_ID FROM (SELECT * FROM task_tags_line WHERE scan_date is not null AND tag_id IN %s AND DATE(scan_date) >= DATE(%s) AND DATE(scan_date) <= DATE(%s) AND temps_passage_daily is not null and date_scan_ok is True) as res"
                   ") AS A WHERE Row_ID <2",
                   (tuple(tag_ids.ids), data['date_start'], data['date_end']))
        dict_keys = {tag_id: [] for tag_id in tag_ids.ids}
        _ = {dict_keys[x[0]].append([x[1], x[2]]) for x in cr.fetchall()}

        for tag_id in tag_ids:
            tag_line = False
            tag_content = dict_keys.get(tag_id.id, False)
            if tag_content:
                tag_line = [tag_id.navire_id.name, tag_id.name]
                if data['navire_ids'] == 'week':
                    diff_day = 6
                else:
                    start_date = fields.Date.from_string(data['date_start'])
                    end_date = fields.Date.from_string(data['date_end'])
                    # Get number of sunday between start and end date
                    nb_sun = np.busday_count(str(start_date), str(end_date), weekmask='Sun')
                    delta = end_date - start_date
                    diff_day = delta.days - nb_sun
                res_avg = (sum([x[1] for x in tag_content]) + ((diff_day - len(tag_content)) * 24)) / diff_day
                res_avg = timedelta(minutes=res_avg)
                tag_line.extend([tag_content[-1][0], str(res_avg).split('.')[0]])
                if diff_time:
                    diff_time += res_avg
                else:
                    diff_time = res_avg
            if tag_line:
                docs.append(tag_line)

        sheet = workbook.add_worksheet(data['date_start'] + ' au ' + data['date_end'])
        sheet.write(0, 0, 'NAVIRE', th_format)
        sheet.set_column(0, 0, 20)
        sheet.write(0, 1, 'TAG', th_format)
        sheet.set_column(1, 1, 50)
        sheet.write(0, 2, 'DATE DERNIER SCAN', th_format)
        sheet.write(0, 3, 'TEMPS Moyenne', th_format)
        sheet.set_column(2, 3, 30)

        for doc in docs:
            sheet.write(i, 0, doc[0], td_format)
            sheet.write(i, 1, doc[1], td_format)
            sheet.write(i, 2, doc[2].strftime('%d/%m/%Y %H:%M') if doc[2] != '' else '', td_format)
            sheet.write(i, 3, doc[3], td_format)
            i += 1
        sheet.write(i, 3, "Moyenne = {}".format(str(diff_time/(len(docs) or 1)).split('.')[0]), td_format)
