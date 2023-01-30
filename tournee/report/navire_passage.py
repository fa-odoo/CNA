from odoo import fields, models, api
from odoo import tools


class NavirePassageTime(models.Model):
    _name = 'navire.times.passage.report'
    _description = 'temps de passage'
    _auto = False

    navire_id = fields.Many2one('navire.navire', 'Navire', readonly=True)
    tag_id = fields.Many2one('tags.tags', 'Tag', readonly=True)
    start_date = fields.Date(string="Date début", readonly=True)
    end_date = fields.Date(string="Date fin", readonly=True)
    scan_week = fields.Char('Semaine', readonly=True)
    scan_month = fields.Char('Mois', readonly=True)
    scan_year = fields.Char('Année', readonly=True)
    passage_time = fields.Float(group_operator='avg', readonly=True)

    def init(self):
        # self._table = 'navire_time_passage_repor'
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
                create or replace view %s as (
WITH ptt AS (
SELECT * FROM
(SELECT *, ROW_NUMBER() OVER (PARTITION BY 
tag_id, DATE(scan_date) ORDER BY scan_date DESC) AS Row_ID FROM (SELECT * FROM task_tags_line WHERE scan_date is not null AND temps_passage_daily is not null and date_scan_ok is True) as res
) AS A WHERE Row_ID <2
)
SELECT max(id) as id, ptt.tag_id as tag_id, ptt.navire_id as navire_id,
	ptt.scan_week as scan_week,
	ptt.scan_month as scan_month ,
	ptt.scan_year as scan_year,
	ptt.scan_week_last_day as end_date , 
	ptt.scan_week_first_day as start_date , 
	((SUM(ptt.temps_passage_daily) + (24*(6-count(ptt.scan_week)))) / (6)) as passage_time, count(ptt.scan_week)
FROM ptt
GROUP BY CONCAT(ptt.scan_week, '/', ptt.scan_year), ptt.tag_id, ptt.navire_id, ptt.scan_week, ptt.scan_month, ptt.scan_year, ptt.scan_week_last_day, ptt.scan_week_first_day
            )"""%(self._table))
