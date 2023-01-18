# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.osv import expression
from ast import literal_eval
from datetime import date, timedelta
import datetime
import matplotlib.dates as mdates


class DashboardBlock(models.Model):
    _inherit = "dashboard.block"

    avg_time = fields.Boolean(string="Temps de passage", default=False, invisible=True)
    start_date = fields.Date(string="Date début")
    end_date = fields.Date(string="Date fin")
    navire_ids = fields.Many2many('navire.navire', string='Navires')

    @api.model
    def create(self, vals):
        if vals.get("avg_time", False) and vals.get("type", False) and vals.get("type", False) != 'graph':
            raise UserError('Le temp de passage doit un être de type Chart')
        return super(DashboardBlock, self).create(vals)

    def get_dashboard_vals(self, action_id):
        """Dashboard block values"""
        block_id = []
        dashboard_block = self.env['dashboard.block'].sudo().search([('client_action', '=', int(action_id))])
        for rec in dashboard_block:
            color = rec.tile_color if rec.tile_color else '#1f6abb;'
            icon_color = rec.tile_color if rec.tile_color else '#1f6abb;'
            text_color = rec.text_color if rec.text_color else '#FFFFFF;'
            vals = {
                'id': rec.id,
                'name': rec.name,
                'type': rec.type,
                'graph_type': rec.graph_type,
                'icon': rec.fa_icon,
                'cols': rec.graph_size,
                'color': 'background-color: %s;' % color,
                'text_color': 'color: %s;' % text_color,
                'icon_color': 'color: %s;' % icon_color,
            }
            domain = []
            if rec.filter:
                domain = expression.AND([literal_eval(rec.filter)])
            if rec.model_name or rec.avg_time:
                if rec.type == 'graph' or rec.avg_time:
                    if rec.avg_time and rec.type == 'graph':
                        x_axis, y_axis, avg_time = self.avg_navire_ids(rec.navire_ids, rec.start_date, rec.end_date)
                        vals.update({'type': 'graph', 'graph_type': 'bar', 'graph_size': 'col-lg-12',
                                     'name': "Temps de passage {} \n Moyenne : {} ".format(
                                         str(rec.start_date) + ' au ' + str(rec.end_date), avg_time)})
                    else:
                        query = self.env[rec.model_name].get_query(domain, rec.operation, rec.measured_field,
                                                                   group_by=rec.group_by)
                        self._cr.execute(query)
                        records = self._cr.dictfetchall()
                        x_axis = []
                        for record in records:
                            x_axis.append(record.get(rec.group_by.name))
                        y_axis = []
                        for record in records:
                            y_axis.append(record.get('value'))
                    vals.update({'x_axis': x_axis, 'y_axis': y_axis})
                else:
                    query = self.env[rec.model_name].get_query(domain, rec.operation, rec.measured_field)
                    self._cr.execute(query)
                    records = self._cr.dictfetchall()
                    magnitude = 0
                    total = records[0].get('value')
                    while abs(total) >= 1000:
                        magnitude += 1
                        total /= 1000.0
                    # add more suffixes if you need them
                    val = '%.2f%s' % (total, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
                    records[0]['value'] = val
                    vals.update(records[0])
            block_id.append(vals)
        return block_id

    def avg_navire_ids(self, navir_ids, start_date, end_date):
        moth_color = {}
        week_data = []
        label_week_data = []
        hour_data = []
        key = 1
        cr = self.env.cr
        navire_ids = str(navir_ids.ids).replace('[', '(').replace(']', ')')
        cr.execute(
            """
            SELECT id FROM tags_tags 
            WHERE navire_id IN {navire_ids}
            ORDER BY navire_id
            """.format(navire_ids=navire_ids))
        tag_ids = [val[0] for val in cr.fetchall()]

        end = start_date + timedelta(days=6)
        start = start_date
        if end <= end_date:
            while end <= end_date:
                hour_res, res_label = self.get_avg_time(tag_ids, start, end, cr)
                if end.strftime("%B")[:3].upper() in moth_color.keys():
                    moth_color[end.strftime("%B")[:3].upper()].append(key)
                else:
                    moth_color[end.strftime("%B")[:3].upper()] = [key]
                hour_data.append(hour_res)
                label_week_data.append(res_label)
                week_data.append(key)
                key += 1
                start = end + timedelta(days=1)
                end = start - timedelta(days=start.weekday()) + timedelta(days=6)
        else:
            hour_res, res_label = self.get_avg_time(tag_ids, start, end_date, cr)
            if end_date.strftime("%B")[:3].upper() in moth_color.keys():
                moth_color[end_date.strftime("%B")[:3].upper()].append(key)
            else:
                moth_color[end_date.strftime("%B")[:3].upper()] = [key]
            hour_data.append(hour_res)
            label_week_data.append(res_label)
            week_data.append(key)
        # specify a date to use for the times
        zero = datetime.datetime(2018, 1, 1)
        time = [zero + t for t in hour_data]
        # convert datetimes to numbers
        zero = mdates.date2num(zero)
        hour_num = [t - zero for t in mdates.date2num(time)]
        return label_week_data, hour_num, str(sum(hour_data, datetime.timedelta()) / len(hour_data)).split('.')[0]

    def get_avg_time(self, tag_ids, start_date, end_date, cr):
        cr.execute(
            "SELECT SUM(avg_date_table.avg_date) FROM ( SELECT tag_id, min(scan_date) as start_date, max(scan_date) as end_date, max(scan_date) - min(scan_date) as avg_date FROM ( SELECT tag_id, scan_date FROM (SELECT ROW_NUMBER() OVER (PARTITION BY tag_id ORDER BY scan_date DESC  NULLS LAST) AS r, t.* FROM task_tags_line t) line WHERE line.r <= 2 AND tag_id IN %s AND DATE(scan_date) >= DATE(%s) AND DATE(scan_date) <= DATE(%s)) scanned_date GROUP BY scanned_date.tag_id) avg_date_table",
            (tuple(tag_ids), str(start_date), str(end_date)))
        res = self._cr.fetchone()
        if res[0]:
            diff_time = res[0] / len(tag_ids)
        else:
            diff_time = timedelta()
        return diff_time, self.get_label(str(diff_time).split('.')[0], end_date)

    def get_label(self, diff_time, end_date):
        if end_date.day <= 7:
            return "S1 {}".format(diff_time)
        if end_date.day <= 14:
            return "S2 {}".format(diff_time)
        if end_date.day <= 21:
            return "S3 {}".format(diff_time)
        return "S4 {}".format(diff_time)
