import functools
import time
from datetime import datetime

from flask import request
from flask_login import login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, send, emit, disconnect

from app import app, socketio, login_manager

from user.management import User, logged_users

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

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
        time.sleep(app.config['TIMESHEET_TIMER'])
        
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

@app.route("/timesheet_notification", methods=['POST'])
def timesheet_notification():
    user = load_user(request.json['user_id'])
    emit(
        'task_notification', 
        request.json, 
        room = user.get_namespace()
        )
