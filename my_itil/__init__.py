# -*- coding: utf-8 -*-

# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from datetime import datetime
import os

from flask import Flask, request, g, url_for as flask_url_for
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel

# Instantiate Flask extensions
csrf_protect = CSRFProtect()
mail = Mail()

def create_app(extra_config_settings={}):
    """Create a Flask applicaction.
    """
    my_it = Flask(__name__) # Instantiate Flask

    # Load my_it Config settings
    my_it.config.from_object('my_it.settings') # common settings
    my_it.config.from_object('my_it.local_settings') # local environment settings
    my_it.config.update(extra_config_settings) # extra e.g. env var

    # Setup Flask-Extensions
    babel = Babel(my_it) # load internationalization module
    mail.init_app(my_it) # Setup Mail service
    csrf_protect.init_app(my_it) # Prevent CSRF attacks

    # Register blueprints
    from my_it.views.misc_views import my_it_blueprint
    my_it.register_blueprint(my_it_blueprint)

    from my_it.views.service_request import service_blueprint
    my_it.register_blueprint(service_blueprint)
    
    # Define bootstrap_is_hidden_field for flask-bootstrap's bootstrap_wtf.html
    from wtforms.fields import HiddenField
    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)
    my_it.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter

    # Setup an error-logger to send emails to my_it.config.ADMINS
    init_email_error_handler(my_it)

    # Use the browser's language preferences to select an available translation
    @babel.localeselector
    def get_locale():
        translations = [str(translation) for translation in babel.list_translations()]
        return 'zh_TW' #request.accept_languages.best_match(translations)
    return my_it

def init_email_error_handler(app):
    """
    Initialize a logger to send emails on error-level messages.
    Unhandled exceptions will now send an email message to app.config.ADMINS.
    """
    if app.debug: return  # Do not send error emails while developing

    # Retrieve email settings from app.config
    host = app.config['MAIL_SERVER']
    port = app.config['MAIL_PORT']
    from_addr = app.config['MAIL_DEFAULT_SENDER']
    username = app.config['MAIL_USERNAME']
    password = app.config['MAIL_PASSWORD']
    secure = () if app.config.get('MAIL_USE_TLS') else None

    # Retrieve app settings from app.config
    to_addr_list = app.config['ADMINS']
    subject = app.config.get('APP_SYSTEM_ERROR_SUBJECT_LINE', 'System Error')

    # Setup an SMTP mail handler for error-level messages
    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler(
        mailhost=(host, port),  # Mail host and port
        fromaddr=from_addr,  # From address
        toaddrs=to_addr_list,  # To address
        subject=subject,  # Subject line
        credentials=(username, password),  # Credentials
        secure=secure,
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    # Log errors using: app.logger.error('Some error message')
