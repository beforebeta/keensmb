import datetime

from . import *


DEBUG = TEMPLATE_DEBUG = DEV = False

ALLOWED_HOSTS = ['*']

CELERY_ALWAYS_EAGER = False

MAILCHIMP_API_KEY = '4f1edbb00b9d47197be82bb7007c1b6d-us7'

STATICFILES_STORAGE = 'keen.web.storage.CachedS3BotoStorage'
COMPRESS_STORAGE = STATICFILES_STORAGE

from boto.s3.connection import ProtocolIndependentOrdinaryCallingFormat

AWS_S3_CALLING_FORMAT = ProtocolIndependentOrdinaryCallingFormat()
AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = True
AWS_REDUCED_REDUNDANCY = True
AWS_STORAGE_BUCKET_NAME = 'keensmb'
AWS_HEADERS = {
    'Cache-Control': 'max-age=31556926',
    'Expires': (datetime.datetime.today() + datetime.timedelta(days=365)).strftime('%a, %d %b %Y %H:%M:%S GMT')
}
AWS_ACCESS_KEY_ID = 'AKIAI22SZIJA336XJZIQ'
AWS_SECRET_ACCESS_KEY = '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'

STATIC_URL = '//s3.amazonaws.com/{0}/{1}/'.format(AWS_STORAGE_BUCKET_NAME, AWS_LOCATION)
COMPRESS_URL = STATIC_URL

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.CSSMinFilter',
]

LOGGING = {
    'version': 1,
    'loggers': {
        '': {
            'level': 'WARN',
            'handlers': ['console'],
        },
        'django': {
            'level': 'WARN',
            'handlers': ['console'],
            'propagate': False,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
}
