from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from datetime import timedelta
import datetime
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter, landscape
import io
import base64



class NavireTransitTimeWizard(models.TransientModel):
    _name = 'navire.transit.time.wizard'

    type = fields.Selection([('week', 'Semaine'), ('month', 'Mois')], default='week', string='Type', required=True)
    date_start = fields.Date(string="Date début", required=True)
    date_end = fields.Date(string="Date fin", compute="compute_date_end")
    end_date = fields.Date(string="Date fin ")
    navire_ids = fields.Many2many('navire.navire', string='Navires', required=True)
    is_graphique = fields.Boolean(string="Rapport Graphique")
    file = fields.Binary(string='File')

    @api.constrains('type', 'date_start')
    def _check_start_end_tag(self):
        for rec in self:
            if rec.date_start and rec.type:
                if rec.is_graphique and rec.date_start.weekday() != 0 or rec.date_start >= rec.end_date:
                    raise UserError("Veuillez choisir une date valide")
                if not rec.is_graphique and rec.type == 'week' and rec.date_start.weekday() != 0 or rec.type == 'month' and rec.date_start.day != 1:
                    raise UserError("Veuillez choisir une date valide")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['navire_ids'] = self.env.context.get('active_ids')
        return res

    def generate_report(self):
        self.ensure_one()
        # check date
        if self.date_start and self.date_end:
            if self.date_start > self.date_end:
                raise Warning('Vous devez choisir une date valide')
        return self.env.ref('tournee.navire_transit_time_xlsx_action').report_action(self, data={'date_start': self.date_start, 'date_end': self.date_end, 'navire_ids': self.navire_ids.ids, 'type': self.type})

    def generate_xlsx_report(self):
        self.ensure_one()
        navire_ids = str(self.navire_ids.ids).replace('[', '(').replace(']', ')')
        cr = self.env.cr
        cr.execute(
            """
            SELECT id FROM tags_tags 
            WHERE navire_id IN {navire_ids}
            ORDER BY navire_id
            """.format(navire_ids=navire_ids))
        tag_ids = [val[0] for val in cr.fetchall()]
        start_date = self.date_start
        end_date = self.end_date
        moth_color = {}
        week_data = []
        label_week_data = []
        hour_data = []
        key = 1
        end = start_date + timedelta(days=6)
        start = start_date
        while end <= end_date:
            hour_res, res_label = self.get_avg_time(tag_ids, start, end, cr)
            if start.strftime("%B")[:3].upper() in moth_color.keys():
                moth_color[start.strftime("%B")[:3].upper()].append(key)
            else:
                moth_color[start.strftime("%B")[:3].upper()] = [key]
            hour_data.append(hour_res)
            label_week_data.append(res_label)
            week_data.append(key)
            key += 1
            start = end + timedelta(days=1)
            end = start - timedelta(days=start.weekday()) + timedelta(days=6)

        # specify a date to use for the times
        zero = datetime.datetime(2018, 1, 1)
        time = [zero + t for t in hour_data]
        # convert datetimes to numbers
        zero = mdates.date2num(zero)
        hour_num = [t - zero for t in mdates.date2num(time)]
        for key, values in moth_color.items():
            plt.bar(values, [max(hour_num)] * len(values), label="BMW", width=1.0, zorder=1)
        plt.legend(moth_color.keys(), bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
        plt.plot(week_data, hour_num, marker='s', c='black', zorder=2)
        plt.xticks(week_data, label_week_data, rotation=75, ha='right')
        plt.tight_layout()
        buf_main_graph = io.BytesIO()
        plt.savefig(buf_main_graph, format='png')
        buf_main_graph.seek(0)
        plt.close()

        fig = plt.figure(figsize=(1, 3.5))
        plot = plt.bar([0], height=[sum(hour_num)/len(week_data)], width = 0.2)
        # Add the data value on head of the bar
        for value in plot:
            height = value.get_height()
            if height != 0.0:
                plt.text(value.get_x() + value.get_width() / 2., 1.002 * height, '%.2f' % float(height), ha = 'center', va = 'bottom')

        buf_summary_graph = io.BytesIO()
        plt.axis('off')
        fig.savefig(buf_summary_graph, format='png')
        buf_summary_graph.seek(0)

        pdf_buf = io.BytesIO()
        can = canvas.Canvas(pdf_buf, pagesize=landscape(letter))
        can.drawString(20, 580, "NAVIRES %s" %(', '.join(self.navire_ids.mapped('name'))))
        can.drawString(20, 560, "TEMPS DE PASSAGE")

        can.drawImage(ImageReader(buf_main_graph), 20, 100, width=400, preserveAspectRatio=True, mask='auto')
        can.drawImage(ImageReader(buf_summary_graph), 600, 260, height=250, preserveAspectRatio=True, mask='auto')

        can.showPage()
        can.save()

        pdf_buf.seek(0)
        self.file = base64.b64encode(pdf_buf.getvalue()).decode()

        return {
            'name': 'med',
            'type': 'ir.actions.act_url',
            'url':  '/web/content/navire.transit.time.wizard/%s/file/%s.pdf?download=true' % (
                    self.id, '{} - {}'.format(str(self.date_start), str(self.end_date))),
        }

    def get_avg_time(self, tag_ids, start_date, end_date, cr):
        diff_time = False
        docs = []
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

        """, (tuple(tag_ids), str(start_date), str(end_date)))

        dict_keys = {tag_id: {} for tag_id in tag_ids}
        for x in cr.fetchall():
            dict_keys[x[0]][x[1].date()] = (x[2], x[3], x[4], x[1])

        for tag_id in tag_ids:
            tag_content = dict_keys.get(tag_id, False)
            if tag_content:
                current_date = start_date
                while current_date <= end_date:
                    if not tag_content.get(current_date, False) and current_date.weekday() != 6:
                        dict_keys[tag_id][current_date] = (0, 0, 1440, '')
                    current_date = current_date + timedelta(days=1)
            tag_content = dict_keys.get(tag_id, False)
            diff_day = 6
            res_avg = sum(t[2] for t in tag_content.values()) / diff_day
            res_avg = timedelta(minutes=res_avg)
            tag_line = [str(res_avg).split('.')[0]]
            if diff_time:
                diff_time += res_avg
            else:
                diff_time = res_avg
            if tag_line:
                docs.append(tag_line)
        return diff_time / (len(docs) or 1), self.get_label(str(diff_time / (len(docs) or 1)).split('.')[0], start_date)

    def get_label(self, diff_time, date_key):
        week_indice = {0: 4, 1: 1, 2:2, 3:3}
        return "S0{} {}".format(week_indice[(date_key.isocalendar()[1]%4)], diff_time)

    @api.depends('date_start', 'type')
    def compute_date_end(self):
        for rec in self:
            if rec.date_start and rec.type:
                if rec.type == 'week':
                    rec.date_end = rec.date_start + timedelta(days=5)
                else:
                    input_dt = rec.date_start
                    next_month = input_dt.replace(month=input_dt.month +1) - timedelta(days=1)
                    # res = next_month - timedelta(days=next_month.day)
                    rec.date_end = next_month
            else:
                rec.date_end = False
