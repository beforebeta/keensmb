import os
import operator
import random

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django_hstore import hstore

from model_utils import Choices

from tracking.models import Visitor


class Timestamps(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def image_upload_path(image, filename):
    return os.path.join(
        settings.MEDIA_ROOT, image.client.slug, 'images', filename)


class Image(Timestamps):

    IMAGE_TARGETS = Choices(
        ('banner', 'Top Banner'),
        ('background', 'Background Image'),
    )

    client = models.ForeignKey('Client', related_name='images')
    file = models.ImageField(upload_to=image_upload_path, max_length=1024)
    content_type = models.CharField(max_length=255)
    target = models.CharField(max_length=32, choices=IMAGE_TARGETS)

    @property
    def url(self):
        return self.file.url()


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
    main_location = models.ForeignKey('Location', null=True, blank=True,
                                      related_name='+')
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

    def get_dashboard(self):
        return self.dashboard_set.all()[0]

    def get_top_customers(self):
        return self.customers.extra(select={'full_name': "upper(core_customer.data -> 'full_name')"}).order_by('-full_name') #TODO: Change

    #Promotions
    def get_top_promotions(self, order_by='-valid_to'):
        #TODO: Change
        return self.promotions.extra(select={'redemptions_percentage': "upper(core_promotion.analytics -> 'redemptions_percentage')"}).order_by(order_by).order_by('-redemptions_percentage')

    def get_active_promotions(self, order_by='-valid_to'):
        #TODO: Change
        return self.promotions.filter(status=Promotion.PROMOTION_STATUS.active).order_by(order_by)

    def get_active_promotions_count(self):
        #TODO: Change
        return self.get_active_promotions().count()


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
    ref_source = models.CharField(max_length=50, null=True, blank=True)

    #name = models.CharField(Client)
    #is_bulk = models.BooleanField(default=False) #is this a source that creats customers in bulk - like mailchimp or setup

    def __unicode__(self):
        return self.slug

    class Meta:
        unique_together = ('client', 'slug')


CUSTOMER_FIELD_NAMES = Choices(
    ('profile_image', 'Profile Image'),
    ('social__facebook', 'Facebook'),
    ('social__twitter', 'Twitter'),
    ('social__googleplus', 'Google Plus'),
    ('full_name', 'Full Name'),
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
    ('phone', 'Phone'),
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
    ('purchase__charitable',
     'Indicates liklihood of Being a Charitable Donor'),
    ('purchase__cooking', 'Purchases cooking magazines; interest in cooking'),
    ('purchase__discount', 'Purchase behavior: Interest in discounts'),
    ('purchase__high_end_brands',
     'Has bought a premium CPG brand in the past 18 months '),
    ('purchase__home_garden', 'Purchases Home & Garden Products'),
    ('purchase__home_improvement', 'Purchases Home Improvement Products'),
    ('purchase__luxury', 'Purchases Luxury Items'),
    ('purchase__magazine', 'Purchases Magazine Subscriptions'),
    ('purchase__outdoor', 'Purchases Outdoor and Adventure Products'),
    ('purchase__pets', 'Purchases Pet Related Products'),
    ('purchase__power_shopper',
     'Purchases Items from Multiple Retail Channels'),
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
    visitor = models.ForeignKey(Visitor, null=True)
    data = hstore.DictionaryField()
    locations = models.ManyToManyField(Location, related_name='customers',
                                       null=True, blank=True)
    enrichment_status = models.CharField(max_length=3,
                                         choices=ENRICHMENT_STATUS,
                                         default="ne")
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

    def name(self):
        _name=self.get_name()
        if _name.strip():
            return _name
        else:
            return self.get_email()

    def get_name(self):
        return  self.data.get(CUSTOMER_FIELD_NAMES.full_name, '')
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
        field_ids = [cf.id for cf in
                     self.client.customer_fields.all().only("id")]
        for field in self.data.keys():
            cf = CustomerField.objects.get(name=field)
            fields.append({"name": field,
                           "value": self.data[field],
                           "group": cf.group.name,
                           "group_ranking": cf.group_ranking,
                           "is_client_relevant": cf.id in field_ids
                           })
        return sorted(fields,
                      key=operator.itemgetter("group", "group_ranking"))

    def has_custom_fields(self):
        return self.client.customer_fields.filter(
            group=CustomerFieldGroup.objects.get(
                name=CustomerFieldGroup.FIELD_GROUPS.custom)).count() > 0

    def __unicode__(self):
        return self.get_name()


########################################################################################################################
# Promotions
########################################################################################################################

class PromotionMedium(Timestamps):
    PROMOTION_PLATFORMS = Choices(
        ('email', 'E-mail'),
        ('fb', 'Facebook'),
        ('tw', 'Twitter'),
        ('pin', 'Pinterest'),
    )

    client = models.ForeignKey(Client)
    platform = models.CharField(max_length=10, choices=PROMOTION_PLATFORMS)
    account_info = hstore.DictionaryField() #account into per medium

class PromotionsManager(models.Manager):

    def get_promotions_for_status(self, status):
        alias_mapping = dict([(key[0],key[0]) for key in Promotion.PROMOTION_STATUS])
        alias_mapping['awaiting'] = 'inapproval'
        alias_mapping['upcoming'] = 'scheduled'
        _status = alias_mapping[status]
        return self.filter(status=_status)

class Promotion(Timestamps):
    PROMOTION_STATUS = Choices(
        ('draft', 'Draft'),
        ('inapproval', 'In Approval'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    )

    client = models.ForeignKey(Client, related_name='promotions')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Name of the promotion', help_text='This is the name that will appear on your Promotion Manager and on the Promotion itself.')
    status = models.CharField(max_length=15, choices=PROMOTION_STATUS, verbose_name='status', help_text='status')
    description = models.TextField(null=True, blank=True, verbose_name='Description', help_text='Tell us more about this promotion. What are the details? Why is it special? What\'s the occasion?<br><i>e.g. "Up to 40% off our beloved socks, just in time for the holiday season!"</i>')
    short_code = models.CharField(max_length=255, null=True, blank=True, verbose_name='', help_text='')
    valid_from = models.DateTimeField(null=True, blank=True, verbose_name='', help_text='')
    valid_to = models.DateTimeField(null=True, blank=True, verbose_name='', help_text='')
    restrictions = models.TextField(null=True, blank=True, verbose_name='', help_text='')
    additional_information = models.TextField(null=True, blank=True, verbose_name='', help_text='')
    redemption_instructions = models.TextField(null=True, blank=True, verbose_name='', help_text='')
    mediums = models.ManyToManyField(PromotionMedium, null=True, blank=True, verbose_name='', help_text='')
    cta_text = models.CharField(max_length=50, null=True, blank=True, verbose_name='', help_text='')
    banner_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='', help_text='')
    image_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='', help_text='')
    send_schedule = models.DateTimeField(null=True, blank=True, verbose_name='', help_text='')
    target_customers = models.ManyToManyField(Customer, null=True, blank=True, verbose_name='', help_text='')

    analytics = hstore.DictionaryField(null=True, blank=True, verbose_name='', help_text='')

    objects = PromotionsManager()

    def save(self, *args, **kwargs):
        if not self.analytics:
            self.analytics = {
                "total_sent"    : str(random.randrange(500, 1000)),
                "redemptions"   : str(random.randrange(100, 500)),
            }
            self.analytics["redemptions_percentage"] = str(int((float(self.analytics["redemptions"])/float(self.analytics["total_sent"]))*100))
        super(Promotion, self).save(*args, **kwargs)
