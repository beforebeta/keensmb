from optparse import make_option
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django import db
from django.db import transaction
from fuzzywuzzy import process
from keen import print_stack_trace
from keen.core.models import *
from keen.web.models import PageCustomerField, SignupForm, Dashboard, HelpText
from dateutil.relativedelta import *

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
def _setup_field(group, group_ranking, name, title, field_type, required=False, width=120):
    print "Setup field %s-%s" % (group, name)
    obj, created = CustomerField.objects.get_or_create(group=group, name=name)

    # unconditionally update these properties
    obj.title = title
    obj.type = field_type
    obj.group_ranking = group_ranking
    obj.required = required
    obj.width = width
    obj.save()

    cast = {
        # 'date': '::date',
        'int': '::integer',
        'float': '::float',
        #'bool': '::bool',
    }.get(field_type, '')

    c = db.connection.cursor()
    try:
        index_name = 'core_customer_data_' + name.replace('#', '_')
        c.execute('''drop index if exists %(index_name)s''' % locals())
        c.execute('''create index %(index_name)s
                    on core_customer(((data->'%(name)s')%(cast)s))''' % locals())
    finally:
        c.close()


def _setup_core():
    section("Creating Customer Field Catalog")

    with transaction.atomic():
        _basic,created = CustomerFieldGroup.objects.get_or_create(name=CustomerFieldGroup.FIELD_GROUPS.basic)
        _household,created = CustomerFieldGroup.objects.get_or_create(name=CustomerFieldGroup.FIELD_GROUPS.household)
        _custom,created = CustomerFieldGroup.objects.get_or_create(name=CustomerFieldGroup.FIELD_GROUPS.custom)

    _string = CustomerField.FIELD_TYPES.string
    _bool = CustomerField.FIELD_TYPES.bool
    _date = CustomerField.FIELD_TYPES.date

    #_setup_field(_basic, 0, CUSTOMER_FIELD_NAMES.profile_image, "Profile Image", _string)
    #_setup_field(_basic, 1, CUSTOMER_FIELD_NAMES.social__facebook, "Facebook", _string)
    #_setup_field(_basic, 2, CUSTOMER_FIELD_NAMES.social__twitter, "Twitter", _string)
    #_setup_field(_basic, 3, CUSTOMER_FIELD_NAMES.social__googleplus, "Google Plus", _string)
    #_setup_field(_basic, 100, CUSTOMER_FIELD_NAMES.full_name, "Full Name", _string)
    #_setup_field(_basic, 300, CUSTOMER_FIELD_NAMES.dob, "Birthday", _date)
    #_setup_field(_basic, 301, CUSTOMER_FIELD_NAMES.age, "Age", _string)
    #_setup_field(_basic, 400, CUSTOMER_FIELD_NAMES.gender, "Gender", _string)
    #_setup_field(_basic, 500, CUSTOMER_FIELD_NAMES.email, "Email", _string)
    #_setup_field(_basic, 600, CUSTOMER_FIELD_NAMES.address__line1, "Address Line 1", _string)
    #_setup_field(_basic, 601, CUSTOMER_FIELD_NAMES.address__line2, "Address Line 2", _string)
    #_setup_field(_basic, 700, CUSTOMER_FIELD_NAMES.address__city, "City", _string)
    #_setup_field(_basic, 800, CUSTOMER_FIELD_NAMES.address__zipcode, "ZipCode", _string)
    #_setup_field(_basic, 900, CUSTOMER_FIELD_NAMES.address__state, "State", _string)
    #_setup_field(_basic, 1000, CUSTOMER_FIELD_NAMES.address__country, "Country", _string)
    #_setup_field(_basic, 1100, CUSTOMER_FIELD_NAMES.phone, "Phone", _string)
    #_setup_field(_basic, 1300, CUSTOMER_FIELD_NAMES.occupation, "Occupation", _string)
    #_setup_field(_basic, 1400, CUSTOMER_FIELD_NAMES.education, "Education", _string)
    #
    #_setup_field(_household, 100, CUSTOMER_FIELD_NAMES.marital_status, "Marital Status", _string)
    #_setup_field(_household, 200, CUSTOMER_FIELD_NAMES.has_children, "Presence of Children", _bool)
    #_setup_field(_household, 300, CUSTOMER_FIELD_NAMES.home_owner_status, "Home Owner Status", _string)
    #_setup_field(_household, 400, CUSTOMER_FIELD_NAMES.income, "Household Income", _string)
    #_setup_field(_household, 500, CUSTOMER_FIELD_NAMES.home_market_value, "Home Market Value", _string)
    #_setup_field(_household, 600, CUSTOMER_FIELD_NAMES.high_net_worth, "High Net Worth", _bool)
    #_setup_field(_household, 700, CUSTOMER_FIELD_NAMES.length_of_residence, "Length of Residence",_bool)
    #
    #_setup_field(_custom, 100, CUSTOMER_FIELD_NAMES.interest__arts, "Interest in Arts and Crafts", _bool)
    #_setup_field(_custom, 200, CUSTOMER_FIELD_NAMES.interest__blogging, "Interest in Blogging", _bool)
    #_setup_field(_custom, 300, CUSTOMER_FIELD_NAMES.interest__books, "Interest in Books", _bool)
    #_setup_field(_custom, 400, CUSTOMER_FIELD_NAMES.interest__business, "Interest in Business", _bool)
    #_setup_field(_custom, 500, CUSTOMER_FIELD_NAMES.interest__health, "Interest in Health and Wellness", _bool)
    #_setup_field(_custom, 600, CUSTOMER_FIELD_NAMES.interest__news, "Interest in News and Current Events", _bool)
    #_setup_field(_custom, 100, CUSTOMER_FIELD_NAMES.purchase__automotive, "Purchases Automotive Goods", _bool)
    #_setup_field(_custom, 200, CUSTOMER_FIELD_NAMES.purchase__baby, "Has Bought a Baby Product", _bool)
    #_setup_field(_custom, 300, CUSTOMER_FIELD_NAMES.purchase__beauty, "Purchases Beauty Products", _bool)
    #_setup_field(_custom, 400, CUSTOMER_FIELD_NAMES.purchase__charitable,"Indicates liklihood of Being a Charitable Donor", _bool)
    #_setup_field(_custom, 500, CUSTOMER_FIELD_NAMES.purchase__cooking, "Purchases cooking magazines; interest in cooking", _bool)
    #_setup_field(_custom, 600, CUSTOMER_FIELD_NAMES.purchase__discount, "Purchase behavior: Interest in discounts", _bool)
    #_setup_field(_custom, 700, CUSTOMER_FIELD_NAMES.purchase__high_end_brands, "Has bought a premium CPG brand in the past 18 months ", _bool)
    #_setup_field(_custom, 800, CUSTOMER_FIELD_NAMES.purchase__home_garden, "Purchases Home & Garden Products", _bool)
    #_setup_field(_custom, 900, CUSTOMER_FIELD_NAMES.purchase__home_improvement, "Purchases Home Improvement Products", _bool)
    #_setup_field(_custom, 1000, CUSTOMER_FIELD_NAMES.purchase__luxury, "Purchases Luxury Items", _bool)
    #_setup_field(_custom, 1100, CUSTOMER_FIELD_NAMES.purchase__magazine, "Purchases Magazine Subscriptions", _bool)
    #_setup_field(_custom, 1200, CUSTOMER_FIELD_NAMES.purchase__outdoor, "Purchases Outdoor and Adventure Products", _bool)
    #_setup_field(_custom, 1300, CUSTOMER_FIELD_NAMES.purchase__pets, "Purchases Pet Related Products", _bool)
    #_setup_field(_custom, 1400, CUSTOMER_FIELD_NAMES.purchase__power_shopper, "Purchases Items from Multiple Retail Channels", _bool)
    #_setup_field(_custom, 1500, CUSTOMER_FIELD_NAMES.purchase__sports, "Purchases Sporting Goods / Sports Related Products", _bool)
    #_setup_field(_custom, 1600, CUSTOMER_FIELD_NAMES.purchase__technology, "Purchases Technology Products", _bool)
    #_setup_field(_custom, 1700, CUSTOMER_FIELD_NAMES.purchase__travel, "Purchases Travel Related Goods", _bool)

    _setup_field(_basic, 0, CUSTOMER_FIELD_NAMES.profile_image,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.profile_image], _string)
    _setup_field(_basic, 1, CUSTOMER_FIELD_NAMES.social__facebook,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.social__facebook], _string)
    _setup_field(_basic, 2, CUSTOMER_FIELD_NAMES.social__twitter,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.social__twitter], _string)
    _setup_field(_basic, 3, CUSTOMER_FIELD_NAMES.social__googleplus,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.social__googleplus], _string)
    _setup_field(_basic, 100, CUSTOMER_FIELD_NAMES.full_name,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.full_name],
                 _string, required=True, width=175)
    _setup_field(_basic, 300, CUSTOMER_FIELD_NAMES.dob,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.dob], _date)
    _setup_field(_basic, 301, CUSTOMER_FIELD_NAMES.age,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.age], _string)
    _setup_field(_basic, 400, CUSTOMER_FIELD_NAMES.gender,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.gender], _string)
    _setup_field(_basic, 500, CUSTOMER_FIELD_NAMES.email,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.email],
                 _string, required=True, width=220)
    _setup_field(_basic, 600, CUSTOMER_FIELD_NAMES.address__line1,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.address__line1], _string)
    _setup_field(_basic, 601, CUSTOMER_FIELD_NAMES.address__line2,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.address__line2], _string)
    _setup_field(_basic, 700, CUSTOMER_FIELD_NAMES.address__city,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.address__city], _string)
    _setup_field(_basic, 800, CUSTOMER_FIELD_NAMES.address__zipcode,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.address__zipcode], _string)
    _setup_field(_basic, 900, CUSTOMER_FIELD_NAMES.address__state,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.address__state], _string)
    _setup_field(_basic, 1000, CUSTOMER_FIELD_NAMES.address__country,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.address__country], _string)
    _setup_field(_basic, 1100, CUSTOMER_FIELD_NAMES.phone,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.phone], _string)
    _setup_field(_basic, 1300, CUSTOMER_FIELD_NAMES.occupation,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.occupation], _string)
    _setup_field(_basic, 1400, CUSTOMER_FIELD_NAMES.education,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.education], _string)

    _setup_field(_household, 100, CUSTOMER_FIELD_NAMES.marital_status,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.marital_status], _string)
    _setup_field(_household, 200, CUSTOMER_FIELD_NAMES.has_children,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.has_children], _bool)
    _setup_field(_household, 300, CUSTOMER_FIELD_NAMES.home_owner_status,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.home_owner_status], _string)
    _setup_field(_household, 400, CUSTOMER_FIELD_NAMES.income,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.income], _string)
    _setup_field(_household, 500, CUSTOMER_FIELD_NAMES.home_market_value,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.home_market_value], _string)
    _setup_field(_household, 600, CUSTOMER_FIELD_NAMES.high_net_worth,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.high_net_worth], _bool)
    _setup_field(_household, 700, CUSTOMER_FIELD_NAMES.length_of_residence,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.length_of_residence],_bool)

    _setup_field(_custom, 100, CUSTOMER_FIELD_NAMES.interest__arts,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.interest__arts], _bool)
    _setup_field(_custom, 200, CUSTOMER_FIELD_NAMES.interest__blogging,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.interest__blogging], _bool)
    _setup_field(_custom, 300, CUSTOMER_FIELD_NAMES.interest__books,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.interest__books], _bool)
    _setup_field(_custom, 400, CUSTOMER_FIELD_NAMES.interest__business,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.interest__business], _bool)
    _setup_field(_custom, 500, CUSTOMER_FIELD_NAMES.interest__health,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.interest__health], _bool)
    _setup_field(_custom, 600, CUSTOMER_FIELD_NAMES.interest__news,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.interest__news], _bool)
    _setup_field(_custom, 100, CUSTOMER_FIELD_NAMES.purchase__automotive,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__automotive], _bool)
    _setup_field(_custom, 200, CUSTOMER_FIELD_NAMES.purchase__baby,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__baby], _bool)
    _setup_field(_custom, 300, CUSTOMER_FIELD_NAMES.purchase__beauty,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__beauty], _bool)
    _setup_field(_custom, 400, CUSTOMER_FIELD_NAMES.purchase__charitable,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__charitable], _bool)
    _setup_field(_custom, 500, CUSTOMER_FIELD_NAMES.purchase__cooking,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__cooking], _bool)
    _setup_field(_custom, 600, CUSTOMER_FIELD_NAMES.purchase__discount,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__discount], _bool)
    _setup_field(_custom, 700, CUSTOMER_FIELD_NAMES.purchase__high_end_brands,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__high_end_brands], _bool)
    _setup_field(_custom, 800, CUSTOMER_FIELD_NAMES.purchase__home_garden,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__home_garden], _bool)
    _setup_field(_custom, 900, CUSTOMER_FIELD_NAMES.purchase__home_improvement,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__home_improvement], _bool)
    _setup_field(_custom, 1000, CUSTOMER_FIELD_NAMES.purchase__luxury,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__luxury], _bool)
    _setup_field(_custom, 1100, CUSTOMER_FIELD_NAMES.purchase__magazine,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__magazine], _bool)
    _setup_field(_custom, 1200, CUSTOMER_FIELD_NAMES.purchase__outdoor,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__outdoor], _bool)
    _setup_field(_custom, 1300, CUSTOMER_FIELD_NAMES.purchase__pets,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__pets], _bool)
    _setup_field(_custom, 1400, CUSTOMER_FIELD_NAMES.purchase__power_shopper,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__power_shopper], _bool)
    _setup_field(_custom, 1500, CUSTOMER_FIELD_NAMES.purchase__sports,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__sports], _bool)
    _setup_field(_custom, 1600, CUSTOMER_FIELD_NAMES.purchase__technology,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__technology], _bool)
    _setup_field(_custom, 1700, CUSTOMER_FIELD_NAMES.purchase__travel,
                 CUSTOMER_FIELD_NAMES_DICT[CUSTOMER_FIELD_NAMES.purchase__travel], _bool)


def _setup_sample_data_promotions(client):
    section("Creating Sample Promotions")

    dashboard, created = Dashboard.objects.get_or_create(client=client)
    now = datetime.datetime.now()
    p, created = Promotion.objects.get_or_create(
        client=client,
        name="Black Friday Campaign",
        status=Promotion.PROMOTION_STATUS.active,
        description="Come to MDO for Exciting Black Friday deals. Get the best deals on Gap, Banana Republic, Old Navy and many more. We have the best deals in New England.",
        short_code="Black Friday Deals"
    )
    if created:
        p.mediums.add(PromotionMedium.objects.get_or_create(client=client, platform=PromotionMedium.PROMOTION_PLATFORMS.email)[0])

    p, created = Promotion.objects.get_or_create(
        client=client,
        name="Free coupon book valued at $750",
        status=Promotion.PROMOTION_STATUS.active,
        description="HOLIDAY SHOPPING IS MAGICAL IN MANCHESTER, VERMONT. Signup to our newsletter at keensmb.com/mdo.signup and receive A COUPON BOOK VALUED AT $750. Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
        short_code="Coupon Book Promo"
    )
    if created:
        p.mediums.add(PromotionMedium.objects.get_or_create(client=client, platform=PromotionMedium.PROMOTION_PLATFORMS.email)[0])

    p, created = Promotion.objects.get_or_create(
        client=client,
        name="Draft Promotion 1",
        status=Promotion.PROMOTION_STATUS.draft,
        description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
        short_code="Draft Promotion 1",
        valid_from=now,
        valid_to=now+relativedelta(years=+1)
    )
    if created:
        p.mediums.add(PromotionMedium.objects.get_or_create(client=client, platform=PromotionMedium.PROMOTION_PLATFORMS.email)[0])

    p, created = Promotion.objects.get_or_create(
        client=client,
        name="Draft Promotion 2",
        status=Promotion.PROMOTION_STATUS.draft,
        description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
        short_code="Draft Promotion 2",
        valid_from=now+relativedelta(years=-1),
        valid_to=now+relativedelta(years=+1)
    )
    if created:
        p.mediums.add(PromotionMedium.objects.get_or_create(client=client, platform=PromotionMedium.PROMOTION_PLATFORMS.email)[0])

    p, created = Promotion.objects.get_or_create(
        client=client,
        name="In Approval Promotion 1",
        status=Promotion.PROMOTION_STATUS.inapproval,
        description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
        short_code="Draft Promotion 1",
        valid_from=now,
        valid_to=now+relativedelta(years=+1)
    )
    if created:
        p.mediums.add(PromotionMedium.objects.get_or_create(client=client, platform=PromotionMedium.PROMOTION_PLATFORMS.email)[0])

    p, created = Promotion.objects.get_or_create(
        client=client,
        name="In Approval Promotion 2",
        status=Promotion.PROMOTION_STATUS.inapproval,
        description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
        short_code="Draft Promotion 2",
        valid_from=now+relativedelta(years=-1),
        valid_to=now+relativedelta(years=+1)
    )
    if created:
        p.mediums.add(PromotionMedium.objects.get_or_create(client=client, platform=PromotionMedium.PROMOTION_PLATFORMS.email)[0])

    p, created = Promotion.objects.get_or_create(
        client=client,
        name="Scheduled Promotion 1",
        status=Promotion.PROMOTION_STATUS.scheduled,
        description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
        short_code="Draft Promotion 1",
        valid_from=now+relativedelta(months=+1),
        valid_to=now+relativedelta(years=+1)
    )
    if created:
        p.mediums.add(PromotionMedium.objects.get_or_create(client=client, platform=PromotionMedium.PROMOTION_PLATFORMS.email)[0])

    p, created = Promotion.objects.get_or_create(
        client=client,
        name="Scheduled Promotion 2",
        status=Promotion.PROMOTION_STATUS.scheduled,
        description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
        short_code="Draft Promotion 2",
        valid_from=now+relativedelta(years=+1),
        valid_to=now+relativedelta(years=+2)
    )
    if created:
        p.mediums.add(PromotionMedium.objects.get_or_create(client=client, platform=PromotionMedium.PROMOTION_PLATFORMS.email)[0])

    p, created = Promotion.objects.get_or_create(
        client=client,
        name="Expired Promotion 1",
        status=Promotion.PROMOTION_STATUS.expired,
        description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
        short_code="Draft Promotion 1",
        valid_from=now+relativedelta(years=-1),
        valid_to=now+relativedelta(months=-1)
    )
    if created:
        p.mediums.add(PromotionMedium.objects.get_or_create(client=client, platform=PromotionMedium.PROMOTION_PLATFORMS.email)[0])

    p, created = Promotion.objects.get_or_create(
        client=client,
        name="Expired Promotion 2",
        status=Promotion.PROMOTION_STATUS.expired,
        description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
        short_code="Draft Promotion 2",
        valid_from=now+relativedelta(years=-2),
        valid_to=now+relativedelta(years=-1)
    )
    if created:
        p.mediums.add(PromotionMedium.objects.get_or_create(client=client, platform=PromotionMedium.PROMOTION_PLATFORMS.email)[0])

    dashboard.refresh()


def _setup_sample_data():
    section("Creating Customer Database")

    #setup default client
    client, created = Client.objects.get_or_create(slug="default_client", name="default_client")
    customer_source, created = CustomerSource.objects.get_or_create(client=client, slug="import")

    address, created = Address.objects.get_or_create(
        street='1 Easy Str', city='Simpleville', state_province='IL',
        country='US', postal_code='12345')
    location = Location.objects.get_or_create(name='default_location',
                                              client=client, address=address)

    customers_appended = open("./data/setup/customers_appended.csv", "r")

    # first line with field names
    csv_schema_fields = [f.strip() for f in next(customers_appended).split(",")]

    # customer fields from db
    all_customer_fields = dict([(c.title,c) for c in CustomerField.objects.all()])

    # We need those fields to import so we add them to dict but do not save
    # into db
    all_customer_fields['First Name'] = CustomerField(name='first_name')
    all_customer_fields['Last Name'] = CustomerField(name='last_name')

    all_field_titles = all_customer_fields.keys()
    clients_customer_fields = [all_customer_fields[process.extractOne(x, all_field_titles)[0]]
                               for x in csv_schema_fields]

    client.customer_fields = [f for f in all_customer_fields.values() if f.name not in ('first_name', 'last_name')]
    client.save()

    with transaction.atomic():
        client.customers.all().delete()

        for customer_text in customers_appended:
            customer_text = customer_text.replace("\r","").decode('latin-1').encode("utf-8")
            customer_text = customer_text.replace("\n","")
            customer_values = customer_text.split(",")
            if len(customer_values) == len(clients_customer_fields):
                c = Customer(client=client, source=customer_source)
                c.set_val(CUSTOMER_FIELD_NAMES.profile_image, '/static/images/icons/dude.svg')
                for i in range(0, len(customer_values)):
                    c.data[clients_customer_fields[i].name] = str(customer_values[i])
                if c.data[CUSTOMER_FIELD_NAMES.age] or \
                    c.data[CUSTOMER_FIELD_NAMES.gender] or \
                    c.data[CUSTOMER_FIELD_NAMES.has_children] or \
                    c.data[CUSTOMER_FIELD_NAMES.income] or \
                    c.data[CUSTOMER_FIELD_NAMES.length_of_residence] or \
                    c.data[CUSTOMER_FIELD_NAMES.marital_status]:
                    c.enrichment_status = Customer.ENRICHMENT_STATUS.en
                    c.enrichment_date = datetime.datetime.now()
                # make full name using first and last name
                c.data['full_name'] = ' '.join((c.data[field] for field in
                                            ('first_name', 'last_name')
                                            if field in c.data))
                # then remove first and last names
                for redundant_field in 'first_name', 'last_name':
                    c.data.pop(redundant_field, None)

                c.save()

    user, created = User.objects.get_or_create(username='default@default.com', email='default@default.com')
    user.set_password('default')
    user.save()

    ClientUser.objects.get_or_create(user=user, client=client)

    PageCustomerField.objects.get_or_create(page='db', client=client)

    form, created = SignupForm.objects.get_or_create(client=client, slug='signup')
    form.fields = CustomerField.objects.filter(
        client=client,
        name__in='full_name email address__zipcode dob phone gender'.split(),
    )
    form.data = {
        'title': 'Default Client Sign-Up',
        'intro': 'Sign-Up now and get free diiner for two',
        'background_img': 'http://keensmb.com/static/special/clients/mdo/images/img11.png',
    }
    form.save()
    _setup_sample_data_promotions(client)

def _setup_web():
    #HelpText
    HelpText.objects.get_or_create(group='promotion', name='name',
        text='This is the name that will appear on your Promotion Manager and on the Promotion itself.')

def setup_all():
    #_setup_core()
    #_setup_sample_data()
    _setup_web()
