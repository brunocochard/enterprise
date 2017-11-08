from datetime import datetime, date, timedelta

from app import app, socketio, login_manager
from flask import render_template, redirect, url_for, request, session

from flask_login import login_user, login_required, logout_user, current_user

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.fields.html5 import DateField

from user.management import User, logged_users, load_user
from notifications.login import background_stuff

from threading import Thread

thread = None

class LoginForm(FlaskForm):
    username = StringField('User Name', default=app.config['TFS_USER'])
    if app.config['TFS_PWD']:
        password = StringField('Password', default=app.config['TFS_PWD'])
    else: 
        password = PasswordField('Password', default=app.config['TFS_PWD'])
    error_message = ''
    login_tfs = SubmitField(label="Log in DevOps Hub")

@app.route("/cub_login", methods=['GET', 'POST'])
def cub_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User(form.username.data, form.password.data)
        if user.is_connected :
            logged_users[user.id] = user
            if user.is_connected() :
                login_user(user)
                app.logger.info('%s logged in successfully', user.id)
                return redirect(url_for('my_requests'))
        app.logger.info('%s failed logged in from %s', user.id, request.remote_addr)
        form.error_message = 'Invalid credentials'

    return render_template('login.html', form = form)

@app.route('/cub_logout')
@login_required
def cub_logout():
    userid = current_user.id
    logout_user()
    app.logger.info('%s logging out', userid)
    return redirect(url_for('cub_login'))

@app.route("/", methods=['GET', 'POST'])
@login_required
def home():
    active_task_table = current_user.run().get_my_activities(state='Active')
    new_task_table = current_user.run().get_my_activities(state='New')
    data = []
    data.append(active_task_table.to_html(classes='time'))
    data.append(new_task_table.to_html(classes='time'))

    global thread
    if thread is None:
        thread = Thread(target=background_stuff, args=[url_for('timesheet_notification', _external=True)])
        thread.start()

    return render_template(
            'home.html',
            data=data
            )      

@app.route('/pygalexample/')
def pygalexample():
    try:
        bar_chart = pygal.HorizontalStackedBar(style=LightGreenStyle)
        bar_chart.title = "sprint 12 timesheet"
        bar_chart.x_labels = map(str, ['bruno', 'Alan', 'Eric'])
        bar_chart.add('dev', [34, 55, 57])
        bar_chart.add('test', [7, 13, 11])
        bar_chart.add('mgt', [39, 12, 12])
        graph_data = bar_chart.render_data_uri()
        return render_template("graphing.html", graph_data = graph_data)
    except Exception, e:
        return(str(e))

