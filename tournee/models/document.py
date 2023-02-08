from odoo import api, fields, models

class Document(models.Model):
    _inherit = 'documents.document'

    navire_id = fields.Many2one('navire.navire', compute='compute_doc_navire', store=True)

    @api.depends('attachment_id', 'attachment_id.res_model', 'attachment_id.res_id')
    def compute_doc_navire(self):
        for rec in self:
            navire =False
            if rec.attachment_id and rec.attachment_id.res_model == 'tags.task.anomalie' and rec.attachment_id.res_id:
                record =  self.env['tags.task.anomalie'].browse(rec.attachment_id.res_id)
                if record:

                    navire = record.navire_id and record.navire_id.id
            rec.navire_id = navire