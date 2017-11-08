import requests

from requests_ntlm import HttpNtlmAuth

from pandas import DataFrame     
import numpy as np 

from tfs.wit import Wit
from tfs.wiql import Query

from app import app

class TFS_session(object):
    def __init__(self, username, password, server, collection = 'DefaultCollection'):
        self.session = requests.Session()
        self.username = username
        self.server = server
        self.session.auth = HttpNtlmAuth(username, password, self.session)
        self.collection = collection
        self.url = self.server + "tfs/" + self.collection + "/"
        self.admin = None

    def is_connected(self):
        return self.session.get(self.url).ok

    def is_admin(self):
        if self.admin is None:
            try:
                self.admin = False
                members = self.get_members(project='ALM Project', team='ALM Admin Team')
                if self.username in members.keys():
                    self.admin = True
                    return self.admin
            except: pass
        return self.admin

    def get_my_profile(self):
        profile_url = self.server + 'tfs/_apis/profile/profiles/me?api-version=1.0'
        response = self.session.get(profile_url)
        return response.json()

    def close(self):
        return self.session.close()

    def get_all_projects(self):
        tfs_api = self.url + '_apis/projects?api-version=2.0'
        response = self.session.get(tfs_api)
        projectList = []
        
        if(response.ok):
            response = response.json()
            for project in response.values()[1]:
                projectList.append((project['name'],project['name']))
        else:
            response.raise_for_status()
            
        return projectList

    def get_epics(self, project):
        tfs_api = self.url + project + '/_apis/wit/wiql?api-version=1.0'
        query = Query("WorkItems")
        query.select('System.Title')
        query.select('System.State')
        query.select('Microsoft.VSTS.Common.ClosedDate')
        query.select('System.AreaPath')
        query.where('System.WorkItemType', '=', 'Epic')
        query.where('System.TeamProject', '=', project)
        query.orderby('Microsoft.VSTS.Common.ClosedDate')

        response = self.session.post(url=tfs_api, json={"query": str(query)})
            
        if(response.ok):
            response = response.json()
            attributes = ""
            id_string = ""
            num_id = 0
            for col in response["columns"]:
                attributes += col['referenceName'] + ","
            for i, col in enumerate(response["workItems"]):
                id_string += str(col['id']) + ","
                if i >= 100:
                    break
            query_api = (self.url + 
                "_apis/wit/WorkItems?ids=" + id_string[:-1] +
                "&fields=" + attributes[:-1] +
                "&asOf=" + response["asOf"] + 
                "&api-version=1.0")
            
            wit_response = self.session.get(query_api)

            return wit_response.json()
        else:
            response.raise_for_status()

    def get_my_activities(self, state = None, from_date = None):
        tfs_api = self.url + '_apis/wit/wiql?api-version=1.0'

        query = Query("WorkItems")
        query.select('System.Id')
        query.select('System.Title')
        query.select('System.State')
        query.select('System.TeamProject')
        query.select('Microsoft.VSTS.Common.Activity')
        query.select('System.Description')
        query.select('Microsoft.VSTS.Scheduling.OriginalEstimate')
        query.select('Microsoft.VSTS.Scheduling.CompletedWork')
        query.select('Microsoft.VSTS.Scheduling.RemainingWork')
        query.where('System.WorkItemType', '=', 'Task')
        if state:
            query.where('System.State', '=', state)
        query.where('System.AssignedTo', '=', '@me')
        if from_date:
            query.where('System.CreatedDate', '>=', from_date)
        query.orderby('Microsoft.VSTS.Common.Activity', 'asc')

        response = self.session.post(url=tfs_api, json={"query": str(query)})
        wit_dataframe = DataFrame(
                columns=[
                'System.Id', 
                "System.Title",
                "System.TeamProject",
                'Microsoft.VSTS.Common.Activity', 
                "System.Description",
                'Microsoft.VSTS.Scheduling.OriginalEstimate',
                'Microsoft.VSTS.Scheduling.CompletedWork',
                'Microsoft.VSTS.Scheduling.RemainingWork'])   
        if(response.ok):
            response = response.json()
            
            attributes = ""
            for col in response["columns"]:
                attributes += col['referenceName'] + ","
                
            id_string = ['']
            query_num = 0
            for i, col in enumerate(response["workItems"]):
                id_string[query_num] += str(col['id']) + ","
                if i != 0 and i % 100 == 0: 
                    query_num +=1
                    id_string.append('')
            
            for substring in id_string:
                query_api = (self.url + 
                            "_apis/wit/WorkItems?ids=" + substring[:-1] +
                            "&fields=" + attributes[:-1] +
                            "&asOf=" + response["asOf"] + 
                            "&api-version=1.0")
                query_response = self.session.get(query_api).json()
                if 'Message' in query_response["value"]: 
                    wit_dataframe = wit_dataframe.rename(columns={
                        'System.Id': 'Id', 
                        'System.Title': 'Title', 
                        'System.State': 'State', 
                        'System.TeamProject': 'Project',
                        'Microsoft.VSTS.Common.Activity': 'Work activity', 
                        'System.Description': 'Description', 
                        'Microsoft.VSTS.Scheduling.OriginalEstimate': 'Estimated',
                        'Microsoft.VSTS.Scheduling.CompletedWork': 'Completed',
                        'Microsoft.VSTS.Scheduling.RemainingWork': 'Remaining'})
                    return wit_dataframe
                for i, each in enumerate(query_response["value"]):
                    wit_dataframe = wit_dataframe.append(each['fields'], ignore_index=True)
            
            wit_dataframe = wit_dataframe.rename(columns={
                    'System.Id': 'Id', 
                    'System.Title': 'Title', 
                    'System.State': 'State', 
                    'System.TeamProject': 'Project',
                    'Microsoft.VSTS.Common.Activity': 'Work activity', 
                    'System.Description': 'Description', 
                    'Microsoft.VSTS.Scheduling.OriginalEstimate': 'Estimated',
                    'Microsoft.VSTS.Scheduling.CompletedWork': 'Completed',
                        'Microsoft.VSTS.Scheduling.RemainingWork': 'Remaining'})
            wit_dataframe['Completed'] = wit_dataframe['Completed'].fillna(0)
            wit_dataframe['Estimated'] = wit_dataframe['Estimated'].fillna(0)
            wit_dataframe['Remaining'] = wit_dataframe['Remaining'].fillna(0)
            wit_dataframe['Work activity'] = wit_dataframe['Work activity'].fillna('undefined')
            wit_dataframe['Title'] = wit_dataframe['Title'].fillna('Not assigned')
            wit_dataframe['State'] = wit_dataframe['State'].fillna('undefined')
            wit_dataframe['Project'] = wit_dataframe['Project'].fillna('Not assigned')
            wit_dataframe['Description'] = wit_dataframe['Description'].fillna('Not defined')
            return wit_dataframe

        else:
            response.raise_for_status()

  
    def get_activities(self,project, from_date, to_date, detail=False):
        tfs_api = self.url + project + '/_apis/wit/wiql?api-version=1.0'

        query = Query("WorkItems")
        query.select('System.AssignedTo')
        query.select('Microsoft.VSTS.Common.Activity')
        query.select('Microsoft.VSTS.Scheduling.OriginalEstimate')
        query.select('Microsoft.VSTS.Scheduling.CompletedWork')
        query.where('System.WorkItemType', '=', 'Task')
        query.where('System.TeamProject', '=', '@project')
        query.where('Microsoft.VSTS.Common.ClosedDate', '>=', from_date)
        query.where('Microsoft.VSTS.Common.ClosedDate', '<=', to_date)
        query.orderby('System.AssignedTo', 'asc')

        response = self.session.post(url=tfs_api, json={"query": str(query)})

        wit_dataframe = DataFrame(
                columns=[
                'System.AssignedTo', 
                'Microsoft.VSTS.Common.Activity', 
                'Microsoft.VSTS.Scheduling.CompletedWork',
                'Microsoft.VSTS.Scheduling.OriginalEstimate'])
        if(response.ok):
            response = response.json()
            if not len(response["workItems"]):
                wit_dataframe = wit_dataframe.rename(columns={
                    'System.AssignedTo': 'Employee', 
                    'Microsoft.VSTS.Common.Activity': 'Work activity', 
                    'Microsoft.VSTS.Scheduling.CompletedWork': 'Completed hours',
                    'Microsoft.VSTS.Scheduling.OriginalEstimate': 'Estimated'})
                return wit_dataframe

            attributes = ""
            for col in response["columns"]:
                attributes += col['referenceName'] + ","
                
            id_string = ['']
            query_num = 0
            for i, col in enumerate(response["workItems"]):
                id_string[query_num] += str(col['id']) + ","
                if i != 0 and i % 100 == 0: 
                    query_num +=1
                    id_string.append('')
            
            for substring in id_string:
                query_api = (self.url + 
                            "_apis/wit/WorkItems?ids=" + substring[:-1] +
                            "&fields=" + attributes[:-1] +
                            "&asOf=" + response["asOf"] + 
                            "&api-version=1.0")
                query_response = self.session.get(query_api).json()
                
                for i, each in enumerate(query_response["value"]):
                    wit_dataframe = wit_dataframe.append(each['fields'], ignore_index=True)
            
            wit_dataframe = wit_dataframe.rename(columns={
                    'System.AssignedTo': 'Employee', 
                    'Microsoft.VSTS.Common.Activity': 'Work activity', 
                    'Microsoft.VSTS.Scheduling.CompletedWork': 'Completed hours',
                    'Microsoft.VSTS.Scheduling.OriginalEstimate': 'Estimated'})
            wit_dataframe['Completed hours'] = wit_dataframe['Completed hours'].fillna(0)
            wit_dataframe['Estimated'] = wit_dataframe['Estimated'].fillna(0)
            wit_dataframe['Work activity'] = wit_dataframe['Work activity'].fillna('undefined')
            wit_dataframe['Employee'] = wit_dataframe['Employee'].fillna('Not assigned')
            if not detail:
                wit_dataframe = wit_dataframe.groupby(['Employee']).agg({'Completed hours':np.sum, 'Estimated':np.sum})
            else:
                wit_dataframe = wit_dataframe.groupby(['Employee', 'Work activity']).agg({'Completed hours':np.sum, 'Estimated':np.sum})
            return wit_dataframe

        else:
            response.raise_for_status()  


    def get_time_report(self,project, from_date, to_date):
        tfs_api = self.url + project + '/_apis/wit/wiql?api-version=1.0'

        query = Query("WorkItems")
        query.select('System.AssignedTo')
        query.select('Microsoft.VSTS.Common.Activity')
        query.select('Microsoft.VSTS.Scheduling.OriginalEstimate')
        query.select('Microsoft.VSTS.Scheduling.CompletedWork')
        query.where('System.WorkItemType', '=', 'Task')
        query.where('System.TeamProject', '=', '@project')
        query.where('Microsoft.VSTS.Common.ClosedDate', '>=', from_date)
        query.where('Microsoft.VSTS.Common.ClosedDate', '<=', to_date)
        query.orderby('System.AssignedTo', 'asc')

        response = self.session.post(url=tfs_api, json={"query": str(query)})
        

        if(response.ok):
            response = response.json()
            task_dict = Wit({'id':'root node'})

            attributes = ""
            for col in response["columns"]:
                attributes += col['referenceName'] + ","
                
            id_string = ['']
            query_num = 0
            for i, col in enumerate(response["workItems"]):

                wit = Wit(json_content = col)
                task_dict.add_child(child = wit)

                id_string[query_num] += str(col['id']) + ","
                if i != 0 and i % 100 == 0: 
                    query_num +=1
                    id_string.append('')
            
            for substring in id_string:
                query_api = (self.url + 
                            "_apis/wit/WorkItems?ids=" + substring[:-1] +
                            "&fields=" + attributes[:-1] +
                            "&asOf=" + response["asOf"] + 
                            "&api-version=1.0")
                query_response = self.session.get(query_api).json()
                
                update_table = query_response["value"]
                if update_table and 'Message' not in update_table:
                    task_dict.update_all(json_table = update_table)

            return task_dict

        else:
            response.raise_for_status()

    def get_feature_tree_index(self, project, from_date, to_date):
        tfs_api = self.url + project + '/_apis/wit/wiql?api-version=1.0'

        query = Query("WorkItemLinks")
        query.select('System.Title')
        query.select('System.WorkItemType')
        query.select('System.AssignedTo')
        query.select('CUB.Field.CostOwner')
        query.select('CUB.Field.Eticket')
        query.select('Microsoft.VSTS.Scheduling.OriginalEstimate')
        query.select('Microsoft.VSTS.Scheduling.CompletedWork')
        query.where('System.TeamProject', '=', '@project', source = True)
        query.where('System.WorkItemType', '=', 'Feature', source = True)
        query.where('System.Links.LinkType', '=', 'System.LinkTypes.Hierarchy-Forward')
        query.where('System.TeamProject', '=', '@project', target = True)
        query.where('System.WorkItemType', '=', 'Task', target = True)
        query.where('System.State', '=', 'Closed', target = True)
        query.where('Microsoft.VSTS.Common.ClosedDate', '>=', from_date, target = True)
        query.where('Microsoft.VSTS.Common.ClosedDate', '<=', to_date, target = True)
        query.mode(type = "recursive", match = "ReturnMatchingChildren")
        query.orderby('Microsoft.VSTS.Common.ClosedDate', 'asc', target = True)

        response = self.session.post(url=tfs_api, json={"query": str(query)})

        if response.ok:
            return response.json()
        else:
            return response.raise_for_status()

    def get_feature_tree(self, project, from_date, to_date, detail=False):
        try: 
            response = self.get_feature_tree_index(project, from_date, to_date)
        except:
            return None

        # Build initial tree of WIT
        feature_dict = Wit({'id':'root node'})

        # Get list of WIT fields to retrieve
        attributes = ""
        for col in response["columns"]:
            attributes += col['referenceName'] + ","
        
        # Get list of WITs to retrieve
        id_string = ['']
        query_num = 0
        for i, col in enumerate(response["workItemRelations"]):
            if i != 0 and i % 100 == 0: 
                query_num +=1
                id_string.append('')
            feature = Wit(json_content = col['target'])
            id_string[query_num] += str(feature.get_id()) + ','
            if 'source' not in col:
                feature_dict.add_child(child = feature)
            else:
                feature_dict.add_descendant(parent_id = col['source']['id'], child = feature)

        # Update tree of WIT with their fields value
        for substring in id_string:
            query_api = (self.url + 
                        "_apis/wit/WorkItems?ids=" + substring[:-1] +
                        "&fields=" + attributes[:-1] +
                        "&asOf=" + response["asOf"] + 
                        "&api-version=1.0")
            query_response = self.session.get(query_api).json()


            update_table = query_response["value"]
            if update_table and 'Message' not in update_table:
                feature_dict.update_all(json_table = update_table)
        return feature_dict
        

    def get_my_requests(self, state = 'Active'):
        tfs_api = self.url + '_apis/wit/wiql?api-version=1.0'

        query = Query("WorkItems")
        query.select('System.Id')
        query.select('System.Title')
        query.select('System.TeamProject')
        query.select('System.Description')
        query.select('CUB.Field.Eticket')
        query.where('System.WorkItemType', '=', 'Feature')
        query.where('System.State', '=', state)
        query.where('System.CreatedBy', '=', '@me')
        query.orderby('System.CreatedDate', 'asc')

        response = self.session.post(url=tfs_api, json={"query": str(query)})
        wit_dataframe = DataFrame(
            columns=[
            'System.Id', 
            "System.Title",
            "System.TeamProject", 
            "System.Description",
            'CUB.Field.Eticket'])
        if(response.ok):
            response = response.json()
            
            attributes = ""
            for col in response["columns"]:
                attributes += col['referenceName'] + ","
                
            id_string = ['']
            query_num = 0
            for i, col in enumerate(response["workItems"]):
                id_string[query_num] += str(col['id']) + ","
                if i != 0 and i % 100 == 0: 
                    query_num +=1
                    id_string.append('')
            
            for substring in id_string:
                query_api = (
                    self.url + 
                    "_apis/wit/WorkItems?ids=" + substring[:-1] +
                    "&fields=" + attributes[:-1] +
                    "&asOf=" + response["asOf"] + 
                    "&api-version=1.0")
                query_response = self.session.get(query_api).json()
                if 'Message' in query_response["value"]: 
                    wit_dataframe = wit_dataframe.rename(columns={
                        'System.Id': 'Id', 
                        'System.Title': 'Title', 
                        'System.TeamProject': 'Project',
                        'System.Description': 'Description', 
                        'CUB.Field.Eticket': 'E-ticket'})
                    return wit_dataframe
                for i, each in enumerate(query_response["value"]):
                    wit_dataframe = wit_dataframe.append(each['fields'], ignore_index=True)
            
            wit_dataframe = wit_dataframe.rename(columns={
                'System.Id': 'Id', 
                'System.Title': 'Title', 
                'System.TeamProject': 'Project',
                'System.Description': 'Description', 
                'CUB.Field.Eticket': 'E-ticket'})

            wit_dataframe['Title'] = wit_dataframe['Title'].fillna('Not assigned')
            wit_dataframe['Project'] = wit_dataframe['Project'].fillna('Not assigned')
            wit_dataframe['Description'] = wit_dataframe['Description'].fillna('Not defined')
            wit_dataframe['E-ticket'] = wit_dataframe['E-ticket'].fillna('Not defined')
            return wit_dataframe

        else:
            response.raise_for_status()

    def create_request(self, project, title, description, e_ticket):
        tfs_api = self.url + project + '/_apis/wit/workitems/$Feature?api-version=1.0'
        patch = []
        patch.append(dict(op="add", path="/fields/System.Title", value=title))
        patch.append(dict(op="add", path="/fields/System.Description", value=description))
        patch.append(dict(op="add", path="/fields/CUB.Field.Eticket", value=e_ticket))
        headers = {'Content-Type': 'application/json-patch+json'}

        response = self.session.patch(url=tfs_api, json=patch, headers = headers)

        if(response.ok):
            app.logger.debug('Request created: %s', response.json())
        else:
            app.logger.debug('Request failed: %s', response)

    def get_permissions(self, securitynamespace='00000000-0000-0000-0000-000000000000'):
        tfs_api = self.url + '_apis/securitynamespaces/' + securitynamespace + '/?api-version=1.0'
        response = self.session.get(url=tfs_api)
        if(response.ok):
            permissions = response.json()['value']
            return {permission['name']: permission for permission in permissions}
        else:
            response.raise_for_status()

    def get_projects(self):
        tfs_api = self.url + '_apis/projects?api-version=2.2'
        response = self.session.get(url=tfs_api)
        if(response.ok):
            projects = response.json()['value']
            return {project['name']: project for project in projects}
        else:
            response.raise_for_status()

    def get_project_areas(self, project):
        tfs_api = self.url + project + '/_apis/wit/classificationnodes/areas?$depth=2'
        response = self.session.get(url=tfs_api)
        if(response.ok):
            try:
                areas = response.json()['children']
                return {area['name']: area for area in areas}
            except:
                return None
        else:
            response.raise_for_status()

    def get_teams(self, project):
        tfs_api = self.url + '_apis/projects/' + project + '/teams?api-version=2.2'
        response = self.session.get(url=tfs_api)
        if(response.ok):
            teams = response.json()['value']
            return {team['name']: team for team in teams}
        else:
            response.raise_for_status()

    def get_members(self, project, team):
        tfs_api = self.url + '_apis/projects/' + project + '/teams/'+ team +'/members?api-version=2.2'
        response = self.session.get(url=tfs_api)
        if(response.ok):
            members = response.json()['value']
            return {member['uniqueName']: member for member in members}
        else:
            response.raise_for_status()


    def get_project_members(self, project):
        teams = self.get_teams(project = project)
        for team_name, team in teams.iteritems():
            team['members'] = self.get_members(project, team_name)
        return teams

    def get_repositories(self, project = None):
        if project:
            tfs_api = self.url + project + '/_apis/git/repositories?api-version=1.0'
        else:
            tfs_api = self.url + '_apis/projects/_apis/git/repositories?api-version=1.0'
        response = self.session.get(url=tfs_api)
        if(response.ok):
            repositories = response.json()['value']
            print('resp = ' + str(repositories))
            return {repository['name']: repository for repository in repositories}
        else:
            response.raise_for_status()
