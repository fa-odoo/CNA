from odoo import api, http, SUPERUSER_ID
from odoo.http import request, Response, JsonRequest

class ApiController(http.Controller):

    @http.route('/web/authenticate_mobile', type='json', auth="none")
    def authenticate(self, db, login, password, employe=None, pin=None, base_location=None):
        request.params['emp'] = employe
        request.params['pin'] = pin
        request.session.authenticate(db, login, password)
        return request.env['ir.http'].session_info()
