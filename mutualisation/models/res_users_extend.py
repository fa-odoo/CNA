from odoo import models, SUPERUSER_ID, fields, api, _
from odoo.http import request
from odoo.exceptions import AccessDenied


class Users(models.Model):
    _inherit = 'res.users'

    is_multi_connexion = fields.Boolean(string="Multi utilisateur")

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        user_id = super()._login(db, login, password, user_agent_env)
        with cls.pool.cursor() as cr:
            self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
            with self._assert_can_auth():
                user = self.search([('id', '=', user_id)], limit=1)
                if user.is_multi_connexion:
                    if 'emp' in request.params and request.params['emp'] != '' and 'pin' in request.params and request.params['pin'] != '':
                        emp = request.env['hr.employee'].with_user(SUPERUSER_ID).search(
                            [('name', '=', request.params['emp']), ('pin', '=', request.params['pin']), ('connect_user_id', '=', user.id)], limit=1)
                        if emp:
                            request.session['emp_id'] = emp.id
                        else:
                            raise AccessDenied(_("Incorrecte employé/pin"))
                    else:
                        raise AccessDenied(_("Saisi employé/pin"))
        return user_id


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    connect_user_id = fields.Many2one('res.users', 'Utilisateur de connexion')