import re
import datetime

from openerp import models, fields, api, exceptions


class Bill(models.Model):
    _name = 'rental.bill'
    occupation_id = fields.Many2one('rental.occupation', string='Occupation', domain=[('move_out_date', '=', None)],
                                    required=True)
    month = fields.Selection(
        [('01', 'January'),
         ('02', 'February'),
         ('03', 'March'),
         ('04', 'April'),
         ('05', 'May'),
         ('06', 'June'),
         ('07', 'July'),
         ('08', 'August'),
         ('09', 'September'),
         ('10', 'October'),
         ('11', 'November'),
         ('12', 'December')
         ],
        string='Month', required=True, default=datetime.date.today().strftime("%m")
    )
    year = fields.Char(string='Year', required=True, default=datetime.date.today().strftime("%Y"))
    date_due = fields.Date(string='Date Due', required=True,
                           default="%s-%s" % (datetime.date.today().strftime("%Y-%m"), "05"))
    amount = fields.Float(string='Amount', required=True)
    payment_ids = fields.One2many('rental.payment', 'bill_id', 'Payments')
    # Computed fields
    amount_paid = fields.Float(string='Amount Paid', compute='compute_amount_paid', store=False)
    balance = fields.Float(string='Balance', compute='compute_balance', store=False)
    _sql_constraints = {
        ('unique_occupation_month_year', 'unique(occupation_id, month,year)', 'A similar bill has already been created.')
    }

    @api.one
    def compute_amount_paid(self):
        amount = 0
        for payment in self.payment_ids:
            amount += payment.amount
        self.amount_paid = amount

    @api.one
    def compute_balance(self):
        self.balance = self.amount - self.amount_paid

    @api.multi
    def name_get(self):
        res = []
        for bill in self:
            name = "%s (%s, %s)" % (bill.occupation_id.unit_id.name, bill.month, bill.year)
            res += [(bill.id, name)]
        return res

    @api.one
    @api.constrains('year')
    def validate_year(self):
        if not self.year_is_valid():
            raise exceptions.ValidationError('Year is not valid.')

    def year_is_valid(self):
        if not re.match("^[0-9]{4}$", self.year):
            return False
        return True

    @api.one
    @api.onchange('month', 'year')
    def reset_due_date(self):
        if not self.year_is_valid():
            raise exceptions.ValidationError('Year is not valid.')
        date_due = "%s-%s-05" % (self.year, self.month)
        self.date_due = date_due

    @api.one
    @api.constrains('amount')
    def validate_amount(self):
        if self.amount == 0:
            raise exceptions.ValidationError('Bill amount cannot be zero')
