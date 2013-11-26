#import colander
#
#
#class Phone(object):
#
#    def __init__(self, message=None):
#        if message is None:
#            message = 'Invalid phone number'
#        self.message = message
#
#    def __call__(self, node, value):
#        clean = self.noise.sub('', value)
#        if self.pattern.match('clean'):
#            raise colander.Invalid(node, self.message)
#
#
#@colander.deferred
#def customer_data_schema(node, kw):
#    """Build customer schema for given client dynamicly.
#    """
#    client = kw['client']
#    groups = {}
#
#    for field in client.customer_fields.order_by('group'):
#        if field.group.
#        if field.type == 'S':
#            schema.add(colander.SchemaNode(colander.Str(), name=field.name,
#                                           missing=None))
#        elif field.type == 'I':
#            schema.add(colander.SchemaNode(colander.Int(), name=field.name,
#                                           missing=None))
#        elif field.type == 'D':
#            schema.add(colander.SchemaNode(colander.Date(), name=field.name,
#                                           missing=None))
#        elif field.type == 'E':
#            schema.add(colander.SchemaNode(colander.Str(), name=field.name,
#                validator=colander.Email(), missing=None))
#        elif field.type == 'U':
#            schema.add(colander.SchemaNode(colander.Date(), name=field.name,
#                validator=colander.URL(), missing=None))
#        elif field.type == 'P':
#            schema.add(colander.SchemaNode(colander.String(), name=field.name,
#                validator=Phone(), missing=None))
#        else:
#            raise ValueError('Unknown customer field {name} type {type!r}'.format(field))
#
#    return schema
#
#
#class NewCustomerSchema(colander.Schema):
#    """New customer schema
#    """
#    email = colander.SchemaNode(colander.Str(), validator=colander.Email())
#    data = customer_data_schema
#
#
#class CustomerSchema(colander.Schema):
#    """Schema for existing customer
#    """
#    id = colander.SchemaNode(colander.Int())
#    email = colander.SchemaNode(colander.Str(), validator=colander.Email())
#    data = customer_data_schema
