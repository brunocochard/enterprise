import pandas as pd
from flask_login import current_user


def create(feature_dict):
    feature_df = feature_dict.to_dataframe()
    feature_df = wit_df.drop('url', 1)
    feature_df = wit_df.drop('System.Id', 1)
    feature_df = wit_df.set_index('id')
    return feature_df

def add_backlog_size(feature_df)
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
        print("==== Computing backlog size asOf - item %s / %s ===="%(index))
        feature_df.set_value(index, 'created_size_feature_backlog', current_user.run().get_backlog_size(
            as_of_date = row['System.CreatedDate'],
            area_path = row['System.AreaPath'],
            wit_type = 'Feature'))
        feature_df.set_value(index, 'created_size_ongoing_feature_backlog', current_user.run().get_backlog_size(
            as_of_date = row['System.CreatedDate'], 
            area_path = row['System.AreaPath'],
            wit_type = 'Feature',
            new = False))
        feature_df.set_value(index, 'created_size_story_backlog', current_user.run().get_backlog_size(
            as_of_date = row['System.CreatedDate'], 
            area_path = row['System.AreaPath'],
            wit_type = 'User Story'))
        feature_df.set_value(index, 'created_size_ongoing_story_backlog', current_user.run().get_backlog_size(
            as_of_date = row['System.CreatedDate'], 
            area_path = row['System.AreaPath'],
            wit_type = 'User Story',
            new = False))
        feature_df.set_value(index, 'created_size_task_backlog', current_user.run().get_backlog_size(
            as_of_date = row['System.CreatedDate'], 
            assigned_to = row['System.AssignedTo'],
            wit_type = 'Task'))
        feature_df.set_value(index, 'created_size_ongoing_task_backlog', current_user.run().get_backlog_size(
            as_of_date = row['System.CreatedDate'], 
            assigned_to = row['System.AssignedTo'],
            wit_type = 'Task',
            new = False))
        feature_df.set_value(index, 'activated_size_feature_backlog', current_user.run().get_backlog_size(
            as_of_date = row['Microsoft.VSTS.Common.ActivatedDate'], 
            area_path = row['System.AreaPath'],
            wit_type = 'Feature'))
        feature_df.set_value(index, 'activated_size_ongoing_feature_backlog', current_user.run().get_backlog_size(
            as_of_date = row['Microsoft.VSTS.Common.ActivatedDate'], 
            area_path = row['System.AreaPath'],
            wit_type = 'Feature',
            new = False))
        feature_df.set_value(index, 'activated_size_story_backlog', current_user.run().get_backlog_size(
            as_of_date = row['Microsoft.VSTS.Common.ActivatedDate'], 
            area_path = row['System.AreaPath'],
            wit_type = 'User Story'))
        feature_df.set_value(index, 'activated_size_ongoing_story_backlog', current_user.run().get_backlog_size(
            as_of_date = row['Microsoft.VSTS.Common.ActivatedDate'], 
            area_path = row['System.AreaPath'],
            wit_type = 'User Story',
            new = False))
        feature_df.set_value(index, 'activated_size_task_backlog', current_user.run().get_backlog_size(
            as_of_date = row['Microsoft.VSTS.Common.ActivatedDate'], 
            assigned_to = row['System.AssignedTo'],
            wit_type = 'Task'))
        feature_df.set_value(index, 'activated_size_ongoing_task_backlog', current_user.run().get_backlog_size(
            as_of_date = row['Microsoft.VSTS.Common.ActivatedDate'], 
            assigned_to = row['System.AssignedTo'],
            wit_type = 'Task',
            new = False))
    feature_df.replace('undefined', np.nan)
    feature_df.dropna(inplace=True)
    feature_df.fillna(na_value, inplace=True)
