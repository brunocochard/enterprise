from datetime import date

from flask_login import login_required, current_user
from flask import render_template, request

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

from app import app
from user.management import User, load_user

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
