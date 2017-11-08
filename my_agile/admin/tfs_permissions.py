from flask_login import login_required, current_user
from flask import render_template

from app import app

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

class PermissionForm(FlaskForm):
    list_project = SelectField(u'Project')

def format_permissions(list_permissions):
	returnHTML = (
		'<table class="table">'
			'<thead>'
				'<tr>'
					'<th class="col-md-1">Name</th>'
					'<th class="col-md-1">Id</th>'
					'<th class="col-md-1">dataspaceCategory</th>'
				'</tr>'
			'</thead>'
		'<tbody>')
	for ns in list_permissions:
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
	for project in list_members:
		returnHTML += (
			'<tr class="success">'
				'<th>' + project['name'] + '</th>'
				'<td>' + project['url'] + '</td>'
				'<td>' + project['description'] + '</td>'
			'</tr>'
			)  
		for team in project['teams']:
			team_name = team['name']
			team_description = team['description']
			for member in team['members']:
				returnHTML += (
					'<tr class="active">'
						'<td>' + team_name + '</td>'
						'<td>' + team_description + '</td>'
						# '<td>' + team['id'] + '</td>'
						# '<td>' + team['identityUrl'] + '</td>'
						'<td>' + member['displayName'] + ' (' + member['uniqueName'] + ')</td>'
					'</tr>'
					)
				team_description=''
				team_name=''
		# for action in ns['actions']:
		# 	returnHTML += (
		# 	'<tr class="active">'
		# 		'<td colspan = "2">' + action['displayName'] + '</td>'
		# 		'<td colspan = "1">' + str(action['bit']) + '</td>'
		# 	'</tr>'
		# 	)      
	return returnHTML + '</tbody></table>'
    
@app.route("/tfs_permissions", methods=['GET', 'POST'])
@login_required
def tfs_permissions():
    form = PermissionForm()
    list_members = []

    for project in current_user.run().get_projects():
		try: 
			description = team['description']
		except:
			description = ''
		list_members.append({
			'name': project['name'],
			'description': description, 
    		'url': app.config['TFS_URL'] + project['name'], 
    		'teams': current_user.run().get_team_members(project = project['name'])})
    list_permissions = current_user.run().get_permissions()
    return render_template(
                'tfs_permissions.html', 
                # form = form, 
                teams = format_teams(list_members),
                permissions=format_permissions(list_permissions))
