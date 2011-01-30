DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'sample_project',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use atrailing slash 
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a trailing slash.
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'lg55-s4-!3kfcdpcsv%kv6i)hh*iu16ms#k)f9i#a*29@@3+9k'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'sample_project.urls'

TEMPLATE_DIRS = ()

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'sample_project.sample_app',
)

AUTH_PROFILE_MODULE = 'sample_app.Profile'
BASE_URL = 'http://www.sample_project.com/'
LOGIN_URL = '/signup/'

# CLIPCLOUD SETTINGS #########################
# Notes:
#   > The oauth keys below are obtained by applying for a Consumer 
#     key @ 'CLIPCLOUD_BASE_URL/api/oauth/consumer-application/'.
#   > After the you apply for (and are granted) a Consumer key, you use those
#     to obtain a RequestToken on behalf of one of your users.
#   > Once a RequestToken is obtain (1 per user), use that token + user
#     verification to obtain an AccessToken (1 per user) that allows you
#     to post and search data on behalf of the user.
##############################################
OAUTH_CONSUMER_KEY = 'jYWmkhZZcrkLmrhaQV'
OAUTH_CONSUMER_SECRET = 'NtM6BDbFRnb6bnTVcyjZcVrwx2yfkMCB'
OAUTH_LOCAL_CALLBACK_URL = "%s%s" % (BASE_URL, 'link-account/')
CLIPCLOUD_BASE_URL = 'http://localhost:8000/'
CLIPCLOUD_REQUEST_TOKEN_URL = "%s%s?oauth_consumer_key=%s&oauth_signature=%s" % (CLIPCLOUD_BASE_URL, 'api/oauth/request_token/', OAUTH_CONSUMER_KEY, OAUTH_CONSUMER_SECRET)
CLIPCLOUD_AUTHORIZATION_URL = "%s%s" % (CLIPCLOUD_BASE_URL, 'api/oauth/authorize/')

try:
    from sample_project.settings_local import *
except Exception, e:
    print 'exp', e
    pass