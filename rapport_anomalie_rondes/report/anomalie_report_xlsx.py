from odoo import models

class PartnerXlsx(models.AbstractModel):
    _name = 'report.rapport_anomalie_rondes.report_anomalie_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, anomalies):

        report_name = "Anomalie"
        sheet = workbook.add_worksheet(report_name[:31])
        header = workbook.add_format({'bold': True, 'font_size':14,'font_name':'Calibri'})
        body_center = workbook.add_format({'align': 'center', 'font_size':14,'font_name':'Calibri'})
        body_left = workbook.add_format({'align': 'left', 'font_size':14,'font_name':'Calibri'})

        # columns width
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 3, 5)
        sheet.set_column(4, 4, 18)
        sheet.set_column(5, 5, 4)
        sheet.set_column(6, 6, 18)
        sheet.set_column(7, 7, 12)
        sheet.set_column(8, 8, 10)
        sheet.set_column(9, 9, 10)
        sheet.set_column(10, 10, 22)
        sheet.set_column(11, 11, 12)
        sheet.set_column(12, 12, 18)
        # sheet.set_column(13, 13, 12)
        sheet.set_column(13, 13, 16)
        sheet.set_column(14, 14, 10)
        sheet.set_column(15, 15, 6)
        sheet.set_column(16, 16, 7)
        sheet.set_column(17, 17, 14)

        # header
        sheet.write(0, 0, "Année", header)
        sheet.write(0, 1, "Mois", header)
        sheet.write(0, 2, "Semaine", header)
        sheet.write(0, 3, "Jour", header)
        sheet.write(0, 4, "Date Anomalie", header)
        sheet.write(0, 5, "Lot", header)
        sheet.write(0, 6, "Designation", header)
        sheet.write(0, 7, "Bd/Td/Axe", header)
        sheet.write(0, 8, "Couple", header)
        sheet.write(0, 9, "Navire", header)
        sheet.write(0, 10, "Responsable zone", header)
        sheet.write(0, 11, "Anomalie", header)
        sheet.write(0, 12, "Commentaire", header)
        # sheet.write(0, 13, "Depuis le", header)
        sheet.write(0, 13, "Déjà signalé", header)
        sheet.write(0, 14, "Criticité", header)
        sheet.write(0, 15, "Etat", header)
        sheet.write(0, 16, "Notes", header)
        sheet.write(0, 17, "Lien photo", header)

        # body
        y = 1
        months = {
            '1': 'Janvier',
            '2': 'Février',
            '3': 'Mars',
            '4': 'Avril',
            '5': 'Mail',
            '6': 'Juin',
            '7': 'Juillet',
            '8': 'Aout',
            '9': 'Septembre',
            '10': 'Octobre',
            '11': 'Novembre',
            '12': 'Décembre'
        }
        for obj in anomalies:
            sheet.write(y, 0, int(obj.year) if obj.year.isdigit() else obj.year, body_center)
            sheet.write(y, 1, months[obj.month], body_center)
            sheet.write(y, 2, int(obj.week) if obj.week.isdigit() else obj.week, body_center)
            sheet.write(y, 3, obj.day, body_center)
            sheet.write(y, 4, obj.date_anomalie.strftime('%d-%m-%Y'), body_center)
            sheet.write(y, 5, int(obj.lot), body_center)
            sheet.write(y, 6, obj.designation, body_center)
            sheet.write(y, 7, obj.bd_td_axe, body_center)
            sheet.write(y, 8, int(obj.couple), body_center)
            sheet.write(y, 9, obj.navire_id.name, body_center)
            sheet.write(y, 10, obj.respo_zone_id.name, body_center)
            sheet.write(y, 11, obj.anomalie_id.name, body_left)
            sheet.write(y, 12, obj.anomalie_commentaire_id.name, body_left)
            # sheet.write(y, 13, obj.depuis_le.strftime('%d-%m-%Y'), body_center)
            sheet.write(y, 13, obj.already_reported, body_center)
            sheet.write(y, 14, obj.criticite, body_center)
            sheet.write(y, 15, obj.state, body_center)
            sheet.write(y, 16, obj.comment, body_center)
            sheet.write(y, 17, obj.url, body_center)

            y = y + 1


