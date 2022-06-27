from odoo import api, fields, models


class ReasonTagNotScanned(models.TransientModel):
    _name = 'add.comment.task.wizard'
    _description = 'we use this class to add comments to project_task and validate a task'

    comments = fields.Text(string="Commentaires", required=False)
    is_required = fields.Boolean()

    def validate(self):
        task = self.env['project.task'].search([('id', '=', self.env.context.get('active_id'))])
        task.comments = self.comments
        task.action_fsm_validate()
