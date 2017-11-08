#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, datetime

from flask import Blueprint, redirect, render_template
from flask import request, url_for
from werkzeug.utils import secure_filename

# from flask_babel import gettext as _, ngettext, lazy_gettext as __

from pyars import erars, cars

my_it_blueprint = Blueprint('main', __name__, template_folder='templates')

from my_it.remedy.client import Remedy_Client
from my_it.remedy.incident_configuration import status_map
from my_it.remedy.incident_configuration import impact_map
from my_it.remedy.incident_configuration import urgency_map
from my_it.remedy.incident_configuration import service_type_map
from my_it.remedy.incident_configuration import reporter_source_map

from my_it.remedy.utils import stamp_to_date, date_to_stamp

username='appadmin'
password='apppwd'

def ar_login():
    ars = erars.erARS()
    ars.Login(server='1.1.1.1', username=username, password=password, charSet='utf-8')
    return ars

# The Home page is accessible to anyone
@my_it_blueprint.route('/')
def home_page():
    (ongoingHighIncidents, numHighIncidents, formFields) = get_home_incidents()

    itsm_data = {}
    itsm_data["numIncidents"] = numHighIncidents
    itsm_data["tableIncidents"] = format_incidents(ongoingHighIncidents, formFields)
    itsm_data["dropdownIncidents"] = format_dropdown(ongoingHighIncidents, formFields)
    return render_template('pages/home_page.html', data = itsm_data)

def get_home_incidents():
    form = 'HPD:IncidentInterface'
    fields = (1, 2, 3, 1000000000, 1000000162, 
            1000000163, 7, 1000000217, 1000000099, 
            1000000018, 1000000164, 303497300)
    query = "'Submitter' = \""+username+"\""
    query += " and 'Status' <= 4 "
    query += " and 'Submit Date' > " + str(date_to_stamp(datetime.datetime.now()) - 60*60*24*100)
    return get_entries(form=form, query=query, fields=fields, sortList=(3,1) , maxRetrieve=1000)

def get_my_incidents():
    form = 'HPD:IncidentInterface'
    fields = (1, 2, 3, 1000000000, 1000000162, 
            1000000163, 7, 1000000217, 1000000099, 
            1000000018, 1000000164, 303497300)
    query = "'Submitter' = \""+username+"\""
    query += " and 'Status' <= 4 and 'Status' <> 7 "
    # query += " and 'Customer Login ID' = \"user_login\" "
    query += " and 'Submit Date' > " + str(date_to_stamp(datetime.datetime.now()) - 60*60*24*10)

    return get_entries(form=form, query=query, fields=fields, sortList=(3,1), maxRetrieve=1000)

def get_entries(form, query, fields, sortList, maxRetrieve):
    with Remedy_Client(server='88.8.143.231', username=username, password=password) as my_remedy:
        try:
            print "get_form_fields"
            form_fields = my_remedy.get_form_fields(form)
            print "get_entries"
            (entries, numMatches) = my_remedy.get_entries(form = form, query=query, fields=fields, sortList = sortList , maxRetrieve = maxRetrieve)
            print "return"
            return entries, numMatches, form_fields
        except:
            print "Error, could not retrieve entries"
            (entries, numMatches) = ([], 0)
    return [], 0, []

def format_incidents(incident_entries, formFields, add_link = False):
    incidentHTML = '<table width="100%" class="table table-striped table-bordered table-hover" id="dataTables-example">'
    incidentHTML += '<thead><tr><th>Description</th>'
    if add_link: incidentHTML += '<th>Link</th>'
    incidentHTML += '<th>Impact</th><th>Urgency</th><th>Assignee</th><th>Submitted</th><th>Status</th></tr></thead><tbody>'
    for entry in incident_entries:
        incidentHTML += '<tr><td>' + entry[1][formFields["Description"]] + '</td>'
        if add_link: incidentHTML += '<td><a href=' + url_for("main.view_incident") + '?id='+ entry[1][1] +'>Open incident</a></td>'
        incidentHTML += '<td>' + impact_map[entry[1][formFields["Impact"]]] + '</td>'
        incidentHTML += '<td>' + urgency_map[entry[1][formFields["Urgency"]]] + '</td>'
        incidentHTML += '<td>' + entry[1][formFields["Assigned Group"]] + '</td>'
        incidentHTML += '<td>' + str(stamp_to_date(entry[1][formFields["Submit Date"]])) + '</td>'
        incidentHTML += '<td>' + status_map[entry[1][formFields["Status"]]] + '</td></tr>'
    incidentHTML += '</tbody></table>'
    return incidentHTML

def format_dropdown(incident_entries, formFields):
    incidentDropdown = ''
    for entry in incident_entries:
        incidentDropdown += '<li class="right clearfix">'
        incidentDropdown += '<a href=' + url_for("main.view_incident") + '?id='+ entry[1][1] +'><div>' 
        description = entry[1][formFields["Description"]]
        if len(description) > 20: short_desc = description[0:20] + "..."
        else: short_desc = description
        incidentDropdown += '<p><strong>' + short_desc + '</strong>'
        incidentDropdown += '<span class="pull-right text-muted">'+status_map[entry[1][formFields["Status"]]]+'</span></p>'
        active_bar = {0: 'progress-bar-danger', 1: 'progress-bar-warning', 2: 'progress-bar-success', 3: 'progress-bar-info', 4: 'progress-bar-info'}
        incidentDropdown += '<div class="progress progress-striped active">'
        incidentDropdown += '<div class="progress-bar ' + active_bar[entry[1][formFields["Priority"]]] + '" role="progressbar" aria-valuenow="'+ str(entry[1][formFields["Status"]]) +'" aria-valuemin="0" aria-valuemax="" style="width: 40%">'
        incidentDropdown += '<span class="sr-only">'+status_map[entry[1][formFields["Status"]]]+'</span>'
        incidentDropdown += '</div></div></div></a></li>'
    # print incidentDropdown
    return incidentDropdown

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, SelectField, TextAreaField, FileField, HiddenField
class Incident_form(FlaskForm):
    request_id = HiddenField(
        label = 'Request ID')
    first_name = StringField(
        label = 'First name', 
        default = u'my name', 
        description = 'Please type in your first name',
        validators=[validators.DataRequired('First name is required')])
    last_name = StringField(
        label = 'Last name', 
        default = 'my name', 
        validators=[validators.DataRequired('Last name is required')])
    service_type = SelectField(
        label = 'Service Type', 
        validators=[validators.DataRequired('Service Type is required')], 
        choices=[(str(k), v) for k, v in service_type_map.iteritems()])
    reporter_source = SelectField(
        label = 'Reporter Source', 
        validators=[validators.DataRequired('Reporter Source is required')],
        choices = [(str(k), v) for k, v in reporter_source_map.iteritems()])
    impact = SelectField(
        label = 'Impact', 
        validators=[validators.DataRequired('Impact is required')], 
        choices=[(str(k), v) for k, v in impact_map.iteritems()])
    urgency = SelectField(
        label = 'Urgency', 
        validators=[validators.DataRequired('urgency is required')], 
        choices=[(str(k), v) for k, v in urgency_map.iteritems()])
    description = TextAreaField(
        label = 'Description', 
        validators=[validators.DataRequired('Description is required'), validators.length(max=200)])
    status = SelectField(
        label = 'Status', 
        validators=[validators.DataRequired('urgency is required')], 
        choices=[(str(k), v) for k, v in status_map.iteritems()])
    attachment = FileField(
        label = 'Attachment')
    submit_incident = SubmitField('Submit incident')

# The page is accessible to anyone
@my_it_blueprint.route('/user_dashboard/', methods=['GET', 'POST'])
def user_dashboard():
    form = Incident_form()

    # Process valid POST
    if request.method == 'POST':
        print "="*10, "POST user dashboard", "="*10
        print form.submit_incident.data
        print "="*10 + "="*10 + "="*10
        # if form.submit_incident.data and incident_form.validate():
        create_incident(form)

    (ongoingHighIncidents, numHighIncidents, formFields) = get_my_incidents()
    itsm_data = {}
    itsm_data["numIncidents"] = numHighIncidents
    itsm_data["tableIncidents"] = format_incidents(ongoingHighIncidents, formFields)    
    itsm_data["dropdownIncidents"] = format_dropdown(ongoingHighIncidents, formFields)

    return render_template('pages/user_dashboard.html', form = form, data = itsm_data)

def create_incident(form):
    UPLOAD_PATH = 'upload'
    print "="*10 + "creating incident" + "="*10
    ars = ar_login()
    fieldValue = { 
        1000000018 : form.last_name.data, # Last Name
        1000000019 : form.first_name.data, # First Name
        1000000099 : form.service_type.data, # Service Type (0: User Service Restoration, 1: User Service Request, 2: Infrastructure Restoration, 3:Infrastructure Event)
        1000000215 : form.reporter_source.data, # Reporter Source (1000~4000, 4200, 5000~11000)
        7 : 1, # status / 7 (new)
        1000000163 : form.impact.data, # Impact / 1000000163
        1000000162 : form.urgency.data, # Urgency / 1000000162
        1000000000 : form.description.data, # Description / 
        303497300: u"Others",
    }
    if form.attachment.data:
        print "="*10 + "Getting file" + "="*10
        file = request.files[form.attachment.name]
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_PATH, filename)
        file.save(filepath)
        fieldValue[301361600] = (filename, 0, 0, filepath) #(attachmentName, origSize, compressedSize, fileName). Then, the file is uploaded from the filesystem automatically 
        print "="*10 + "attached file" + "="*10

    print "="*10 + "commit an incident" + "="*10
    with Remedy_Client(server='1.1.1.1', username=username, password=password) as my_remedy:
        try:
            entryId = my_remedy.create_entry('HPD:IncidentInterface_Create', fieldValue)
            print "="*10 + "created an incident" + "="*10
        except:
            print "Error, could not create entry"

def get_incident(form, incident_id):
    print "="*10 + ' retrieving ' + "="*10
    ars = ar_login()
    form.request_id.data = incident_id
    with Remedy_Client(server='1.1.1.1', username=username, password=password) as my_remedy:
        try:
            incident = my_remedy.get_entry('HPD:IncidentInterface', incident_id)
            form.first_name.data = incident[1000000019]
            form.last_name.data = incident[1000000018]
            form.status.data = incident[7]
            form.service_type.data = incident[1000000099]
            form.reporter_source.data = incident[1000000215]
            form.impact.data = str(incident[1000000163])
            form.urgency.data = str(incident[1000000162])
            form.description.data = str(incident[1000000000])
            print "="*10 + "retrieved incident" + "="*10
        except:
            print "Error, could not retrieve entry"

def update_incident(form):
    print "="*10 + ' updating ' + "="*10
    print form.description.data
    print "="*10 + "="*10 + "="*10
    new_value = {
        # 7: form.status.data,
        # 1000000099: form.service_type.data,
        # 1000000215: form.reporter_source.data,
        # 1000000163: form.impact.data,
        # 1000000162: form.urgency.data,
        1000000000: form.description.data,
    }

    with Remedy_Client(server='1.1.1.1', username=username, password=password) as my_remedy:
        try:
            return my_remedy.update_entry('HPD:Help Desk', form.request_id.data, new_value)
            # return my_remedy.update_entry('HPD:IncidentInterface', 'INC000000003309', new_value)
        except:
            print '='*20 + " error " + '='*20
            print 'ERROR modifying entry!'
            print my_remedy.status()
            print '='*20 + " error " + '='*20

# The Home page is accessible to anyone
@my_it_blueprint.route('/view_incident', methods=['GET', 'POST'])
def view_incident():
    form = Incident_form()
    if request.method == 'POST':
        print "="*10 + "post request" + "="*10
        form = Incident_form(request.form)
        incident = update_incident(form)
    else:
        incident = get_incident(form, request.args.get('id'))

    (ongoingHighIncidents, numHighIncidents, formFields) = get_my_incidents()
    itsm_data = {}
    itsm_data["numIncidents"] = numHighIncidents
    itsm_data["tableIncidents"] = format_incidents(ongoingHighIncidents, formFields, add_link = True)

    return render_template('pages/view_incident.html', form=form, data = itsm_data)

