from datetime import date, timedelta

from flask_login import login_required, current_user
from flask import render_template, request

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields.html5 import DateField

from app import app
from user.management import User, load_user

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
