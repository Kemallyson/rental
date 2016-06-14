from openerp import models, fields, api, exceptions


class Occupation(models.Model):
    _name = 'rental.occupation'
    _rec_name = 'id'
    tenant_id = fields.Many2one('rental.tenant', string='Tenant', domain=[('is_current', '=', False)], required=True)
    unit_id = fields.Many2one('rental.unit', string='Unit', domain=[('is_occupied', '=', False)], required=True)
    move_in_date = fields.Date(string='Move In Date', required=True)
    move_out_date = fields.Date(string='Move Out Date')
    deposit_paid = fields.Float(string='Deposit Paid', required=True)

    @api.multi
    def name_get(self):
        res = []
        for occ in self:
            name = "%s (%s)" % (occ.unit_id.name, occ.tenant_id.name)
            res += [(occ.id, name)]
        return res

    @api.onchange('unit_id')
    def on_change_unit_id(self):
        if self.unit_id:
            self.deposit_paid = self.unit_id.rent_amount
        else:
            self.deposit_paid = 0

    @api.constrains('deposit_paid')
    def validate_deposit_paid(self):
        if self.deposit_paid < 0:
            raise exceptions.ValidationError('Deposit paid cannot be a negative value')
