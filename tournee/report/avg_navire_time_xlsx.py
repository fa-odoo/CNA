# -*- coding: utf-8 -*-


from odoo import api, fields, models
from datetime import timedelta

class AvgNavireTimeXlsx(models.AbstractModel):
    _name = 'report.tournee.avg_navire_time_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        th_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9D9D9'})
        td_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
        docs = {}
        date_res = []
        date_index = False
        start_date = fields.Date.from_string(data['date_start'])
        end_date = fields.Date.from_string(data['date_end'])
        cr = self.env.cr
        i = 0
        y = 1

        for navire_id in data['navire_ids']:
            end = start_date + timedelta(days=6)
            start = start_date
            navire_ids = str([navire_id]).replace('[', '(').replace(']', ')')
            cr.execute(
                """
                SELECT id FROM tags_tags 
                WHERE navire_id IN {navire_ids}
                ORDER BY navire_id
                """.format(navire_ids=navire_ids))
            tag_ids = [val[0] for val in cr.fetchall()]

            docs[data['navire_names'][i]] = {}
            while end <= end_date:
                hour_res, res_label = self.get_avg_time(tag_ids, start, end, cr)

                start = end + timedelta(days=1)
                end = start - timedelta(days=start.weekday()) + timedelta(days=6)
                docs[data['navire_names'][i]][str(res_label)] = str(hour_res).split('.')[0]
                if not date_index:
                    date_res.append(str(res_label))
            if not date_index:
                date_index = date_res
            i += 1

        sheet = workbook.add_worksheet(data['date_start'] + ' au ' + data['date_end'])
        sheet.write(0, 0, 'NAVIRE', th_format)
        sheet.set_column(0, 0, 20)

        for date_el in date_index:
            x = 1
            sheet.write(0, y, date_el, th_format)
            for key, value in docs.items():
                sheet.write(x, 0, key, td_format)
                sheet.write(x, y, value[str(date_el)], td_format)
                sheet.set_column(x, y, 20)
                x += 1
            y += 1

    def get_avg_time(self, tag_ids, start_date, end_date, cr):
        cr.execute("""
                SELECT MAX(res_t.total_count), COUNT(*)
                FROM 
                    (SELECT SUM(COUNT(tag_id)) OVER() AS total_count
                    FROM task_tags_line 
                    WHERE scan_date is not null AND
                    tag_id in %s AND 
                    DATE(scan_date) >= DATE(%s) AND 
                    DATE(scan_date) <= DATE(%s) AND date_scan_ok is true
                    GROUP BY tag_id) res_t
                """, (tuple(tag_ids), str(start_date), str(end_date)))

        sql_res = self.env.cr.fetchone()
        scan_tot, row_count = sql_res[0] or 1, sql_res[1] or 1

        return timedelta(hours=(88 * int(row_count)) / int(scan_tot)), start_date
