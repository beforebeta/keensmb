from django.db import models
from django.contrib.auth.models import User
from django_hstore import hstore
from model_utils import Choices
import operator



class Timestamps(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Image(Timestamps):

    IMAGE_TYPES = Choices(
        ('s', 'Small'),
        ('m', 'Medium'),
        ('b', 'Big'),
    )

    url = models.CharField(max_length=255)
    type = models.CharField(max_length=1, choices=IMAGE_TYPES)
    client = models.ForeignKey('Client')


class Address(Timestamps):

    #subject to change
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=255)
    state_province = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __unicode__(self):
        return u','.join((self.street, self.city, self.state_province,
                          self.country, self.postal_code))


class Location(Timestamps):

    name = models.CharField(max_length=255)
    client = models.ForeignKey('Client', related_name='locations')
    address = models.ForeignKey('Address')

    class Meta:
        unique_together = ('name', 'client')

    def __unicode__(self):
        return self.name


class CustomerFieldGroup(Timestamps):

    FIELD_GROUPS = Choices(
        ('basic', 'Basic Information'),
        ('household', 'Household Information'),
        ('custom', 'Custom Fields'),
    )

    name = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name

class CustomerField(Timestamps):

    FIELD_TYPES = Choices(
        ('string', 'String'),
        ('int', 'Integer'),
        ('date', 'Date'),
        ('url', 'URL'),
        ('email', 'E-mail Address'),
        ('float', 'Float'),
        ('location', 'Location'),
        ('bool', 'Bool')
    )

    name = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=255, unique=True)
    group = models.ForeignKey(CustomerFieldGroup, related_name='fields')
    group_ranking = models.IntegerField(default=99999999)
    type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    width = models.IntegerField(null=True, blank=True)

    def group_name(self):
        try:
            return self.group.name
        except:
            return ""

    def __unicode__(self):
        return self.name


class Client(Timestamps):

    slug = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    main_location = models.ForeignKey('Location', null=True, blank=True, related_name='+')
    customer_fields = models.ManyToManyField(CustomerField)

    def customer_page(self, offset=0, filter=None, page_size=100):
        q = self.customers.all()
        if not filter is None:
            q = q.filter(**filter)
        q = q.extra(select={'email': "upper(core_customer.data -> 'email')"})
        q = q.order_by('email')
        return q[offset:offset + page_size]

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class ClientUser(Timestamps):

    client = models.ForeignKey(Client)
    user = models.OneToOneField(User)
    is_manager = models.BooleanField(default=False)

    class Meta:
        unique_together = ('client', 'user')


class CustomerSource(Timestamps):

    client = models.ForeignKey(Client)
    slug = models.CharField(max_length=50)
    url = models.TextField(blank=True, null=True)
    # this may be a reference to a specific web.models.SignupForm model or a
    # mailchimp list or anything else
    ref_id = models.IntegerField(null=True, blank=True)
    ref_source = models.CharField(max_length=50,null=True, blank=True)

    def __unicode__(self):
        return self.slug

    class Meta:
        unique_together = ('client', 'slug')


CUSTOMER_FIELD_NAMES = Choices(
    ('profile_image', 'Profile Image'),
    ('social__facebook', 'Facebook'),
    ('social__twitter', 'Twitter'),
    ('social__googleplus', 'Google Plus'),
    ('first_name', 'First Name'),
    ('last_name', 'Last Name'),
    ('dob', 'Birthday'),
    ('age', 'Age'),
    ('email', 'Email'),
    ('gender', 'Gender'),
    ('address__line1', 'Address Line 1'),
    ('address__line2', 'Address Line 2'),
    ('address__city', 'City'),
    ('address__zipcode', 'ZipCode'),
    ('address__state', 'State'),
    ('address__country', 'Country'),
    ('phone__mobile', 'Mobile Phone'),
    ('phone__home', 'Home Phone'),
    ('occupation', 'Occupation'),
    ('education', 'Education'),
    ('marital_status', 'Marital Status'),
    ('has_children', 'Presence of Children'),
    ('home_owner_status', 'Home Owner Status'),
    ('income', 'Household Income'),
    ('home_market_value', 'Home Market Value'),
    ('high_net_worth', 'High Net Worth'),
    ('length_of_residence', 'Length of Residence'),
    ('interest__arts', 'Interest in Arts and Crafts'),
    ('interest__blogging', 'Interest in Blogging'),
    ('interest__books', 'Interest in Books'),
    ('interest__business', 'Interest in Business'),
    ('interest__health', 'Interest in Health and Wellness'),
    ('interest__news', 'Interest in News and Current Events'),
    ('purchase__automotive', 'Purchases Automotive Goods'),
    ('purchase__baby', 'Has Bought a Baby Product'),
    ('purchase__beauty', 'Purchases Beauty Products'),
    ('purchase__charitable', 'Indicates liklihood of Being a Charitable Donor'),
    ('purchase__cooking', 'Purchases cooking magazines; interest in cooking'),
    ('purchase__discount', 'Purchase behavior: Interest in discounts'),
    ('purchase__high_end_brands', 'Has bought a premium CPG brand in the past 18 months '),
    ('purchase__home_garden', 'Purchases Home & Garden Products'),
    ('purchase__home_improvement', 'Purchases Home Improvement Products'),
    ('purchase__luxury', 'Purchases Luxury Items'),
    ('purchase__magazine', 'Purchases Magazine Subscriptions'),
    ('purchase__outdoor', 'Purchases Outdoor and Adventure Products'),
    ('purchase__pets', 'Purchases Pet Related Products'),
    ('purchase__power_shopper', 'Purchases Items from Multiple Retail Channels'),
    ('purchase__sports', 'Purchases Sporting Goods / Sports Related Products'),
    ('purchase__technology', 'Purchases Technology Products'),
    ('purchase__travel', 'Purchases Travel Related Goods')
)

CUSTOMER_FIELD_NAMES_DICT = dict(CUSTOMER_FIELD_NAMES)

class Customer(Timestamps):

    ENRICHMENT_STATUS = Choices(
        ('ne', 'Not Enriched'),
        ('in', 'In Enrichment'),
        ('en', 'Enriched'),
    )

    client = models.ForeignKey('Client', related_name='customers')
    source = models.ForeignKey(CustomerSource)
    data = hstore.DictionaryField()
    locations = models.ManyToManyField(Location, related_name='customers', null=True, blank=True)
    enrichment_status = models.CharField(max_length=3, choices=ENRICHMENT_STATUS, default="ne")
    enrichment_date = models.DateTimeField(null=True, blank=True)

    objects = hstore.HStoreManager()

    def save(self, *args, **kwargs):
        for f in CustomerField.objects.all():
            if f.name not in self.data:
                self.data[f.name] = ""
        super(Customer, self).save(*args, **kwargs)

    def set_val(self, field_name, val):
        self.data[field_name] = val

    def get_profile_image(self):
        try:
            return self.data[CUSTOMER_FIELD_NAMES.profile_image]
        except:
            return "/static/images/icons/dude.svg"

    def get_name(self):
        first_name = self._return_field(CUSTOMER_FIELD_NAMES.first_name)
        last_name = self._return_field(CUSTOMER_FIELD_NAMES.last_name)
        if first_name or last_name:
            return "%s %s" % (first_name, last_name)
        else:
            return ""
    get_name.short_description = 'Name'

    def get_email(self):
        return self._return_field(CUSTOMER_FIELD_NAMES.email)
    get_email.short_description = 'Email'

    def get_dob(self):
        return self._return_field(CUSTOMER_FIELD_NAMES.dob)

    def get_formatted_gender(self):
        try:
            g = self._return_field(CUSTOMER_FIELD_NAMES.gender).lower().strip()
            if g == "f" or g == "female":
                return "Female"
            elif g == "m" or g == "male":
                return "Male"
            else:
                return ""
        except:
            return ""

    def get_formatted_facebook_username(self):
        f = self._return_field(CUSTOMER_FIELD_NAMES.social__facebook)
        if f:
            return "facebook.com/%s" % f
        else:
            return ""

    def get_formatted_twitter_username(self):
        f = self._return_field(CUSTOMER_FIELD_NAMES.social__twitter)
        if f:
            return "@%s" % f
        else:
            return ""

    def is_enriched(self):
        return self.enrichment_status == Customer.ENRICHMENT_STATUS.en

    def get_formatted_googleplus_username(self):
        f = self._return_field(CUSTOMER_FIELD_NAMES.social__googleplus)
        if f:
            return "plus.google/%s" % f
        else:
            return ""

    def _return_field(self, field_name):
        try:
            if self.data[field_name]:
                return self.data[field_name]
            else:
                return ""
        except:
            return ""

    def get_field_list(self):
        """ returns customer field data in the following format:
            [
                field 1 - {"name":"", "value":"", "group":"", "group_ranking:""},
                field 2 - {"name":"", "value":"", "group":"", "group_ranking:""}
            ]
            orders by group and group_ranking
        """
        fields = []
        field_ids = [cf.id for cf in self.client.customer_fields.all().only("id")]
        for field in self.data.keys():
            cf = CustomerField.objects.get(name=field)
            fields.append({"name": field,
                           "value": self.data[field],
                           "group": cf.group.name,
                           "group_ranking": cf.group_ranking,
                           "is_client_relevant": cf.id in field_ids
                          })
        return sorted(fields, key=operator.itemgetter("group", "group_ranking"))

    def has_custom_fields(self):
        return self.client.customer_fields.filter(
            group=CustomerFieldGroup.objects.get(name=CustomerFieldGroup.FIELD_GROUPS.custom)).count() > 0

    def __unicode__(self):
        return self.get_name()
