# -*- coding: utf-8 -*-
from datetime import date

from odoo import api, fields, models
import calendar
from dateutil import rrule
from datetime import timedelta

class PresenceTimeReportXlsx(models.AbstractModel):
    _name = 'report.tournee.presence_time_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        th_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'bg_color': '#D9D9D9'})
        td_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
        res = {}
        start_date = fields.Date.from_string(data['start_date'])
        end_date = fields.Date.from_string(data['end_date'])
        month_list = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
            if dt.year not in res.keys():
                res[dt.year] = {}
            res[dt.year][month_list[dt.month-1]] = []
        print('res',res)
        sheet = workbook.add_worksheet(data['start_date'] + ' au ' + data['end_date'])
        y_sum = 1
        y = 1
        sheet.write(1, 0, "MOIS", th_format)
        sheet.write(2, 0, "NAVIRES", th_format)
        sheet.write(3, 0, "ORG", th_format)
        sheet.write(4, 0, "HEURES VENDUES", th_format)
        sheet.write(5, 0, "TOTAL HEURES VENDUES", th_format)
        sheet.set_column(0, 0, 25)
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
            date_start = date(year=dt.year, month=dt.month, day=1)
            date_end = date(year=dt.year, month=dt.month, day=calendar.monthrange(dt.year, dt.month)[1])
            presence_time_ids = self.env['presence.time'].search([('start_date', '>=', date_start), ('end_date', '<=', date_end)])
            peripheral_timing_ids = self.env['peripheral.timing'].search([('start_date', '>=', date_start), ('end_date', '<=', date_end)])

            count_org = 0
            sum_sold = 0
            sum_bord = timedelta(0)

            for peripheral_timing_id in peripheral_timing_ids:
                sum_bord += peripheral_timing_id.end_date - peripheral_timing_id.start_date
            for presence_time_id in presence_time_ids:
                sheet.write(1, y, month_list[dt.month - 1], td_format)
                sheet.write(2, y, str(presence_time_id.navire_id.name), td_format)
                sheet.write(3, y, str(presence_time_id.organisation_id.name), td_format)
                sheet.write(4, y, str(presence_time_id.hours_sold), td_format)
                sum_sold += presence_time_id.hours_sold
                count_org += 1
                y += 1
            if presence_time_ids:
                if count_org != 1:
                    sheet.merge_range(5, y_sum, 5, y_sum + count_org - 1, str(sum_sold) + " / " + str(sum_bord), td_format)
                else:
                    sheet.write(5, y-1, str(sum_sold) + " / " + str(sum_bord), td_format)
                y_sum += 1
