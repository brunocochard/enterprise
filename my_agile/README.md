#install new libraries

  pip install --download=//$libraries --trusted-host pypi.python.org --proxy=pxwsg:80 -r requirements.txt
  pip install --no-index --find-links=libraries -r requirements.txt

#run on dev environemtn
  export AGILEXCHANGE_SETTINGS=/home/almrsadm/agilexchange/settings.cfg
  for PROD: python app.py
  For DEV/UAT: python app.py DEV


# start mod_wsgi server
  sudo tail -f /etc/mod_wsgi-express-80/error_log
  gunicorn --worker-class eventlet -w 1 module:app

# create new mod_wsgi server
  sudo mod_wsgi-express setup-server agilexchange/app.wsgi --port=80 --user almrsadm --group almrsg --server-root=/etc/mod_wsgi-express-80
  sudo /etc/mod_wsgi-express-80/apachectl start
