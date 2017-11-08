#Source\venv\Scripts\activate
#cd Source\DevOpsHub
#python app.py

from flask import Flask
from flask_login import LoginManager, current_user

from flask_bootstrap import Bootstrap
from flask_bootstrap.nav import BootstrapRenderer

from flask_nav import Nav, register_renderer
from flask_nav.elements import Navbar, View, Subgroup

from flask_socketio import SocketIO
import eventlet
import eventlet.wsgi
import flask_excel as excel
from flask_session import Session

from argparse import ArgumentParser
from config import *

from logging.config import dictConfig

# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#     }},
#     # 'handlers': {'wsgi': {
#     #     'class': 'logging.StreamHandler',
#     #     'stream': 'ext://flask.logging.wsgi_errors_stream',
#     #     'formatter': 'default'
#     # }},
#     'root': {
#         'level': 'INFO',
#         'handlers': ['wsgi']
#     }
# })

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s - %(message)s {%(pathname)s:%(lineno)d}',
    }}
})

app = Flask(__name__)

arg_parser = ArgumentParser()
arg_parser.add_argument('env', nargs='?')
args = arg_parser.parse_args()

app.config['ENV'] = (args.env or "PRD")
if app.config['ENV'] == 'PRD':
    app.config.from_object('config.ProductionConfig')
elif app.config['ENV'] == 'UAT':
    app.config.from_object('config.AcceptanceConfig')
else:
    app.config.from_object('config.DefaultConfig')
app.config['TFS_URL'] = (
        "http://" + app.config['TFS_SERVER'] + ":" +
        str(app.config['TFS_PORT']) + "/tfs/" +
        app.config['TFS_COLLECTION'] + "/")

import os
if os.name != 'nt':
    app.config.from_envvar('AGILEXCHANGE_SETTINGS')

excel.init_excel(app)
Bootstrap(app)
Session(app)
socketio = SocketIO(app, manage_session=False)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'cub_login'

class CustomRenderer(BootstrapRenderer):
    def visit_Navbar(self, node):
        nav_tag = super(CustomRenderer, self).visit_Navbar(node)
        nav_tag['class'] += 'navbar navbar-default navbar-fixed-top'
        return nav_tag

register_renderer(app, 'custom', CustomRenderer)        

nav = Nav()

@nav.navigation()
def nav_bar():
    nav = Navbar(
        'agileXchange',
        View('Home', 'home'),
        Subgroup(
            'Activities',
            View('Projects', 'projects'),
            View('My Requests', 'my_requests')),
        Subgroup(
            'TFS Reports',
            View('Cost Report', 'cost_report'),
            View('Time Report', 'time_report'),
            View('Time Chart', 'time_graph'))
        )
    
    if current_user.is_authenticated and current_user.run().is_connected():
        if current_user.run().is_admin() or app.config['ENV'] == 'DEV':
            nav.items.append(Subgroup(
                'In Dev',
                View('Admin', 'view_projects')))
        nav.items.append(View('Logout', 'logout'))
    else:
        nav.items.append(View('Login', 'login'))

    return nav

nav.init_app(app)

from user.home import *
from activities.projects import *
from activities.dashboard import *
from report.cost_report import *
from report.time_report import *
from report.time_graph import *
from admin.admin_dashboard import *

if __name__ == "__main__":
    import sys;
    reload(sys);
    sys.setdefaultencoding("utf8")

    import logging
    from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
    handler = TimedRotatingFileHandler(app.config['SESSION_FILE_DIR']+'/flask.log', when='midnight', interval=1)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s {%(pathname)s:%(lineno)d}")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)
    
    socketio.run(app, log_output=False)
    eventlet.sleep()
    eventlet.monkey_patch()
    eventlet.wsgi.server(eventlet.listen(('',80), app))
    # app.run()



