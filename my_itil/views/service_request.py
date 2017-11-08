#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, datetime

from flask import Blueprint, redirect, render_template
from flask import request, url_for
from werkzeug.utils import secure_filename

from flask_babel import gettext as _, ngettext, lazy_gettext as __

from pyars import erars, cars

service_blueprint = Blueprint('service_request', __name__, template_folder='templates')

from my_it.remedy.incident_configuration import status_map
from my_it.remedy.incident_configuration import impact_map
from my_it.remedy.incident_configuration import urgency_map
from my_it.remedy.incident_configuration import service_type_map
from my_it.remedy.incident_configuration import reporter_source_map

access_system_name_map = {1: "Internal portal", 2: "staff website"}
access_app_type_map = {1: "Reset password", 2: "Unlock password", 3: "Password application"}

def stamp_to_date(date_int):
    date_date = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=date_int-1)
    return date_date.strftime('%Y-%m-%d %H:%M')

def date_to_stamp(date_date):
    date_int =  (date_date - datetime.datetime(1970, 1, 1)).total_seconds()
    return int(date_int)

def ar_login():
    ars = erars.erARS()
    username='appadmin'
    password='Bmc#123'
    ars.Login(server='88.8.143.231', username=username, password=password, charSet='utf-8')
    return ars

# The Home page is accessible to anyone
@service_blueprint.route('/new_service_request', methods=['GET', 'POST'])
def new_service_request():
    form = Request_form()
    return render_template('pages/new_service_request.html', form=form)#, form=form, data = itsm_data)

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, SelectField, TextAreaField, FileField, HiddenField
class Request_form(FlaskForm):
    request_id = HiddenField(
        label = 'Request ID')
    service_type = HiddenField(
        label = 'Service Type')
    job_classification = HiddenField(
        label = 'Job Classification')
    service_action = HiddenField(
        label = 'Job Classification')
    submit = SubmitField('Submit request', id="submit_request")

# ajax response to display list of Request services available
@service_blueprint.route('/get_service_types', methods=['GET', 'POST'])
def get_service_types():
    service_types = {
            'Access to Internal Website': 'icon/global-icon.png',
            'Communication Systems':'icon/chat-icon.png'
            'Network and Telephone Services':'icon/cloud-network.png',
            'NT Security Accounts': 'icon/shield-icon.png',
            'Business IT Sytems': 'icon/bank-icon.png',
    }
    return render_template(
        'forms/service_type_choice.html', 
        choice_title = 'Please choose a service type :',
        service_types = {k:url_for('static', filename = v) for k,v in service_types.items()})

# ajax response to display list of Request services available
@service_blueprint.route('/get_service_jobs', methods=['GET', 'POST'])
def get_service_jobs():
    service_type = request.form['form_values[1]']
    if service_type =='Access to Internal Website': 
        service_jobs = {
                'Password for Bank Portal': 'icon/password-portal.png', 
                'Password for Group Site': 'icon/password-group.png', 
                'Virtual Code for Bank Portal': 'icon/calculator-icon.png',
                'Security Controls for Bank Portal': 'icon/keys-icon.png',
                'VDI User Groups and System': 'icon/vdi.png'
                }
    elif service_type == 'Communication Systems':
        service_jobs = {
                'MDM User Groups and System': 'icon/mobile-icon.png', 
                'Mobile Conference Administrator Access': 'icon/Announcement-icon.png', 
                'External Media Access': 'icon/news-media.png',
                'Public Affairs Mail Account': 'icon/world-stat-icon.png',
                }
    elif service_type == 'Network and Telephone Services':
        service_jobs = {
                'General Network': 'icon/networking-icon.png', 
                'Wifi': 'icon/wifi.png', 
                'VoIP Phone': 'icon/voip-phone.png',
                'Video Conference': 'icon/video.png',
                'Other': 'icon/network-phone.png',
                }
    elif service_type == 'NT Security Accounts':
        service_jobs = {
                'Account Password': 'icon/name-card-icon.png', 
                'Mail Account': 'icon/email-icon.png', 
                'Computer Log In Settings': 'icon/settings-icon.png',
                'Outsourcing Vendor Account': 'icon/bus-icon.png',
                'PC shared folder': 'icon/Folder-icon.png',
                }
    elif service_type == 'Business IT Sytems':
        service_jobs = {
                'Biz System 1': 'icon/statistics-market-icon.png',
                'Biz System 2': 'icon/money-transfer.png',
                'Biz System 3': 'icon/dollar-exchange.png',
                'Biz System 4': 'icon/atm-machine.png',
                }
    else:
        service_jobs = {'Internal portal password': 'icon/password-portal.png'}
    return render_template(
        'forms/service_type_choice.html', 
        choice_title = 'Please choose a job type :',
        service_types = {k:url_for('static', filename = v) for k,v in service_jobs.items()})

# ajax response to display list of Request services available
@service_blueprint.route('/get_service_actions', methods=['GET', 'POST'])
def get_service_actions():
    service_type = request.form['form_values[1]']
    service_actions = {
                'New': 'icon/addition-icon.png',
                'Delete ': 'icon/recycle-bin-icon.png',
                'Change': 'icon/edit-pen.png',
                }
    return render_template(
        'forms/service_type_choice.html', 
        choice_title = 'Please choose an action :',
        service_types = {k:url_for('static', filename = v) for k,v in service_actions.items()})

# The Home page is accessible to anyone
@service_blueprint.route('/get_service_form', methods=['GET', 'POST'])
def get_service_form():    
    print "="*10 + "get service form" + "="*10
    print "Request method = " +request.method
    dict = request.form
    html = '<h2>nothing here</h2>'
    for key in dict:
        print "request.form[" + key + "]: " + dict[key]
    print "="*10 + "get service form" + "="*10
    if request.form["form_values[1]"] and request.form["form_values[1]"] == 'Access to Internal Website':
        if request.form["form_values[2]"] == 'Password for Portal':
            form = Account_request_form()
            request_title = request.form["form_values[3]"] + ' ' + request.form["form_values[2]"],
            html = render_template(
                'forms/account_request_internal_website.html', 
                request_title = request.form["form_values[3]"] + ' ' + request.form["form_values[2]"],
                form=form)
    elif request.form["form_values[2]"] and request.form["form_values[3]"]:
        html = '<h3> ' + request.form["form_values[3]"] + ' ' + request.form["form_values[2]"] + '</h3><div>This type of requested haven\'t been implemented yet, please contact Help Desk directly</div>'
    else:
        html = '<h2>nothing here</h2>'
    return html

def get_form(service_type, job_classification, service_action):

    switcher = {
        'Access to Internal Website': {},
        'Communication Systems': {},
        'Network and Telephone Services': {},
        'NT Security Accounts': {},
        'Business IT Sytems': {},
        'Offshore IT Sytems': {},
        'default':{}
    }
    return switcher.get(service_type, "default").get(job_classification, "default").get(service_action, "default")

class Account_request_form(Request_form):
    nt_account = StringField(
        label = 'Account', 
        default = u'account', 
        description = 'Please type in the Naccount of requester',
        validators=[validators.DataRequired('Account is required')])
    notes = TextAreaField(
        label = 'Notes', 
        validators=[validators.length(max=200)])
    attachment = FileField(
        label = 'Attachment')

@service_blueprint.route('/create_service_request', methods=['GET', 'POST'])
def create_service_request():
    request_form = Request_form(request.form)
    print request_form.service_type.data
    print "="*10 + "create_service_request" + "="*10
    dict = request.form
    for key in dict:
        print "request.form[" + key + "]: " + dict[key]
    print "="*10 + "create_service_request" + "="*10
    return '<h2> a request has been created </h2>'
