from app import app, login_manager
from flask_login import UserMixin
from tfs.client import TFS_session

logged_users = {}

@login_manager.user_loader
def load_user(user_id):
    if user_id in logged_users:
        return logged_users[user_id]
    return None

class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.namespace = None
        self.tfs = TFS_session(
                username = username, 
                password = password, 
                server =  "http://" + app.config['TFS_SERVER'] + ":" + str(app.config['TFS_PORT']) + "/"
                )
    
    def is_connected(self):
        return self.tfs.is_connected()

    def post(self, url, json):
        return self.tfs.session.post(url, json=json)

    def __repr__(self):
        return self.id

    def get_id(self):
        return self.id

    def run_tfs(self):
        return self.tfs

    def set_namespace(self, namespace):
        self.namespace = namespace

    def get_namespace(self):
        return self.namespace

    def get_my_activities(self, state = 'Active'):
        return self.tfs.get_my_activities(state)

    def get_my_requests(self, state = 'Active'):
        return self.tfs.get_my_requests(state)

    def get_all_projects(self):
        return self.tfs.get_all_projects()

    def get_epics(self, project):
        return self.tfs.get_epics(project = project)

    def run(self):
        return self.tfs

    def get_activities(self, project, from_date, to_date, detail):
        return self.tfs.get_activities(
            project = project, 
            from_date = from_date, 
            to_date = to_date,
            detail = detail)

    def get_time_report(self, project, from_date, to_date):
        return self.tfs.get_time_report(
            project = project, 
            from_date = from_date, 
            to_date = to_date)

    def get_feature_tree(self, project, from_date, to_date, detail):
        return self.tfs.get_feature_tree(
            project = project, 
            from_date = from_date, 
            to_date = to_date,
            detail = detail)

    def create_request(self, project, title, description, e_ticket):
        return self.tfs.create_request( 
            project= project, 
            title = title, 
            description = description,
            e_ticket= e_ticket)
