from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import AccessError


class TaskTagsLine(models.Model):
    _inherit = 'task.tags.line'

    create_emp_id = fields.Many2one(comodel_name="hr.employee", string="Créateur", tracking=True)
    write_emp_id = fields.Many2one(comodel_name="hr.employee", string="Dernière modification par", tracking=True)

    @api.model
    def create(self, values):
        res = super(TaskTagsLine, self).create(values)

        if request.session.get('uid'):
            if self.env['res.users'].search([('id', '=', request.session.get('uid'))]).is_multi_connexion:
                if request.session.get('emp_id'):
                    res.create_emp_id = request.session['emp_id']
                    res.write_emp_id = request.session['emp_id']
                else:
                    raise AccessError(_('Merci de vous reconnecter'))
            else:
                emp_id = self.env['hr.employee'].search([('user_id', '=', request.session.get('uid'))])
                if emp_id:
                    res.create_emp_id = emp_id.id
                    res.write_emp_id = emp_id.id

        return res

    def write(self, values):

        if request.session.get('uid'):
            if self.env['res.users'].search([('id', '=', request.session.get('uid'))]).is_multi_connexion:
                if request.session.get('emp_id'):
                    values['write_emp_id'] = request.session['emp_id']
                else:
                    raise AccessError(_('Merci de vous reconnecter'))
            else:
                emp_id = self.env['hr.employee'].search([('user_id', '=', request.session.get('uid'))])
                if emp_id:
                    values['write_emp_id'] = emp_id.id

        return super(TaskTagsLine, self).write(values)


