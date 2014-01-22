from . import *


DEBUG = TEMPLATE_DEBUG = DEV = True

CELERY_ALWAYS_EAGER = False

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
