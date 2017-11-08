# -*- coding: utf-8 -*-

from flask_login import login_required, current_user
from flask import render_template
import flask_excel as excel

from app import app

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

dict_items = {}
list_items_csv = []

class PermissionForm(FlaskForm):
    list_project = SelectField(u'Project')
    export_excel = SubmitField(label="Export to Excel")

def format_projects(list_projects):
	returnHTML = (
		'<table class="table">'
			'<thead>'
				'<tr>'
					'<th class="col-md-2">Name</th>'
					'<th class="col-md-10">Description</th>'
				'</tr>'
			'</thead>'
		'<tbody>')
	del list_items_csv[:]
	list_items_csv.append(['Project Name', 'Project Description'])
	for project in list_projects.values():
		try: 
			description = project['description']
		except:
			description = ''
		returnHTML += (
			'<tr class="success">'
				'<th><a id="'+project['name']+'Link" href = "'+ project['url'] +'" target="_blank">' + project['name'] + '</a></th>'
				'<td>' + description + '</td>'
			'</tr>'
			)
		list_items_csv.append([project['name'], description])
		# for action in ns['actions']:
		# 	returnHTML += (
		# 	'<tr class="active">'
		# 		'<td colspan = "2">' + project['displayName'] + '</td>'
		# 		'<td colspan = "1">' + str(project['bit']) + '</td>'
		# 	'</tr>'
		# 	)      
	return returnHTML + '</tbody></table>'

def format_areas(list_project_areas):
	returnHTML = (
		'<table class="table table-striped">'
			'<thead>'
				'<tr>'
					'<th class="col-md-2">Project</th>'
					'<th class="col-md-10">Areas</th>'
				'</tr>'
			'</thead>'
		'<tbody>')
	del list_items_csv[:]
	list_items_csv.append(['Project Name', 'Area Name'])
	for project in list_project_areas.values():
		project_name = project['name']
		
		try:
			for area in project['areas'].values():
				row_class = 'success' if project_name != '' else 'active'
				returnHTML += (
					'<tr class="'+ row_class +'">'
						'<th>' + project_name + '</th>'
						'<td><a id="' + area['name']+'Link" href = "' + project['url']+ '/' + area['name'] + '" target="_blank">' + area['name'] + '</a></td>'
					'</tr>'
					)
				project_name = ''
				list_items_csv.append([project['name'], area['name']])
		except:
			returnHTML += (
				'<tr class="success">'
					'<th>' + project_name + '</th>'
					'<td><sub>None</sub></td>'
				'</tr>'
				)
			list_items_csv.append([project['name'], ''])
	return returnHTML + '</tbody></table>'

def format_permissions(list_permissions):
	returnHTML = (
		'<table class="table">'
			'<thead>'
				'<tr>'
					'<th class="col-md-7">Name</th>'
					'<th class="col-md-3">Id</th>'
					'<th class="col-md-2">dataspaceCategory</th>'
				'</tr>'
			'</thead>'
		'<tbody>')
	del list_items_csv[:]
	list_items_csv.append(['Permission Name', 'Permission ID', 'Dataspace Category', 'Action Name', 'Action Bit'])
	for ns in list_permissions.values():
		returnHTML += (
			'<tr class="success">'
				'<th>' + ns['name'] + '</th>'
				'<td>' + ns['namespaceId'] + '</td>'
				'<td>' + ns['dataspaceCategory'] + '</td>'
			'</tr>'
			)      
		for action in ns['actions']:
			returnHTML += (
			'<tr class="active">'
				'<td colspan = "2">' + action['displayName'] + '</td>'
				'<td colspan = "1">' + str(action['bit']) + '</td>'
			'</tr>'
			)
			list_items_csv.append([ns['name'], ns['namespaceId'], ns['dataspaceCategory'], action['displayName'], action['bit']])
	return returnHTML + '</tbody></table>'

def format_teams(list_members):
	returnHTML = (
		'<table class="table">'
			'<thead>'
				'<tr>'
					'<th class="col-md-2">Project</th>'
					'<th class="col-md-2">URL</th>'
					'<th class="col-md-8">Description</th>'
				'</tr>'
			'</thead>'
		'<tbody>')
	del list_items_csv[:]
	list_items_csv.append(['Project Name', 'Project URL', 'Project Description', 'Team Name', 'Team Description', 'Member Name', 'AD Account'])
	for project in list_members.values():
		project['description'] = project.get('description', '')
		project_description = project['description']
		returnHTML += (
			'<tr class="success">'
				'<th>' + project['name'] + '</th>'
				'<td>' + project['url'] + '</td>'
				'<td>' + project['description'] + '</td>'
			'</tr>'
			)  
		for team in project['teams'].values():
			team_name = team['name']
			team['description'] = team.get('description', '')
			team_description = team['description']
			for member in team['members'].values():
				returnHTML += (
					'<tr class="active">'
						'<td>' + team_name + '</td>'
						'<td>' + team_description + '</td>'
						'<td>' + member['displayName'] + ' (' + member['uniqueName'] + ')</td>'
					'</tr>'
					)
				list_items_csv.append([project['name'], project['url'], project['description'], team['name'], team['description'], member['displayName'], member['uniqueName']])    
				team_description=''
				team_name=''
	return returnHTML + '</tbody></table>'

def format_repositories(list_project_repositories):
	returnHTML = (
		'<table class="table table-striped">'
			'<thead>'
				'<tr>'
					'<th class="col-md-2">Project</th>'
					'<th class="col-md-10">Repository</th>'
				'</tr>'
			'</thead>'
		'<tbody>')
	del list_items_csv[:]
	list_items_csv.append(['Project Name', 'Area Name', 'URL'])
	for project in list_project_repositories.values():
		project_name = project['name']
		try:
			for repository in project['repositories'].values():
				row_class = 'success' if project_name != '' else 'active'
				returnHTML += (
					'<tr class="'+ row_class +'">'
						'<th>' + project_name + '</th>'
						'<td><a id="' + repository['name'] +'Link" href = "' + repository['remoteUrl'] + '" target="_blank">' + repository['name'] + '</a></td>'
					'</tr>'
					)
				project_name = ''
				list_items_csv.append([project['name'], repository['name'], repository['remoteUrl']])
		except:
			returnHTML += (
				'<tr class="success">'
					'<th>' + project_name + '</th>'
					'<td><sub>None</sub></td>'
				'</tr>'
				)
			list_items_csv.append([project['name'], ''])
	return returnHTML + '</tbody></table>'

@app.route("/export_admin_records", methods=['GET'])
@login_required
def export_admin_records():
	return excel.make_response_from_array(list_items_csv, "csv", file_name="tfs_project_areas")
    
@app.route("/view_projects", methods=['GET'])
@login_required
def view_projects():
    form = PermissionForm()
    dict_items = current_user.run().get_projects()
    return render_template(
                'admin_dashboard.html', 
                form = form,
                data=format_projects(dict_items))
    
@app.route("/view_areas", methods=['GET'])
@login_required
def view_areas():
    form = PermissionForm()
    dict_items = current_user.run().get_projects()
    for project_name, project in dict_items.iteritems():
    	project['areas'] = current_user.run().get_project_areas(project = project_name)
    return render_template(
                'admin_dashboard.html', 
                form = form, 
                data = format_areas(dict_items))
    
@app.route("/view_permissions", methods=['GET'])
@login_required
def view_permissions():
    form = PermissionForm()
    dict_items = current_user.run().get_permissions()
    return render_template(
                'admin_dashboard.html', 
                form = form,
                data=format_permissions(dict_items))

    
@app.route("/view_teams", methods=['GET'])
@login_required
def view_teams():
    form = PermissionForm()
    dict_items = current_user.run().get_projects()
    for project_name, project in dict_items.iteritems():
    	project['teams'] = current_user.run().get_project_members(project_name)
    return render_template(
                'admin_dashboard.html', 
                form = form,
                data = format_teams(dict_items))
    
@app.route("/view_repositories", methods=['GET'])
@login_required
def view_repositories():
    form = PermissionForm()
    dict_items = current_user.run().get_projects()
    for project_name, project in dict_items.iteritems():
    	try:
    		project['repositories'] = current_user.run().get_repositories(project_name)
    	except:
    		project['repositories'] = {'name': 'Not Set', 'remoteUrl': project['url']+ '/_git/' + project['name']}
    return render_template(
                'admin_dashboard.html', 
                form = form,
                data=format_repositories(dict_items))
