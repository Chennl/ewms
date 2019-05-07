from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
from flask_login import LoginManager
 
import logging,os
from logging.handlers import RotatingFileHandler,SMTPHandler




from flask_moment import Moment

# naming_convention = {
#     "ix": 'ix_%(column_0_label)s',
#     "uq": "uq_%(table_name)s_%(column_0_name)s",
#     "ck": "ck_%(table_name)s_%(column_0_name)s",
#     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#     "pk": "pk_%(table_name)s"
# }
#db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message =  '请登入后访问应该网页'#Please log in to access this page.'
moment = Moment()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    # #for Vue前台项目

    # # 通过 static_folder 指定静态资源路径，以便 index.html 能正确访问 CSS 等静态资源
    # # template_folder 指定模板路径，以便 render_template 能正确渲染 index.html
    # APP = Flask(
    #     __name__, static_folder="../dist/static", template_folder="../dist")

    # #for Vue前台项目  结束


    db.init_app(app)
    migrate.init_app(app,db)
    login.init_app(app)
    moment.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.materials import bp as materials_bp
    app.register_blueprint(materials_bp,url_prefix='/material')

    from app.projects import bp as projects_bp
    app.register_blueprint(projects_bp,url_prefix='/project')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.warehouse import bp as warehouse_bp
    app.register_blueprint(warehouse_bp, url_prefix='/warehouse')

    #init  folders
    if not os.path.exists(app.config['UPLOAD_FOLDER_PATH']):
        os.mkdir(app.config['UPLOAD_FOLDER_PATH'])
    if not os.path.exists(app.config['LOGGING_FOLDER_PATH']):
        os.mkdir(app.config['LOGGING_FOLDER_PATH'])

    file_handler = RotatingFileHandler('logs/ewms.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter( '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('ewms startup')

    #  if app.config['MAIL_SERVER']:
    #     auth = None
    #     if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
    #         auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    #     secure = None
    #     if app.config['MAIL_USE_TLS']:
    #         secure = ()
    #     mail_handler = SMTPHandler(
    #         mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
    #         fromaddr='no-reply@' + app.config['MAIL_SERVER'],
    #         toaddrs=app.config['ADMINS'], subject='Microblog Failure',
    #         credentials=auth, secure=secure)
    #     mail_handler.setLevel(logging.ERROR)
    #     app.logger.addHandler(mail_handler)

    return app
 
from app import models 