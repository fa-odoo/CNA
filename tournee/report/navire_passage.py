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
                    WITH added_row_number AS (
  SELECT
    tag_id, navire_id, scan_date, scan_week, scan_month, scan_year,id,scan_week_first_day, scan_week_last_day,
    ROW_NUMBER() OVER(PARTITION BY scan_week, scan_year, tag_id, navire_id ORDER BY scan_date DESC) AS row_number
  FROM task_tags_line  where date_scan_ok=True
)
SELECT
 max(id) AS id,
tag_id as tag_id
, navire_id as navire_id,
 scan_week as   scan_week,
 scan_month as scan_month , 
 scan_week_last_day as end_date , 
 scan_week_first_day as start_date , 
 scan_year as scan_year,max(scan_date),extract(epoch from age(max(scan_date) , min(scan_date) )) / (60 * 60) as passage_time
FROM added_row_number 
WHERE (row_number = 1 OR row_number = 2)
 GROUP by tag_id, navire_id, scan_week,scan_month, scan_year, scan_week_last_day,scan_week_first_day
            )"""%(self._table))
