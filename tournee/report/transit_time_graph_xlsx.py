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
        week_data = []
        label_week_data = []
        hour_data = []
        key = 1
        cr = self.env.cr
        navire_ids = str(data['navire_ids']).replace('[', '(').replace(']', ')')
        cr.execute(
            """
            SELECT id FROM tags_tags 
            WHERE navire_id IN {navire_ids}
            ORDER BY navire_id
            """.format(navire_ids=navire_ids))
        tag_ids = [val[0] for val in cr.fetchall()]
        start_date = fields.Date.from_string(data['start_date'])
        end_date = fields.Date.from_string(data['end_date'])

        end = start_date + timedelta(days=6)
        start = start_date
        if end <= end_date:
            while end <= end_date:
                hour_res, res_label = self.get_avg_time(tag_ids, start, end, cr)
                if hour_res != False:
                    hour_data.append(hour_res)
                    label_week_data.append(res_label)
                    week_data.append(key)
                    key += 1
                start = end + timedelta(days=1)
                end = start - timedelta(days=start.weekday()) + timedelta(days=6)
        else:
            hour_res, res_label = self.get_avg_time(tag_ids, start, end_date, cr)
            if hour_res != False:
                hour_data.append(hour_res)
                label_week_data.append(res_label)
                week_data.append(key)

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

    def get_avg_time(self, tag_ids, start_date, end_date, cr):
        diff_time = False
        cr.execute(
            "SELECT SUM(avg_date_table.avg_date) FROM ( SELECT tag_id, min(scan_date) as start_date, max(scan_date) as end_date, max(scan_date) - min(scan_date) as avg_date FROM ( SELECT tag_id, scan_date FROM (SELECT ROW_NUMBER() OVER (PARTITION BY tag_id ORDER BY scan_date DESC  NULLS LAST) AS r, t.* FROM task_tags_line t) line WHERE line.r <= 2 AND tag_id IN %s AND DATE(scan_date) >= DATE(%s) AND DATE(scan_date) <= DATE(%s)) scanned_date GROUP BY scanned_date.tag_id) avg_date_table",
            (tuple(tag_ids), str(start_date), str(end_date)))
        res = self._cr.fetchone()
        if res[0]:
            diff_time = res[0] / len(tag_ids)
        return diff_time, self.get_label(str(diff_time).split('.')[0], end_date)

    def get_label(self, diff_time, end_date):
        if end_date.weekday() <= 7:
            return "S4 {}".format(diff_time)
        if end_date.weekday() <= 14:
            return "S3 {}".format(diff_time)
        if end_date.weekday() <= 21:
            return "S2 {}".format(diff_time)
        return "S1 {}".format(diff_time)
