from openerp import models, fields, api, exceptions


class Unit(models.Model):
    _name = 'rental.unit'
    name = fields.Char(string='Name', required=True)
    property_id = fields.Many2one('rental.property', string='Property', required=True)
    rent_amount = fields.Float(string='Rent Amount', required=True)
    electricity_meter_no = fields.Char(string='Electricity Meter No')
    water_meter_no = fields.Char(string='Water Meter No')
    unit_use = fields.Selection([('commercial', 'Commercial'), ('residential', 'Residential')], string='Use',
                                required=True)
    area = fields.Float(string='Area in sq Feet')
    unit_type = fields.Selection(
        [('single', 'Single Room'), ('bedsitter', 'Bed Sitter'), ('1br', '1 Bedroom'), ('2br', '2 Bedroom'),
         ('3br', '3 Bedroom'), ('4br', '4 Bedroom'), ('5br', '5 Bedroom')], string='Type')

    is_occupied = fields.Boolean(string='Is Occupied', default=False, compute='compute_occupation_status', store=True)

    # one2many relations
    occupation_ids = fields.One2many('rental.occupation', 'unit_id', string='Occupations')
    _sql_constraints = {('unique_name', 'unique(property_id,name)', 'Units within a property must have unique names')}

    @api.one
    @api.depends('occupation_ids.move_out_date')
    def compute_occupation_status(self):
        domain = [('move_out_date', '=', None), ('unit_id', '=', self.id)]
        num_occupations = self.env['rental.occupation'].search_count(domain)
        if num_occupations > 0:
            self.is_occupied = True
        else:
            self.is_occupied = False

    @api.one
    @api.onchange('unit_use')
    def unit_use_reset_dependents(self):
        if self.unit_use == 'commercial':
            self.unit_type = None
        if self.unit_use == 'residential':
            self.area = 0

    @api.constrains('rent_amount')
    def validate_rent_amount(self):
        if self.rent_amount <= 0:
            raise exceptions.ValidationError('Rent amount must be greater than zero')
