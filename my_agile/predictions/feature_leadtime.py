from datetime import datetime, date
import pandas as pd
import numpy as np
import pickle
import itertools

from keras import losses

from flask_login import login_required, current_user
from flask import render_template, request

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

import pygal
from pygal.style import LightGreenStyle

from app import app
from user.management import User, load_user
from predictions import feature_learning

class RequestForm(FlaskForm):
    title = StringField('Request title')
    description = StringField('description')
    list_project = SelectField(u'Project')
    create_request = SubmitField(label="Create new request")
    confidence = ''
    
@app.route("/feature_leadtime", methods=['GET', 'POST'])
@login_required
def feature_leadtime():
    form = RequestForm()
    form.list_project.choices = current_user.get_all_projects()
    data_file = 'Credit Card-2017-08-22.csv'
    clf_type = None #"nn"
    clf_file = 'linearRegression-2017-08-22-test.pickle'
    clf_columns = ['created_size_feature_backlog', 'created_size_ongoing_feature_backlog', 'created_size_story_backlog', 'created_size_ongoing_story_backlog', 'created_size_ongoing_task_backlog', 'activated_size_ongoing_feature_backlog', 'activated_size_ongoing_story_backlog', 'activated_size_task_backlog', 'activated_size_ongoing_task_backlog', 'ActivationTime']
    clf_columns.append('CompletionTime')
    project = 'EBTNTB2C04-MyBank'
    training_time = date.today().strftime('%Y-%m-%d')
    na_value = -99999
    na_string = str(na_value)

    if data_file:
        print("==== Retrieving data from CSV ====")
        feature_data = pd.DataFrame.from_csv(data_file)

    else:
        print("==== Retrieving data from TFS ====")
        feature_data = feature_learning.get(
                project = project,
                from_date = '2017-02-01',
                wit_type = 'Feature',
                state = 'Closed')
        feature_data = feature_learning.add_backlog_size(feature_data)

        if not project: 
            project = 'all'
        feature_data.to_csv(project+'-'+ training_time +'.csv')

    feature_data = feature_learning.remove_na(feature_data)

    print("==== Building dataset ====")
    feature_data = feature_learning.transform(feature_data)
    if clf_type:
        feature_train_data = feature_learning.sample(frac=0.8, random_state=1)
        feature_test_data = feature_learning.drop(feature_train_data.index)

#TODO split train/test for X, Y with feature_learning.split(feature_data)
        df_examples, df_label = feature_learning.split(feature_data)
        X, Y = np.array(df_examples, ndmin=2), np.array(df_label, ndmin=2).T
        X_train, X_test, Y_train, Y_test = cross_validation.train_test_split(X, Y, test_size=0.2)
        # parameters, costs = feature_learning.train_network(X_train.T, Y_train.T)
        # predictions, cost = feature_learning.test_network(X.T, Y.T, parameters)
        # feature_data['Forecast'] = predictions.T
        num_iterations = 50000
        print_step = 5000
        learning_rates = [0.0001, 0.0005, 0.001, 0.003, 0.05]
        # parameters0, costs0 = feature_learning.train_network(X_train.T, Y_train.T, num_iterations = num_iterations, print_step = print_step, learning_rate = learning_rates[1], n_h1 = 14, n_h2 = 7)
        # parameters1, costs1 = feature_learning.train_network(X_train.T, Y_train.T, num_iterations = num_iterations, print_step = print_step, learning_rate = learning_rates[1], n_h1 = 14, n_h2 = 14)
        # parameters2, costs2 = feature_learning.train_network(X_train.T, Y_train.T, num_iterations = num_iterations, print_step = print_step, learning_rate = learning_rates[1], n_h1 = 28, n_h2 = 12)
        parameters3, costs3 = feature_learning.train_network(X_train.T, Y_train.T, num_iterations = num_iterations, print_step = print_step, learning_rate = learning_rates[1], n_h1 = 28, n_h2 = 14)
        # parameters4, costs4 = feature_learning.train_network(X_train.T, Y_train.T, num_iterations = num_iterations, print_step = print_step, learning_rate = learning_rates[1], n_h1 = 28, n_h2 = 16)
        cost_chart = pygal.Line(style=LightGreenStyle, legend_at_bottom=True)
        cost_chart.title = "cost by iterations"
        cost_chart.x_labels = map(str, range(num_iterations/print_step))
        # cost_chart.add('test 0', costs0)
        # cost_chart.add('test 1', costs1)
        # cost_chart.add('test 2', costs2)
        cost_chart.add('test 3', costs3)
        # cost_chart.add('test 4', costs4)
        predictions, cost = feature_learning.test_network(X.T, Y.T, parameters3)
        feature_data['Forecast'] = predictions.T

        form.confidence += "achieved mean_squared_error of of %s <BR>"%str(losses.mean_squared_error(Y, predictions.T,))
        form.confidence += "achieved mean_absolute_error of %s <BR>"%str(losses.mean_absolute_error(Y, predictions.T))
        graph_data = cost_chart.render_data_uri()
        return render_template(
            'feature_leadtime.html', 
            form = form, 
            data=feature_data.to_html(classes='time'),
            graph_data = graph_data)

    if clf_file:
        print("==== Testing loaded classifier ====")
        training = feature_learning.validate(clf_file, feature_data[clf_columns])
        
        feature_data['Forecast'] = training['forecast']
        form.confidence += "achieved confidence of %s <BR>"%str(training['confidence'])
        form.confidence += "achieved variance of of %s <BR>"%str(training['variance'])
        form.confidence += "achieved absolute error of of %s <BR>"%str(training['mean_square_error'])
        form.confidence += "achieved squared of of %s <BR>"%str(training['mean_absolute_error'])
        return render_template(
            'feature_leadtime.html', 
            form = form, 
            data=feature_data.to_html(classes='time'))

    #shuffle rows
    df_examples, df_label = feature_learning.split(feature_data)
    best_linear_training = feature_learning.train_linear_combination(df_examples, df_label)

    form.confidence = "Best confidence achieved of %s for combination of %s"%(
        str(best_linear_training['best_confidence']),
        str(best_linear_training['best_combination']))

    with open('linearRegression-'+ training_time + '-test.pickle', 'wb') as f:
        best_clf.fit(np.array(df_examples), np.array(df_label))
        pickle.dump(best_linear_training['best_clf'], f)

    return render_template('feature_leadtime.html', form = form, data=feature_data.to_html(classes='time'))
