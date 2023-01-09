# -*- coding: utf-8 -*-

from odoo import models, fields
from dateutil.rrule import rrule, MONTHLY
import random


class NavireTransitTimeXlsx(models.AbstractModel):
    _name = 'report.tournee.navire_transit_time_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        diff_time = False
        i = 1
        docs = []
        default_domain = []
        th_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9D9D9'})
        td_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
        tag_ids = self.env['tags.tags'].sudo().search([('navire_id', 'in', data['navire_ids'])], order='navire_id')

        if data['date_start']:
            default_domain.append(('scan_date', '>=', fields.Date.from_string(data['date_start'])))
        if data['date_end']:
            default_domain.append(('scan_date', '<=', fields.Date.from_string(data['date_end'])))
        for tag_id in tag_ids:
            before_tag_line_id = False
            tag_line = [tag_id.navire_id.name, tag_id.name]
            domain = default_domain.copy()
            domain.append(('tag_id', '=', tag_id.id))
            tag_line_id = self.env['task.tags.line'].sudo().search(domain, order='scan_date desc', limit=1)

            if tag_line_id:
                tag_line.append(tag_line_id.scan_date)
                domain.extend([('task_id', '!=', tag_line_id.task_id.id), ('id', '!=', tag_line_id.id)])
                before_tag_line_id = self.env['task.tags.line'].sudo().search(domain, order='scan_date desc', limit=1)
            else:
                tag_line.append('')

            if before_tag_line_id:
                tag_line.extend([before_tag_line_id.scan_date, str(tag_line_id.scan_date - before_tag_line_id.scan_date)])
                if diff_time:
                    diff_time += tag_line_id.scan_date - before_tag_line_id.scan_date
                else:
                    diff_time = tag_line_id.scan_date - before_tag_line_id.scan_date
            else:
                tag_line.extend(['', ''])
            docs.append(tag_line)

        sheet = workbook.add_worksheet(data['date_start'] + ' au ' + data['date_end'])
        sheet.write(0, 0, 'NAVIRE', th_format)
        sheet.set_column(0, 0, 20)
        sheet.write(0, 1, 'TAG', th_format)
        sheet.set_column(1, 1, 50)
        sheet.write(0, 2, 'DATE DERNIER SCAN', th_format)
        sheet.write(0, 3, 'DATE SCAN PRÉCÉDENT', th_format)
        sheet.write(0, 4, 'TEMPS ENTRE LES DEUX', th_format)
        sheet.set_column(2, 4, 30)

        for doc in docs:
            sheet.write(i, 0, doc[0], td_format)
            sheet.write(i, 1, doc[1], td_format)
            sheet.write(i, 2, doc[2].strftime('%d/%m/%Y %H:%M') if doc[2] != '' else '', td_format)
            sheet.write(i, 3, doc[3].strftime('%d/%m/%Y %H:%M') if doc[3] != '' else '', td_format)
            sheet.write(i, 4, doc[4], td_format)
            i += 1
        sheet.write(i, 4, "Moyenne = {}".format(str(diff_time/len(tag_ids)).split('.')[0]), td_format)

