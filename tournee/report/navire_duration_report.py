# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
import random
from dateutil.rrule import rrule, MONTHLY


class ReportNavireDuration(models.AbstractModel):
    _name = "report.tournee.navire_duration_report_tmp"

    @api.model
    def _get_report_values(self, docids, data=None):
        print("_get_report_values_get_report_values")
        months_in_year = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
        # colors = ['#0000ff', '#008000', '#ff0000', '#00bfbf', '#bf00bf', '#bfbf00', '#1f77b4', '#ff7f0e', '#2ca02c',
        #           '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        docs = self.env['navire.navire'].browse(data['form']['navire_ids']).sudo()
        colors = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                 for i in range(len(docs))]

        start_date = fields.Date.from_string(data['form']['start_date'])
        end_date = fields.Date.from_string(data['form']['end_date'])
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
            duration_data[navire] = {'theoretical_duration': [], 'percent_duration': [],'real_duration': [], 'org': [], 'color':  colors[color_index]}
            color_index+=1
            duration_ids = navire.duration_ids.filtered(lambda r: r.start_date and r.end_date and
                                                                  r.start_date >= start_date and
                                                                  r.end_date <= end_date)
            for year in months_data:
                for i in range(len(months_data[year])):
                    duration_id = duration_ids.filtered(lambda d: d.end_date.year == year and d.end_date.month == i + 1)
                    if duration_id:
                        duration_data[navire]['org'].append(duration_id.org)
                        duration_data[navire]['theoretical_duration'].append(duration_id.theoretical_duration)
                        duration_data[navire]['real_duration'].append(duration_id.real_duration)
                        duration_data[navire]['percent_duration'].append(duration_id.percent_duration)
                    else:
                        duration_data[navire]['org'].append("")
                        duration_data[navire]['theoretical_duration'].append(0.0)
                        duration_data[navire]['real_duration'].append(0.0)
                        duration_data[navire]['percent_duration'].append(0.00)

        print('report_months_data', months_data)
        print('reportduration_data', duration_data)
        return {
            'doc_ids': data['form']['navire_ids'],
            'doc_model': 'navire.navire',
            'docs': docs,
            'months_data': months_data,
            'duration_data': duration_data,
            'start_date': start_date,
            'end_date': end_date
        }
