# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import timedelta

class Naviretime(models.Model):
    _name = 'navire.time'
    _description = 'Temps de passage moyenne'

    navire_id = fields.Many2one('navire.navire', 'Navire')
    tag_id = fields.Many2one('tags.tags', 'Tag')
    start_date = fields.Date(string="Date début", required=True)
    end_date = fields.Date(string="Date fin", required=True)
    week = fields.Char('Semaine',)
    month = fields.Char('Mois', )
    year = fields.Char('Année', )
    passage_time = fields.Float(group_operator='avg')


    @api.model
    def _cron_create_lines(self):

        navire_ids = self.env['navire.navire'].search([])
        self.env.cr.execute("""delete from navire_time;""")
        self.env.cr.commit()
        navire_ids.create_navire_time()
        # cr = self.env.cr
        # for navire_id in navire_ids:
        #     nb = 0
        #     avg = False
        #     cr.execute(
        #         """
        #         SELECT id FROM tags_tags
        #         WHERE navire_id = navire_id
        #         """.format(navire_id=navire_id.id))
        #     today = fields.Date().today()
        #     start_week = today - timedelta(days=today.weekday())
        #     end_week = start_week + timedelta(days=4)
        #     tag_ids = [val[0] for val in cr.fetchall()]
        #
        #     for tag_id in tag_ids:
        #         scan_ids = self.env['task.tags.line'].search([('scan_date', '>=', start_week),
        #                                                       ('scan_date', '<=', end_week),
        #                                                       ('scan_date', '<=', end_week),
        #                                                       ('tag_id', '<=', tag_id),
        #                                                       ('date_scan_ok', '=', True)], order='scan_date desc', limit=2)
        #         if scan_ids:
        #             nb += 1
        #             if len(scan_ids) > 1:
        #                 if avg:
        #                     avg += scan_ids[0].scan_date - scan_ids[1].scan_date
        #                 else:
        #                     avg = scan_ids[0].scan_date - scan_ids[1].scan_date
        #
        #     navire_time_id = self.env['navire.time'].search([('navire_id', '=', navire_id.id), ('start_date', '=', start_week), ('end_date', '=', end_week)])
        #     avg_time = 0
        #     if nb:
        #         avg_time = (avg/nb).total_seconds() / 3600
        #     if navire_time_id and nb:
        #         navire_time_id.avg_time = avg_time
        #     else:
        #         self.env['navire.time'].create({
        #             'navire_id': navire_id.id,
        #             'start_date': start_week,
        #             'end_date': end_week,
        #             'avg_time': avg_time,
        #         })
