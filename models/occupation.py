from openerp import models, fields, api


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
