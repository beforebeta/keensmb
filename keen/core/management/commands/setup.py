from optparse import make_option
from django.core.management.base import BaseCommand
from django.conf import settings
from fuzzywuzzy import process
from keen import print_stack_trace
from keen.core.models import *

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--all', action='store_true', dest='all', default=False, help='setup all'),)

    def handle(self, *args, **options):
        err = self.stderr
        out = self.stdout
        if options['all']:
            setup_all()


def section(message):
    print " "
    print "*"*60
    print message
    print "*"*60


################################################################################################################
# Setup Core
################################################################################################################
def _setup_field(group, group_ranking, name, description, field_type, length=-1):
    print "Setup field %s-%s" % (group, name)
    obj,created = CustomerField.objects.get_or_create(grouping=group,
                                             group_ranking=group_ranking,
                                             name=name,
                                             description=description,
                                             type=field_type,
                                             length=length)
    print created

def _setup_core():
    section("Creating Customer Field Catalog")

    _basic = CustomerField.FIELD_GROUPS.basic
    _household = CustomerField.FIELD_GROUPS.household
    _custom = CustomerField.FIELD_GROUPS.custom

    _string = CustomerField.FIELD_TYPES.string
    _bool = CustomerField.FIELD_TYPES.bool
    _date = CustomerField.FIELD_TYPES.date

    _setup_field(_basic, 100, "first_name", "First Name", _string)
    _setup_field(_basic, 200, "last_name", "Last Name", _string)
    _setup_field(_basic, 300, "dob", "Birthday", _date)
    _setup_field(_basic, 301, "age", "Age", _string)
    _setup_field(_basic, 400, "email", "Email", _string)
    _setup_field(_basic, 500, "gender", "Gender", _string)
    _setup_field(_basic, 600, "address#line1", "Address Line 1", _string)
    _setup_field(_basic, 601, "address#line2", "Address Line 2", _string)
    _setup_field(_basic, 700, "address#city", "City", _string)
    _setup_field(_basic, 800, "address#zipcode", "ZipCode", _string)
    _setup_field(_basic, 900, "address#state", "State", _string)
    _setup_field(_basic, 1000, "address#country", "Country", _string)
    _setup_field(_basic, 1100, "phone#mobile", "Mobile Phone", _string)
    _setup_field(_basic, 1200, "phone#home", "Home Phone", _string)
    _setup_field(_basic, 1300, "occupation", "Occupation", _string)
    _setup_field(_basic, 1400, "education", "Education", _string)

    _setup_field(_household, 100, "marital_status", "Marital Status", _string)
    _setup_field(_household, 200, "has_children", "Presence of Children", _bool)
    _setup_field(_household, 300, "home_owner_status", "Home Owner Status", _string)
    _setup_field(_household, 400, "income", "Household Income", _string)
    _setup_field(_household, 500, "home_market_value", "Home Market Value", _string)
    _setup_field(_household, 600, "high_net_worth", "High Net Worth", _bool)
    _setup_field(_household, 700, "length_of_residence", "Length of Residence",_bool)

    _setup_field(_custom, 100, "interest#arts", "Interest in Arts and Crafts", _bool)
    _setup_field(_custom, 200, "interest#blogging", "Interest in Blogging", _bool)
    _setup_field(_custom, 300, "interest#books", "Interest in Books", _bool)
    _setup_field(_custom, 400, "interest#business", "Interest in Business", _bool)
    _setup_field(_custom, 500, "interest#health", "Interest in Health and Wellness", _bool)
    _setup_field(_custom, 600, "interest#news", "Interest in News and Current Events", _bool)

    _setup_field(_custom, 100, "purchase#automotive", "Purchases Automotive Goods", _bool)
    _setup_field(_custom, 200, "purchase#baby", "Has Bought a Baby Product", _bool)
    _setup_field(_custom, 300, "purchase#beauty", "Purchases Beauty Products", _bool)
    _setup_field(_custom, 400, "purchase#charitable","Indicates liklihood of Being a Charitable Donor", _bool)
    _setup_field(_custom, 500, "purchase#cooking", "Purchases cooking magazines; interest in cooking", _bool)
    _setup_field(_custom, 600, "purchase#discount", "Purchase behavior: Interest in discounts", _bool)
    _setup_field(_custom, 700, "purchase#high_end_brands", "Has bought a premium CPG brand in the past 18 months ", _bool)
    _setup_field(_custom, 800, "purchase#home_garden", "Purchases Home & Garden Products", _bool)
    _setup_field(_custom, 900, "purchase#home_improvement", "Purchases Home Improvement Products", _bool)
    _setup_field(_custom, 1000, "purchase#luxury", "Purchases Luxury Items", _bool)
    _setup_field(_custom, 1100, "purchase#magazine", "Purchases Magazine Subscriptions", _bool)
    _setup_field(_custom, 1200, "purchase#outdoor", "Purchases Outdoor and Adventure Products", _bool)
    _setup_field(_custom, 1300, "purchase#pets", "Purchases Pet Related Products", _bool)
    _setup_field(_custom, 1400, "purchase#power_shopper", "Purchases Items from Multiple Retail Channels", _bool)
    _setup_field(_custom, 1500, "purchase#sports", "Purchases Sporting Goods / Sports Related Products", _bool)
    _setup_field(_custom, 1600, "purchase#technology", "Purchases Technology Products", _bool)
    _setup_field(_custom, 1700, "purchase#travel", "Purchases Travel Related Goods", _bool)

def _setup_sample_data():

    #setup default client
    client,created = Client.objects.get_or_create(slug="default_client", name="default_client")
    customer_source,created = CustomerSource.objects.get_or_create(client=client, slug="import")

    #setup default field list
    if client.customer_fields.all().count() == 0:
        #only setup fields is nothing has been manually created
        customers_appended = open("./data/setup/customers_appended.csv", "r").readlines()
        csv_schema_fields = [f.strip() for f in customers_appended[0].split(",")]
        all_customer_fields = dict([(c.description,c) for c in CustomerField.objects.all()])
        clients_customer_fields = map(lambda x:
                                      all_customer_fields[process.extractOne(x, all_customer_fields.keys())[0]],
                                      csv_schema_fields)
        assert len(csv_schema_fields) == len(clients_customer_fields) #should map all fields
        for customer_text in customers_appended[1:]:
            customer_text = customer_text.replace("\r","")
            customer_text = customer_text.replace("\n","")
            customer_values = customer_text.split(",")
            if len(customer_values) == len(clients_customer_fields):
                c = Customer(client=client, source=customer_source)
                for i in range(0, len(customer_values)):
                    c.data[clients_customer_fields[i].name] = str(customer_values[i])
                print c.data
                c.save()


def setup_all():
    _setup_core()
    _setup_sample_data()

