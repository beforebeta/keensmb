from . import *


DEBUG = TEMPLATE_DEBUG = DEV = False

ALLOWED_HOSTS = ['*']

CELERY_ALWAYS_EAGER = False

MAILCHIMP_API_KEY = '4f1edbb00b9d47197be82bb7007c1b6d-us7'

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
