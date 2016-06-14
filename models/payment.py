from openerp import models, fields, api, exceptions


class Payment(models.Model):
    _name = 'rental.payment'
    bill_id = fields.Many2one('rental.bill', string='Rental Bill', required=True, domain=[('balance', '>', 0)])
    amount = fields.Float(string='Amount', required=True)
    paid_by = fields.Char(string='Paid By', required=True)

    @api.multi
    def name_get(self):
        res = []
        for payment in self:
            name = "Payment Ref No: %s" % payment.id
            res += [(payment.id, name)]
        return res

    @api.one
    @api.constrains('amount')
    def validate_amount(self):
        if self.amount <= 0:
            raise exceptions.ValidationError('Amount paid must be greater than zero')
        if self.amount > self.bill_id.balance:
            raise exceptions.ValidationError('Amount paid cannot be greater than the outstanding balance')

    # Set the payee name to that of the tenant responsible for the selected bill
    @api.one
    @api.onchange('bill_id')
    def compute_paid_by(self):
        self.paid_by = self.bill_id.occupation_id.tenant_id.name

    # Set the amount about to be paid to the balance of the selected bill
    @api.one
    @api.onchange('bill_id')
    def compute_amount(self):
        self.amount = self.bill_id.balance
