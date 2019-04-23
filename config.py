import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

#import a .env file before the Config class is created
load_dotenv(os.path.join(basedir,'.env'))

class Config(object):
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'ews.db')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/my753721'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

 

    
    SECRET_KEY = os.environ.get('SECRET_KEY') or "093BE540-764A-4ABD-882D-F1196956A658"
     
    MATERIALS_PER_PAGE = 30
    PROJECTS_PER_PAGE = 10



    MAIL_SERVER='smtp.126.com'
    MAIL_PORT='25'
    MAIL_USE_TLS=1
    MAIL_USERNAME='chennl_hz@126.com'
    MAIL_PASSWORD='chennl1975a'


    UPLOAD_FOLDER_PATH = os.path.join(basedir, 'uploads')
    LOGGING_FOLDER_PATH = os.path.join(basedir, 'logs')