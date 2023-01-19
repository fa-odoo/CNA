# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import timedelta

class Naviretime(models.Model):
    _name = 'navire.time'
    _description = 'Temps de passage moyenne'

    name = fields.Char('Nom', compute='_compute_name', store=True)
    navire_id = fields.Many2one('navire.navire', 'Navire')
    start_date = fields.Date(string="Date début", required=True)
    end_date = fields.Date(string="Date fin", required=True)
    week = fields.Char('Semaine', compute='_compute_related_date')
    month = fields.Char('Mois', compute='_compute_related_date')
    year = fields.Char('Année', compute='_compute_related_date')
    avg_time = fields.Float(string='Temps de passage moyenne')

    @api.depends('avg_time', 'week')
    def _compute_name(self):
        for rec in self:
            if rec.avg_time and rec.week:
                rec.name = "S{} {}".format(rec.week, rec.avg_time)

    @api.depends('start_date')
    def _compute_related_date(self):
        for rec in self:
            if rec.start_date:
                rec.week = rec.start_date.isocalendar()[1]
                rec.month = rec.start_date.month
                rec.year = rec.start_date.year

    def _cron_create_lines(self):
        navire_ids = self.env['navire.navire'].search([])
        cr = self.env.cr
        for navire_id in navire_ids:
            nb = 0
            avg = False
            cr.execute(
                """
                SELECT id FROM tags_tags 
                WHERE navire_id = navire_id
                """.format(navire_id=navire_id.id))
            today = fields.Date().today()
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=4)
            tag_ids = [val[0] for val in cr.fetchall()]

            for tag_id in tag_ids:
                navire_ids = self.env['task.tags.line'].search([('scan_date', '>=', start_week), ('scan_date', '<=', end_week), ('scan_date', '<=', end_week), ('tag_id', '<=', tag_id), ('date_scan_ok', '=', True)], order='scan_date desc', limit=2)
                if navire_ids:
                    nb += 1
                    if len(navire_ids) > 1:
                        if avg:
                            avg += navire_ids[0].scan_date - navire_ids[1].scan_date
                        else:
                            avg = navire_ids[0].scan_date - navire_ids[1].scan_date

            navire_time_id = self.env['navire.time'].search([('navire_id', '=', navire_id.id), ('start_date', '=', start_week), ('end_date', '=', end_week)])

            if navire_time_id:
                navire_time_id.avg_time = avg/nb
            else:
                self.env['navire.time'].create({
                    'navire_id': navire_id.id,
                    'start_date': start_week,
                    'end_date': end_week,
                    'avg_time': (avg/nb).total_seconds() / 3600,
                })
