# -*- coding: utf-8 -*-

from odoo import models, fields
from pytz import timezone, utc


class IncidentDurationReportXlsx(models.AbstractModel):
    _name = 'report.activities.incident_duration_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        th_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#A4A4A4'})
        td_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9D9D9', 'text_wrap': True})
        evnt_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9D9D9', 'text_wrap': True})
        i = 1

        start_date = fields.Date.from_string(data['start_date'])
        end_date = fields.Date.from_string(data['end_date'])
        incident_ids = self.env['cna.incident'].search([('report_type', '=', 'incident'), ('create_date', '>=', start_date), ('create_date', '<=', end_date)])

        sheet = workbook.add_worksheet(data['start_date'] + ' au ' + data['end_date'])
        sheet.write(0, 0, 'DATE', th_format)
        sheet.write(0, 1, 'HEURE', th_format)
        sheet.set_column(0, 1, 12)
        sheet.write(0, 2, 'LIEU', th_format)
        sheet.set_column(2, 2, 20)
        sheet.write(0, 3, 'ÉVÈNEMENT', th_format)
        sheet.set_column(3, 3, 30)
        sheet.write(0, 4, 'NOM VICTIME', th_format)
        sheet.write(0, 5, 'BADGE VICTIME', th_format)
        sheet.set_column(4, 5, 15)
        sheet.write(0, 6, 'SCTÉ VICTIME', th_format)
        sheet.set_column(6, 6, 15)
        sheet.write(0, 7, 'NOM AUTEUR', th_format)
        sheet.write(0, 8, 'BADGE AUTEUR', th_format)
        sheet.set_column(7, 8, 15)
        sheet.write(0, 9, 'SCTÉ AUTEUR', th_format)
        sheet.set_column(9, 9, 15)
        sheet.write(0, 10, 'COMMENTAIRE', th_format)
        sheet.set_column(10, 10, 50)

        for incident_id in incident_ids:
            sheet.write(i, 0, str(utc.localize(incident_id.date_start).astimezone(timezone(self.env.user.tz or self.env.context.get('tz') or 'UTC')).strftime('%d/%m/%Y')), td_format)
            sheet.write(i, 1, str(utc.localize(incident_id.date_start).astimezone(timezone(self.env.user.tz or self.env.context.get('tz') or 'UTC')).strftime("%H:%M")), td_format)
            sheet.write(i, 2, incident_id.lieu.name if incident_id.lieu else "", td_format)
            sheet.write(i, 3, incident_id.incident_type_id.name if incident_id.incident_type_id else "", evnt_format)
            sheet.write(i, 4, incident_id.victime, td_format)
            sheet.write(i, 5, incident_id.victime_badge, td_format)
            sheet.write(i, 6, incident_id.victime_company, td_format)
            sheet.write(i, 7, incident_id.auteur, td_format)
            sheet.write(i, 8, incident_id.auteur_badge, td_format)
            sheet.write(i, 9, incident_id.auteur_company, td_format)

            sheet.write(i, 10, incident_id.description if incident_id.description else "", td_format)
            i += 1
