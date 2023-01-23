# -*- coding: utf-8 -*-

from odoo import models, fields
from dateutil.rrule import rrule, MONTHLY
import random
import datetime


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

        cr.execute("SELECT tag_id, max(scan_date) as end_date, max(scan_date) - min(scan_date) as avg_date FROM "
                   "(SELECT *, ROW_NUMBER() OVER (PARTITION BY "
                   "tag_id ORDER BY scan_date DESC) AS Row_ID FROM (SELECT * FROM task_tags_line WHERE tag_id IN %s AND DATE(scan_date) >= DATE(%s) AND DATE(scan_date) <= DATE(%s) AND scan_date is not null and date_scan_ok is True) as res"
                   ") AS A WHERE Row_ID <3 GROUP BY tag_id",
                   (tuple(tag_ids.ids), data['date_start'], data['date_end']))

        tags_line = {x[0]: [x[1], x[2]] for x in cr.fetchall()}
        for tag_id in tag_ids:
            tag_line = False
            tag_content = tags_line.get(tag_id.id, False)
            if tag_content:
                tag_line = [tag_id.navire_id.name, tag_id.name]
                tag_line.extend([tag_content[0], str(tag_content[1])])
                if diff_time:
                    diff_time += tag_content[1]
                else:
                    diff_time = tag_content[1]
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
