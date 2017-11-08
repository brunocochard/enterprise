# -*- coding: utf-8 -*-

import os

# *****************************
# Environment specific settings
# *****************************

# DO NOT use "DEBUG = True" in production environments
DEBUG = True

# DO NOT use Unsecure Secrets in production environments
# Generate a safe one with:
#     python -c "import os; print repr(os.urandom(24));"
SECRET_KEY = 'This is an UNSECURE Secret. CHANGE THIS for production environments.'

# Flask-Mail settings
# For smtp.gmail.com to work, you MUST set "Allow less secure apps" to ON in Google Accounts.
# Change it in https://myaccount.google.com/security#connectedapps (near the bottom).
MAIL_SERVER = '127.0.0.1'
# MAIL_PORT = 25
# MAIL_SERVER = 'smtp.mysmtp.com.tw'
MAIL_PORT = 587
MAIL_USE_SSL = False
# MAIL_USE_TLS = True
MAIL_USE_TLS = False
MAIL_USERNAME = 'yourname@mymail.com'
MAIL_PASSWORD = 'password'
MAIL_DEFAULT_SENDER = '"Your Name" <yourname@mymail.com>'

ADMINS = [
    '"Admin MyIT" <my-it@mymail.com>',
    '"Admin DEV" <my_it.dev@mymail.com>',
    ]
