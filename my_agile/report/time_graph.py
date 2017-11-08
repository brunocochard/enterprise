from datetime import date, timedelta

from flask_login import login_required, current_user
from flask import render_template, request

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields.html5 import DateField

from app import app
from user.management import User, load_user

import pygal
from pygal.style import LightGreenStyle

from pandas import DataFrame
import numpy as np

class TimeForm(FlaskForm):
    list_project = SelectField(u'Project')
    from_date = DateField('From date', default=date.today() - timedelta(days=30), format='%Y-%m-%d')
    to_date = DateField('To date', default=date.today(), format='%Y-%m-%d')
    run_report = SubmitField(label="Run simple report")
    run_detailed_report = SubmitField(label="Run detailed report")


@app.route("/time_graph", methods=['GET', 'POST'])
@login_required
def time_graph():
    form = TimeForm()
    form.list_project.choices = current_user.get_all_projects()
    form.list_project.default = app.config['TFS_PROJECT']
    this_month_tasks = current_user.run().get_my_activities(
        from_date = date.today().replace(day=1).strftime('%Y-%m-%d'))
    if this_month_tasks.empty:
        this_month_tasks = DataFrame([['Development', 0.0, 0.0]], columns=['Work activity', "Completed", "Remaining"]) 
    this_month_tasks = this_month_tasks.groupby(['Work activity']).agg({'Completed':np.sum, 'Remaining':np.sum})
    activities = ['Development', 'Requirement', 'Testing', 'Meeting', 'Design', 'Deployment', 'Documentation', 'Maintenance', 'Training', 'undefined']
    empty_row  = this_month_tasks.xs(this_month_tasks.index[0]).copy()
    empty_row[:] = 0.0
    for activity in activities:
        try:
            this_month_tasks.index.get_loc(activity)
        except:
            empty_row.name=activity
            this_month_tasks = this_month_tasks.append(empty_row)
    radar_chart = pygal.Radar(style=LightGreenStyle, height= 300, fill=True, legend_at_bottom=True)
    radar_chart.x_labels = list(this_month_tasks.index)
    radar_chart.add('Completed', list(this_month_tasks['Completed']))
    radar_chart.add('Remaining', list(this_month_tasks['Remaining']))
    graph_data = radar_chart.render_data_uri()

    if request.method == 'POST':
        wit_table = current_user.get_time_report(
            project = form.list_project.data,
            from_date = form.from_date.data.strftime('%Y-%m-%d'),
            to_date = form.to_date.data.strftime('%Y-%m-%d'))

        assignees = []
        completed_hours=[]
        estimated_hours=[]
        activity_hours = {}
        all_activities = {}

        for each in wit_table.get_children():
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
                bar_chart.x_labels = assignees
                bar_chart.add('completed', completed_hours)
                bar_chart.add('estimated', estimated_hours)

                graph_data = bar_chart.render_data_uri()
                return render_template(
                        "time_graph.html", 
                        form = form,
                        graph_data = graph_data)
            else:
                dot_chart = pygal.Dot(
                	x_label_rotation=30,
                	style=LightGreenStyle,
                	height= 35*len(all_activities),
                	show_legend=False)
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
        return render_template('time_graph.html', form = form, graph_data = graph_data)    
