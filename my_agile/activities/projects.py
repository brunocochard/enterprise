from datetime import datetime, date

from flask_login import login_required, current_user
from flask import render_template, request

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

from app import app
from user.management import User, load_user

class WitForm(FlaskForm):
    list_project = SelectField(u'list projects')
    select_project = SubmitField(label="Select Project")    
    
@app.route("/projects", methods=['GET', 'POST'])
@login_required
def projects():
    form = WitForm()

    form.list_project.choices = current_user.get_all_projects()
    list_items = [dict(title='name',state='state', created='created', closed='closed', area='area')]

    if request.method == 'POST':
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
    return render_template('projects.html', form = form, list_items=list_items)

@app.route("/my_project_areas", methods=['GET'])
@login_required
def my_project_areas():
    form = WitForm()

    all_projects = current_user.get_all_projects()
    list_items = [dict(title='name',state='state', created='created', closed='closed', area='area')]

    returnHTML = (
        '<table class="table table-hover">'
            '<thead>'
                '<tr>'
                    '<th class="col-md-2">project</th>'
                    '<th class="col-md-2">area</th>'
                '</tr>'
            '</thead>'
        '<tbody>')
    for project in [project_tuple[1] for project_tuple in all_projects]:
        area = current_user.run().get_areas(project = project)
        returnHTML += (
            '<tr class="success">'
                '<td>'+ project +'</td>'
                '<td>' + area.get_attr('name') + '</td>'
            '</tr>')
        for child_area in area.get_children():
            # child2 = [grandchild.get_attr('name') for grandchild in child_area.get_children()]
            returnHTML += (
                '<tr class="active">'
                    '<td></td>'
                    '<td>' + child_area.get_attr('name') +'</td>'
                '</tr>')    
    returnHTML += '</tbody></table>'
    return render_template('my_project_areas.html', data=returnHTML)    
