from . import *


DEBUG = TEMPLATE_DEBUG = DEV = True

INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

MAILCHIMP_API_KEY = '4f1edbb00b9d47197be82bb7007c1b6d-us7'
