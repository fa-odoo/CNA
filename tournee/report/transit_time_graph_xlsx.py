# -*- coding: utf-8 -*-

from odoo import models, fields
from dateutil.rrule import rrule, MONTHLY
from datetime import date, timedelta
import random
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import datetime
class TransitTimeGraphXlsx(models.AbstractModel):
    _name = 'report.tournee.transit_time_graph_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        key = 1
        cr = self.env.cr
        print("data['navire_ids']",data['navire_ids'])
        navire_ids = str(data['navire_ids']).replace('[', '(').replace(']', ')')
        cr.execute(
            """
            SELECT id FROM tags_tags 
            WHERE navire_id IN {navire_ids}
            ORDER BY navire_id
            """.format(navire_ids=navire_ids))
        tag_ids = [val[0]for val in cr.fetchall()]
        print('===========tag_ids', tag_ids)
        start_date = fields.Date.from_string(data['start_date'])
        end_date = fields.Date.from_string(data['end_date'])

        # import datetime module
        week_data = []
        label_week_data = []
        hour_data = []

        end = start_date + timedelta(days=6)
        start = start_date
        if end <= end_date:
            while end <= end_date:
                hour_res, res_label = self.get_avg_time(tag_ids, start, end)
                if hour_res != False:
                    print('hour_res', hour_res)
                    hour_data.append(hour_res)
                    label_week_data.append(res_label)
                    week_data.append(key)
                    key += 1
                start = end + timedelta(days=1)
                end = start - timedelta(days=start.weekday()) + timedelta(days=6)

        else:
            hour_res, res_label = self.get_avg_time(tag_ids, start, end_date)
            if hour_res != False:
                hour_data.append(hour_res)
                label_week_data.append(res_label)
                week_data.append(key)

        print('=======================', key)
        print('label_week_data', label_week_data)
        print('hour_data', hour_data)
        print('week_data', week_data)
        # specify a date to use for the times
        zero = datetime.datetime(2018, 1, 1)
        time = [zero + t for t in hour_data]
        # convert datetimes to numbers
        zero = mdates.date2num(zero)
        hour_num = [t - zero for t in mdates.date2num(time)]

        plt.plot(week_data, hour_num, marker='s', c='black', zorder=1)
        plt.xticks(ticks=range(0, len(week_data)), labels=label_week_data, rotation=70)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        sheet = workbook.add_worksheet(data['start_date'] + ' au ' + data['end_date'])
        sheet.write(3, 4, "Temps de passage")
        sheet.insert_image(4, 4, "image.png", {'image_data': buf})

    def get_avg_time(self, tag_ids, start_date, end_date):
        diff_time = False
        default_domain = []
        if start_date:
            default_domain.append(('scan_date', '>=', start_date))
        if end_date:
            default_domain.append(('scan_date', '<=', end_date))
        for tag_id in tag_ids:
            before_tag_line_id = False
            domain = default_domain.copy()
            domain.append(('tag_id', '=', tag_id))
            tag_line_id = self.env['task.tags.line'].sudo().search(domain, order='scan_date desc', limit=2)
            print('domain ',domain)
            print('ltag_line_id ',tag_line_id)
            print('len(tag_line_id) ',len(tag_line_id))
            if len(tag_line_id) >= 2:
                print('============================= ')
                if diff_time:
                    diff_time += tag_line_id[0].scan_date - tag_line_id[1].scan_date
                else:
                    diff_time = tag_line_id[0].scan_date - tag_line_id[1].scan_date
        if diff_time:
            diff_time = diff_time / len(tag_ids)
        return diff_time, self.get_label(str(diff_time).split('.')[0], end_date)

    def get_label(self, diff_time, end_date):
        if end_date.weekday() <= 7:
            return "S4 {}".format(diff_time)
        if end_date.weekday() <= 14:
            return "S3 {}".format(diff_time)
        if end_date.weekday() <= 21:
            return "S2 {}".format(diff_time)
        return "S1 {}".format(diff_time)