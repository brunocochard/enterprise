# enterprise

    Status: Project under development, only prototype capabilities for the moment
    next tasks: merge my_itil and my_agile, get ready for prod

# Configuring SMTP

Copy the `local_settings_example.py` file to `local_settings.py`.

    cp app/local_settings_example.py app/local_settings.py

Edit the `local_settings.py` file.

Specifically set all the MAIL_... settings to match your SMTP settings

Note that Google's SMTP server requires the configuration of "less secure apps".
See https://support.google.com/accounts/answer/6010255?hl=en

Note that Yahoo's SMTP server requires the configuration of "Allow apps that use less secure sign in".
See https://help.yahoo.com/kb/SLN27791.html

## Running the app

    # Start the Flask development web server
    #export ITSM_SETTINGS=/home/almrsadm/myit/settings.cfg
    python manage.py runserver

Point your web browser to http://localhost:5000/

## Running the automated tests

    # Start the Flask development web server
    py.test tests/

# Start the Flask development web server
 py.test tests/

# start mod_wsgi server
sudo tail -f /etc/mod_wsgi-express-80/error_log
gunicorn --worker-class eventlet -w 1 module:app

# create new mod_wsgi server
sudo mod_wsgi-express setup-server myit/app.wsgi --port=80 --user almrsadm --group almrsg --server-root=/etc/mod_wsgi-express-80
sudo /etc/mod_wsgi-express-80/apachectl start

## Acknowledgements

With thanks to the following Flask extensions:

* [Flask](http://flask.pocoo.org/)
* [Flask-Login](https://flask-login.readthedocs.io/)

<!-- Please consider leaving this line. Thank you -->
[Flask-User-starter-app](https://github.com/lingthio/Flask-User-starter-app) was used as a starting point for an app in this code repository.
