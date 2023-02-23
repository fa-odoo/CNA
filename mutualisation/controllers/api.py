from odoo import api, http, SUPERUSER_ID
from odoo.http import request, Response, JsonRequest
from werkzeug.exceptions import NotFound

import logging
_logger = logging.getLogger(__name__)

class ApiController(http.Controller):

    @http.route('/web/authenticate_mobile', type='json', auth="none")
    def authenticate(self, db, login, password, employe=None, pin=None, base_location=None):
        request.params['emp'] = employe
        request.params['pin'] = pin
        company_id = request.env['res.company'].sudo().search([])[0]
        if not company_id.sync_mobile:
            _logger.info("Connexion API est désactivé")
            return False
        request.session.authenticate(db, login, password)
        return request.env['ir.http'].session_info()
