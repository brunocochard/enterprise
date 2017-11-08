class DefaultConfig(object):
    DEBUG=True
    TFS_USER="tfs"
    TFS_PWD="P@ssw0rd"
    TFS_SERVER="alm"
    TFS_PORT=8080
    TFS_COLLECTION="DefaultCollection"
    TFS_PROJECT="my_project"
    SECRET_KEY='somethinglongthatisratherdifficulttoremember'
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR='C:\../../Source\session'
    TIMESHEET_TIMER = 10
    
class AcceptanceConfig(DefaultConfig):
    TFS_SERVER="alm01"
    TFS_PROJECT="Digital"

    
class ProductionConfig(DefaultConfig):
    DEBUG=True
    TFS_USER=""
    TFS_PWD=""
    TFS_SERVER="alm"
    TIMESHEET_TIMER = 900
