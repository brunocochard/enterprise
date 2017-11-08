from datetime import date, timedelta

from flask_login import login_required, current_user
from flask import render_template, request

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields.html5 import DateField

import flask_excel as excel

from app import app
from user.management import User, load_user

list_items_csv = []

class TimeForm(FlaskForm):
    list_project = SelectField(u'Project')
    from_date = DateField('From date', default=date.today() - timedelta(days=30), format='%Y-%m-%d')
    to_date = DateField('To date', default=date.today(), format='%Y-%m-%d')
    run_report = SubmitField(label="Run simple report")
    run_detailed_report = SubmitField(label="Run detailed report")
    export_cost_report = SubmitField(label="Export to Excel")

def format_report(feature_dict, detail):
    del list_items_csv[:]
    if not detail: 
        returnHTML = (
            '<table class="table table-hover">'
                '<thead>'
                    '<tr>'
                        '<th class="col-md-4">Feature Title</th>'
                        '<th class="col-md-2">E-Ticket</th>'
                        '<th class="col-md-4">Cost Owner</th>'
                        '<th class="col-md-1">Estimated</th>'
                        '<th class="col-md-1">Completed</th>'
                    '</tr>'
                '</thead>'
            '<tbody>')
        list_items_csv.append(['Feature Title', 'E-Ticket', 'Cost Owner', 'Estimated', 'Completed'])

    else: 
        returnHTML = (
            '<table class="table">'
                '<thead>'
                    '<tr>'
                        '<th class="col-md-2">Feature Title</th>'
                        '<th class="col-md-1">E-Ticket</th>'
                        '<th class="col-md-1">Cost Owner</th>'
                        '<th class="col-md-2">Story Title</th>'
                        '<th class="col-md-2">Task Title</th>'
                        '<th class="col-md-2">Assignee</th>'
                        '<th class="col-md-1">Estimated</th>'
                        '<th class="col-md-1">Completed</th>'
                    '</tr>'
                '</thead>'
            '<tbody>')

        list_items_csv.append(['Feature Title', 'E-Ticket', 'Cost Owner', 'Story Title', 'Task Title', 'Assignee', 'Estimated', 'Completed'])

    for feature in feature_dict.get_children():
        feature_completed = 0
        feature_estimated = 0
        if detail and feature.get_attr('System.WorkItemType') == 'Task':
            try: 
                completed = feature.get_attr('Microsoft.VSTS.Scheduling.CompletedWork')
                feature_completed += completed
            except: completed = '-'
            try: 
                estimated = feature.get_attr('Microsoft.VSTS.Scheduling.OriginalEstimate')
                feature_estimated += estimated
            except: estimated = '-'
            returnHTML += (
                '<tr class="active">'
                    '<td>This task is not related to any feature</td>'
                    '<td></td>'
                    '<td></td>'
                    '<td></td>'
                    '<td>'+ feature.get_attr('System.Title') +'</td>'
                    '<td>'+ feature.get_attr('System.AssignedTo') +'</td>'
                    '<td>'+ str(completed) +'</td>'
                    '<td>'+ str(estimated) +'</td>'
                '</tr>'
                )
            list_items_csv.append([
                'task unrelated to feature',
                '',
                '',
                '',
                feature.get_attr('System.Title'),
                feature.get_attr('System.AssignedTo'),
                completed,
                estimated])

        elif detail: 
            returnHTML += (
                '<tr class="success">'
                    '<td>' + feature.get_attr('System.Title') + '</td>'
                    '<td>' + feature.get_attr('CUB.Field.Eticket') + '</td>'
                    '<td>' + feature.get_attr('CUB.Field.CostOwner') + '</td>'
                    '<td></td>'
                    '<td></td>'
                    '<td></td>'
                    '<td></td>'
                    '<td></td>'
                '</tr>'
                )
        for story in feature.get_children():
            if detail: 
                returnHTML += (
                    '<tr class="active">'
                        '<td></td>'
                        '<td></td>'
                        '<td></td>'
                        '<td>'+ story.get_attr('System.Title') +'</td>'
                        '<td></td>'
                        '<td></td>'
                        '<td></td>'
                        '<td></td>'
                    '</tr>'
                    )
            for task in story.get_children():
                try: 
                    completed = task.get_attr('Microsoft.VSTS.Scheduling.CompletedWork')
                    feature_completed += completed
                except: completed = '-'
                try: 
                    estimated = task.get_attr('Microsoft.VSTS.Scheduling.OriginalEstimate')
                    feature_estimated += estimated
                except: estimated = '-'
                if detail: 
                    returnHTML += (
                        '<tr class="active">'
                            '<td></td>'
                            '<td></td>'
                            '<td></td>'
                            '<td></td>'
                            '<td>'+ task.get_attr('System.Title') +'</td>'
                            '<td>'+ task.get_attr('System.AssignedTo') +'</td>'
                            '<td>'+ str(completed) +'</td>'
                            '<td>'+ str(estimated) +'</td>'
                        '</tr>'
                        )
                    list_items_csv.append([
                        feature.get_attr('System.Title'),
                        feature.get_attr('CUB.Field.Eticket'),
                        feature.get_attr('CUB.Field.CostOwner'),
                        story.get_attr('System.Title'),
                        task.get_attr('System.Title'),
                        task.get_attr('System.AssignedTo'),
                        completed,
                        estimated])
        if not detail:
            if feature.get_attr('System.WorkItemType') == 'Task':
                returnHTML += (
                    '<tr>'
                        '<td>' + feature.get_attr('System.Title') + '</td>'
                        '<td></td>'
                        '<td>Task unrelated to feature</td>'
                        '<td>'+ str(feature_completed) +'</td>'
                        '<td>'+ str(feature_estimated) +'</td>'
                    '</tr>'
                    )
                list_items_csv.append([
                    feature.get_attr('System.Title'),
                    '',
                    'Task unrelated to feature',
                    feature_completed,
                    feature_estimated])
            else:
                returnHTML += (
                    '<tr>'
                        '<td>' + feature.get_attr('System.Title') + '</td>'
                        '<td>' + feature.get_attr('CUB.Field.Eticket') + '</td>'
                        '<td>' + feature.get_attr('CUB.Field.CostOwner') + '</td>'
                        '<td>'+ str(feature_completed) +'</td>'
                        '<td>'+ str(feature_estimated) +'</td>'
                    '</tr>'
                    )
                list_items_csv.append([
                    feature.get_attr('System.Title'),
                    feature.get_attr('CUB.Field.Eticket'),
                    feature.get_attr('CUB.Field.CostOwner'),
                    feature_completed,
                    feature_estimated])

        elif feature.get_attr('System.WorkItemType') != 'Task':
            returnHTML += (
                '<tr class="warning">'
                    '<td></td>'
                    '<td></td>'
                    '<td></td>'
                    '<td></td>'
                    '<td></td>'
                    '<th>Total feature</th>'
                    '<th>'+ str(feature_completed) +'</th>'
                    '<th>'+ str(feature_estimated) +'</th>'
                '</tr>'
                )
    returnHTML += '</tbody></table>'
    return returnHTML

@app.route("/cost_report", methods=['GET', 'POST'])
@login_required
def cost_report():
    form = TimeForm()
    form.list_project.choices = current_user.run().get_all_projects()
    form.list_project.default = app.config['TFS_PROJECT']

    if request.method == 'POST':
        if form.export_cost_report.data:
            return excel.make_response_from_array(list_items_csv, "xls", file_name="tfs_cost_report")

        feature_dict = current_user.run().get_feature_tree(
            project= form.list_project.data, 
            from_date = form.from_date.data.strftime('%Y-%m-%d'), 
            to_date = form.to_date.data.strftime('%Y-%m-%d'))

        return render_template(
                'cost_report.html', 
                form = form, 
                data=format_report(feature_dict, form.run_detailed_report.data),
                excel_export = '<div class="col-md-2"><input class="btn btn-primary btn-block" id="export_cost_report" name="export_cost_report" type="submit" value="Export to Excel"></div>')

    return render_template('cost_report.html', form = form)
