from datetime import datetime, date, timedelta

from app import app, socketio, login_manager
from flask import render_template, redirect, url_for, request, session
import functools

from flask_login import login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, send, emit, disconnect

from requests import post

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.fields.html5 import DateField

from user.management import User, logged_users, load_user

import time
from threading import Thread, Event

thread = None

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

class LoginForm(FlaskForm):
    username = StringField('User Name', default=app.config['TFS_USER'])
    if app.config['TFS_PWD']:
        password = StringField('Password', default=app.config['TFS_PWD'])
    else: 
        password = PasswordField('Password', default=app.config['TFS_PWD'])
    error_message = ''
    login_tfs = SubmitField(label="Log in DevOps Hub")

@app.route("/login", methods=['GET', 'POST'])
def login():

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User(form.username.data, form.password.data)
        if user.is_connected :
            logged_users[user.id] = user
            if user.is_connected() :
                login_user(user)
                return redirect(url_for('home'))
        form.error_message = 'Invalid credentials'

    return render_template('login.html', form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@socketio.on('status', namespace = '/timesheet')
@authenticated_only
def timesheet_message(msg):
    emit('status', {'status': msg['status']})

@socketio.on('connect', namespace = '/timesheet')
@authenticated_only
def timesheet_connect():
    user_id = current_user.get_id()
    logged_users[user_id].set_namespace(request.sid)
    emit('userid', {'userid': user_id})
    # emit('status', {'status': 'Connected user +'+ userid})

    result_table = logged_users[user_id].run().get_my_activities(state='Active')
    t = datetime.now().strftime("%H:%M:%S")

    if len(result_table.index):
        emit_title= result_table.iloc[0,3] + " Task: " + result_table.iloc[0,1] + " in project " + result_table.iloc[0,2]
        emit_url = app.config['TFS_URL']+ result_table.iloc[0,2] +'/_workitems?id='+str(result_table.iloc[0,0])
        emit_data = 'Are you still working on this task?'
    else:
        emit_title= "You currently don't have any active task."
        emit_data = 'Maybe you should create or activate a task'
        emit_url = app.config['TFS_URL']
    emit(
        'task_notification', 
        {'title': emit_title, 'time':t, 'data': emit_data,'url':emit_url}, 
        namespace = '/timesheet',
        room = logged_users[user_id].get_namespace())

@socketio.on('disconnect_request', namespace = '/timesheet')
@authenticated_only
def disconnect_request():
    emit('status', {'status': 'user disconnected'})

@socketio.on('message')
@authenticated_only
def handle_message(msg):
    send(msg, broadcast=True)

def background_stuff(url):
    while (True):
        time.sleep(15)
        t = datetime.now().strftime("%H:%M:%S")
        for user_id in logged_users :
            # if logged_users[user_id].is_authenticated:
                result_table = logged_users[user_id].run().get_my_activities(state='Active')
                room = logged_users[user_id].get_namespace()
                
                if len(result_table.index):
                    emit_title= result_table.iloc[0,3] + " Task: " + result_table.iloc[0,1] + " in project " + result_table.iloc[0,2]
                    emit_url = app.config['TFS_URL']+ result_table.iloc[0,2] +'/_workitems?id='+str(result_table.iloc[0,0])
                    emit_data = 'Are you still working on this task?'
                else:
                    emit_title= "You currently don't have any active task."
                    emit_data = 'Maybe you should create or activate a task'
                    emit_url = app.config['TFS_URL']
                socketio.emit(
                    'task_notification', 
                    {'title': emit_title, 'time':t, 'data': emit_data,'url':emit_url}, 
                    namespace = '/timesheet',
                    room = room)

@app.route("/", methods=['GET', 'POST'])
@login_required
def home():
    app.logger.info('%s requested /home', current_user.id)
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

@app.route("/timesheet_notification", methods=['POST'])
def timesheet_notification():
    user = load_user(request.json['user_id'])
    emit(
        'task_notification', 
        request.json, 
        room = user.get_namespace()
        )

class WitForm(FlaskForm):
    list_project = SelectField(u'list projects')
    select_project = SubmitField(label="Select Project")    
    
@app.route("/wits", methods=['GET', 'POST'])
@login_required
def wits():
    form = WitForm()

    form.list_project.choices = current_user.get_all_projects()
    list_items = [dict(title='name',state='state', created='created', closed='closed', area='area')]

    if request.method == 'POST':
        app.logger.info('%s requested /epics for %s', current_user.id, form.list_project.data)
        all_wits = current_user.get_epics(project= form.list_project.data)
        list_items = []
        for each in all_wits['value']:
            try:
                closed_date = each['fields']['Microsoft.VSTS.Common.ClosedDate'].rsplit('T', 1)[0]
                closed_date = datetime.strptime(closed_date, '%Y-%m-%d').date()
            except:
                closed_date = 'NaN'
            
            try:
                created_date=each['fields']['System.CreatedDate'].rsplit('T', 1)[0]
                created_date = datetime.strptime(created_date, '%Y-%m-%d').date()
            except :
                created_date = 'NaN'
            try:
                list_items.append(dict(
                        title=each['fields']['System.Title'], 
                        state=each['fields']['System.State'], 
                        created=created_date, 
                        closed=closed_date, 
                        area=each['fields']['System.AreaPath']))
            except : 
                list_items = [dict(title='no work items found',state='---', created='---', closed='---', area='---')]
    return render_template('wits.html', form = form, list_items=list_items)

class TimeForm(FlaskForm):
    list_project = SelectField(u'Project')
    from_date = DateField('From date', default=date.today() - timedelta(days=30), format='%Y-%m-%d')
    to_date = DateField('To date', default=date.today(), format='%Y-%m-%d')
    run_report = SubmitField(label="Run simple report")
    run_detailed_report = SubmitField(label="Run detailed report")
    
@app.route("/time_report", methods=['GET', 'POST'])
@login_required
def time_report():
    form = TimeForm()
    form.list_project.choices = current_user.get_all_projects()
    form.list_project.default = app.config['TFS_PROJECT']
    
    if request.method == 'POST':
        app.logger.info('%s requested /time_report for %s', current_user.id, form.list_project.data)
        result_table = current_user.get_activities(
            project = form.list_project.data, 
            from_date = form.from_date.data.strftime('%Y-%m-%d'), 
            to_date = form.to_date.data.strftime('%Y-%m-%d'),
            detail = form.run_detailed_report.data)

        return render_template(
                'time_report.html', 
                form = form, 
                data=result_table.to_html(classes='time'))
    else:
        return render_template('time_report.html', form = form)


import pygal
from pygal.style import LightGreenStyle

@app.route("/time_graph", methods=['GET', 'POST'])
@login_required
def time_graph():
    form = TimeForm()
    form.list_project.choices = current_user.get_all_projects()
    form.list_project.default = app.config['TFS_PROJECT']
    
    if request.method == 'POST':
        app.logger.info('%s requested /time_graph for %s', current_user.id, form.list_project.data)
        wit_table = current_user.get_time_report(
            project = form.list_project.data, 
            from_date = form.from_date.data.strftime('%Y-%m-%d'), 
            to_date = form.to_date.data.strftime('%Y-%m-%d'))

        assignees = []
        completed_hours=[]
        estimated_hours=[]
        activity_hours = {}
        all_activities = {}      

        for each in wit_table.get_children().values():
            if each.get_attr('System.AssignedTo') == "undefined": 
                assignee = 'Not assigned'
            else : 
                assignee = each.get_attr('System.AssignedTo')

            if each.get_attr('Microsoft.VSTS.Scheduling.CompletedWork') == "undefined": 
                completed = 0.0
            else : 
                completed = each.get_attr('Microsoft.VSTS.Scheduling.CompletedWork')

            if each.get_attr('Microsoft.VSTS.Scheduling.OriginalEstimate') == "undefined": 
                estimated = 0.0
            else : 
                estimated = each.get_attr('Microsoft.VSTS.Scheduling.OriginalEstimate')

            activity = each.get_attr('Microsoft.VSTS.Common.Activity')

            if assignee not in assignees:
                assignees.append(assignee)
                completed_hours.append(completed)
                estimated_hours.append(estimated)
                
                if activity == "undefined": all_activities[assignee] = [completed, 0, 0, 0, 0]
                elif activity == "Development": all_activities[assignee] = [0, completed, 0, 0, 0]
                elif activity == "Testing": all_activities[assignee] = [0,0,completed, 0, 0]
                elif activity == "Deployment": all_activities[assignee] = [0,0,0,completed, 0]
                else: all_activities[assignee] = [0,0,0,0,completed]
            else:
                assignee_index = assignees.index(assignee)
                completed_hours[assignee_index] +=  completed
                estimated_hours[assignee_index] += estimated

                if activity == "undefined": all_activities[assignee][0] += completed
                elif activity == "Development": all_activities[assignee][1] += completed
                elif activity == "Testing": all_activities[assignee][2] += completed
                elif activity == "Deployment": all_activities[assignee][3] += completed
                else : all_activities[assignee][4] += completed
        try:
            if not form.run_detailed_report.data:
                bar_chart = pygal.Bar(style=LightGreenStyle, height= 300, legend_at_bottom=True)
                bar_chart.title = "Estimated VS Completed"
                bar_chart.x_labels = map(str, assignees)

                bar_chart.add('completed', completed_hours)
                bar_chart.add('estimated', estimated_hours)

                graph_data = bar_chart.render_data_uri()
                return render_template(
                        "time_graph.html", 
                        form = form,
                        graph_data = graph_data)
            else:
                dot_chart = pygal.Dot(x_label_rotation=30,style=LightGreenStyle, height= 900, legend_at_bottom=True)
                dot_chart.title = 'Work assignment Ratio'
                dot_chart.x_labels = ['Undefined', 'Development', 'Testing', 'Deployment', 'Others']
                for k,v in all_activities.items(): 
                    dot_chart.add(k, v)
                graph_data = dot_chart.render_data_uri()
                return render_template(
                        "time_graph.html", 
                        form = form,
                        graph_data = graph_data)
        except Exception, e:
            return(str(e))
    else:
        return render_template('time_graph.html', form = form)


class TimeForm(FlaskForm):
    list_project = SelectField(u'Project')
    from_date = DateField('From date', default=date.today() - timedelta(days=30), format='%Y-%m-%d')
    to_date = DateField('To date', default=date.today(), format='%Y-%m-%d')
    run_report = SubmitField(label="Run simple report")
    run_detailed_report = SubmitField(label="Run detailed report")

@app.route("/cost_report", methods=['GET', 'POST'])
@login_required
def cost_report():
    form = TimeForm()
    form.list_project.choices = current_user.get_all_projects()
    form.list_project.default = app.config['TFS_PROJECT']

    if request.method == 'POST':
        app.logger.info('%s requested /cost_report for %s', current_user.id, form.list_project.data)
        result_table = current_user.get_feature_tree(
            project= form.list_project.data, 
            from_date = form.from_date.data.strftime('%Y-%m-%d'), 
            to_date = form.to_date.data.strftime('%Y-%m-%d'),
            detail = form.run_detailed_report.data)

        return render_template(
                'cost_report.html', 
                form = form, 
                data=result_table)

        # return render_template(
        #         'cost_report.html', 
        #         form = form, 
        #         data=result_table.to_html(classes='time'))
    return render_template('cost_report.html', form = form)        

@app.route('/pygalexample/')
def pygalexample():
    try:
        app.logger.info('%s requested /pygal_example for %s', current_user.id, form.list_project.data)
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


class RequestForm(FlaskForm):
    title = StringField('Request title')
    description = StringField('description')
    list_project = SelectField(u'Project')
    create_request = SubmitField(label="Create new request")

@app.route("/my_requests", methods=['GET', 'POST'])
@login_required
def my_requests():
    form = RequestForm()
    form.list_project.choices = current_user.get_all_projects()
    form.list_project.default = app.config['TFS_PROJECT']

    active_request_table = current_user.get_my_requests(state='Active')
    new_request_table = current_user.get_my_requests(state='New')
    data = []
    data.append(active_request_table.to_html(classes='time'))
    data.append(new_request_table.to_html(classes='time'))
    
    if request.method == 'POST':
        today_str = date.today().strftime('%Y-%m-%d')
        new_request = current_user.create_request(
            project= form.list_project.data, 
            title = form.title.data, 
            description = form.description.data,
            e_ticket = 'TFS-GEN-XXX-' + today_str)

        active_request_table = current_user.get_my_requests(state='Active')
        new_request_table = current_user.get_my_requests(state='New')
        data = []
        data.append(active_request_table.to_html(classes='time'))
        data.append(new_request_table.to_html(classes='time'))
        return render_template(
                'my_requests.html', 
                form = form, 
                data=data)

    return render_template(
            'my_requests.html', 
            form = form, 
            data=data
            )
