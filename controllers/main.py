from odoo import http
from odoo.http import request

class ServiceRequestController(http.Controller):

    # Override/Inherit a template (ví dụ tạo 1 route trả về template)
    @http.route('/service/requests', type='http', auth='user', website=True)
    def list_service_requests(self, **kwargs):
        requests = request.env['service.request'].search([])
        return request.render('service_request_managemen.portal_my_service_requests', {
            'requests': requests
        })
