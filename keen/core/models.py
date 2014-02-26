import os
import operator
import random
import urllib
import datetime

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now
from django_hstore import hstore

from jsonfield import JSONField
from model_utils import Choices

from keen import util, print_stack_trace, InvalidOperationException

from tracking.models import Visitor


class Timestamps(models.Model):

    created = models.DateTimeField(editable=False, blank=True)
    modified = models.DateTimeField(editable=False, blank=True)

    def save(self, *args, **kw):
        if not self.id:
            if not self.created:
                self.created = now()
        self.modified = now()
        super(Timestamps, self).save(*args, **kw)

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

    #look at https://developers.google.com/maps/documentation/staticmaps/
    #to create these urls for now
    map_image_url = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.refresh_map_image_url()
        super(Address, self).save(*args, **kwargs)

    def refresh_map_image_url(self):
        address = str(self)
        old_address = None
        try:
            if self.id:
                old_address = str(Address.objects.get(id=self.id))
        except:
            print_stack_trace()
        if address and address != old_address:
            escaped_address = urllib.quote(address, safe='~()*!.\'')
            self.map_image_url = "http://maps.googleapis.com/maps/api/staticmap?center=%s&zoom=14&size=400x267&maptype=roadmap&sensor=false" % escaped_address
            try:
                from geopy import geocoders
                g = geocoders.GoogleV3()
                place, (lat, lng) = g.geocode(address)
                if lat and lng:
                    self.map_image_url += "&markers=%s,%s" % (str(lat),str(lng))
            except:
                print_stack_trace()

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
    alt_title = models.CharField(max_length=255, unique=True, null=True, blank=True)
    group = models.ForeignKey(CustomerFieldGroup, related_name='fields')
    group_ranking = models.IntegerField(default=99999999)
    type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    width = models.IntegerField(null=True, blank=True)
    choices = JSONField(null=True, blank=True)
    hidden = models.BooleanField(default=False)

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
    web_url = models.TextField(blank=True, null=True)
    ref_id_type = models.CharField(max_length=255, null=True, blank=True)
    ref_id = models.CharField(max_length=255, null=True, blank=True)

    # Use the signup form code field if you want to attach any code to every signup form
    # for example if you want to attach remarketing tags or analytics tags
    signup_form_code = models.TextField(blank=True, null=True, default="")

    def customer_page(self, offset=0, filter=None, page_size=100):
        q = self.customers.all()
        if not filter is None:
            q = q.filter(**filter)
        q = q.extra(select={'email': "upper(core_customer.data -> 'email')"})
        q = q.order_by('email')
        return q[offset:offset + page_size]

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name

    def new_customers(self):
        return self.customers.filter(created__gte=util.get_first_day_of_month_as_dt())

    def get_top_customers(self, count=5):
        return self.customers.extra(
            select={'full_name': "upper(core_customer.data -> 'full_name')"}
        ).order_by('-full_name')[:count] #TODO: Change

    #Promotions
    def promotions_this_month(self):
        return self.promotions.filter(
            Q(valid_from__gte=util.get_first_day_of_month_as_dt()) | Q(valid_from__isnull=True),
            Q(valid_to__lte=util.get_last_day_of_month_as_dt()) | Q(valid_to__isnull=True),
        )

    def get_top_promotions(self, order_by='-valid_to', count=4):
        #TODO: Change
        return self.promotions.filter(status__in=[Promotion.PROMOTION_STATUS.active, Promotion.PROMOTION_STATUS.expired]).extra(
            select={'redemptions_percentage': "upper(core_promotion.analytics -> 'redemptions_percentage')"}
        ).order_by(order_by).order_by('-redemptions_percentage')[:count]

    def get_active_promotions(self, order_by='-valid_to', count=4):
        #TODO: Change
        return self.promotions.filter(status=Promotion.PROMOTION_STATUS.active).order_by(order_by)[:count]

    def get_active_promotions_count(self):
        #TODO: Change
        return self.promotions.filter(status=Promotion.PROMOTION_STATUS.active).count()


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

    def get_promotions_for_status(self, status, client):
        alias_mapping = dict([(key[0],key[0]) for key in Promotion.PROMOTION_STATUS])
        alias_mapping['awaiting'] = 'inapproval'
        alias_mapping['upcoming'] = 'scheduled'
        _status = alias_mapping[status]
        return self.filter(status=_status).filter(client=client)

import uuid
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    #print os.path.join('../keen/web/static/uploads/images', filename)
    #return os.path.join('../keen/web/static/uploads/images', filename)
    return os.path.join('uploads/images', filename)

class Promotion(Timestamps):
    PROMOTION_STATUS = Choices(
        ('draft', 'Draft'),
        ('inapproval', 'In Approval'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    )

    SEND_LATER_CHOICES = Choices(
        (True, 'later'),
        (False, 'now')
    )

    client = models.ForeignKey(Client, related_name='promotions')
    name = models.CharField(max_length=255, verbose_name='Name of the promotion', help_text='This is the name that will appear on your Promotion Manager and on the Promotion itself.')
    status = models.CharField(max_length=15, choices=PROMOTION_STATUS, verbose_name='status', help_text='status', default=PROMOTION_STATUS.draft)
    description = models.TextField(null=True, blank=True, verbose_name='Description', help_text='Tell us more about this promotion. What are the details? Why is it special? What\'s the occasion?<br><br><i>e.g. "Up to 40% off our beloved socks, just in time for the holiday season!"</i>')
    short_code = models.CharField(max_length=255, verbose_name='', help_text='This is a really brief description, to be read at a glance. <br><br><i>e.g. $5 OFF, BUY 1 GET 1 FREE, SALE</i>')
    valid_from = models.DateField(null=True, blank=True, verbose_name='', help_text='')
    valid_to = models.DateField(null=True, blank=True, verbose_name='', help_text='Provide the start date and expiry date for this promotion. Otherwise, it will by default continue indefinitely.')
    restrictions = models.TextField(null=True, blank=True, verbose_name='', help_text='<i>e.g. Promotion codes may not be combined with other offers; Limit one promotion code per customer; void where prohibited; Each promotion code can be used only once, unless otherwise specified etc.</i>')
    additional_information = models.TextField(null=True, blank=True, verbose_name='', help_text='Use this space to provide any additional information about your business or this promotion, or even upcoming promotions.')
    redemption_instructions = models.TextField(verbose_name='', help_text='When a customer redeems your promotion, they receive a unique code. Provide instructions that explain how you want them to use that code.')
    mediums = models.ManyToManyField(PromotionMedium, null=True, blank=True, verbose_name='', help_text='Select which kinds of promotions you would like to send: Email, Mobile, Facebook, and/or Twitter. You can select more than one promotion platform. All promotions will provide identical information.')
    cta_text = models.CharField(max_length=50, default="Redeem", verbose_name='', help_text='You can customize the text to appear on the redemption button. By default the call to action will be "REDEEM." <br><br><i>e.g. "Get This Deal!"; "Reveal Code"</i>')
    banner_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='', help_text='If you have already uploaded a banner logo, we completed this step for you. If you have not uploaded a logo, you can upload one here.')
    image_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='', help_text='Every promotion has to have an image. The image must be 300 px wide and have a height of 290 px. You may also use photos that you have uploaded for previous promotions.')
    send_later = models.BooleanField(default=False, choices=SEND_LATER_CHOICES)
    send_schedule = models.DateTimeField(null=True, blank=True, verbose_name='', help_text='You can send this promotion immediately after completing this form or you can schedule a specific start date and time. and we will automatically activate the promotion for you then.')
    target_audience = JSONField(null=True, blank=True)
    analytics = hstore.DictionaryField(null=True, blank=True, verbose_name='', help_text='')

    objects = PromotionsManager()

    def approve(self):
        if self.status in [Promotion.PROMOTION_STATUS.draft, Promotion.PROMOTION_STATUS.inapproval]:
            if self.valid_to and self.valid_to < datetime.date.today():
                raise InvalidOperationException("You need to adjust the validity of the promotion before it is approved. The promotion's validity period is in the past.")
            if not self.banner_url:
                raise InvalidOperationException("Banner image is missing.")
            if not self.image_url:
                raise InvalidOperationException("Promotion image is missing.")
            #if not self.valid_from or self.valid_from > datetime.datetime.today():
            #    self.status = Promotion.PROMOTION_STATUS.scheduled
            #else:
            #    self.status = Promotion.PROMOTION_STATUS.active
            self.status = Promotion.PROMOTION_STATUS.scheduled
            self.save()
        else:
            raise InvalidOperationException("You can only approve promotions that haven't been scheduled or activated yet.")
    approve.alters_data = True

    def save(self, *args, **kwargs):
        if not self.analytics:
            self.analytics = {
                "total_sent"    : str(random.randrange(500, 1000)),
                "redemptions"   : str(random.randrange(100, 500)),
            }
            self.analytics["redemptions_percentage"] = str(int((float(self.analytics["redemptions"])/float(self.analytics["total_sent"]))*100))
        if not self.send_later:
            self.send_schedule = None
        if self.valid_to and not self.valid_from:
            self.valid_from = datetime.date.today()
        super(Promotion, self).save(*args, **kwargs)
