# -*- coding: utf-8 -*-
from odoo import api, fields, models


class NavireDuration(models.Model):
    _name = 'navire.duration'
    _description = "Durée Navire"
    _order = "start_date"

    @api.depends('navire_id', 'navire_id.ronde_ids', 'navire_id.ronde_ids.first_scan', 'navire_id.ronde_ids.tourne_duration')
    def _compute_real_duration(self):
        for rec in self:
            task_ids = self.env['project.task'].search([('navire_id', '=', rec.navire_id._origin.id), ('first_scan', '<=', rec.end_date), ('first_scan', '>=', rec.start_date)])
            rec.real_duration = sum(task_id.tourne_duration for task_id in task_ids)

    @api.depends('theoretical_duration', 'percent_duration')
    def _compute_percent_duration(self):
        for rec in self:
            if rec.real_duration and rec.theoretical_duration:
                rec.percent_duration = (rec.real_duration / rec.theoretical_duration) * 100
            else:
                rec.percent_duration = 0.0

    start_date = fields.Date(string="Date de début", required=True)
    end_date = fields.Date(string="Date de fin", required=True)
    org = fields.Char(string="ORG", required=True)
    theoretical_duration = fields.Float(string="Durée théorique", required=True)
    real_duration = fields.Float(string="Durée réelle", compute=_compute_real_duration, store=True)
    percent_duration = fields.Float(string="Durée %", compute=_compute_percent_duration, store=True)
    navire_id = fields.Many2one('navire.navire', string='Navire', required=True)
