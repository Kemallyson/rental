from openerp import models, fields, api


class Tenant(models.Model):
    _name = 'rental.tenant'

    name = fields.Char(string='Tenant Name', required=True)
    national_id_no = fields.Char(string='National ID Number', required=True)
    email_address = fields.Char(string='Email Address')
    phone_no = fields.Char(string='Phone Number', required=True)
    is_current = fields.Boolean(string='Is Current', default=False, compute='compute_occupation_status', store=True)
    # one2many relations
    occupation_ids = fields.One2many('rental.occupation', 'tenant_id', string='Occupations')

    _sql_constraints = {('unique_national_id_no', 'unique(national_id_no)', 'National ID Number must be unique')}

    @api.onchange('name')
    def strip_name(self):
        if self.name:
            self.name = self.name.strip()

    @api.one
    @api.depends('occupation_ids.move_out_date')
    def compute_occupation_status(self):
        domain = ['&', ('move_out_date', '=', None), ('tenant_id', '=', self.id)]
        num_occupations = self.env['rental.occupation'].search_count(domain)
        if num_occupations > 0:
            self.is_current = True
        else:
            self.is_current = False
