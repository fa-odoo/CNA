# -*- coding: utf-8 -*-

from odoo import models, fields
from dateutil.rrule import rrule, MONTHLY
import random
from datetime import timedelta
import numpy as np
from pytz import timezone, utc

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

        # cr.execute(""
        #            "SELECT tag_id, scan_date, temps_passage_daily FROM "
        #            "(SELECT *, ROW_NUMBER() OVER (PARTITION BY "
        #            "tag_id, DATE(scan_date) ORDER BY scan_date DESC) AS Row_ID FROM (SELECT * FROM task_tags_line WHERE scan_date is not null AND tag_id IN %s AND DATE(scan_date) >= DATE(%s) AND DATE(scan_date) <= DATE(%s) AND temps_passage_daily is not null and date_scan_ok is True) as res"
        #            ") AS A WHERE Row_ID <2",
        #            (tuple(tag_ids.ids), data['date_start'], data['date_end']))

        # cr.execute("""SELECT tag_id, max(scan_date), sum(temps_passage_daily), count(*),
        # case when sum(temps_passage_daily) = 0  then 1440
        #     when count(*)  = 1 then 1440
        #     else sum(temps_passage_daily)/count(*) end as temps_passage_daily_avg
        #  FROM task_tags_line
        #  WHERE scan_date is not null and
        #   tag_id in %s AND DATE(scan_date) >= DATE(%s) AND
        #    DATE(scan_date) <= DATE(%s) and date_scan_ok is true
        #     group by tag_id, date_trunc('day',scan_date)""", (tuple(tag_ids.ids), data['date_start'], data['date_end']))

        cr.execute("""SELECT tag_id, max(scan_date), sum(temps_passage_daily), count(*),
    CASE WHEN count(CASE WHEN temps_passage_daily > 0 THEN 1 END) = 0
         THEN 1440
         ELSE sum(CASE WHEN temps_passage_daily > 0 THEN temps_passage_daily ELSE 0 END) / count(CASE WHEN temps_passage_daily > 0 THEN 1 END)
    END as temps_passage_daily_avg
FROM task_tags_line 
WHERE scan_date is not null and
    tag_id in %s AND 
    DATE(scan_date) >= DATE(%s) AND 
    DATE(scan_date) <= DATE(%s) AND date_scan_ok is true 
    
GROUP BY tag_id, date_trunc('day', scan_date)

""", (tuple(tag_ids.ids), data['date_start'], data['date_end']))
        dict_keys = {tag_id: {}for tag_id in tag_ids.ids}
        for x in cr.fetchall():

            dict_keys[x[0]][x[1].date()]=(x[2], x[3], x[4], x[1])
        start_date = fields.Date.from_string(data['date_start'])
        end_date = fields.Date.from_string(data['date_end'])
        for tag_id in tag_ids:
            tag_line = False
            tag_content = dict_keys.get(tag_id.id, False)
            max_tag_date = tag_content.values() and  max(t[3] for t in tag_content.values() ) or ''
            if tag_content:
                current_date = start_date
                while current_date <= end_date:
                    if not tag_content.get(current_date, False) and current_date.weekday() != 6:
                        dict_keys[tag_id.id][current_date] = (0,0, 1440, '')
                    current_date = current_date +timedelta(days=1)
            tag_content = dict_keys.get(tag_id.id, False)
            tag_line = [tag_id.navire_id.name, tag_id.name, max_tag_date]
            if data['type'] == 'week':
                diff_day = 6
            else:
                start_date = fields.Date.from_string(data['date_start'])
                end_date = fields.Date.from_string(data['date_end'])
                # Get number of sunday between start and end date
                nb_sun = np.busday_count(str(start_date), str(end_date), weekmask='Sun')
                delta = end_date - start_date
                diff_day = delta.days +1 - nb_sun
            # res_avg = (sum([x[1] for x in tag_content]) + ((diff_day - len(tag_content)) * 24)) / diff_day
            res_avg = sum(t[2] for t in tag_content.values())/diff_day
            res_avg = timedelta(minutes=res_avg)
            tag_line.append(str(res_avg).split('.')[0])
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
        tz = timezone(self.env.user.tz or self.env.context.get('tz') or 'UTC')

        for doc in docs:
            sheet.write(i, 0, doc[0], td_format)
            sheet.write(i, 1, doc[1], td_format)
            sheet.write(i, 2, doc[2].astimezone(tz).strftime('%d/%m/%Y %H:%M') if doc[2] != '' else '', td_format)
            sheet.write(i, 3, doc[3], td_format)
            i += 1
        sheet.write(i, 3, "Moyenne = {}".format(str(diff_time/(len(docs) or 1)).split('.')[0]), td_format)
