from odoo import models, fields, api

class ServiceRequestReopenWizard(models.TransientModel):
    _name = 'service.request.reopen.wizard'
    _description = 'Reopen Service Request Wizard'

    request_id = fields.Many2one('service.request', string='Service Request', required=True)
    reason = fields.Text(string='Reason', required=True)

    def action_confirm_reopen(self):
        self.ensure_one()
        # Update state to draft
        self.request_id.state = 'draft'
        
        # Post message to chatter
        self.request_id.message_post(
            body=f"Request reopened by {self.env.user.name}. Reason: {self.reason}"
        )
        
        # Schedule activity for assigned user
        if self.request_id.assigned_to:
            self.request_id.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=self.request_id.assigned_to.id,
                summary='Request Reopened',
                note=f'This request has been reopened for the following reason: {self.reason}'
            )
        
        return {'type': 'ir.actions.act_window_close'}
