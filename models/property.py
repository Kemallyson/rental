from openerp import models, fields, api


class Property(models.Model):
    _name = 'rental.property'
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description', required=True)
    unit_ids = fields.One2many('rental.unit', 'property_id', string='Units')
    num_units = fields.Integer(string='No of Units', compute='compute_num_units', store=False)
    _sql_constraints = {('unique_name', 'unique(name)', 'Name of property must be unique.')}

    @api.one
    def compute_num_units(self):
        self.num_units = len(self.unit_ids)
