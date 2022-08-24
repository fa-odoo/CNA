# -*- coding: utf-8 -*-

from odoo import models, fields
from dateutil.rrule import rrule, MONTHLY
import random


class NavireDurationReportXlsx(models.AbstractModel):
    _name = 'report.tournee.navire_duration_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):

        months_in_year = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
        docs = self.env['navire.navire'].browse(data['navire_ids']).sudo()
        colors = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                  for i in range(len(docs))]

        start_date = fields.Date.from_string(data['start_date'])
        end_date = fields.Date.from_string(data['end_date'])
        years = list(range(start_date.year, end_date.year + 1))

        months = [dt.strftime("%m")
                  for dt in rrule(MONTHLY, dtstart=start_date,
                                  until=end_date)]
        months_data = {}
        duration_data = {}
        for year in years:
            if "12" in months:
                months_data[year] = [months_in_year[int(m) - 1] for m in months[:months.index("12") + 1]]
                months = months[months.index("12") + 1:]
            else:
                months_data[year] = [months_in_year[int(m) - 1] for m in months]
                break
        color_index = 0
        for navire in docs:
            duration_data[navire] = {'theoretical_duration': [], 'percent_duration': [], 'real_duration': [], 'org': [],
                                     'color': colors[color_index]}
            color_index += 1
            duration_ids = navire.duration_ids.filtered(lambda r: r.start_date and r.end_date and
                                                                  r.start_date >= start_date and
                                                                  r.end_date <= end_date)
            for year in months_data:
                for i in range(len(months_data[year])):
                    duration_id = duration_ids.filtered(lambda d: d.end_date.year == year and d.end_date.month == i + 1)
                    if duration_id:
                        duration_data[navire]['org'].append(duration_id.org)
                        duration_data[navire]['theoretical_duration'].append(
                            '{0:02.0f}:{1:02.0f}'.format(*divmod(float(duration_id.theoretical_duration) * 60, 60)))
                        duration_data[navire]['real_duration'].append(
                            '{0:02.0f}:{1:02.0f}'.format(*divmod(float(duration_id.real_duration) * 60, 60)))
                        duration_data[navire]['percent_duration'].append('{:.2f}'.format(duration_id.percent_duration))
                    else:
                        duration_data[navire]['org'].append("")
                        duration_data[navire]['theoretical_duration'].append("")
                        duration_data[navire]['real_duration'].append("")
                        duration_data[navire]['percent_duration'].append("")

        slim_bold_border_format = workbook.add_format(
            {'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        top_left_right_format = workbook.add_format(
            {'bold': True, 'border': 1, 'top': 2, 'left': 2, 'right': 2, 'align': 'center', 'valign': 'vcenter'})
        left_bold_format = workbook.add_format(
            {'bold': True, 'border': 1, 'left': 2, 'align': 'center', 'valign': 'vcenter'})
        right_format = workbook.add_format({'border': 1, 'right': 2, 'align': 'center', 'valign': 'vcenter'})
        right_bold_format = workbook.add_format(
            {'bold': True, 'border': 1, 'right': 2, 'align': 'center', 'valign': 'vcenter'})
        bottom_format = workbook.add_format({'border': 1, 'bottom': 2, 'align': 'center', 'valign': 'vcenter'})
        bottom_right_format = workbook.add_format(
            {'border': 1, 'right': 2, 'bottom': 2, 'align': 'center', 'valign': 'vcenter'})
        sheet = workbook.add_worksheet(data['start_date'] + ' au ' + data['end_date'])
        year_col = 2
        month_col = 2
        duration_row = 3
        last_months = 0

        for year in months_data:
            if len(months_data[year]) != 1:
                sheet.merge_range(1, year_col, 1, year_col + len(months_data[year]) - 1, year, top_left_right_format)
            else:
                sheet.write(1, year_col + len(months_data[year]) - 1, year, top_left_right_format)

            year_col += len(months_data[year])
            for month in months_data[year]:
                if month_col == 2:
                    sheet.write(2, month_col, month, left_bold_format)
                elif month_col == len(months_data[year]) + 1 + last_months:
                    sheet.write(2, month_col, month, right_bold_format)
                else:
                    sheet.write(2, month_col, month, slim_bold_border_format)
                month_col += 1
            last_months += len(months_data[year])

        sheet.set_column(1, 1, 20)
        for duration in duration_data:
            org_col = 2
            theoretical_duration_col = 2
            percent_duration_col = 2
            real_duration_col = 2
            bg_color = duration_data[duration]['color']
            slim_border_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
            left_right_format = workbook.add_format(
                {'bold': True, 'border': 1, 'left': 2, 'right': 2, 'align': 'center', 'valign': 'vcenter',
                 'bg_color': bg_color})
            top_left_right_format = workbook.add_format(
                {'bold': True, 'border': 1, 'top': 2, 'left': 2, 'right': 2, 'align': 'center', 'valign': 'vcenter',
                 'bg_color': bg_color})
            bottom_left_right_format = workbook.add_format(
                {'bold': True, 'border': 1, 'bottom': 2, 'left': 2, 'right': 2, 'align': 'center', 'valign': 'vcenter',
                 'bg_color': bg_color})
            slim_border_color_format = workbook.add_format(
                {'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': bg_color})
            right_color_format = workbook.add_format(
                {'border': 1, 'right': 2, 'align': 'center', 'valign': 'vcenter', 'bg_color': bg_color})
            bottom_color_format = workbook.add_format(
                {'border': 1, 'bottom': 2, 'align': 'center', 'valign': 'vcenter', 'bg_color': bg_color})
            bottom_right_color_format = workbook.add_format(
                {'border': 1, 'right': 2, 'bottom': 2, 'align': 'center', 'valign': 'vcenter', 'bg_color': bg_color})

            if duration_row == 3:
                sheet.write(duration_row, 1, duration.name, top_left_right_format)
            else:
                sheet.write(duration_row, 1, duration.name, left_right_format)
            sheet.write(duration_row + 1, 1, 'Théorique', left_right_format)
            sheet.write(duration_row + 2, 1, 'Réelle', left_right_format)
            if duration_row == (4 * (len(duration_data) - 1) + 3):
                sheet.write(duration_row + 3, 1, '%', bottom_left_right_format)
            else:
                sheet.write(duration_row + 3, 1, '%', left_right_format)
            # ADD ORG line
            for org in duration_data[duration]['org']:
                if org == "":
                    if org_col == len(duration_data[duration]['org']) + 1 or (org_col - 1) % 12 == 0:
                        sheet.write(duration_row, org_col, org, right_format)
                    else:
                        sheet.write(duration_row, org_col, org, slim_border_format)
                else:
                    if org_col == len(duration_data[duration]['org']) + 1 or (org_col - 1) % 12 == 0:
                        sheet.write(duration_row, org_col, org, right_color_format)
                    else:
                        sheet.write(duration_row, org_col, org, slim_border_color_format)
                org_col += 1
            # ADD theoretical duration line
            for theoretical_duration in duration_data[duration]['theoretical_duration']:
                if theoretical_duration == "":
                    if theoretical_duration_col == len(duration_data[duration]['theoretical_duration']) + 1 or (
                            theoretical_duration_col - 1) % 12 == 0:
                        sheet.write(duration_row + 1, theoretical_duration_col, theoretical_duration, right_format)
                    else:
                        sheet.write(duration_row + 1, theoretical_duration_col, theoretical_duration,
                                    slim_border_format)
                else:
                    if theoretical_duration_col == len(duration_data[duration]['theoretical_duration']) + 1 or (
                            theoretical_duration_col - 1) % 12 == 0:
                        sheet.write(duration_row + 1, theoretical_duration_col, theoretical_duration,
                                    right_color_format)
                    else:
                        sheet.write(duration_row + 1, theoretical_duration_col, theoretical_duration,
                                    slim_border_color_format)
                theoretical_duration_col += 1
            # ADD real duration line
            for real_duration in duration_data[duration]['real_duration']:
                if real_duration == "":
                    if real_duration_col == len(duration_data[duration]['real_duration']) + 1 or (
                            real_duration_col - 1) % 12 == 0:
                        sheet.write(duration_row + 2, real_duration_col, real_duration, right_format)
                    else:
                        sheet.write(duration_row + 2, real_duration_col, real_duration, slim_border_format)
                else:
                    if real_duration_col == len(duration_data[duration]['real_duration']) + 1 or (
                            real_duration_col - 1) % 12 == 0:
                        sheet.write(duration_row + 2, real_duration_col, real_duration, right_color_format)
                    else:
                        sheet.write(duration_row + 2, real_duration_col, real_duration, slim_border_color_format)
                real_duration_col += 1
            # ADD percent duration line
            for percent_duration in duration_data[duration]['percent_duration']:
                if percent_duration == "":
                    if (percent_duration_col == len(duration_data[duration]['percent_duration']) + 1 or (
                            percent_duration_col - 1) % 12 == 0) and duration_row + 4 == len(duration_data) * 4 + 3:
                        sheet.write(duration_row + 3, percent_duration_col, percent_duration, bottom_right_format)
                    elif percent_duration_col == len(duration_data[duration]['percent_duration']) + 1 or (
                            percent_duration_col - 1) % 12 == 0:
                        sheet.write(duration_row + 3, percent_duration_col, percent_duration, right_format)
                    elif duration_row + 4 == len(duration_data) * 4 + 3:
                        sheet.write(duration_row + 3, percent_duration_col, percent_duration, bottom_format)
                    else:
                        sheet.write(duration_row + 3, percent_duration_col, percent_duration, slim_border_format)
                else:
                    if (percent_duration_col == len(duration_data[duration]['percent_duration']) + 1 or (
                            percent_duration_col - 1) % 12 == 0) and duration_row + 4 == len(duration_data) * 4 + 3:
                        sheet.write(duration_row + 3, percent_duration_col, percent_duration, bottom_right_color_format)
                    elif percent_duration_col == len(duration_data[duration]['percent_duration']) + 1 or (
                            percent_duration_col - 1) % 12 == 0:
                        sheet.write(duration_row + 3, percent_duration_col, percent_duration, right_color_format)
                    elif duration_row + 4 == len(duration_data) * 4 + 3:
                        sheet.write(duration_row + 3, percent_duration_col, percent_duration, bottom_color_format)
                    else:
                        sheet.write(duration_row + 3, percent_duration_col, percent_duration, slim_border_color_format)
                percent_duration_col += 1
            duration_row += 4
