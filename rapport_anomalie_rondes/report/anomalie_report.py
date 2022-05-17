# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields



class report_anomalies(models.AbstractModel):
    _name = 'report.rapport_anomalie_rondes._report_anomalie_rondes'

    @api.model
    def _get_report_values(self, docids, data=None):
        all_tags_task_anomalie = data['form']['tags_ids']
        docs= []
        tags_task_anomalies_ids = self.env['tags.task.anomalie'].search([('id', 'in', all_tags_task_anomalie)])
        if tags_task_anomalies_ids:
            for tag in tags_task_anomalies_ids:
                tag_data = {}
                tag_data['year'] = tag.year
                tag_data['week'] = tag.week
                tag_data['date_anomalie'] = tag.date_anomalie.strftime('%d/%m/%Y')
                tag_data['lot'] = tag.lot
                tag_data['bd_td_axe'] = tag.bd_td_axe
                tag_data['couple'] = tag.couple
                tag_data['respo_zone_id'] = tag.respo_zone_id.name
                tag_data['anomalie_id'] = tag.anomalie_id.name
                tag_data['anomalie_commentaire_id'] = tag.anomalie_commentaire_id.name
                tag_data['depuis_le'] = tag.depuis_le
                tag_data['criticite'] = tag.criticite
                tag_data['green_color_state'] = tag.green_color_state
                tag_data['blue_color_state'] = tag.blue_color_state

                tag_data['red_color_criticite'] = tag.red_color_criticite
                tag_data['orange_color_criticite'] = tag.orange_color_criticite
                tag_data['yellow_color_criticite'] = tag.yellow_color_criticite

                tag_data['comment'] = tag.comment
                tag_data['url'] = tag.url
                tag_data['state_a'] = tag.state
                if tag.state == 'draft':
                    tag_data['state'] = 'Prise de contact'
                elif tag.state == 'resolu':
                    tag_data['state'] = 'Resolu'
                else:
                    tag_data['state'] = ''

                if tag.day == '0':
                    tag_data['day'] = 'Lundi'
                if tag.day == '1':
                    tag_data['day'] ='Mardi'
                if tag.day == '2':
                    tag_data['day'] = 'Mercredi'
                if tag.day == '3':
                    tag_data['day'] = 'Jeudi'
                if tag.day == '4':
                    tag_data['day'] = 'Vendredi'
                if tag.day == '5':
                    tag_data['day'] = 'Samedi'
                if tag.day == '6':
                    tag_data['day'] = 'Dimanche'
                if tag.month == '1':
                    tag_data['month'] = 'Janvier'
                if tag.month == '2':
                    tag_data['month'] = 'Fevrier'
                if tag.month == '3':
                    tag_data['month'] = 'Mars'
                if tag.month == '4':
                    tag_data['month'] = 'Avril'
                if tag.month == '5':
                    tag_data['month'] = 'Mai'
                if tag.month == '6':
                    tag_data['month'] = 'Juin'
                if tag.month == '7':
                    tag_data['month'] = 'Juillet'
                if tag.month == '8':
                    tag_data['month'] = 'Aout'
                if tag.month == '9':
                    tag_data['month'] = 'Septembre'
                if tag.month == '10':
                    tag_data['month'] = 'Octobre'
                if tag.month == '11':
                    tag_data['month'] = 'Novembre'
                if tag.month == '12':
                    tag_data['month'] = 'Decembre'

                docs.append(tag_data)

        return {
            'docs': docs,
            'data': data,
            'docids': docids,
            'company': self.env.user.company_id.name,
            'today': fields.Date.today().strftime('%d/%m/%Y'),

        }
