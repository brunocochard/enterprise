# -*- coding: utf-8 -*-

# Settings common to all environments (development|staging|production)
# Place environment specific settings in env_settings.py
# An example file (env_settings_example.py) can be used as a starting point

import os

# Application settings
APP_NAME = "MyIT Self-Service"
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " system error"

# Flask settings
CSRF_ENABLED = True

# Internationalization settings
BABEL_DEFAULT_LOCALE = 'zh_TW'
BABEL_DEFAULT_TIMEZONE = "Asia/Taipei"
SUPPORTED_LANGUAGES = {'en': 'English', 'zh_Hant_TW': 'Traditional Chinese', 'zh_Hans_CN': 'Simplified Chinese', 'zh_TW': 'Traditional Chinese', 'zh_CN': 'Simplified Chinese'}
