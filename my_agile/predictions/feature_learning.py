import pandas as pd
import numpy as np
import pickle
from datetime import datetime, date
import time
from keras.layers.normalization import BatchNormalization
from flask_login import current_user
from sklearn import svm
from sklearn.metrics import explained_variance_score, mean_squared_error, mean_absolute_error

NA_VALUE = -99999
NA_STR = str(NA_VALUE)

def get(project = None, from_date = '2017-02-01', wit_type = 'Feature', state = 'Closed'):
	feature_dict = current_user.run().get_all_wit(
	    project = project,
	    from_date = from_date,
	    wit_type = wit_type,
	    state = state)
	feature_df = feature_dict.to_dataframe()
	feature_df = feature_df.drop('url', 1)
	feature_df = feature_df.drop('System.Id', 1)
	feature_df = feature_df.set_index('id')
	return feature_df

def add_backlog_size(feature_df):
    feature_df['created_size_feature_backlog'] = 0
    feature_df['created_size_ongoing_feature_backlog'] = 0
    feature_df['created_size_story_backlog'] = 0
    feature_df['created_size_ongoing_story_backlog'] = 0
    feature_df['created_size_task_backlog'] = 0
    feature_df['created_size_ongoing_task_backlog'] = 0
    feature_df['activated_size_feature_backlog'] = 0
    feature_df['activated_size_ongoing_feature_backlog'] = 0
    feature_df['activated_size_story_backlog'] = 0
    feature_df['activated_size_ongoing_story_backlog'] = 0
    feature_df['activated_size_task_backlog'] = 0
    feature_df['activated_size_ongoing_task_backlog'] = 0

    for index, row in feature_df.iterrows():
        print("==== Computing backlog size asOf - item %s ===="%(index))
        feature_df.set_value(index, 'created_size_feature_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['System.CreatedDate']),
            area_path = str(row['System.AreaPath']),
            wit_type = 'Feature'))
        feature_df.set_value(index, 'created_size_ongoing_feature_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['System.CreatedDate']), 
            area_path = str(row['System.AreaPath']),
            wit_type = 'Feature',
            new = False))
        feature_df.set_value(index, 'created_size_story_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['System.CreatedDate']), 
            area_path = str(row['System.AreaPath']),
            wit_type = 'User Story'))
        feature_df.set_value(index, 'created_size_ongoing_story_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['System.CreatedDate']), 
            area_path = str(row['System.AreaPath']),
            wit_type = 'User Story',
            new = False))
        feature_df.set_value(index, 'created_size_task_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['System.CreatedDate']), 
            assigned_to = str(row['System.AssignedTo']),
            wit_type = 'Task'))
        feature_df.set_value(index, 'created_size_ongoing_task_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['System.CreatedDate']), 
            assigned_to = str(row['System.AssignedTo']),
            wit_type = 'Task',
            new = False))
        feature_df.set_value(index, 'activated_size_feature_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['Microsoft.VSTS.Common.ActivatedDate']), 
            area_path = str(row['System.AreaPath']),
            wit_type = 'Feature'))
        feature_df.set_value(index, 'activated_size_ongoing_feature_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['Microsoft.VSTS.Common.ActivatedDate']), 
            area_path = str(row['System.AreaPath']),
            wit_type = 'Feature',
            new = False))
        feature_df.set_value(index, 'activated_size_story_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['Microsoft.VSTS.Common.ActivatedDate']), 
            area_path = str(row['System.AreaPath']),
            wit_type = 'User Story'))
        feature_df.set_value(index, 'activated_size_ongoing_story_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['Microsoft.VSTS.Common.ActivatedDate']), 
            area_path = str(row['System.AreaPath']),
            wit_type = 'User Story',
            new = False))
        feature_df.set_value(index, 'activated_size_task_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['Microsoft.VSTS.Common.ActivatedDate']), 
            assigned_to = str(row['System.AssignedTo']),
            wit_type = 'Task'))
        feature_df.set_value(index, 'activated_size_ongoing_task_backlog', current_user.run().get_backlog_size(
            as_of_date = str(row['Microsoft.VSTS.Common.ActivatedDate']), 
            assigned_to = str(row['System.AssignedTo']),
            wit_type = 'Task',
            new = False))
    feature_df.replace('undefined', np.nan)
    feature_df.dropna(inplace=True)
    feature_df.fillna(NA_VALUE, inplace=True)
    return feature_df

def remove_na(feature_df):
	feature_df = feature_df.replace(to_replace='undefined', value=np.nan)
	feature_df = feature_df.replace(to_replace=NA_STR, value=np.nan)
	feature_df = feature_df.dropna(axis=0)
	return feature_df

def transform(feature_df):
	feature_df['StartDate'] = datetime.strptime('2017-02-01 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')

	feature_df['CreatedDate'] = pd.to_datetime(feature_df['System.CreatedDate'], format="%Y-%m-%d")
	feature_df = feature_df.drop('System.CreatedDate', 1)

	feature_df['ActivatedDate'] = pd.to_datetime(feature_df['Microsoft.VSTS.Common.ActivatedDate'], format="%Y-%m-%d")
	feature_df = feature_df.drop('Microsoft.VSTS.Common.ActivatedDate', 1)

	feature_df['ClosedDate'] = pd.to_datetime(feature_df['Microsoft.VSTS.Common.ClosedDate'], format="%Y-%m-%d")
	feature_df = feature_df.drop('Microsoft.VSTS.Common.ClosedDate', 1)

	feature_df = pd.concat([feature_df, pd.get_dummies(feature_df['System.TeamProject'])], axis=1)
	feature_df = pd.concat([feature_df, pd.get_dummies(feature_df['System.AreaPath'])], axis=1)
	feature_df = pd.concat([feature_df, pd.get_dummies(feature_df['System.AssignedTo'])], axis=1)

	feature_df['ActivationTime'] = (feature_df['ActivatedDate'] - feature_df['CreatedDate']).dt.days
	feature_df['ActivationTime'] = np.ceil(feature_df['ActivationTime']/7)
	feature_df['timefromstart'] = (feature_df['CreatedDate'] - feature_df['StartDate']).dt.days
	feature_df['timefromstart'] = np.ceil(feature_df['timefromstart']/7)
	feature_df['CompletionTime'] = (feature_df['ClosedDate'] - feature_df['CreatedDate']).dt.days
	feature_df['CompletionTime'] = np.ceil(feature_df['CompletionTime']/7)

	feature_df = feature_df.drop(['System.AreaPath','System.TeamProject', 'System.AssignedTo'], 1)
	feature_df = feature_df.drop(['StartDate','CreatedDate','ActivatedDate','ClosedDate'], 1)

	return feature_df

def split(feature_data):
	feature_data = feature_data.iloc[np.random.permutation(len(feature_data))]
	# split_index = round(len(feature_data)*ratio)

	df_examples = feature_data.drop(['CompletionTime'], 1)
	df_label = feature_data['CompletionTime']

	return df_examples, df_label

def train_linear_combination(df_examples, df_label):
	best_confidence = 0
	best_combination = ()
	X_columns = list(df_examples.columns)
	for i in range(1, len(X_columns)+1):
		col_combination = list(itertools.combinations(X_columns,i))
		for combination in col_combination:
			df_X_iter = df_examples
			for col in X_columns:
				if col not in combination:
					df_X_iter = df_X_iter.drop(col, 1)
			feature_train_data = df_examples.sample(frac=0.8, random_state=1)
        	feature_test_data = df_examples.drop(feature_train_data.index)
#TODO split X and Y  with feature_learning.split(feature_data)
			X, y = np.array(df_X_iter), np.array(df_label)
			X = BatchNormalization()

			print '.',
			clf = svm.SVR(kernel = 'linear')
			clf.fit(X_train, y_train)

			confidence = clf.score(X_test, y_test)
			if confidence > best_confidence:
				best_confidence = confidence
				best_combination = combination
				best_clf = clone(clf)
				print("found new best confidence of %s with columns %s"%(str(best_confidence), str(best_combination)))
				print("Combination columns = %s"%str(X_train.shape[1]))
	return dict(
		best_confidence= best_confidence,
		best_combination= best_combination,
		best_clf= best_clf
		)

def validate(filename, feature_data):
	clf = pickle.load(open(filename, 'rb'))

	X = np.array(feature_data.drop('CompletionTime', 1))
	y = np.array(feature_data['CompletionTime'])
	X = preprocessing.scale(X)
	forecast = clf.predict(X)

	return dict(
		forecast= forecast,
		confidence= clf.score(X, y),
		variance= explained_variance_score(y, forecast, multioutput = 'uniform_average'),
		mean_square_error= mean_squared_error(y, forecast, multioutput = 'uniform_average'),
		mean_absolute_error= mean_absolute_error(y, forecast, multioutput = 'uniform_average')
		)

def layer_sizes(X, hidden1, hidden2, Y):
	"""
	Arguments:
	X -- input dataset of shape (input size, number of examples)
	Y -- labels of shape (output size, number of examples)

	Returns:
	n_x -- the size of the input layer
	n_h -- the size of the hidden layer
	n_y -- the size of the output layer
	"""

	n_x = X.shape[0] # size of input layer
	n_h1 = hidden1
	n_h2 = hidden2
	n_y = Y.shape[0] # size of output layer

	return (n_x, n_h1, n_h2, n_y)

def initialize_parameters(n_x, n_h1, n_h2, n_y):
	"""
	Argument:
	n_x -- size of the input layer
	n_h -- size of the hidden layer
	n_y -- size of the output layer

	Returns:
	params -- python dictionary containing your parameters:
	            W1 -- weight matrix of shape (n_h, n_x)
	            b1 -- bias vector of shape (n_h, 1)
	            W2 -- weight matrix of shape (n_y, n_h)
	            b2 -- bias vector of shape (n_y, 1)
	"""

	W1 = np.random.randn(n_h1, n_x)*0.01
	b1 = np.zeros((n_h1, 1))
	W2 = np.random.randn(n_h2, n_h1)*0.01
	b2 = np.zeros((n_h2, 1))
	W3 = np.random.randn(n_y, n_h2)*0.01
	b3 = np.zeros((n_y, 1))

	assert (W1.shape == (n_h1, n_x))
	assert (b1.shape == (n_h1, 1))
	assert (W2.shape == (n_h2, n_h1))
	assert (b2.shape == (n_h2, 1))	
	assert (W3.shape == (n_y, n_h2))
	assert (b3.shape == (n_y, 1))

	parameters = {
		"W1": W1,
		"b1": b1,
		"W2": W2,
		"b2": b2,
		"W3": W3,
		"b3": b3}

	return parameters

def forward_propagation(X, parameters):
	"""
	Argument:
	X -- input data of size (n_x, m)
	parameters -- python dictionary containing your parameters (output of initialization function)

	Returns:
	A2 -- The linear output of the second activation
	cache -- a dictionary containing "Z1", "A1", "Z2" and "A2"
	"""
	# Retrieve each parameter from the dictionary "parameters"
	W1 = parameters['W1']
	b1 = parameters['b1']
	W2 = parameters['W2']
	b2 = parameters['b2']
	W3 = parameters['W3']
	b3 = parameters['b3']

	# Implement Forward Propagation to calculate A2 (probabilities)
	Z1 = np.dot(W1, X) + b1
	A1 = np.tanh(Z1)
	Z2 = np.dot(W2, A1) + b2
	A2 = np.tanh(Z2)
	Z3 = np.dot(W3, A2) + b3
	A3 = Z3

	assert(A3.shape == (1, X.shape[1]))

	cache = {"Z1": Z1,
		 "A1": A1,
		 "Z2": Z2,
		 "A2": A2,
		 "Z3": Z3,
		 "A3": A3}

	return A3, cache

def compute_cost(A3, Y, parameters):
	"""
	Computes the cross-entropy cost given in equation (13)

	Arguments:
	A2 -- The sigmoid output of the second activation, of shape (1, number of examples)
	Y -- "true" labels vector of shape (1, number of examples)
	parameters -- python dictionary containing your parameters W1, b1, W2 and b2

	Returns:
	cost -- cross-entropy cost given equation (13)
	"""

	m = Y.shape[1] # number of example

	# Compute the cross-entropy cost
	logprobs = None
	# cost = float((mean_squared_error(Y_train.T,predictions.T)**0.5)/float(Y_train.size)*100)
	cost = np.sum((Y-A3)**2)/m
	# cost = -1/m*np.sum(np.multiply(Y, np.log(A2)) + np.multiply((1-Y), np.log(1-A2)))

	cost = np.squeeze(cost)     # makes sure cost is the dimension we expect. 
	                            # E.g., turns [[17]] into 17 
	assert(isinstance(cost, float))

	return cost

def backward_propagation(parameters, cache, X, Y):
	"""
	Implement the backward propagation using the instructions above.

	Arguments:
	parameters -- python dictionary containing our parameters 
	cache -- a dictionary containing "Z1", "A1", "Z2" and "A2".
	X -- input data of shape (2, number of examples)
	Y -- "true" labels vector of shape (1, number of examples)

	Returns:
	grads -- python dictionary containing your gradients with respect to different parameters
	"""
	m = X.shape[1]

	# First, retrieve W1 and W2 from the dictionary "parameters".
	W1 = parameters['W1']
	W2 = parameters['W2']
	W3 = parameters['W3']
	    
	# Retrieve also A1 and A2 from dictionary "cache".
	A1 = cache['A1']
	A2 = cache['A2']
	A3 = cache['A3']

	# Backward propagation: calculate dW1, db1, dW2, db2. 
	dZ3= A3-Y
	dW3 = np.dot(dZ3,A2.T)/m
	db3 = np.sum(dZ3, axis = 1, keepdims = True)/m
	dZ2 = np.multiply(np.dot(W3.T, dZ3), 1-np.power(A2, 2))
	dW2 = np.dot(dZ2, A1.T)/m
	db2 = np.sum(dZ2, axis = 1, keepdims = True)/m
	dZ1 = np.multiply(np.dot(W2.T, dZ2), 1-np.power(A1, 2))
	dW1 = np.dot(dZ1, X.T)/m
	db1 = np.sum(dZ1, axis = 1, keepdims = True)/m

	grads = {"dW1": dW1,
		 "db1": db1,
		 "dW2": dW2,
		 "db2": db2,
		 "dW3": dW3,
		 "db3": db3}
	return grads

def update_parameters(parameters, grads, learning_rate = 0.1):
	"""
	Updates parameters using the gradient descent update rule given above

	Arguments:
	parameters -- python dictionary containing your parameters 
	grads -- python dictionary containing your gradients 

	Returns:
	parameters -- python dictionary containing your updated parameters 
	"""
	# Retrieve each parameter from the dictionary "parameters"
	W1 = parameters['W1']
	b1 = parameters['b1']
	W2 = parameters['W2']
	b2 = parameters['b2']
	W3 = parameters['W3']
	b3 = parameters['b3']

	# Retrieve each gradient from the dictionary "grads"
	dW1 = grads['dW1']
	db1 = grads['db1']
	dW2 = grads['dW2']
	db2 = grads['db2']
	dW3 = grads['dW3']
	db3 = grads['db3']

	# Update rule for each parameter
	W1 = W1 - learning_rate*dW1
	b1 = b1 - learning_rate*db1
	W2 = W2 - learning_rate*dW2
	b2 = b2 - learning_rate*db2
	W3 = W3 - learning_rate*dW3
	b3 = b3 - learning_rate*db3

	parameters = {"W1": W1,
		"b1": b1,
		"W2": W2,
		"b2": b2,
		"W3": W3,
		"b3": b3}

	return parameters

def nn_model(X, Y, n_h1, n_h2, num_iterations = 10000, print_cost=False, print_step = 1000, learning_rate = 0.1):
	"""
	Arguments:
	X -- dataset of shape (2, number of examples)
	Y -- labels of shape (1, number of examples)
	n_h -- size of the hidden layer
	num_iterations -- Number of iterations in gradient descent loop
	print_cost -- if True, print the cost every 1000 iterations

	Returns:
	parameters -- parameters learnt by the model. They can then be used to predict.
	"""
	n_x = layer_sizes(X, n_h1, n_h2, Y)[0]
	n_y = layer_sizes(X, n_h1, n_h2, Y)[3]

	# Initialize parameters, then retrieve W1, b1, W2, b2. Inputs: "n_x, n_h, n_y". Outputs = "W1, b1, W2, b2, parameters".
	parameters = initialize_parameters(n_x, n_h1, n_h2, n_y)
	W1 = parameters['W1']
	b1 = parameters['b1']
	W2 = parameters['W2']
	b2 = parameters['b2']
	W3 = parameters['W3']
	b3 = parameters['b3']

	# Loop (gradient descent)
	costs = []
	for i in range(0, num_iterations):
		# Forward propagation. Inputs: "X, parameters". Outputs: "A2, cache".
		A3, cache = forward_propagation(X, parameters)

		# Cost function. Inputs: "A2, Y, parameters". Outputs: "cost".
		cost = compute_cost(A3, Y, parameters)
		if cost>1000: break
		# Backpropagation. Inputs: "parameters, cache, X, Y". Outputs: "grads".
		grads = backward_propagation(parameters, cache, X, Y)

		# Gradient descent parameter update. Inputs: "parameters, grads". Outputs: "parameters".
		parameters = update_parameters(parameters, grads, learning_rate)

		# Print the cost every 1000 iterations
		
		if print_cost and i % print_step == 0:
			print ("Cost after iteration %i: %f" %(i, cost))
			costs.append(cost)
			# print ("grads after iteration %i: %s" %(i, str(grads)))

	return parameters, costs

def predict(parameters, X):
	"""
	Using the learned parameters, predicts a class for each example in X

	Arguments:
	parameters -- python dictionary containing your parameters 
	X -- input data of size (n_x, m)

	Returns
	predictions -- vector of predictions of our model (red: 0 / blue: 1)
	"""

	# Computes probabilities using forward propagation, and classifies to 0/1 using 0.5 as the threshold.
	predictions, cache = forward_propagation(X, parameters)

	return predictions

def train_network(X_train, Y_train, num_iterations = 10000, print_step = 1000, learning_rate = 0.1, n_h1 = 14, n_h2 = 5):
	parameters, costs = nn_model(
		X_train, Y_train, 
		n_h1 = n_h1, n_h2 = n_h2, 
		num_iterations = num_iterations, 
		print_cost=True, 
		print_step = print_step, 
		learning_rate = learning_rate)
	predictions = predict(parameters, X_train)
	cost = compute_cost(predictions, Y_train, parameters)
	
	print ('Accuracy: %d' % cost + '%')
	return parameters, costs

def test_network(X_test, Y_test, parameters):
	predictions = predict(parameters, X_test)
	cost = compute_cost(predictions, Y_test, parameters)
	
	print ('Accuracy: %d' % cost + '%')
	return predictions, cost

# def validate_network(X, Y,num_iterations = 10000, num_records=20):
# 	split_index = np.ceil(X.size*0.8)
# 	X_split = np.vsplit(X, split_index)
# 	X_train, X_test = X_split[0],X_split[1]
# 	Y_split = np.vsplit(Y, split_index)
# 	Y_train, Y_test = Y_split[0],Y_split[1]

# 	for i in range(0, 20):
# 		parameters, cost_train[i] = train_network(X_train, Y_train)
# 		predictions, cost_test[i] = test_network(X_test, Y_test, parameters)

import keras
from keras.models import Sequential
from kera.layers import Dense, Dropout, Activation

def keras_model(feature_dataframe):
	model = Sequential()

	# 1st layer
	model.add(Dense(64, input_dim=4, init='uniform'))
	model.add(BatchNormalization())
	model.add(Dropout())
	model.add(Activation('relu'))

	# 2nd layer
	model.add(Dense(64, init='uniform'))
	model.add(BatchNormalization())
	model.add(Activation('relu'))

	# Output layer
	model.add(Dense(64, init='uniform'))
	model.add(BatchNormalization())
	model.add(Activation('softmax'))

	gradient_descent = SGD(lr=0.01, decaty=1e-6, momumtum=0.9)
	model.compile(loss='', optimizer=gradient_descent)

	model.fit(X_train, Y_train, nb_epoch=10, batch_size=16, show_accuracy=True, validation_split=0.2)
