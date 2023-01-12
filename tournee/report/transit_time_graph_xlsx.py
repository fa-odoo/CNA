# -*- coding: utf-8 -*-

from odoo import models, fields
from dateutil.rrule import rrule, MONTHLY
import random
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import io

class TransitTimeGraphXlsx(models.AbstractModel):
    _name = 'report.tournee.transit_time_graph_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):

        year = [2014, 2015, 2016, 2017, 2018, 2019]
        tutorial_count = [39, 117, 111, 110, 67, 29]

        plt.plot(year, tutorial_count, color="#6c3376", linewidth=3, marker='o')
        plt.xlabel('Year')
        plt.ylabel('Number of futurestud.io Tutorials')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        sheet = workbook.add_worksheet(data['start_date'] + ' au ' + data['end_date'])
        sheet.write( 3, 3, "percent_duration")
        sheet.insert_image(4, 4, "image.png", {'image_data': buf})