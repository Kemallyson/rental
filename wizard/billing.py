import logging
import datetime
import re

from openerp import models, fields, api, exceptions

_logger = logging.getLogger(__name__)


class BillingWizard(models.TransientModel):
    _name = 'rental.billing_wizard'
    occupation_ids = fields.Many2many('rental.occupation', string='Occupations', domain=[('move_out_date', '=', None)])
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

    message = fields.Char(string='Message', default='', readonly=True)

    @api.one
    @api.onchange('month', 'year')
    def reset_due_date(self):
        if not self.year_is_valid():
            raise exceptions.ValidationError('Year is not valid.')
        if not self.month:
            raise exceptions.ValidationError('Month is not selected.')
        date_due = "%s-%s-05" % (self.year, self.month)
        self.date_due = date_due

    @api.one
    @api.constrains('year')
    def validate_year(self):
        if not self.year_is_valid():
            raise exceptions.ValidationError('Year is not valid.')

    @api.multi
    def add_all_occupations(self):
        self.ensure_one()
        ids = self.env['rental.occupation'].search([('move_out_date', '=', None)])
        self.occupation_ids = ids
        # reopen wizard form
        return self.do_reopen_form()

    @api.multi
    def generate_bills(self):
        self.ensure_one()
        if len(self.occupation_ids) == 0:
            raise exceptions.ValidationError('Occupations are required to generate bills.')
        num_created_bills = 0
        num_skipped_bills = 0
        for occ in self.occupation_ids:
            if not self.bill_exists(occ.id, self.month, self.year):
                bill = {'occupation_id': occ.id, 'month': self.month, 'year': self.year,
                        'amount': occ.unit_id.rent_amount,
                        'date_due': self.date_due}
                self.env['rental.bill'].create(bill)
                _logger.info("Bill %s(%s-%s) successfully generated" % (occ.unit_id.name, self.month, self.year))
                num_created_bills += 1
            else:
                _logger.warning(
                    "Bill %s(%s-%s) could not be generated because it exists!" % (
                        occ.unit_id.name, self.month, self.year))
                num_skipped_bills += 1
        message = "Bills generated: %s. Bills skipped(Pre-existent): %s" % (num_created_bills, num_skipped_bills)
        self.message = message
        _logger.info(message)

        return self.do_reopen_form()

    def year_is_valid(self):
        if not re.match("^[0-9]{4}$", self.year):
            return False
        return True

    def bill_exists(self, occupation_id, month, year):
        num_bills = self.env['rental.bill'].search_count(
            [('occupation_id', '=', occupation_id), ('month', '=', month), ('year', '=', year)])
        if num_bills == 1:
            return True
        return False

    @api.multi
    def do_reopen_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }
